from __future__ import print_function

from builtins import str
import traceback
import sys
import pandas
import random

from tqdm import tqdm

from django.db.models import Q
from django.db import connection, models
from django.core.exceptions import EmptyResultSet
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from pewtils import chunk_list, is_null, decode_text, vector_concat_text
from django_pewtils import field_exists, filter_field_dict, get_model, inspect_delete
from pewanalytics.text import TextDataFrame, get_fuzzy_partial_ratio, get_fuzzy_ratio


def _create_object(
    model,
    unique_data,
    update_data=None,
    save_nulls=False,
    empty_lists_are_null=True,
    allow_list_overlaps=False,
    logger=None,
    command_log=None,
):

    """
    This function attempts to create a new object using the provided unique_data and update_data dictionaries.
    It will automatically skip over fields that don't exist, and will determine whether to skip over null values based
    on the save_nulls and empty_lists_are_null parameters.

    :param model: The model the object is on
    :param unique_data: A dictionary of query filtering parameters that must, taken together, be unique to the object
    being created
    :param update_data: A dictionary of fields to update once the object is created
    :param save_nulls: Whether or not to save null values in `update_data`
    :param empty_lists_are_null: Whether or not empty lists should be considered null
    :param logger: Optional logging object
    :return: The created object
    """

    warning = ""
    try:
        # if not save_nulls:  # I (Patrick) removed this since you always want to drop __ filter fields from
        # unique data before creating an object. the slight additional overhead of always running filter_field_dict
        # even when save_nulls is True is offset by the benefit of being able to use filter searches in
        # create_or_update (see the mturk_trust_code command for an example, where code__variable is a unique constraint
        unique_data = filter_field_dict(
            unique_data,
            drop_nulls=(not save_nulls),
            empty_lists_are_null=empty_lists_are_null,
        )
        if update_data:
            update_data = filter_field_dict(
                update_data,
                drop_nulls=(not save_nulls),
                empty_lists_are_null=empty_lists_are_null,
            )
        original_unique_data = unique_data
        if update_data:
            for field in list(update_data.keys()):
                if field_exists(model, field) and field not in list(unique_data.keys()):
                    unique_data[field] = update_data[field]
        try:
            existing = model.objects.create(**unique_data)
            existing = model.objects.get(pk=existing.pk)
        except Exception as e:
            # NOTE - this happened once when the database connection cut out; just had to try running it again
            try:
                existing = get_model(model._meta.model_name).objects.create(
                    **unique_data
                )
                existing = get_model(model._meta.model_name).objects.get(
                    pk=existing.pk
                )  # refresh data
            except:
                existing = get_model(model._meta.model_name).objects.filter(
                    **original_unique_data
                )
                if existing.count() == 1:
                    existing = existing[0]
                    for key, value in update_data.items():
                        setattr(existing, key, value)
                    existing.save()
                else:
                    raise e
            # for some reason, django can have issues when using a custom manager and a custom save function
            # so, for example, saving Document objects can raise an IntegrityError (it thinks there's a duplicate
            # primary key) but "refreshing" the manager by reloading the model seems to resolve these issues, in the
            # rare event that it happens
        if logger:
            logger.info("Created new %s %s" % (str(model), str(unique_data)))
        if command_log and hasattr(existing, "command_logs"):
            existing.command_logs.add(command_log)
            existing.commands.add(command_log.command)
    except:
        if logger:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.info(
                "%s %s %s %s"
                % (str(exc_type), str(exc_value), str(traceback.format_exc()), warning)
            )
        raise

    return existing


def _update_object(
    model,
    existing,
    update_data=None,
    save_nulls=False,
    empty_lists_are_null=True,
    only_update_existing_nulls=False,
    allow_list_overlaps=False,
    logger=None,
    command_log=None,
    **save_kwargs
):

    """
    This function updates an existing object in a manner very similar to _create_object.  The "save_nulls" parameter
    determines whether or not null values should be saved to the existing object.  The "empty_lists_are_null" parameter
    determines whether or not empty lists should be treated as nulls.  The "only_update_existing_nulls" parameter
    determines whether or not existing data on the object will be overwritten; if True, then only empty fields
    will be written, and existing non-null data will be preserved.

    :param model: The model the object belongs to
    :param existing: The existing object
    :param update_data: A dictionary of fields and values to update the object with
    :param save_nulls: Whether or not to update the object with null values that exist in `update_data`
    :param empty_lists_are_null: Whether or not to consider empty lists as being null
    :param only_update_existing_nulls: If `True`, only update fields on the object that existing in `update_data` if
    the current value on the object is None
    :param allow_list_overlaps:
    :param logger: An optional logging object
    :return: The updated object
    """

    if update_data:
        try:
            update_data = filter_field_dict(
                update_data,
                drop_nulls=(not save_nulls),
                empty_lists_are_null=empty_lists_are_null,
            )
            for field in list(update_data.keys()):
                if field_exists(model, field) and (
                    not only_update_existing_nulls
                    or is_null(
                        getattr(existing, field),
                        empty_lists_are_null=empty_lists_are_null,
                    )
                ):
                    if (
                        isinstance(getattr(existing, field), list)
                        and allow_list_overlaps
                    ):
                        vals = list(getattr(existing, field))
                        for val in update_data[field]:
                            if val not in vals:
                                vals.append(val)
                        setattr(existing, field, vals)
                    else:
                        setattr(existing, field, update_data[field])
            existing.save(**save_kwargs)
            if command_log and hasattr(existing, "command_logs"):
                existing.command_logs.add(command_log)
                existing.commands.add(command_log.command)
        except Exception:
            if logger:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.info(
                    "%s %s %s"
                    % (str(exc_type), str(exc_value), str(traceback.format_exc()))
                )
            raise

    return existing


class BasicExtendedManager(models.QuerySet):

    """
    An extension of a Django QuerySet with additional helper functions. Can be used as a manager on any model like so:

    .. code-block:: python

        class MyModel(models.Model):
            objects = BasicExtendedManager().as_manager()

    """

    def __init__(self, *args, **kwargs):

        super(BasicExtendedManager, self).__init__(*args, **kwargs)
        self.functions = {}
        self.default_function = None

    def to_df(self):

        """
        Returns the QuerySet as a Pandas DataFrame, reading directly from the table in SQL.

        :return: A Pandas DataFrame of the QuerySet objects.
        """

        try:
            query, params = self.query.sql_with_params()
        except EmptyResultSet:
            return pandas.DataFrame()

        return pandas.io.sql.read_sql_query(query, connection, params=params)

    def chunk(self, size=100, tqdm_desc=None, randomize=False):

        """
        Helps save memory by iterating over the primary keys of objects in a QuerySet and yielding the results in
        chunks rather than all at once.

        :param size: The number of objects to load in each chunk. Larger values will be more efficient but require
        more memory.
        :param tqdm_desc: Optional description to use in the progress bar while looping over the QuerySet.
        :param randomize: Whether or not to randomly sort the objects in the QuerySet.
        :return: An iterable that yields each object in the QuerySet.
        """

        ids = self.values_list("pk", flat=True)
        if randomize:
            ids = list(ids)
            random.shuffle(ids)
        if tqdm_desc:
            iterator = tqdm(chunk_list(ids, size), desc=tqdm_desc)
        else:
            iterator = chunk_list(ids, size)
        for chunk in iterator:
            for obj in self.model.objects.filter(pk__in=chunk):
                yield obj

    def sample(self, size):

        """
        Draws a random sample from a QuerySet.

        :param size: The size of the sample
        :return: A QuerySet representing the sampled objects
        """

        ids = self.values_list("pk", flat=True)
        ids = list(ids)
        random.shuffle(ids)
        sample = ids[:size]

        return self.model.objects.filter(pk__in=sample)

    def chunk_update(self, size=100, tqdm_desc="Updating", **to_update):

        """
        Iterates over a QuerySet and applies an update to them in chunks rather than all at once, to save memory.

        :param size: The size of each chunk. Larger chunk sizes will be more efficient but cost more memory.
        :param tqdm_desc: Optional description for the progress bar
        :param to_update: A dictionary of fields and values to update them to. Operates like Django's `update` function
        """

        ids = self.values_list("pk", flat=True)
        if tqdm_desc:
            iterator = tqdm(chunk_list(ids, size), desc=tqdm_desc)
        else:
            iterator = chunk_list(ids, size)
        for chunk in iterator:
            self.model.objects.filter(pk__in=chunk).update(**to_update)

    def chunk_delete(self, size=100, tqdm_desc="Deleting"):

        """
        Iterates over a QuerySet and deletes objects in chunks rather than all at once, to save memory.

        :param size: The size of each chunk. Larger chunk sizes will be more efficient but cost more memory.
        :param tqdm_desc: Optional description for the progress bar
        """

        ids = self.values_list("pk", flat=True)
        if tqdm_desc:
            iterator = tqdm(chunk_list(ids, size), desc=tqdm_desc)
        else:
            iterator = chunk_list(ids, size)
        for chunk in iterator:
            self.model.objects.filter(pk__in=chunk).delete()

    def inspect_delete(self, counts=False):

        """
        Returns a dictionary of all of the objects that would be deleted were you to call `.delete()` on the QuerySet.
        Keys are models and values are either the count or a QuerySet of model objects, depending on `count`.

        :param counts: Whether or not to return counts.
        :return: Dictionary of objects (or counts of objects) to be deleted, by model.
        """

        return inspect_delete(self.all(), counts=counts)

    def get_if_exists(
        self,
        unique_data,
        match_any=False,
        search_nulls=False,
        empty_lists_are_null=True,
        allow_list_overlaps=False,
        logger=None,
    ):

        """
        This function takes a dictionary of key-value pairs that specify one or more fields for a given model, and the
        value that each field should take, respectively. In effect, this allows you to use dictionaries to apply
        complex multi-condition queries to fetch particular objects, based on the assumption that the combination of
        conditions passed via unique_data should refer to one, and only one, object within this model. It will return
        None if no objects match the conditions specified, or raise a MultipleObjectsReturned error if the query
        parameters were not unique in their combination and returned more than one object.

        :param unique_data: A dictionary of filter values, e.g. Model.objects.get_if_exists({"year_id": 2016})
        :param match_any: If True, returns a match if ANY of the keys in the unique_data dictionary select an object
        :param search_nulls: If False (default), it will ignore unique_data keys with null values
        :param empty_lists_are_null: If True (default), it will treat empty lists the same as it does null values
        (otherwise it will treat them like non-nulls)
        :param logger: Optional logger for recording errors
        :return: The object, if it was found successfully
        """

        search_data = filter_field_dict(
            unique_data,
            drop_nulls=(not search_nulls),
            empty_lists_are_null=empty_lists_are_null,
            drop_underscore_joins=False,
        )
        if len(list(search_data.keys())) > 0:

            if allow_list_overlaps:
                for k in list(search_data.keys()):
                    if isinstance(search_data[k], list):
                        search_data["{}__overlap".format(k)] = search_data[k]
                        del search_data[k]

            existing = None
            try:
                if match_any:
                    query = Q()
                    for field in list(search_data.keys()):
                        query |= Q(**{field: search_data[field]})
                    existing = self.filter(query).distinct()
                    if existing.count() > 1:
                        raise self.model.MultipleObjectsReturned
                    elif existing.count() == 0:
                        raise self.model.DoesNotExist
                    else:
                        existing = existing[0]
                else:
                    existing = self.get(**search_data)
            except self.model.DoesNotExist:
                existing = None
            except self.model.MultipleObjectsReturned:
                if logger:
                    logger.error(
                        "%s get_if_exists query on %s returned multiple rows"
                        % (str(search_data), str(self.model))
                    )
                print("Data passed: %s" % str(unique_data))
                print("Data searched: %s" % str(search_data))
                if existing:
                    print("Objects matched: {}".format(existing))
                else:
                    print(
                        "Objects matched: %s"
                        % str(list(self.filter(**search_data).values()))
                    )
                raise
        else:
            existing = None

        return existing

    def create_or_update(
        self,
        unique_data,
        update_data=None,
        match_any=False,
        return_object=True,
        search_nulls=False,
        save_nulls=False,
        empty_lists_are_null=True,
        only_update_existing_nulls=False,
        allow_list_overlaps=False,
        logger=None,
        command_log=None,
        force_create=False,
        **save_kwargs
    ):
        """
        This function builds off of the get_if_exists function, and allows you to pass a dictionary of unique_data
        values to:
            * Select an object, if it exists
            * If it doesn't exist, combine unique_data and any additional values in update_data, and create a new object
            * If it does exist, update the object with any additional values in update_data
            * Return the object, if return_object=True

        This can be used to very flexibly define a unique object, along with additional fields that shouldn't be part
        of an object's "uniqueness", and then take any and all steps needed to ensure that the object exists and has
        the properties that you want it to have.

        :param unique_data: A dictionary of filter values, e.g. Model.objects.create_or_update({"id_field": id})
        :param update_data: A dictionary with data with which to update the object (keys that do not exist as fields on
        the object will be ignored)
        :param match_any: If True, returns a match if ANY of the keys in the unique_data dictionary select an object
        :param return_object: If True, the updated object will be returned (otherwise nothing gets returned)
        :param search_nulls: If False (default), it will ignore unique_data keys with null values
        :param save_nulls: If True, null values will be saved and will overwrite existing data (default False, which
        skips over null values)
        :param empty_lists_are_null: If True (default), it will treat empty lists the same as it does null values
        (otherwise it will treat them like non-nulls)
        :param only_update_existing_nulls: If True, the object will only be update currently-null fields with non-null
        values (values that already exist will not be updated)
        :param logger: Optional logger for recording errors
        :param command_log: Optional `django_commander.CommandLog` object, which will be added to the selected object's
        many-to-many command/command_log fields, if it has them
        :param force_create: If True, this function will assume that the object does not exist and will skip the
        get_if_exists check
        :return: The created or updated object
        """

        if force_create:
            existing = None
        else:
            existing = self.get_if_exists(
                unique_data,
                match_any=match_any,
                search_nulls=search_nulls,
                empty_lists_are_null=empty_lists_are_null,
                allow_list_overlaps=allow_list_overlaps,
                logger=logger,
            )
        if not existing:
            try:
                existing = _create_object(
                    self.model,
                    unique_data,
                    update_data=update_data,
                    save_nulls=save_nulls,
                    empty_lists_are_null=empty_lists_are_null,
                    allow_list_overlaps=allow_list_overlaps,
                    logger=logger,
                    command_log=command_log,
                )
            except Exception as e:
                existing = self.get_if_exists(
                    unique_data,
                    match_any=match_any,
                    search_nulls=search_nulls,
                    empty_lists_are_null=empty_lists_are_null,
                    allow_list_overlaps=allow_list_overlaps,
                    logger=logger,
                )
                if existing:
                    existing = _update_object(
                        self.model,
                        existing,
                        update_data=update_data,
                        save_nulls=save_nulls,
                        empty_lists_are_null=empty_lists_are_null,
                        only_update_existing_nulls=only_update_existing_nulls,
                        allow_list_overlaps=allow_list_overlaps,
                        logger=logger,
                        command_log=command_log,
                        **save_kwargs
                    )
                else:
                    raise e
        elif update_data:
            existing = _update_object(
                self.model,
                existing,
                update_data=update_data,
                save_nulls=save_nulls,
                empty_lists_are_null=empty_lists_are_null,
                only_update_existing_nulls=only_update_existing_nulls,
                allow_list_overlaps=allow_list_overlaps,
                logger=logger,
                command_log=command_log,
                **save_kwargs
            )
        else:
            if command_log and hasattr(existing, "command_logs"):
                existing.command_logs.add(command_log)
                existing.commands.add(command_log.command)
        if return_object:
            return existing

    def fuzzy_ratios(
        self,
        field_names,
        text,
        min_ratio=None,
        allow_partial=False,
        max_partial_difference=100,
    ):
        """
        Given a snippet of text, computes the fuzzy ratios between the text and text that is stored on one or more
        fields on all of the objects in the QuerySet.

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :param min_ratio: The minimum fuzzy ratio allowed to return results.
        :param allow_partial: Whether or not to allow partial fuzzy ratios when computing text similarity.
        :param max_partial_difference: The maximum difference between the absolute and partial ratio that's
        allowed to return a result.
        :return: A list of results with the primary keys of the compared objects and their fuzzy ratios
        """

        results = []
        for row in self.values("pk", *field_names):
            result = row
            row["fuzzy_ratio"] = get_fuzzy_ratio(
                " ".join([row[field_name] for field_name in field_names]), text
            )
            if allow_partial:
                partial_ratio = get_fuzzy_partial_ratio(
                    " ".join([row[field_name] for field_name in field_names]), text
                )
                substring_variation = abs(result["fuzzy_ratio"] - partial_ratio)
                row["fuzzy_ratio"] = max([row["fuzzy_ratio"], partial_ratio])
            if (not min_ratio or row["fuzzy_ratio"] >= min_ratio) and (
                not allow_partial or substring_variation <= max_partial_difference
            ):
                results.append(result)

        return sorted(results, key=lambda x: x["fuzzy_ratio"], reverse=True)

    def fuzzy_ratio_best_match(
        self,
        field_names,
        text,
        min_ratio=None,
        allow_partial=False,
        max_partial_difference=100,
    ):

        """
        Returns the object with the greatest fuzzy ratio in the QuerySet. Equivalent to calling:

        .. code-block:: python

            >>> result = my_query_set.fuzzy_ratios(["text_field"], "test")
            >>> MyModel.objects.get(pk=result[0].pk)

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :param min_ratio: The minimum fuzzy ratio allowed to return results.
        :param allow_partial: Whether or not to allow partial fuzzy ratios when computing text similarity.
        :param max_partial_difference: The maximum difference between the absolute and partial ratio that's
        allowed to return a result.
        :return: A tuple of the object in the QuerySet that has the greatest similarity to the provided text, and
        its fuzzy ratio
        """

        results = self.fuzzy_ratios(
            field_names,
            text,
            min_ratio=min_ratio,
            allow_partial=allow_partial,
            max_partial_difference=max_partial_difference,
        )
        if len(results) == 0:
            return None
        else:
            return (self.get(pk=results[0]["pk"]), results[0]["fuzzy_ratio"])

    def levenshtein_differences(self, field_names, text, max_difference=None):

        """
        Given a set of text fields and some comparison text, computes the Levenshtein differences between the
        comparison text and the text that's stored in the fields on the objects in the QuerySet.

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :param max_difference: The maximum difference allowed for a result to be returned.
        :return: A list of results with the primary keys of the compared objects and their Levenshtein differences
        """

        try:
            text = str(text)
        except (UnicodeEncodeError, UnicodeDecodeError):
            text = decode_text(text)
        if len(field_names) > 1:
            search_field = "CONCAT({0})".format(", ' ', ".join(field_names))
        else:
            search_field = field_names[0]
        search_field = "substring({} from 1 for 255)".format(search_field)
        query = self.extra(
            select={
                "difference": "levenshtein({0}, %s) / length({0})::float".format(
                    search_field
                )
            },
            select_params=(text,),
        ).order_by("difference")
        if max_difference:
            query = query.extra(
                where=[
                    "levenshtein({0}, %s) / length({0})::float <= %s".format(
                        search_field
                    )
                ],
                params=[text, max_difference],
            )

        return query.values("pk", "difference", *field_names)

    def levenshtein_difference_best_match(self, field_names, text, max_difference=None):

        """
        Returns the object with the smallest Levenshtein difference in the QuerySet. Equivalent to calling:

        .. code-block:: python

            >>> result = my_query_set.levenshtein_differences(["text_field"], "test")
            >>> MyModel.objects.get(pk=result[0].pk)

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :param max_difference: The maximum difference allowed for a result to be returned.
        :return: A tuple of the object in the QuerySet that has the smallest difference with the provided
        text and its Levenshtein difference
        """

        results = self.levenshtein_differences(
            field_names, text, max_difference=max_difference
        )
        if results.count() == 0:
            return None
        else:
            return (self.get(pk=results[0]["pk"]), results[0]["difference"])

    def tfidf_similarities(self, field_names, text, min_similarity=None):

        """
        Given one or more text fields, computes the TF-IDF cosine similarities between the objects in the QuerySet and
        other and returns a list of results with the primary keys of the compared objects and their similarities.

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :param min_similarity: The minimum similarity allowed for a result to be returned.
        :return: A list of results with the primary keys of the compared objects and their TF-IDF similarities
        """

        df = pandas.DataFrame(list(self.values("pk", *field_names)))
        df["search_text"] = vector_concat_text(*[df[f] for f in field_names])
        h = TextDataFrame(df, "search_text")
        similarities = h.search_corpus(text)
        results = []
        for index, row in similarities.iterrows():
            pk = df.loc[index]["pk"]
            if not min_similarity or row["search_cosine_similarity"] >= min_similarity:
                result = self.model.objects.filter(pk=pk).values("pk", *field_names)[0]
                result["similarity"] = row["search_cosine_similarity"]
                results.append(result)
        return results

    def tfidf_similarity_best_match(self, field_names, text, min_similarity=None):

        """
        Returns the object with the highest TF-IDF cosine similarity in the QuerySet. Equivalent to calling:

        .. code-block:: python

            >>> result = my_query_set.tfidf_similarities(["text_field"], "test")
            >>> MyModel.objects.get(pk=result[0].pk)

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :param min_similarity: The minimum similarity allowed for a result to be returned.
        :return: A tuple of the object in the QuerySet that has the highest similarity with the provided
        text, and its TF-IDF similarity
        """

        results = self.tfidf_similarities(
            field_names, text, min_similarity=min_similarity
        )
        if len(results) == 0:
            return None
        else:
            return (self.get(pk=results[0]["pk"]), results[0]["similarity"])

    def trigram_similarities(self, field_names, text, min_similarity=None):

        """
        Given one or more text fields, computes the trigram similarities between the objects in the QuerySet and other objects in the
        table and returns a list of results with the primary keys of the compared objects and their similarities.
        (Uses Postgres' built-in trigram similarity module)

        :param field_names: The names of the text fields to compare
        :param min_similarity: The minimum similarity allowed for a result to be returned.
        :return: A list of results with the primary keys of the compared objects and their trigram similarities
        """

        try:
            text = str(text)
        except (UnicodeEncodeError, UnicodeDecodeError):
            text = decode_text(text)

        if len(field_names) > 1:
            search_field = "CONCAT({0})".format(", ' ', ".join(field_names))
        else:
            search_field = field_names[0]
        query = self.extra(
            select={"similarity": "similarity({0}, %s)".format(search_field)},
            select_params=(text,),
        ).order_by("-similarity")
        if min_similarity:
            query = query.extra(
                where=["similarity({0}, %s) >= %s".format(search_field)],
                params=[text, min_similarity],
            )

        return query.values("pk", "similarity", *field_names)

    def trigram_similarity_best_match(self, field_names, text, min_similarity=None):

        """
        Returns the object with the highest trigram similarity in the QuerySet. Equivalent to calling:

        .. code-block:: python

            >>> result = my_query_set.trigram_similarities(["text_field"], "test")
            >>> MyModel.objects.get(pk=result[0].pk)

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :param min_similarity: The minimum similarity allowed for a result to be returned.
        :return: A tuple of the object in the QuerySet that has the highest similarity with the provided
        text, and its trigram similarity
        """

        results = self.trigram_similarities(
            field_names, text, min_similarity=min_similarity
        )
        if results.count() == 0:
            return None
        else:
            return (self.get(pk=results[0]["pk"]), results[0]["similarity"])

    def postgres_search(self, field_names, text):

        """
        Runs a Postgres full text search on one or more text fields across a given QuerySet. Returns an
        ordered QuerySet of results with an additional `rank` attribute on each object that scores the matches.

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :return: An ordered QuerySet of search results
        """

        vector = SearchVector(*field_names)
        query = SearchQuery(text)
        return self.annotate(rank=SearchRank(vector, query)).order_by("-rank")
