from builtins import object
from django.db import models
from django.db.models.deletion import Collector

from pewtils import is_not_null, decode_text
from django_pewtils import get_model
from django_pewtils.managers import BasicExtendedManager


class BasicExtendedModel(models.Model):
    class Meta(object):
        abstract = True

    objects = BasicExtendedManager().as_manager()

    def inspect_delete(self):

        collector = Collector(using='default')
        collector.collect([self])
        return collector.dependencies

    def related_object_counts(self, nonzero_only=False):

        objs = {}
        for f in self._meta.get_fields():
            if f.is_relation:
                if f.one_to_one or f.many_to_one:
                    if hasattr(self, f.name) and is_not_null(getattr(self, f.name)):
                        objs[f.name] = True
                    else:
                        objs[f.name] = False
                elif f.one_to_many or f.many_to_many:
                    objs[f.name] = getattr(self, f.name).count()

        if nonzero_only:
            return {k: v for k, v in objs.items() if v > 0}
        else:
            return objs

    def related_objects(self, nonzero_only=False):

        objs = {}
        for f in self._meta.get_fields():
            if f.is_relation:
                if f.one_to_one or f.many_to_one:
                    if hasattr(self, f.name):
                        objs[f.name] = getattr(self, f.name)
                    else:
                        objs[f.name] = None
                elif f.one_to_many or f.many_to_many:
                    objs[f.name] = getattr(self, f.name).all()

        if nonzero_only:
            return {k: v for k, v in objs.items() if v.count() > 0}
        else:
            return objs

    def fuzzy_ratio(self, field_names, text, allow_partial=False, max_partial_difference=100):

        return get_model(self._meta.model_name).objects.filter(pk=self.pk).fuzzy_ratios(field_names, text,
                                                                                        allow_partial=allow_partial,
                                                                                        max_partial_difference=max_partial_difference)[
            0]['fuzzy_ratio']

    def similar_by_fuzzy_ratios(self, field_names, text, min_ratio=90, allow_partial=False, max_partial_difference=10):

        return get_model(self._meta.model_name).objects.exclude(pk=self.pk).fuzzy_ratios(field_names, text,
                                                                                         min_ratio=min_ratio,
                                                                                         allow_partial=allow_partial,
                                                                                         max_partial_difference=max_partial_difference)

    def levenshtein_difference(self, field_names, text):

        return \
        get_model(self._meta.model_name).objects.filter(pk=self.pk).levenshtein_differences(field_names, text)[0][
            'difference']

    def similar_by_levenshtein_differences(self, field_names, text, max_difference=.2):

        return get_model(self._meta.model_name).objects.exclude(pk=self.pk).levenshtein_differences(field_names, text,
                                                                                                    max_difference=max_difference)

    def tfidf_similarity(self, field_names, text):

        return get_model(self._meta.model_name).objects.filter(pk=self.pk).tfidf_similarities(field_names, text)[0][
            'similarity']

    def similar_by_tfidf_similarity(self, field_names, text, min_similarity=.9):

        return get_model(self._meta.model_name).objects.exclude(pk=self.pk).tfidf_similarities(field_names, text,
                                                                                               min_similarity=min_similarity)

    def trigram_similarity(self, field_names, text):

        return get_model(self._meta.model_name).objects.filter(pk=self.pk).trigram_similarities(field_names, text)[0][
            'similarity']

    def similar_by_trigram_similarity(self, field_names, text, min_similarity=.9):

        return get_model(self._meta.model_name).objects.exclude(pk=self.pk).trigram_similarities(field_names, text,
                                                                                                 min_similarity=min_similarity)
