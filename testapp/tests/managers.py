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


class ManagerTests(DjangoTestCase):
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

    def test_to_df(self):

        import pandas as pd

        df = TestModel.objects.all().to_df()
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual(len(df.columns), 7)
        self.assertEqual(len(df), TestModel.objects.all().count())
        df = TestModel.objects.filter(pk=99999).to_df()
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual(len(df), 0)

    def test_chunk(self):

        items = []
        for item in TestModel.objects.all().chunk(randomize=True):
            items.append(item)
        self.assertTrue(len(items) == TestModel.objects.count())

    def test_sample(self):

        sample = TestModel.objects.sample(10)
        self.assertTrue(sample.count() == 10)

    def test_chunk_update(self):

        TestModel.objects.chunk_update(size=2, text_field="test")
        for obj in TestModel.objects.all():
            self.assertEqual(obj.text_field, "test")

    def test_chunk_delete(self):

        TestModel.objects.chunk_delete(size=2)
        self.assertTrue(TestModel.objects.count() == 0)

    def test_inspect_delete(self):

        from django_pewtils import get_model

        m2m_model = get_model("testmodel_many_to_many", app_name="testapp")
        m2m_self_model = get_model("testmodel_many_to_many_self", app_name="testapp")

        to_delete = TestModel.objects.all().inspect_delete(counts=True)
        self.assertEqual(to_delete[TestModel], 50)
        self.assertEqual(to_delete[m2m_model], 150)
        self.assertEqual(to_delete[m2m_self_model], 50)
        self.assertEqual(len(to_delete.keys()), 3)

        to_delete = TestModel.objects.all().inspect_delete(counts=False)
        self.assertEqual(to_delete[TestModel].count(), 50)
        self.assertEqual(to_delete[m2m_model].count(), 150)
        self.assertEqual(to_delete[m2m_self_model].count(), 50)
        self.assertEqual(len(to_delete.keys()), 3)

    def test_get_if_exists(self):

        obj = TestModel.objects.get_if_exists({"pk": 1})
        self.assertIsNotNone(obj)
        obj = TestModel.objects.get_if_exists(
            {"pk": 123456, "text_field": obj.text_field}, match_any=True
        )
        self.assertIsNotNone(obj)
        obj = TestModel.objects.get_if_exists(
            {"pk": 1, "text_field": []}, match_any=True, empty_lists_are_null=True
        )
        self.assertIsNotNone(obj)
        obj = TestModel.objects.get_if_exists({"text_field": None}, search_nulls=True)
        self.assertIsNone(obj)
        SecondTestModel.objects.filter(pk=1).update(text_field=None)
        obj = SecondTestModel.objects.get_if_exists(
            {"text_field": None}, search_nulls=True
        )
        self.assertIsNotNone(obj)

        obj = TestModel.objects.get_if_exists({"pk": 1})
        obj.array_field = ["12345"]
        obj.save()

        obj = TestModel.objects.get_if_exists(
            {"array_field": ["12345", "67890"]}, allow_list_overlaps=False
        )
        self.assertIsNone(obj)

        obj = TestModel.objects.get_if_exists(
            {"array_field": ["12345", "67890"]}, allow_list_overlaps=True
        )
        self.assertIsNotNone(obj)

    def test_create_or_update(self):

        new_text = "testing one two three"
        unique_data = {"pk": 1}
        update_data = {"text_field": new_text}

        obj = TestModel.objects.create_or_update({"pk": 99999}, {"text_field": "test"})
        self.assertEqual(obj.pk, 99999)
        self.assertEqual(obj.text_field, "test")

        obj = TestModel.objects.create_or_update(
            unique_data, update_data=update_data, only_update_existing_nulls=True
        )
        self.assertNotEqual(obj.text_field, new_text)

        obj = TestModel.objects.create_or_update(unique_data, update_data=update_data)
        self.assertEqual(obj.text_field, new_text)

        obj = SecondTestModel.objects.create_or_update(
            unique_data, update_data={"text_field": None}
        )
        self.assertIsNotNone(obj.text_field)

        obj = SecondTestModel.objects.create_or_update(
            unique_data, update_data={"text_field": None}, save_nulls=True
        )
        self.assertIsNone(obj.text_field)

        obj = SecondTestModel.objects.create_or_update(
            {"text_field": None},
            update_data={"text_field": "woot"},
            only_update_existing_nulls=True,
            search_nulls=True,
        )
        self.assertEqual(obj.text_field, "woot")

        new_record = {"pk": 1, "array_field": ["12345"], "text_field": "one"}
        obj = TestModel.objects.create_or_update(
            {"pk": new_record["pk"], "array_field": new_record["array_field"]},
            update_data=new_record,
            match_any=True,
            search_nulls=False,
            empty_lists_are_null=True,
            save_nulls=False,
            only_update_existing_nulls=False,
            return_object=True,
        )
        self.assertEqual(obj.array_field, ["12345"])
        self.assertEqual(obj.text_field, "one")

        new_record = {"pk": 1, "text_field": None}
        obj = TestModel.objects.create_or_update(
            {"pk": new_record["pk"]},
            update_data=new_record,
            match_any=True,
            search_nulls=False,
            empty_lists_are_null=True,
            save_nulls=False,
            only_update_existing_nulls=False,
            return_object=True,
        )
        self.assertEqual(obj.array_field, ["12345"])
        self.assertEqual(obj.text_field, "one")

        new_record = {"array_field": ["12345", "67890"]}
        obj = TestModel.objects.create_or_update(
            {"array_field": new_record["array_field"]},
            update_data=new_record,
            match_any=True,
            search_nulls=False,
            empty_lists_are_null=True,
            save_nulls=False,
            only_update_existing_nulls=False,
            allow_list_overlaps=True,
            return_object=True,
        )
        self.assertEqual(obj.array_field, ["12345", "67890"])

        new_record = {"pk": 1, "text_field": None, "array_field": ["12345", "abcde"]}
        obj = TestModel.objects.create_or_update(
            {"pk": new_record["pk"], "array_field": new_record["array_field"]},
            update_data=new_record,
            match_any=True,
            search_nulls=False,
            empty_lists_are_null=True,
            save_nulls=False,
            only_update_existing_nulls=False,
            allow_list_overlaps=True,
            return_object=True,
        )
        self.assertEqual(obj.array_field, ["12345", "67890", "abcde"])
        self.assertEqual(obj.text_field, "one")

    def test_fuzzy_ratio(self):

        result = TestModel.objects.all().fuzzy_ratios(
            ["text_field"], "quick movie review", allow_partial=True
        )
        self.assertEqual(result[0]["pk"], 1)
        self.assertEqual(result[0]["fuzzy_ratio"], 100)

        result, fuzzy_ratio = TestModel.objects.all().fuzzy_ratio_best_match(
            ["text_field"], "quick movie review", allow_partial=True
        )
        self.assertEqual(result.pk, 1)
        self.assertEqual(fuzzy_ratio, 100)

    def test_levenshtein_difference(self):

        result = TestModel.objects.all().levenshtein_differences(
            ["text_field"], "quick movie review"
        )
        self.assertEqual(result[0]["pk"], 1)
        self.assertAlmostEqual(result[0]["difference"], 0.91, 2)

        result, difference = TestModel.objects.all().levenshtein_difference_best_match(
            ["text_field"], "quick movie review"
        )
        self.assertEqual(result.pk, 1)
        self.assertAlmostEqual(difference, 0.91, 2)

    def test_tfidf_similarity(self):

        result = TestModel.objects.all().tfidf_similarities(
            ["text_field"], "quick movie review"
        )
        self.assertEqual(result[0]["pk"], 1)
        self.assertAlmostEqual(result[0]["similarity"], 0.35, 2)

        result, similarity = TestModel.objects.all().tfidf_similarity_best_match(
            ["text_field"], "quick movie review"
        )
        self.assertEqual(result.pk, 1)
        self.assertAlmostEqual(similarity, 0.35, 2)

    def test_trigram_similarity(self):

        result = TestModel.objects.all().trigram_similarities(
            ["text_field"], "quick movie review"
        )
        self.assertEqual(result[0]["pk"], 1)
        self.assertAlmostEqual(result[0]["similarity"], 0.134, 2)

        result, similarity = TestModel.objects.all().trigram_similarity_best_match(
            ["text_field"], "quick movie review"
        )
        self.assertEqual(result.pk, 1)
        self.assertAlmostEqual(similarity, 0.134, 2)

    def test_postgres_search(self):

        results = TestModel.objects.all().postgres_search(
            ["text_field"], "quick movie review"
        )
        self.assertEqual(results[0].pk, 1)
        self.assertEqual(results[0].rank, 0.285735)

    def tearDown(self):
        from django.conf import settings
        import shutil, os

        cache_path = os.path.join(settings.BASE_DIR, settings.LOCAL_CACHE_ROOT)
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
