from __future__ import print_function
import unittest
import copy

from django.test import TestCase as DjangoTestCase
from django.conf import settings
from django.core.management import call_command

from testapp.models import TestModel, SecondTestModel

class BaseTests(DjangoTestCase):

    """
    To test, navigate to pewtils root folder and run `python -m unittest tests`
    """

    def setUp(self):

        import nltk

        nltk.download("movie_reviews")

        for fileid in nltk.corpus.movie_reviews.fileids()[:50]:
            obj2 = SecondTestModel.objects.create(text_field=nltk.corpus.movie_reviews.raw(fileid))
            obj = TestModel.objects.create(text_field=nltk.corpus.movie_reviews.raw(fileid), second_related_object=obj2)

    def test_get_model(self):

        from django_pewtils import get_model
        get_model("TestModel", app_name="testapp")
        self.assertTrue(True)

    def test_reset_django_connection(self):

        from django_pewtils import reset_django_connection
        reset_django_connection(app_name="testapp")
        self.assertTrue(True)

    def test_filter_field_dict(self):

        from django_pewtils import filter_field_dict

        lookup_dict = {
            "bioguide_id": None,
            "icpsr_id": "12345",
            "fec_ids": [],
            "party__name": "Democratic Party"
        }

        lookup = copy.deepcopy(lookup_dict)
        result = filter_field_dict(lookup)
        self.assertTrue(result=={'icpsr_id': '12345', 'fec_ids': []})

        lookup = copy.deepcopy(lookup_dict)
        result = filter_field_dict(lookup, drop_nulls=False)
        self.assertTrue(result == {'bioguide_id': None, 'icpsr_id': '12345', 'fec_ids': []})

        lookup = copy.deepcopy(lookup_dict)
        result = filter_field_dict(lookup, empty_lists_are_null=True)
        self.assertTrue(result == {'icpsr_id': '12345'})

        lookup = copy.deepcopy(lookup_dict)
        result = filter_field_dict(lookup, drop_underscore_joins=False)
        self.assertTrue(result == {'party__name': 'Democratic Party', 'icpsr_id': '12345', 'fec_ids': []})

        obj = TestModel.objects.all()[0]
        result = filter_field_dict({"content_object": obj})
        self.assertTrue(result["object_id"]==obj.pk)
        self.assertTrue(result["content_type"].name=="test model")

    def test_field_exists(self):

        from django_pewtils import field_exists
        self.assertTrue(field_exists(TestModel, "text_field"))
        self.assertFalse(field_exists(TestModel, "fake_field"))

    def test_get_fields_with_model(self):

        from django_pewtils import get_fields_with_model

        fields = get_fields_with_model(TestModel)
        self.assertTrue(len(fields)==3)
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
        self.assertTrue(len(names)==4)

    def test_consolidate_objects(self):

        from django_pewtils import consolidate_objects

        one = TestModel.objects.get(pk=1)
        two = TestModel.objects.get(pk=2)
        one = consolidate_objects(source=two, target=one)
        self.assertTrue(TestModel.objects.filter(pk=1).count() == 1)
        self.assertTrue(TestModel.objects.filter(pk=2).count() == 0)
        # TODO: this should be much more extensive

    # def test_run_partial_postgres_search(self):
    #
    #     from django_pewtils import run_partial_postgres_search
    #     results = run_partial_postgres_search(TestModel, "film*", ["text_field"])
    #     print(results)
    #     # TODO: this can't be done on sqlite

    def test_inspect_delete(self):

        to_delete = SecondTestModel.objects.all().inspect_delete(counts=True)
        self.assertTrue(to_delete[TestModel]==50)
        self.assertTrue(to_delete[SecondTestModel]==50)
        self.assertTrue(len(to_delete.keys()) == 2)
        to_delete = TestModel.objects.all().inspect_delete(counts=True)
        self.assertTrue(to_delete[TestModel]==50)
        self.assertTrue(len(to_delete.keys())==1)

        to_delete = SecondTestModel.objects.all()[0].inspect_delete(counts=True)
        self.assertTrue(to_delete[TestModel] == 1)
        self.assertTrue(to_delete[SecondTestModel] == 1)
        self.assertTrue(len(to_delete.keys()) == 2)
        to_delete = TestModel.objects.all()[0].inspect_delete(counts=True)
        self.assertTrue(to_delete[TestModel] == 1)
        self.assertTrue(len(to_delete.keys()) == 1)

    def test_related_objects(self):
        results = TestModel.objects.all()[0].related_objects(counts=True)
        self.assertTrue(results['second_related_object']==1)
        self.assertTrue(len(results.keys())==1)
        results = SecondTestModel.objects.all()[0].related_objects(counts=True)
        self.assertTrue(results['first_related_object'] == 1)
        self.assertTrue(len(results.keys()) == 1)

    def test_fuzzy_ratio(self):
        review = TestModel.objects.all()[0]
        result = review.fuzzy_ratio(["text_field"], review.text_field[:100], allow_partial=True)
        self.assertTrue(result == 100)

    def test_similar_by_tfidf_similarity(self):
        review = TestModel.objects.all()[0]
        result = review.similar_by_tfidf_similarity(
            ["text_field"],
            review.text_field,
            min_similarity=.5
        )
        self.assertTrue(len(result)==2)

    def test_tfidf_similarity_best_match(self):
        review = TestModel.objects.all()[0]
        result = TestModel.objects.all().tfidf_similarity_best_match(
            ["text_field"],
            review.text_field,
            min_similarity=.5
        )
        self.assertTrue(result['pk']==1)

    def tearDown(self):
        pass


# class DjangoBaseTests(DjangoTestCase):
#     """
#     To test, navigate to pewtils root folder and run `python -m unittest tests`
#     """
#
#     def setUp(self):
#         pass
#
#     def test_get_model(self):
#         from django_pewtils import get_model
#
#         get_model("Document", app_name="django_learning")
#         self.assertTrue(True)
#
#     def tearDown(self):
#         pass