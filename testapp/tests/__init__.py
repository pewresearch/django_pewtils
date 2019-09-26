from __future__ import print_function
import unittest
import copy
import pandas as pd
import os

from django.test import TestCase as DjangoTestCase
from django.conf import settings

from pewtils import is_not_null

from testapp.models import TestModel, SecondTestModel


class BaseTests(DjangoTestCase):

    """
    To test, navigate to django_pewtils root folder and run `python manage.py test testapp.tests`
    """

    def setUp(self):

        reviews = pd.read_csv(
            os.path.join(settings.BASE_DIR, "testapp", "test_data.csv")
        )
        for index, row in reviews[:50].iterrows():
            if is_not_null(row["text"]):
                obj2 = SecondTestModel.objects.create(
                    text_field=row["text"][:200], id=index
                )
                obj = TestModel.objects.create(
                    text_field=row["text"][:200], second_related_object=obj2, id=index
                )

    def test_get_model(self):

        from django_pewtils import get_model

        for name in ["TestModel", "test model", "testmodel", "test_model"]:
            self.assertIsNotNone(get_model(name, app_name="testapp"))
            self.assertIsNotNone(get_model(name))

    # TODO: find a way to test this; problem is, Django unit tests are transactional so this kills them
    # def test_reset_django_connection(self):
    #
    #     from django_pewtils import reset_django_connection
    #     reset_django_connection(app_name="testapp")
    #     self.assertTrue(True)

    def test_filter_field_dict(self):

        from django_pewtils import filter_field_dict

        lookup_dict = {
            "bioguide_id": None,
            "icpsr_id": "12345",
            "fec_ids": [],
            "party__name": "Democratic Party",
        }

        lookup = copy.deepcopy(lookup_dict)
        result = filter_field_dict(lookup)
        self.assertEqual(result, {"icpsr_id": "12345", "fec_ids": []})

        lookup = copy.deepcopy(lookup_dict)
        result = filter_field_dict(lookup, drop_nulls=False)
        self.assertEqual(
            result, {"bioguide_id": None, "icpsr_id": "12345", "fec_ids": []}
        )

        lookup = copy.deepcopy(lookup_dict)
        result = filter_field_dict(lookup, empty_lists_are_null=True)
        self.assertEqual(result, {"icpsr_id": "12345"})

        lookup = copy.deepcopy(lookup_dict)
        result = filter_field_dict(lookup, drop_underscore_joins=False)
        self.assertEqual(
            result,
            {"party__name": "Democratic Party", "icpsr_id": "12345", "fec_ids": []},
        )

        obj = TestModel.objects.all()[0]
        result = filter_field_dict({"content_object": obj})
        self.assertEqual(result["object_id"], obj.pk)
        self.assertEqual(result["content_type"].name, "test model")

    def test_field_exists(self):

        from django_pewtils import field_exists

        self.assertTrue(field_exists(TestModel, "text_field"))
        self.assertFalse(field_exists(TestModel, "fake_field"))

    def test_get_fields_with_model(self):

        from django_pewtils import get_fields_with_model

        fields = get_fields_with_model(TestModel)
        self.assertEqual(len(fields), 3)
        fields = [f[0].name for f in fields]
        self.assertTrue("id" in fields)
        self.assertTrue("text_field" in fields)
        self.assertTrue("second_related_object" in fields)

    def test_get_all_field_names(self):

        from django_pewtils import get_all_field_names

        names = get_all_field_names(TestModel)
        self.assertTrue("id" in names)
        self.assertTrue("text_field" in names)
        self.assertTrue("second_related_object" in names)
        self.assertTrue("second_related_object_id" in names)
        self.assertEqual(len(names), 4)

    def test_consolidate_objects(self):

        from django_pewtils import consolidate_objects

        one = TestModel.objects.get(pk=1)
        two = TestModel.objects.get(pk=2)
        one = consolidate_objects(source=two, target=one)
        self.assertEqual(TestModel.objects.filter(pk=1).count(), 1)
        self.assertEqual(TestModel.objects.filter(pk=2).count(), 0)
        # TODO: this should be much more extensive

    def test_inspect_delete(self):

        to_delete = SecondTestModel.objects.all().inspect_delete(counts=True)
        self.assertEqual(to_delete[TestModel], 50)
        self.assertEqual(to_delete[SecondTestModel], 50)
        self.assertEqual(len(to_delete.keys()), 2)
        to_delete = TestModel.objects.all().inspect_delete(counts=True)
        self.assertEqual(to_delete[TestModel], 50)
        self.assertEqual(len(to_delete.keys()), 1)

        to_delete = SecondTestModel.objects.all()[0].inspect_delete(counts=True)
        self.assertEqual(to_delete[TestModel], 1)
        self.assertEqual(to_delete[SecondTestModel], 1)
        self.assertEqual(len(to_delete.keys()), 2)
        to_delete = TestModel.objects.all()[0].inspect_delete(counts=True)
        self.assertEqual(to_delete[TestModel], 1)
        self.assertEqual(len(to_delete.keys()), 1)

    def test_related_objects(self):

        results = TestModel.objects.all()[0].related_objects(counts=True)
        self.assertEqual(results["second_related_object"], 1)
        self.assertEqual(len(results.keys()), 1)
        results = SecondTestModel.objects.all()[0].related_objects(counts=True)
        self.assertEqual(results["first_related_object"], 1)
        self.assertEqual(len(results.keys()), 1)

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

    def test_create_or_update(self):

        new_text = "testing one two three"
        unique_data = {"pk": 1}
        update_data = {"text_field": new_text}

        obj = TestModel.objects.create_or_update(
            unique_data, update_data=update_data, only_update_existing_nulls=True
        )
        self.assertFalse(obj.text_field == new_text)

        obj = TestModel.objects.create_or_update(unique_data, update_data=update_data)
        self.assertTrue(obj.text_field == new_text)

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
        self.assertTrue(obj.text_field == "woot")

    def test_to_df(self):

        import pandas as pd

        df = TestModel.objects.all().to_df()
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_chunk(self):

        items = []
        for item in TestModel.objects.all().chunk(randomize=True):
            items.append(item)
        self.assertTrue(len(items) == TestModel.objects.count())

    def test_sample(self):

        sample = TestModel.objects.sample(10)
        self.assertTrue(sample.count() == 10)

    def test_chunk_delete(self):

        TestModel.objects.chunk_delete()
        self.assertTrue(TestModel.objects.count() == 0)

    def test_inspect_delete(self):

        result = TestModel.objects.inspect_delete(counts=True)
        self.assertTrue(result[TestModel] == 50)

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

        result = TestModel.objects.all().fuzzy_ratios(
            ["text_field"], "quick movie review", allow_partial=True
        )
        self.assertEqual(result[0]["pk"], 1)
        self.assertEqual(result[0]["fuzzy_ratio"], 100)

        result = TestModel.objects.all().fuzzy_ratio_best_match(
            ["text_field"], "quick movie review", allow_partial=True
        )
        self.assertEqual(result["pk"], 1)
        self.assertEqual(result["fuzzy_ratio"], 100)

    def test_tfidf_similarity(self):

        review = TestModel.objects.all()[0]
        result = review.tfidf_similarity(["text_field"], review.text_field[:100])
        self.assertAlmostEqual(result, 0.74, 2)

        result = review.similar_by_tfidf_similarity(["text_field"], min_similarity=0.1)
        self.assertEqual(result[0]["pk"], 19)
        self.assertAlmostEqual(round(result[0]["similarity"], 2), 0.21, 2)

        result = TestModel.objects.all().tfidf_similarities(
            ["text_field"], "quick movie review"
        )
        self.assertEqual(result[0]["pk"], 1)
        self.assertAlmostEqual(round(result[0]["similarity"], 2), 0.35, 2)

        result = TestModel.objects.all().tfidf_similarity_best_match(
            ["text_field"], "quick movie review"
        )
        self.assertEqual(result["pk"], 1)
        self.assertAlmostEqual(round(result["similarity"], 2), 0.35, 2)

    def test_levenshtein_difference(self):

        review = TestModel.objects.all()[0]
        result = review.levenshtein_difference(["text_field"], review.text_field[:100])
        self.assertAlmostEqual(result, 0.5, 2)

        result = review.similar_by_levenshtein_differences(
            ["text_field"], max_difference=0.9
        )[0]
        self.assertEqual(result["pk"], 19)
        self.assertEqual(result["difference"], 0.74)

    def test_trigram_similarity(self):

        review = TestModel.objects.all()[0]
        result = review.trigram_similarity(["text_field"], review.text_field[:100])
        self.assertAlmostEqual(result, 0.51, 2)
        result = review.similar_by_trigram_similarity(
            ["text_field"], min_similarity=0.1
        )[0]
        self.assertEqual(result["pk"], 49)
        self.assertAlmostEqual(result["similarity"], 0.10, 2)

    def test_run_partial_postgres_search(self):

        from django_pewtils import run_partial_postgres_search

        results = run_partial_postgres_search(TestModel, "film*", ["text_field"])
        for result in results:
            self.assertTrue("film" in result.text_field)

    def tearDown(self):
        pass
