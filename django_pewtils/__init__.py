from __future__ import print_function
from builtins import object

import shutil
import re
import importlib
import os
import imp
import datetime
import warnings

from itertools import chain
from contextlib import closing
from collections import defaultdict

from pewtils import is_null, is_not_null
from pewtils.io import FileHandler

from django.core.exceptions import ImproperlyConfigured, AppRegistryNotReady
from django.db import transaction

try:
    from django.contrib.admin.utils import NestedObjects
    from django.db import DEFAULT_DB_ALIAS
    from django.apps import apps
    from django.db import IntegrityError
    from django.core.cache import cache
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Case, When
    from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
except (ImproperlyConfigured, AppRegistryNotReady):
    pass


def detect_primary_app():

    """
    Attempts to detect the primary app by looking for `manage.py` and `settings.py`

    :return: The name of the primary app, if found
    :rtype: str
    """

    app_name = None
    if "manage.py" in os.listdir(os.getcwd()):
        with closing(open("manage.py", "r")) as manage_file:
            text = manage_file.read()
        app_names = re.findall(r"[\"\']([^\"\']+)\.settings[\"\']", text)
        if len(app_names) == 1:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                app_name = app_names[0]
    return app_name


def load_app(app_name=None, path=None, env=None):

    """
    Sets up a Django application to run outside of the Django shell. You can also pass this function a path to add to
    the `sys.path` and a dictionary of additional environment variables to add to `os.environ`. The function must
    be able to find a valid `app_name`.settings module to work.

    :param app_name: The name of the Django application (if not provided, will attempt to auto-detect)
    :type app_name: str
    :param path: Optional path to add to the Python path. Can be a list or string.
    :type path: str or list
    :param env: Optional dictionary of variables to add to `os.environ`
    :type env: dict
    """

    if not app_name:
        app_name = detect_primary_app()
        if not app_name:
            raise Exception(
                "Couldn't detect the primary app, please provide the name in `app_name`."
            )

    if not env:
        env = {}
    import os, django

    for k, v in env.items():
        os.environ[k] = v
    if path:
        import sys

        if isinstance(path, list):
            for p in path:
                sys.path.insert(0, p)
        else:
            sys.path.insert(0, path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{}.settings".format(app_name))
    django.setup()


def get_model(name, app_name=None):

    """
    Returns a Django model class via a string lookup. If the string that was passed in fails to match directly to a
    model, several variations will be tried that include lowercasing and removing or swapping out underscores and/or
    spaces. If the string matches to multiple models from different applications, the function will fail to return
    anything. You can provide an optional `app_name` to this function to deal with ambiguous cases.

    :param name: Name of the model
    :type name: str
    :param app_name: Name of the app
    :type app_name: str
    :return: Django model class

    Usage::

        from django_pewtils import get_model

        >> get_model("contenttype")
        django.contrib.contenttypes.models.ContentType

    """

    model = None
    names = [
        name,
        name.lower(),
        name.replace("_", "").replace(" ", ""),
        name.replace("_", "").replace(" ", "").lower(),
        name.replace("_", " "),
        name.replace("_", " ").lower(),
        name.replace(" ", "_"),
        name.replace(" ", "_").lower(),
    ]
    if app_name:
        for name in names:
            try:
                model = apps.get_model(app_name, name)
                break
            except LookupError:
                pass
    else:
        for name in names:
            try:
                model = ContentType.objects.get(model=name).model_class()
                break
            except ContentType.DoesNotExist:
                pass
            except ContentType.MultipleObjectsReturned:
                pass
    if not model:
        print("Couldn't find a model named '{}'".format(name))
        if not app_name:
            print(
                "Try specifying the name of the app; there may be more than one model with this name"
            )
    return model


def reset_django_connection(app_name=None):

    """
    Will reload a Django application and reset the database connection. If an `app_name` is not specified, it will
    search for it in `settings.SITE_NAME`.

    :param app_name: The name of the application to reload/reset (if not provided, will attempt to auto-detect)
    :type app_name: str
    """

    if not app_name:
        app_name = detect_primary_app()
        if not app_name:
            raise Exception(
                "Couldn't detect the primary app, please provide the name in `app_name`."
            )
    load_app(app_name)
    from django.db import connection

    connection.close()


def reset_django_connection_wrapper(app_name=None):

    """
    Decorator for `reset_django_connection`

    :param app_name: The name of the primary app (if not provided, will attempt to auto-detect)
    :return:
    """

    def _reset_django_connection_wrapper(handle):
        def wrapper(self, *args, **options):
            reset_django_connection(app_name)
            return handle(self, *args, **options)

        return wrapper

    return _reset_django_connection_wrapper


def inspect_delete(items, counts=False):

    """
    Takes a QuerySet and determines how deleting it would affect other objects in the database, accounting for
    cascades. Returns a dictionary where keys are each model in the database that will be affected, and the values
    are either QuerySets of the items that will be deleted (if `count=False`) or the number of records that will be
    deleted (if `count=True`).

    :param items: A Django QuerySet
    :param counts: Whether to return QuerySets or counts
    :return: A dictionary representing the objects in various tables that would be deleted

    Usage::

        >>> inspect_delete(Politician.objects.filter(bioguide_id="S000033"), counts=True)
        defaultdict(list,
                    {logos.models.agents.Politician: 1,
                     logos.models.agents.Politician_commands: 21,
                     logos.models.agents.Politician_command_logs: 1112,
                     logos.models.agents.PoliticianPersonalMetric: 47,
                     logos.models.agents.PoliticianPersonalMetric_commands: 27,
                     logos.models.agents.PoliticianPersonalMetric_command_logs: 167,
                     logos.models.media.NewsArticle_relevant_politicians: 96109,
                     logos.models.media.BallotpediaPage: 1,
                     logos.models.media.WikipediaPage: 1,
                     logos.models.media.WikipediaPage_commands: 1,
                     logos.models.media.WikipediaPage_command_logs: 1,
                     logos.models.government.CommitteeMembership: 63,
                     logos.models.government.CommitteeMembership_commands: 63,
                     logos.models.government.CommitteeMembership_command_logs: 63,
                     logos.models.government.Caucus_members: 1,
                     logos.models.government.Bill_cosponsors: 2638,
                     logos.models.government.Vote_votes_for: 3320,
                     logos.models.government.Vote_votes_against: 1918,
                     logos.models.government.Vote_votes_abstained: 343,
                     logos.models.government.LegislativeHearing_attendees: 1059})


    """

    collector = NestedObjects(using=DEFAULT_DB_ALIAS)
    collector.collect(items)

    def _collapse_results(result, to_delete):
        if isinstance(result, list):
            for obj in result:
                to_delete = _collapse_results(obj, to_delete)
        else:
            to_delete[result._meta.model].append(result.pk)
        return to_delete

    to_delete = _collapse_results(collector.nested(), defaultdict(list))
    for model, ids in to_delete.items():
        if counts:
            to_delete[model] = model.objects.filter(pk__in=ids).count()
        else:
            to_delete[model] = model.objects.filter(pk__in=ids)
    return to_delete


def filter_field_dict(
    dict, drop_nulls=True, empty_lists_are_null=False, drop_underscore_joins=True
):

    """
    A utility function that clears out the contents of a dictionary based on boolean toggles.

    :param dict: Dictionary of values to prune
    :param drop_nulls: If True (default=True), keys with null values are deleted (using utils.is_null())
    :param empty_lists_are_null: If True (default=False), empty lists are considered null
    :param drop_underscore_joins: If True (default=True), keys that contain "__" are dropped
    :return: The pruned dictionary
    """

    if dict:
        for k in list(dict.keys()):
            if (drop_underscore_joins and "__" in k) or (
                drop_nulls
                and is_null(dict[k], empty_lists_are_null=empty_lists_are_null)
            ):
                del dict[k]

        if "content_object" in list(dict.keys()):
            dict["content_type"] = ContentType.objects.get_for_model(
                dict["content_object"]
            )
            dict["object_id"] = dict["content_object"].pk
            del dict["content_object"]

    return dict


def field_exists(model, field):

    """
    Checks whether a field exists on a model

    :param model: The model class to check
    :param field: The name of the field
    :return: True if the field exists on the model, else False
    """

    return field in get_all_field_names(model)


def get_all_field_names(model):

    """
    Returns a list of all field names on a given model.

    :param model: A Django model class
    :return: List of field names

    Usage::

        from django_pewtils import get_all_field_names

        >>> get_all_field_names(Politician)
        ['id', 'first_name', 'nickname', 'last_name', 'fec_ids', 'bioguide_id', 'icpsr_ids', 'instagram_ids']


    """

    return list(
        set(
            chain.from_iterable(
                (field.name, field.attname)
                if hasattr(field, "attname")
                else (field.name,)
                for field in model._meta.get_fields()
                # For complete backwards compatibility, you may want to exclude
                # GenericForeignKey from the results.
                if not (field.many_to_one and field.related_model is None)
            )
        )
    )


class AmbiguousConsolidationError(Exception):

    """
    Exception that gets raised when `consolidate_objects` cannot determine how to collapse dependent objects.
    """

    pass


class ConsolidationCascadeError(Exception):

    """
    Exception that gets raise when `consolidate_objects` must collapse related objects and
    `consolidate_related_uniques` is not enabled
    """

    pass


def consolidate_objects(
    source=None, target=None, overwrite=False, consolidate_related_uniques=False
):

    """
    A function for merging two objects from the same model into a single object; extremely useful for de-duplicating.
    Because the effects of this function cannot be reversed, the required parameters `source` and `target` are
    defined as keyword arguments to make things very explicit, but the function will raise an error if you do not
    provide both. The function will loop over all fields and relations on the source and if the field or relation on
    the target object is null, it will set the value to that of the source object. If the field or relation is already
    set and it can only take one value (e.g. a foreign key) then it will only update the target object with the source
    object's value if `overwrite` is set to `True`; by default, it will preserve any values on the target object.
    For many-to-many fields, any objects related to the source but not the target will be added to the target's
    existing relations. Postgres ArrayFields are also addressed in such a manner. Any objects that are related to the
    source will have their relations redirected to the target. Self-references on the source will also obviously be
    redirected at the target since the objects are being merged. In cases where there are conflicting unique relations
    (e.g. source and target have two different unique one-to-one relationships with other objects, or a merge will
    result in a unique_together constraint being violated), this function has the ability to recursively cascade to
    those relationships and consolidate dependent relations. That is, the conflicting related objects will be merged
    first, prior to merging the primary source and target. Since this behavior might be unexpected, the function raises
    an error by default and provides information on the additional objects that will be consolidated. To proceed with
    the merge, `consolidate_related_uniques` must be set to `True`. If this cascading merge behavior runs into a
    situation where a dependent pair has additional conflicting relationships with other objects outside of the
    original source and target, it will be unclear which value to preserve and which to overwrite, so the function
    will raise an error. For example, if your original objects A and B have one-to-ones with objects C and D, if
    cascading is enabled then C will be merged with D using the behavior selected via `overwrite`. However, if C and D
    in turn have foreign key or one-to-one relationships with other objects that are NOT A and B themselves, since
    these relations cannot be merged into a union (as with a many-to-many), it will be ambiguous as to which relation
    to preserve and which to overwrite, so the merge will be aborted.

    NOTE ON COMPLEX RELATIONS: this function has not been tested on all possible database schema and if your objects
    have many different relationships with varying unique constraints, it may behave in unexpected ways. You should
    expect that related object relations will be redirected to the target and objects that are related to the source
    will have those relations set to null unless `overwrite` is `True`. If `consolidate_related_uniques` is `True`,
    other objects may also be merged, and if any ambiguous merging situations are encountered, the function will
    do its best to detect them and abort the merge so that you can handle the dependent merges explicitly as you
    choose. Generally speaking, you can expect that the only properties of related objects that will change will be the
    relations those objects have to the source/target objects themselves, or non-relation values that will be
    consolidated according to `overwrite` when `consolidate_related_uniques` is enabled and there are otherwise no
    conflicts between the two objects. But if you have complex model relations and are unsure how this function will
    operate, it is best to perform dependent merges manually so you can monitor and control the behavior.

    NOTE ON NON-NULLABLE RELATIONS: When `consolidate_related_uniques` is `True`, some relationships will have to be
    temporarily set to null for merges to be performed successfully. If your unique relations are not nullable then
    errors will likely occur.

    NOTE ON TRANSACTIONS: This entire function is wrapped in a transaction; if an error occurs the entire operation
    will be safely rolled back.

    :param source: The object to merge into the target (to be deleted)
    :param target: The object to preserve (and optionally update)
    :param overwrite: Whether or not to overwrite existing non-null values on the target with values from the source
    :param consolidate_related_uniques: If conflicting unique relationships (like one-to-ones) exist, attempt to
    consolidate the conflicting objects in addition to the source and target (if there are additional relations that
    must be collapsed, then an error will be raised.) If dependent relations exist and this is not set to `True`, then
    an error will be raised.
    :return: The remaining target object

    Usage::

        from django_pewtils import consolidate_objects

        consolidate_objects(
            source=duplicate_obj,
            target=obj,
            overwrite=False,  # False means that we'll prefer preserving the target's existing values if we encounter conflicts
            consolidate_related_uniques=False  # Unless we set this to True, the function will raise an error if there are conflicting relationships that can't be merged
        )

    """

    if not source or not target:
        raise Exception("You must provide a source and a target")
    elif source._meta.model != target._meta.model:
        raise Exception("The two objects must belong to the same model class")
    else:

        # Make a note of the "final" source and target
        main_source = source
        main_target = target

        with transaction.atomic():

            # Get any dependencies
            new_obj_mapper = defaultdict(dict)
            pairs = _get_unique_relations(source=source, target=target)

            # If there are cascades and you haven't specified that cascading consolidation should occur, raise an error
            if len(pairs) > 1 and not consolidate_related_uniques:
                additional_uniques = [p for p in pairs if p[0] != source]
                raise ConsolidationCascadeError(
                    "Consolidating these objects will require the merging of additional objects due to unique "
                    "relation constraints: {}.\n To continue with the consolidation process, please set "
                    "`consolidate_related_uniques` to True.".format(additional_uniques)
                )

            delayed_updates = []
            # Loop over all of the pairs that need to be collapsed
            for source, target in pairs:

                # If any of the objects have already been consolidated and updated, then we need to
                # update our references to the new objects
                if source.pk in new_obj_mapper[source._meta.model].keys():
                    source = new_obj_mapper[source._meta.model][source.pk]
                if target.pk in new_obj_mapper[target._meta.model].keys():
                    target = new_obj_mapper[target._meta.model][target.pk]

                if source != target:

                    # Just to be sure that we have the absolute most up-to-date objects, we'll refresh from the DB
                    source.refresh_from_db()
                    target.refresh_from_db()

                    fields = source._meta.get_fields()

                    # If we're currently doing a cascaded consolidation, we need to check for potential issues
                    if source != main_source:
                        for f in fields:
                            # For each foreign key or one-to-one field, if there are conflicting values and one or both
                            # of them aren't being explicitly tracked by the consolidation process as a source or target
                            # then it's unclear which one to pick to keep and which one to clear. Accordingly, we'll
                            # raise an error and force you to handle the merge `overwrite` behavior yourself.
                            if f.one_to_one or f.many_to_one:
                                # If the values aren't the same and they don't both point to objects that are
                                # themselves getting merged, then we don't know what to do here and we're going to yell.
                                if getattr(source, f.name) != getattr(
                                    target, f.name
                                ) and (
                                    (
                                        getattr(source, f.name)
                                        not in [p[0] for p in pairs]
                                        and getattr(source, f.name)
                                        not in [p[1] for p in pairs]
                                    )
                                    or (
                                        getattr(target, f.name)
                                        not in [p[0] for p in pairs]
                                        and getattr(target, f.name)
                                        not in [p[1] for p in pairs]
                                    )
                                ):
                                    raise AmbiguousConsolidationError(
                                        "({} -> {}) consolidation cascaded to ({} -> {}), but these objects have "
                                        "conflicting '{}' relations ({} vs {}) and it's unclear "
                                        "should be preserved. Please consolidate the dependent pair manually and "
                                        "specify `overwrite`.".format(
                                            main_source,
                                            main_target,
                                            source,
                                            target,
                                            f.name,
                                            getattr(source, f.name),
                                            getattr(target, f.name),
                                        )
                                    )

                    # Loop over all fields on the model
                    for f in fields:

                        if not f.is_relation and not f.primary_key:
                            # If it's not a relation
                            if isinstance(getattr(target, f.name), list) and isinstance(
                                getattr(source, f.name), list
                            ):
                                # If it's a list, then set the new value to the union
                                setattr(
                                    target,
                                    f.name,
                                    list(
                                        set(getattr(source, f.name)).union(
                                            set(getattr(target, f.name))
                                        )
                                    ),
                                )
                            elif (
                                is_null(
                                    getattr(target, f.name), empty_lists_are_null=True
                                )
                                or overwrite
                            ):
                                # Otherwise, it's a normal value
                                # If overwrite is True and the value on source isn't null
                                # then we'll update the target object
                                if not f.primary_key:
                                    val = getattr(source, f.name)
                                    if f.unique:
                                        # If it's a unique value, we need to clear out the value on source
                                        setattr(source, f.name, None)
                                        source.save()
                                    setattr(target, f.name, val)
                        elif f.one_to_one or f.many_to_one:
                            # If it's a one-to-one or foreign key
                            if hasattr(target, f.name) and (
                                is_null(
                                    getattr(target, f.name), empty_lists_are_null=True
                                )
                                or overwrite
                            ):
                                # If the value on target is null, or we're overwriting
                                if (
                                    is_not_null(source.pk)
                                    and hasattr(source, f.name)
                                    and is_not_null(getattr(source, f.name))
                                ):
                                    if f.concrete:
                                        # If the relation is on the source/target model
                                        if getattr(source, f.name) == source:
                                            # If it's a self-reference, then update it to target
                                            setattr(target, f.name, target)
                                        else:
                                            # Otherwise, set it to whatever is on the source
                                            setattr(
                                                target, f.name, getattr(source, f.name)
                                            )
                                        # Clear out the source relation
                                        setattr(source, f.name, None)
                                        source.save()
                                    else:
                                        # In this case, the relation is stored on the related model
                                        # Since there could be conflicts if we're doing cascading merges, we'll clear
                                        # it out and then circle back at the end and set it to the proper value
                                        related_object = getattr(source, f.name)
                                        setattr(
                                            related_object, f.remote_field.name, None
                                        )
                                        delayed_updates.append(
                                            (
                                                related_object._meta.model,
                                                related_object.pk,
                                                f.remote_field.name,
                                                target._meta.model,
                                                target.pk,
                                            )
                                        )
                                        related_object.save()

                        elif f.one_to_many:

                            if hasattr(f, "object_id_field_name"):
                                # In this case, it's a generic relation
                                pk_field = f.object_id_field_name
                                for related_object in getattr(source, f.name).all():
                                    setattr(related_object, pk_field, target.pk)
                                    related_object.save()
                            else:
                                # Otherwise, we're just updating the related object and redirecting the foreign key
                                # to the new target object
                                for related_object in getattr(source, f.name).all():
                                    setattr(related_object, f.remote_field.name, target)
                                    related_object.save()

                        elif f.many_to_many:
                            if hasattr(f, "through"):
                                through = f.through
                            else:
                                through = f.remote_field.through
                            if (
                                through._meta.auto_created
                                and hasattr(source, f.name)
                                and hasattr(target, f.name)
                            ):
                                # If it's a many-to-many object, we'll set the target's M2M relation to the union
                                # If there's a custom through table, those foreign key relations will appear as FKs
                                # And will be updated separately
                                merged_objects = (
                                    getattr(source, f.name).all()
                                    | getattr(target, f.name).all()
                                )
                                getattr(target, f.name).set(merged_objects)

                    if hasattr(source, "history"):
                        # If you have a django-historical-records manager installed on the model, we'll update the
                        # historical records
                        for h in source.history.all():
                            h.id = target.pk
                            h.save()

                    # Save the new target in the map so we can update any downstream references to the old source
                    new_obj_mapper[source._meta.model][source.pk] = target

                    try:
                        # Attempt to save the target before deleting the source, just to be safe, but if there's a
                        # unique constraint collision, the source needs to go before the target is saved
                        target.save()
                        source.delete()
                    except IntegrityError:
                        source.delete()
                        target.save()
                    target.refresh_from_db()

            # Now we'll loop over any relations that weren't updated due to conflicts and make sure everything is
            # set to what it should be
            for model, pk, field, val_model, val_pk in delayed_updates:
                # First we'll get the object and related object and pass them through the mapper in case they were
                # merged into new objects. If not, we'll fetch them directly from the model.
                obj = new_obj_mapper[model].get(pk, None)
                if not obj:
                    try:
                        obj = model.objects.get(pk=pk)
                    except model.DoesNotExist:
                        obj = None
                    if not obj:
                        raise Exception("Couldn't find object: {} {}".format(model, pk))
                val_obj = new_obj_mapper[val_model].get(val_pk, None)
                if not val_obj:
                    try:
                        val_obj = val_model.objects.get(pk=val_pk)
                    except val_model.DoesNotExist:
                        val_obj = None
                    if not val_obj:
                        raise Exception(
                            "Couldn't find object: {} {}".format(val_model, val_pk)
                        )
                # Now we'll set the relation to its correct value
                obj.refresh_from_db()
                val_obj.refresh_from_db()
                setattr(obj, field, val_obj)
                obj.save()

            # And we're done!
            target.refresh_from_db()
            return target


def _get_unique_relations(source, target, pairs=None, recursion=0):

    """
    An internal helper function for `consolidate_objects` that takes a source and target object, and recursively
    loops over their relations to find any related objects that have unique constraints that would raise a conflict if
    the source and target objects were merged. For example, a one-to-one relationship between source and object A, and
    target and object B; in such a case, object A and object B cannot both be related to target, so they too must be
    merged. This additional merge, in turn, may result in the need for yet more merging, hence the need for recursion.

    :param source: The object to be collapsed into target
    :param target: The target object to be preserved/updated
    :param pairs: Recursive parameter to track pairs that have already been detected
    :param recursion: The level of recursion (used for sorting prior to returning the final list)
    :return: A list of (source, target) tuples indicating pairs of objects that must be merged in order for the
    first merge to be successful
    """

    if not pairs:
        # Initialize a dictionary with the original pair and recursion level 0
        pairs = {(source, target): 0}
    source_rels = source.related_objects()
    target_rels = target.related_objects()

    if source._meta.model == target._meta.model:
        # Loop over all relations on the source/target model
        for f in source._meta.get_fields():
            if f.name in source_rels.keys() and f.name in target_rels.keys():
                # If the relation exists in both the source and target
                if (
                    (f.one_to_one or (f.many_to_one and f.unique))
                    and hasattr(source, f.name)
                    and hasattr(target, f.name)
                    and is_not_null(getattr(source, f.name))
                    and is_not_null(getattr(target, f.name))
                ):
                    # And if it's a one-to-one or unique foreign key and both objects have a value
                    pair = (getattr(source, f.name), getattr(target, f.name))
                    if pair not in pairs.keys():
                        # And the pair of related objects haven't yet been identified
                        # Then check them for unique relation conflicts as well
                        pairs[pair] = recursion
                        pairs.update(
                            _get_unique_relations(
                                *pair, pairs=pairs, recursion=recursion + 1
                            )
                        )
                elif f.one_to_many:
                    # Otherwise, if it's a foreign key on another model - and it's possible that the current source
                    # object could be party of a unique_together constraint, so we need to check for that

                    # First, let's gather up any unique_together constraints on the related model
                    unique_togethers = []
                    for fieldset in f.remote_field.model._meta.unique_together:
                        if type(fieldset) == tuple:
                            for field in fieldset:
                                unique_togethers.append(field)
                        else:
                            unique_togethers.append(fieldset)

                    if (
                        hasattr(f.remote_field, "unique") and f.remote_field.unique
                    ) or f.remote_field.name in unique_togethers:
                        # If the relation itself is part of the related model's uniqueness (either by being explicitly
                        # flagged as such, or by being a part of a unique_together constraint, then let's see if there are
                        # any related objects that are identical except for their link to source vs target
                        other_unique_fields = []
                        for other in f.remote_field.model._meta.get_fields():
                            # First let's loop over all of the other fields in the related model and get an exhaustive
                            # list of everything that makes the related model objects unique; we already know about
                            # THIS field and any unique_together conditions, but other fields might be unique too
                            if (
                                other.name != "id"
                                and other.name != f.remote_field.name
                                and (
                                    (
                                        hasattr(other, "unique")
                                        and other.unique
                                        and not other.one_to_one
                                    )
                                    or other.name in unique_togethers
                                )
                            ):
                                other_unique_fields.append(other.name)

                        target_objs = getattr(target, f.name).all()
                        for t in target_objs:
                            # Now we're going to loop over every single object that's linked to the target, to
                            # see if there's any overlap with those linked to source - related objects that are
                            # identical in uniqueness except for being linked to source vs. target
                            source_objs = getattr(source, f.name).all()
                            for other in other_unique_fields:
                                source_objs = source_objs.filter(
                                    **{other: getattr(t, other)}
                                )
                            alt_source_objs = getattr(source, f.name).all()
                            for other in unique_togethers:
                                if other != f.remote_field.name:
                                    alt_source_objs = alt_source_objs.filter(
                                        **{other: getattr(t, other)}
                                    )
                            source_objs = source_objs | alt_source_objs
                            for s in source_objs:
                                # If there are any objects related to source that will conflict with objects related to
                                # the target if the foreign key is changed, then we need to consolidate those too
                                pair = (s, t)
                                if pair not in pairs.keys():
                                    # So if it's a pairing we haven't seen, let's recursively check it too
                                    pairs[pair] = recursion
                                    pairs.update(
                                        _get_unique_relations(
                                            *pair, pairs=pairs, recursion=recursion + 1
                                        )
                                    )

    if recursion == 0:
        # If we've finally rolled back up to the top level, let's sort all of the pairs we identified in the order
        # in which we identified them, and return a list
        pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)
        pairs = [p[0] for p in pairs if p[0][0] != source]
        pairs.append((source, target))
        return pairs
    else:
        # Otherwise we're still in recursion and we'll keep the pairs in dictionary form
        return pairs


class CacheHandler(object):
    def __init__(self, path, use_database=False, hash=True, **options):

        """
        A wrapper around `pewtils.io.FileHandler` that also has the ability to use Django's built-in database caching.

        :param path: The folder path to store cache data. If the database is used, this will serve as a key prefix.
        :param use_database: Whether or not to use the Django database caching or a cache folder via `FileHandler`.
        :param hash: Whether or not to hash the keys.
        :param options: Additional options for the `FileHandler` (like using S3 vs a local folder)
        """

        self.path = path
        self.file_handler = FileHandler(self.path, **options)
        self.use_database = use_database
        self.hash = hash
        if self.use_database:
            self.cached_keys = []

    def write(self, key, value, timeout=None):

        """
        Write a value to the cache.

        :param key: The key to use to look up the stored value.
        :param value: The value to save to the cache.
        :param timeout: Optional timeout for the key to expire. Default is 5 minutes for database caching, and None for
        file-based caching.
        :return:
        """

        if self.use_database:
            if self.hash:
                key = self.file_handler.get_key_hash(key)
            k = "/".join([self.path, key])
            self.cached_keys.append(k)
            if not timeout:
                timeout = 60.0 * 5.0
                print(
                    "Database caching requires a timeout, but none was provided. Setting expiration at 5 minutes."
                )
            cache.set(k, value, timeout)
        else:
            value = {
                "value": value,
                "timeout": datetime.datetime.now() + datetime.timedelta(seconds=timeout)
                if timeout
                else None,
            }
            self.file_handler.write(key, value, hash_key=self.hash, format="pkl")

    def read(self, key):

        """
        Read a value from the cache.

        :param key: The key to use to look up the stored value.
        :return: The stored value from the cache.
        """

        if self.use_database:
            if self.hash:
                key = self.file_handler.get_key_hash(key)
            k = "/".join([self.path, key])
            return cache.get(k)
        else:
            value = self.file_handler.read(key, hash_key=self.hash, format="pkl")
            if value:
                if value["timeout"] and value["timeout"] < datetime.datetime.now():
                    self.clear_key(key)
                    return None
                else:
                    return value["value"]
            else:
                return value

    def clear(self):

        """
        Clear out all keys currently in the cache. If you are using the database, only values that have been
        stored by this `CacheHandler` instance will be cleared out. Otherwise, the whole folder path will be removed.
        """

        if self.use_database:
            print(
                "Warning: only keys that have been set by this CacheHandler instance will be cleared"
            )
            for k in self.cached_keys:
                cache.set(k, None)
        else:
            if not self.file_handler.use_s3:
                try:
                    shutil.rmtree(self.file_handler.path)
                except OSError:
                    pass
            else:
                bucket_list = self.file_handler.s3.list(prefix=self.path)
                self.file_handler.s3.delete_keys([key.name for key in bucket_list])

    def clear_key(self, key):

        """
        Clear a specific key from the cache.

        :param key: The key to clear out.
        """

        if self.use_database:
            if self.hash:
                key = self.file_handler.get_key_hash(key)
            k = "/".join([self.path, key])
            cache.set(k, None)
        else:
            self.file_handler.clear_file(key, hash_key=self.hash, format="pkl")


def get_app_settings_folders(settings_dir_list_var):

    """
    Used to identify multiple values of a Django setting that are spread across multiple apps. Assumes that your
    primary app is the only one with a `settings.py` file, that it contains a setting whose value is a list, and that
    other apps may also set values for that setting in their app configuration, which may contain additional values in
    a list. For example, `django_learning` has a default set of dataset extractors, but also allows you to create your
    own in your own app. In order for `django_learning` to identify your own custom extractors and make them accessible
    via `django_learning.utils.dataset_extractors`, it needs to know not only about its own folders but also the
    folders in your own app where you store your own custom extractors. By passing `DJANGO_LEARNING_DATASET_EXTRACTORS`
    into this function, any list of folder paths that you store in that variable on your own app will also be added to
    the folders stored for that setting by `django_learning` in its own app configuration. In theory this can be
    used to unify any list settings that are spread out across multiple apps, but its use so far has been for compiling
    lists of folder paths.

    :param settings_dir_list_var: The name of the setting that exists on your app (must be a list), which may also
    exist in the configuration of other installed apps.
    :return: The union of all values for this settings across all installed apps, including your own
    """

    # In theory, installable Django apps aren't supposed to have settings.py files
    # So we can auto-detect the root project this way

    try:
        apps.get_app_configs()
    except (AppRegistryNotReady, ImproperlyConfigured):
        app_name = detect_primary_app()
        if app_name:
            load_app(app_name)
            apps.get_app_configs()
        else:
            raise Exception(
                "Django is not set up and the primary app could not be detected"
            )

    from django.conf import settings

    dirs = []
    if hasattr(settings, settings_dir_list_var):
        dirs.extend(getattr(settings, settings_dir_list_var))
    return list(set(dirs))


def run_partial_postgres_search(model, text, fields, max_results=250, min_rank=0.0):

    """
    Assuming that you have Postgres' Trigram Extension installed, this function will allow you to run a full text
    search on one or more text fields.

    This function allows for the use of trailing wildcards (`*`) but otherwise will only find exact matches. If
    multiple tokens are passed (separated by spaces) then it will consider these terms bound by an `AND` boolean
    operator.

    :param model: The model you want to search
    :param text: The search query (one or more terms, with optional suffix wildcards)
    :param fields: List of fields to search on the model
    :param max_results: Top N results you want to return
    :param min_rank: The minimum SearchRank value that results must have to be returned.
    :return: A QuerySet of results.

    Usage::

        from django_pewtils import run_partial_postgres_search

        >>> run_partial_postgres_search(Politician, "Dwayne Rock Johnson", ("first_name", "nickname", "last_name"))
        <PoliticianManager [<Politician: Dwayne 'The Rock' Johnson>, '...(remaining elements truncated)...']>

    """

    text = re.sub(r"[!\'()|&]", " ", text).strip()
    if text:
        text = re.sub(r"\s+", " & ", text)
        text += ":*"
    query = SearchQuery(text)
    vector = SearchVector(*fields)
    queryset = (
        model.objects.annotate(rank=SearchRank(vector, query))
        .distinct()
        .filter(rank__gt=min_rank)
        .order_by("-rank")
        .distinct()[:max_results]
    )
    sql, sql_params = queryset.query.get_compiler(using=queryset.db).as_sql()
    sql = re.sub("plainto_tsquery", "to_tsquery", sql)
    sql_params = tuple(["''" if p == "" else p for p in list(sql_params)])
    results = model.objects.raw(sql, sql_params)
    pk_list = [r.pk for r in results]
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
    queryset = model.objects.filter(pk__in=pk_list).order_by(preserved)
    return queryset
