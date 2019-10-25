from __future__ import print_function
import unittest
import copy
import pandas as pd
import itertools
import time
import os

from django.test import TestCase as DjangoTestCase
from django.conf import settings

from pewtils import is_not_null

from testapp.models import TestModel, SecondTestModel


class AbstractModelTests(DjangoTestCase):

    """
    To test, navigate to django_pewtils root folder and run `python manage.py test testapp.tests`.
    To assess coverage, run `coverage run manage.py test testapp.tests` and then run `coverage report -m`.
    """

    def setUp(self):

        reviews = pd.read_csv(
            os.path.join(settings.BASE_DIR, "testapp", "test_data.csv")
        )
        for index, row in reviews[:50].iterrows():
            if is_not_null(row["text"]):
                obj = TestModel.objects.create(
                    text_field=row["text"][:200], id=index, array_field=[str(index)]
                )
                obj2 = SecondTestModel.objects.create(
                    text_field=row["text"][:200], id=index, foreign_key_unique=obj
                )

        for obj in TestModel.objects.all():
            index += 1
            obj.foreign_key = SecondTestModel.objects.order_by("?")[0]
            obj.foreign_key_self = obj
            obj.one_to_one = SecondTestModel.objects.get(pk=obj.pk)
            obj.one_to_one_self = obj
            for obj2 in SecondTestModel.objects.order_by("?")[:3]:
                obj.many_to_many.add(obj2)
            obj.many_to_many_self.add(obj)
            obj.save()

        for obj2 in SecondTestModel.objects.all():
            obj2.foreign_key = TestModel.objects.exclude(pk=obj2.pk).order_by("?")[0]
            obj2.foreign_key_unique = TestModel.objects.get(pk=obj2.pk)
            obj2.save()

    def test_inspect_delete(self):

        from django_pewtils import get_model

        m2m_model = get_model("testmodel_many_to_many", app_name="testapp")
        m2m_self_model = get_model("testmodel_many_to_many_self", app_name="testapp")

        to_delete = TestModel.objects.all()[0].inspect_delete(counts=True)
        self.assertEqual(to_delete[TestModel], 1)
        self.assertEqual(to_delete[m2m_model], 3)
        self.assertEqual(to_delete[m2m_self_model], 1)
        self.assertEqual(len(to_delete.keys()), 3)

        to_delete = TestModel.objects.all()[0].inspect_delete(counts=False)
        self.assertEqual(to_delete[TestModel].count(), 1)
        self.assertEqual(to_delete[m2m_model].count(), 3)
        self.assertEqual(to_delete[m2m_self_model].count(), 1)
        self.assertEqual(len(to_delete.keys()), 3)

    def test_related_objects(self):

        results = TestModel.objects.filter(foreign_key_reverse__isnull=False)[
            0
        ].related_objects(counts=True)
        self.assertEqual(results["many_to_many_self"], 1)
        self.assertEqual(results["many_to_many"], 3)
        self.assertEqual(results["many_to_many_self_reverse"], 1)
        self.assertEqual(results["one_to_one_self_reverse"], 1)
        self.assertEqual(results["one_to_one"], 1)
        self.assertGreater(results["foreign_key_reverse"], 0)
        self.assertEqual(results["foreign_key_self_reverse"], 1)
        self.assertEqual(results["foreign_key"], 1)
        self.assertEqual(results["foreign_key_unique_reverse"], 1)
        self.assertEqual(results["one_to_one_self"], 1)
        self.assertEqual(results["foreign_key_self"], 1)
        self.assertEqual(len(results.keys()), 11)

        results = TestModel.objects.filter(foreign_key_reverse__isnull=False)[
            0
        ].related_objects(counts=False)
        self.assertEqual(results["many_to_many_self"].count(), 1)
        self.assertEqual(results["many_to_many"].count(), 3)
        self.assertEqual(results["many_to_many_self_reverse"].count(), 1)
        self.assertEqual(results["one_to_one_self_reverse"].count(), 1)
        self.assertEqual(results["one_to_one"].count(), 1)
        self.assertGreater(results["foreign_key_reverse"].count(), 0)
        self.assertEqual(results["foreign_key_self_reverse"].count(), 1)
        self.assertEqual(results["foreign_key"].count(), 1)
        self.assertEqual(results["foreign_key_unique_reverse"].count(), 1)
        self.assertEqual(results["one_to_one_self"].count(), 1)
        self.assertEqual(results["foreign_key_self"].count(), 1)
        self.assertEqual(len(results.keys()), 11)

        obj = SecondTestModel.objects.filter(foreign_key_reverse__isnull=False)[0]
        for related in obj.many_to_many_reverse.all():
            related.many_to_many.clear()

        results = obj.related_objects(counts=True)
        self.assertGreater(results["foreign_key_reverse"], 0)
        self.assertEqual(results["one_to_one_reverse"], 1)
        self.assertEqual(results["foreign_key_unique"], 1)
        self.assertEqual(results["many_to_many_reverse"], 0)
        self.assertEqual(results["foreign_key"], 1)
        self.assertEqual(len(results.keys()), 5)

        results = obj.related_objects(counts=True, nonzero_only=True)
        self.assertGreater(results["foreign_key_reverse"], 0)
        self.assertEqual(results["one_to_one_reverse"], 1)
        self.assertEqual(results["foreign_key_unique"], 1)
        self.assertEqual(results["foreign_key"], 1)
        self.assertEqual(len(results.keys()), 4)

        results = obj.related_objects(counts=False)
        self.assertGreater(results["foreign_key_reverse"].count(), 0)
        self.assertEqual(results["one_to_one_reverse"].count(), 1)
        self.assertEqual(results["foreign_key_unique"].count(), 1)
        self.assertEqual(results["many_to_many_reverse"].count(), 0)
        self.assertEqual(results["foreign_key"].count(), 1)
        self.assertEqual(len(results.keys()), 5)

    def test_fuzzy_ratio(self):

        review = TestModel.objects.all()[0]

        result = review.fuzzy_ratio(
            ["text_field"], review.text_field[:100], allow_partial=True
        )
        self.assertTrue(result == 100)

        result = review.similar_by_fuzzy_ratios(
            ["text_field"], min_ratio=10, allow_partial=True, max_partial_difference=80
        )
        self.assertEqual(result[0]["pk"], 5)
        self.assertEqual(result[0]["fuzzy_ratio"], 46)

    def test_levenshtein_difference(self):

        review = TestModel.objects.all()[0]
        result = review.levenshtein_difference(["text_field"], review.text_field[:100])
        self.assertAlmostEqual(result, 0.5, 2)

        result = review.similar_by_levenshtein_differences(
            ["text_field"], max_difference=0.9
        )[0]
        self.assertEqual(result["pk"], 19)
        self.assertEqual(result["difference"], 0.74)

    def test_tfidf_similarity(self):

        review = TestModel.objects.all()[0]
        result = review.tfidf_similarity(["text_field"], review.text_field[:100])
        self.assertAlmostEqual(result, 0.74, 2)

        result = review.similar_by_tfidf_similarity(["text_field"], min_similarity=0.1)
        self.assertEqual(result[0]["pk"], 19)
        self.assertAlmostEqual(round(result[0]["similarity"], 2), 0.21, 2)

    def test_trigram_similarity(self):

        review = TestModel.objects.all()[0]
        result = review.trigram_similarity(["text_field"], review.text_field[:100])
        self.assertAlmostEqual(result, 0.51, 2)
        result = review.similar_by_trigram_similarity(
            ["text_field"], min_similarity=0.1
        )[0]
        self.assertEqual(result["pk"], 19)
        self.assertAlmostEqual(result["similarity"], 0.184739, 2)

    def tearDown(self):
        pass
