from builtins import object
from django.db import models
from django.db.models.deletion import Collector

from pewtils import is_not_null, decode_text
from django_pewtils import get_model, inspect_delete
from django_pewtils.managers import BasicExtendedManager


class BasicExtendedModel(models.Model):

    """
    An extended Django abstract model class that provides additional utility functions.
    """

    class Meta(object):
        abstract = True

    objects = BasicExtendedManager().as_manager()

    def inspect_delete(self, counts=False):

        """
        Can be called on any model object; returns all objects and relations that would be deleted if the
        object itself is deleted.

        :param counts: If `True`, will return counts of the objects to be deleted. Otherwise returns QuerySets
        :return: A dictionary of models/relations (keys) and the counts or QuerySets of objects to be deleted (values)
        """

        return inspect_delete([self], counts=counts)

    def related_objects(self, counts=False, nonzero_only=False):

        """
        Returns a dictionary of all of the other objects that are related to the object.

        :param counts: If `True`, will return counts of the related objects. Otherwise returns QuerySets
        :param nonzero_only: If `True`, empty relations will not be included in the dictionary.
        :return: A dictionary of relation fields on the model (keys) and the counts or QuerySets of the related
        objects (values)
        """

        objs = {}
        for f in self._meta.get_fields():
            if f.is_relation:
                if f.one_to_one or f.many_to_one:
                    if hasattr(self, f.name) and is_not_null(getattr(self, f.name)):
                        objs[f.name] = getattr(self, f.name)
                        objs[f.name] = objs[f.name]._meta.model.objects.filter(
                            pk=objs[f.name].pk
                        )
                    else:
                        objs[f.name] = None
                elif (f.one_to_many or f.many_to_many) and hasattr(self, f.name):
                    objs[f.name] = getattr(self, f.name).all()

        if nonzero_only:
            objs = {k: v for k, v in objs.items() if v.count() > 0}
        if counts:
            objs = {k: v.count() if v else 0 for k, v in objs.items()}
        return objs

    def fuzzy_ratio(
        self, field_names, text, allow_partial=False, max_partial_difference=100
    ):

        """
        Given a snippet of text, computes the fuzzy ratio between the text and text that is stored on one or more
        fields on the object.

        :param field_names: The names of the fields to compare the text against.
        :param text: A string of text to compare
        :param allow_partial: Whether or not to allow partial fuzzy ratios when computing text similarity.
        :param max_partial_difference: The maximum difference between the absolute and partial ratio that's
        allowed to return a result.
        :return: The fuzzy ratio between the object and the comparison text
        """

        return (
            get_model(self._meta.model_name)
            .objects.filter(pk=self.pk)
            .fuzzy_ratios(
                field_names,
                text,
                allow_partial=allow_partial,
                max_partial_difference=max_partial_difference,
            )[0]["fuzzy_ratio"]
        )

    def similar_by_fuzzy_ratios(
        self, field_names, min_ratio=90, allow_partial=False, max_partial_difference=10
    ):

        """
        Given one or more text fields, computes the fuzzy ratios between the object and other objects in the
        table and returns a list of results with the primary keys of the compared objects and their fuzzy ratios.

        :param field_names: The names of the text fields to compare
        :param min_ratio: The minimum fuzzy ratio allowed to return results.
        :param allow_partial: Whether or not to allow partial fuzzy ratios when computing text similarity.
        :param max_partial_difference: The maximum difference between the absolute and partial ratio that's
        allowed to return a result.
        :return: A list of results with the primary keys of the compared objects and their fuzzy ratios
        """

        text = " ".join(
            [decode_text(getattr(self, f)) for f in field_names if getattr(self, f)]
        )
        return (
            get_model(self._meta.model_name)
            .objects.exclude(pk=self.pk)
            .fuzzy_ratios(
                field_names,
                text,
                min_ratio=min_ratio,
                allow_partial=allow_partial,
                max_partial_difference=max_partial_difference,
            )
        )

    def levenshtein_difference(self, field_names, text):

        """
        Given a set of text fields and some comparison text, computes the Levenshtein difference between the
        comparison text and the text that's stored in the fields on the object.

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :return: The Levenshtein difference between the provided text and the text on the object
        """

        return (
            get_model(self._meta.model_name)
            .objects.filter(pk=self.pk)
            .levenshtein_differences(field_names, text)[0]["difference"]
        )

    def similar_by_levenshtein_differences(self, field_names, max_difference=0.2):

        """
        Given one or more text fields, computes the Levenshtein differences between the object and other objects in the
        table and returns a list of results with the primary keys of the compared objects and their differences.

        :param field_names: The names of the text fields to compare
        :param max_difference: The maximum difference allowed for a result to be returned.
        :return: A list of results with the primary keys of the compared objects and their Levenshtein differences
        """

        text = " ".join(
            [decode_text(getattr(self, f)) for f in field_names if getattr(self, f)]
        )
        return (
            get_model(self._meta.model_name)
            .objects.exclude(pk=self.pk)
            .levenshtein_differences(field_names, text, max_difference=max_difference)
        )

    def tfidf_similarity(self, field_names, text):

        """
        Given a set of text fields and some comparison text, computes the TF-IDF cosine similarity between the
        comparison text and the text that's stored in the fields on the object.

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :return: The TF-IDF similarity between the provided text and the text on the object
        """

        return (
            get_model(self._meta.model_name)
            .objects.filter(pk=self.pk)
            .tfidf_similarities(field_names, text)[0]["similarity"]
        )

    def similar_by_tfidf_similarity(self, field_names, min_similarity=0.9):

        """
        Given one or more text fields, computes the TF-IDF cosine similarities between the object and other objects in
        the table and returns a list of results with the primary keys of the compared objects and their similarities.

        :param field_names: The names of the text fields to compare
        :param min_similarity: The minimum similarity allowed for a result to be returned.
        :return: A list of results with the primary keys of the compared objects and their TF-IDF similarities
        """

        text = " ".join(
            [decode_text(getattr(self, f)) for f in field_names if getattr(self, f)]
        )
        return (
            get_model(self._meta.model_name)
            .objects.exclude(pk=self.pk)
            .tfidf_similarities(field_names, text, min_similarity=min_similarity)
        )

    def trigram_similarity(self, field_names, text):

        """
        Given a set of text fields and some comparison text, computes the trigram similarity between the
        comparison text and the text that's stored in the fields on the object. (Uses Postgres' built-in
        trigram similarity module)

        :param field_names: The names of the text fields to compare
        :param text: A string of text to compare
        :return: The trigram similarity between the provided text and the text on the object
        """

        return (
            get_model(self._meta.model_name)
            .objects.filter(pk=self.pk)
            .trigram_similarities(field_names, text)[0]["similarity"]
        )

    def similar_by_trigram_similarity(self, field_names, min_similarity=0.9):

        """
        Given one or more text fields, computes the trigram similarities between the object and other objects in the
        table and returns a list of results with the primary keys of the compared objects and their similarities.
        (Uses Postgres' built-in trigram similarity module)

        :param field_names: The names of the text fields to compare
        :param min_similarity: The minimum similarity allowed for a result to be returned.
        :return: A list of results with the primary keys of the compared objects and their trigram similarities
        """

        text = " ".join(
            [decode_text(getattr(self, f)) for f in field_names if getattr(self, f)]
        )
        return (
            get_model(self._meta.model_name)
            .objects.exclude(pk=self.pk)
            .trigram_similarities(field_names, text, min_similarity=min_similarity)
        )
