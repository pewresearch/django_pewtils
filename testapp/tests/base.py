from django.conf import settings
from django.test import TestCase as DjangoTestCase
from pewtils import is_not_null
from testapp.models import TestModel, SecondTestModel, ThroughTestModel
import copy
import itertools
import os
import pandas as pd
import time


class BaseTests(DjangoTestCase):

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
            if obj.pk % 3 == 0:
                ThroughTestModel.objects.create(owner=obj.one_to_one, related=obj)
            elif obj.pk % 2 == 0:
                ThroughTestModel.objects.create(owner=obj.foreign_key, related=obj)

        for obj2 in SecondTestModel.objects.all():
            obj2.foreign_key = TestModel.objects.exclude(pk=obj2.pk).order_by("?")[0]
            obj2.foreign_key_unique = TestModel.objects.get(pk=obj2.pk)
            obj2.save()

    def test_detect_primary_app(self):

        from django_pewtils import detect_primary_app

        result = detect_primary_app()
        self.assertEqual(result, "testapp")

    def test_load_app(self):
        # TODO: figure out how to test this
        pass

    def test_get_model(self):

        from django_pewtils import get_model

        for name in ["TestModel", "test model", "testmodel", "test_model"]:
            model = get_model(name, app_name="testapp")
            self.assertEqual(model, TestModel)
            model = get_model(name)
            self.assertIsNotNone(model, TestModel)

    # TODO: find a way to test this; problem is, Django unit tests are transactional so this kills them
    # def test_reset_django_connection(self):
    #
    #     from django_pewtils import reset_django_connection
    #     reset_django_connection(app_name="testapp")
    #     self.assertTrue(True)

    def test_inspect_delete(self):

        from django_pewtils import get_model

        m2m_model = get_model("testmodel_many_to_many", app_name="testapp")
        m2m_self_model = get_model("testmodel_many_to_many_self", app_name="testapp")

        to_delete = SecondTestModel.objects.all().inspect_delete(counts=True)
        self.assertEqual(to_delete[SecondTestModel], 50)
        self.assertEqual(to_delete[m2m_model], 150)
        self.assertEqual(len(to_delete.keys()), 3)

        to_delete = SecondTestModel.objects.all().inspect_delete(counts=False)
        self.assertEqual(to_delete[SecondTestModel].count(), 50)
        self.assertEqual(to_delete[m2m_model].count(), 150)
        self.assertEqual(len(to_delete.keys()), 3)

        to_delete = TestModel.objects.all().inspect_delete(counts=True)
        self.assertEqual(to_delete[TestModel], 50)
        self.assertEqual(to_delete[m2m_model], 150)
        self.assertEqual(to_delete[m2m_self_model], 50)
        self.assertEqual(len(to_delete.keys()), 4)

        to_delete = TestModel.objects.all().inspect_delete(counts=False)
        self.assertEqual(to_delete[TestModel].count(), 50)
        self.assertEqual(to_delete[m2m_model].count(), 150)
        self.assertEqual(to_delete[m2m_self_model].count(), 50)
        self.assertEqual(len(to_delete.keys()), 4)

        to_delete = SecondTestModel.objects.all()[0].inspect_delete(counts=True)
        self.assertEqual(to_delete[SecondTestModel], 1)
        self.assertIn(m2m_model, to_delete)
        self.assertEqual(len(to_delete.keys()), 3)

        to_delete = SecondTestModel.objects.all()[0].inspect_delete(counts=False)
        self.assertEqual(to_delete[SecondTestModel].count(), 1)
        self.assertIn(m2m_model, to_delete)
        self.assertEqual(len(to_delete.keys()), 3)

        to_delete = TestModel.objects.all()[0].inspect_delete(counts=True)
        self.assertEqual(to_delete[TestModel], 1)
        self.assertIn(m2m_model, to_delete)
        self.assertEqual(to_delete[m2m_self_model], 1)
        self.assertEqual(len(to_delete.keys()), 4)

        to_delete = TestModel.objects.all()[0].inspect_delete(counts=False)
        self.assertEqual(to_delete[TestModel].count(), 1)
        self.assertIn(m2m_model, to_delete)
        self.assertEqual(to_delete[m2m_self_model].count(), 1)
        self.assertEqual(len(to_delete.keys()), 4)

    def test_filter_field_dict(self):

        from django_pewtils import filter_field_dict

        lookup_dict = {
            "bioguide_id": None,
            "icpsr_id": "12345",
            "fec_ids": [],
            "party__name": "The America Party",
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
            {"party__name": "The America Party", "icpsr_id": "12345", "fec_ids": []},
        )

        obj = TestModel.objects.all()[0]
        result = filter_field_dict({"content_object": obj})
        self.assertEqual(result["object_id"], obj.pk)
        self.assertEqual(result["content_type"].name, "test model")

    def test_field_exists(self):

        from django_pewtils import field_exists

        self.assertTrue(field_exists(TestModel, "text_field"))
        self.assertFalse(field_exists(TestModel, "fake_field"))

    def test_get_all_field_names(self):

        from django_pewtils import get_all_field_names

        names = get_all_field_names(TestModel)
        # Fields on TestModel
        self.assertIn("id", names)
        self.assertIn("text_field", names)
        self.assertIn("foreign_key", names)
        self.assertIn("foreign_key_id", names)
        self.assertIn("foreign_key_self", names)
        self.assertIn("foreign_key_self_id", names)
        self.assertIn("foreign_key_self_reverse", names)
        self.assertIn("one_to_one", names)
        self.assertIn("one_to_one_id", names)
        self.assertIn("one_to_one_self", names)
        self.assertIn("one_to_one_self_reverse", names)
        self.assertIn("one_to_one_self_id", names)
        self.assertIn("many_to_many", names)
        self.assertIn("many_to_many_self", names)
        self.assertIn("many_to_many_self_reverse", names)
        self.assertIn("array_field", names)
        # Reverse relations on SecondTestModel
        self.assertIn("foreign_key_reverse", names)
        self.assertIn("foreign_key_self_reverse", names)
        self.assertEqual(len(names), 20)

        names = get_all_field_names(SecondTestModel)
        # Fields on SecondTestModel
        self.assertIn("id", names)
        self.assertIn("text_field", names)
        self.assertIn("foreign_key", names)
        self.assertIn("foreign_key_id", names)
        self.assertIn("foreign_key_unique", names)
        self.assertIn("foreign_key_unique_id", names)
        self.assertIn("dummy_field", names)
        # Reverse relations on TestModel
        self.assertIn("foreign_key_reverse", names)
        self.assertIn("one_to_one_reverse", names)
        self.assertIn("many_to_many_reverse", names)
        self.assertEqual(len(names), 12)

    def test_consolidate_objects(self):

        from django_pewtils import consolidate_objects, _get_unique_relations
        from django_pewtils import (
            AmbiguousConsolidationError,
            ConsolidationCascadeError,
        )
        from tqdm import tqdm

        # Loop over all possible parameter combinations
        for (
            clear_target_text,
            clear_related_uniques,
            overwrite,
            consolidate_related_uniques,
            prevent_consolidation_error,
        ) in tqdm(
            itertools.product(
                [True, False],
                [True, False],
                [True, False],
                [True, False],
                [True, False],
            ), disable=os.environ.get("DISABLE_TQDM", False),
            desc="Testing consolidate_objects",
        ):

            # Refresh the test database with brand new objects
            self.tearDown()
            TestModel.objects.all().delete()
            SecondTestModel.objects.all().delete()
            self.setUp()

            # Pick and random source and target
            source = TestModel.objects.order_by("?")[0]
            target = TestModel.objects.exclude(pk=source.pk).order_by("?")[0]

            # Make changes to the text and/or relations if desired
            if clear_related_uniques:
                # Remove conflicts that would cause a ConsolidationCascadeError
                source.one_to_one = None
                source.save()
                for related in source.foreign_key_unique_reverse.all():
                    related.foreign_key_unique = None
                    related.save()
            if clear_target_text:
                # Clear text to test overwriting
                target.text_field = None
                target.save()
            if clear_related_uniques:
                # Remove conflicts that would cause a ConsolidationCascadeError
                target.one_to_one = None
                target.save()
                for related in target.foreign_key_unique_reverse.all():
                    related.foreign_key_unique = None
                    related.save()
            if (
                not clear_related_uniques
                and consolidate_related_uniques
                and prevent_consolidation_error
            ):
                # Remove conflicts that would cause a AmbiguousConsolidationError
                for related in source.foreign_key_unique_reverse.all():
                    related.foreign_key = None
                    related.save()
                target.one_to_one.foreign_key = None
                target.one_to_one.save()
                for related in target.foreign_key_unique_reverse.all():
                    related.foreign_key = None
                    related.save()

            # Get a map of all of the related objects that will be affected
            pairs = _get_unique_relations(source, target)
            related_id_updates = {}
            for s, t in pairs:
                if s._meta.model == SecondTestModel:
                    related_id_updates[s.pk] = t.pk

            # Get all of the source relations
            source_id = source.pk
            source_text = source.text_field
            source_array = source.array_field
            source_fk_id = related_id_updates.get(
                int(source.foreign_key.pk), int(source.foreign_key.pk)
            )
            source_fk_related_ids = list(
                source.foreign_key_reverse.values_list("pk", flat=True)
            )
            source_fk_related_ids = [
                related_id_updates.get(s, s) for s in source_fk_related_ids
            ]
            source_one_to_one_id = (
                int(source.one_to_one.pk) if source.one_to_one else None
            )
            source_one_to_one_id = related_id_updates.get(
                source_one_to_one_id, source_one_to_one_id
            )
            source_many_to_many_ids = list(
                source.many_to_many.values_list("pk", flat=True)
            )
            source_many_to_many_ids = [
                related_id_updates.get(s, s) for s in source_many_to_many_ids
            ]
            source_through_ids = list(
                source.many_to_many_through_reverse.values_list("pk", flat=True)
            )

            # Get all of the target relations
            related_fk_uniques = list(
                target.foreign_key_unique_reverse.values_list("pk", flat=True)
            )
            target_id = target.pk
            target_text = target.text_field
            target_array = target.array_field
            target_fk_id = related_id_updates.get(
                int(target.foreign_key.pk), int(target.foreign_key.pk)
            )
            target_fk_related_ids = list(
                target.foreign_key_reverse.values_list("pk", flat=True)
            )
            target_fk_related_ids = [
                related_id_updates.get(t, t) for t in target_fk_related_ids
            ]
            target_one_to_one_id = (
                int(target.one_to_one.pk) if target.one_to_one else None
            )
            target_one_to_one_id = related_id_updates.get(
                target_one_to_one_id, target_one_to_one_id
            )
            target_many_to_many_ids = list(
                target.many_to_many.values_list("pk", flat=True)
            )
            target_many_to_many_ids = [
                related_id_updates.get(t, t) for t in target_many_to_many_ids
            ]
            target_through_ids = list(
                target.many_to_many_through_reverse.values_list("pk", flat=True)
            )

            # And now we deduplicate
            if not clear_related_uniques and not consolidate_related_uniques:
                # If we didn't clear dependent relations and we're not cascading, an error should occur
                self.assertRaises(
                    ConsolidationCascadeError,
                    consolidate_objects,
                    **{
                        "source": source,
                        "target": target,
                        "overwrite": overwrite,
                        "consolidate_related_uniques": consolidate_related_uniques,
                    }
                )
            elif (
                not clear_related_uniques
                and consolidate_related_uniques
                and not prevent_consolidation_error
            ):
                # If we're consolidating relations but we didn't clear out their conflicts, an error should occur
                self.assertRaises(
                    AmbiguousConsolidationError,
                    consolidate_objects,
                    **{
                        "source": source,
                        "target": target,
                        "overwrite": overwrite,
                        "consolidate_related_uniques": consolidate_related_uniques,
                    }
                )
            else:
                # Otherwise, things should consolidate nicely
                target = consolidate_objects(
                    source=source,
                    target=target,
                    overwrite=overwrite,
                    consolidate_related_uniques=consolidate_related_uniques,
                )

                # Make sure that the source was removed and self-references were preserved
                self.assertEqual(TestModel.objects.filter(pk=source_id).count(), 0)
                self.assertEqual(TestModel.objects.filter(pk=target_id).count(), 1)
                self.assertEqual(target.foreign_key_self.pk, target.pk)
                self.assertEqual(target.one_to_one_self.pk, target.pk)

                # Make sure the foreign key was correctly set
                if overwrite:
                    self.assertEqual(target.foreign_key.pk, source_fk_id)
                else:
                    self.assertEqual(target.foreign_key.pk, target_fk_id)

                # Make sure the text was correctly set
                if clear_target_text or overwrite:
                    self.assertEqual(target.text_field, source_text)
                else:
                    self.assertEqual(target.text_field, target_text)

                # If we didn't clear out dependent relations then cascading should have occurred
                if not clear_related_uniques:
                    # So the one-to-ones should have been collapsed too
                    self.assertEqual(target.one_to_one.pk, target_one_to_one_id)
                    self.assertEqual(source_one_to_one_id, target_one_to_one_id)
                    self.assertEqual(
                        SecondTestModel.objects.filter(pk=target_one_to_one_id).count(),
                        1,
                    )

                # Regardless, non-dependent/unique related objects should still exist
                self.assertEqual(
                    SecondTestModel.objects.filter(pk=target_fk_id).count(), 1
                )
                self.assertEqual(
                    SecondTestModel.objects.filter(pk=source_fk_id).count(), 1
                )

                # Many-to-many relations should have been collapsed
                new_target_many_to_many_ids = list(
                    target.many_to_many.values_list("pk", flat=True)
                )
                for pk in source_many_to_many_ids:
                    # All source relations should be preserved
                    self.assertIn(pk, new_target_many_to_many_ids)
                for pk in target_many_to_many_ids:
                    # All target relations should be preserved
                    self.assertIn(pk, new_target_many_to_many_ids)
                all_many_to_many_ids = list(
                    set(source_many_to_many_ids).union(set(target_many_to_many_ids))
                )
                for pk in new_target_many_to_many_ids:
                    # And there shouldn't be any new relations besides the originals
                    self.assertIn(pk, all_many_to_many_ids)

                # Same goes for the many-to-many self-reference relations we created
                new_target_many_to_many_self_ids = list(
                    target.many_to_many_self.values_list("pk", flat=True)
                )
                self.assertIn(target.pk, new_target_many_to_many_self_ids)
                self.assertEqual(len(new_target_many_to_many_self_ids), 1)

                # And the through table relations
                new_target_through_ids = list(
                    target.many_to_many_through_reverse.values_list("pk", flat=True)
                )
                for pk in set(source_through_ids).union(set(target_through_ids)):
                    pk = related_id_updates.get(pk, pk)
                    self.assertIn(pk, new_target_through_ids)

                # All related SecondTestModel objects should have their foreign keys forwarded
                new_fk_related_ids = list(
                    target.foreign_key_reverse.values_list("pk", flat=True)
                )
                for pk in source_fk_related_ids:
                    # Objects related to source should now be related to target
                    self.assertEqual(
                        SecondTestModel.objects.get(pk=pk).foreign_key.pk, target.pk
                    )
                    self.assertIn(pk, new_fk_related_ids)
                for pk in target_fk_related_ids:
                    # All of the objects previously related to target should still be related
                    self.assertEqual(
                        SecondTestModel.objects.get(pk=pk).foreign_key.pk, target.pk
                    )
                    self.assertIn(pk, new_fk_related_ids)
                all_fk_related_ids = list(
                    set(source_fk_related_ids).union(set(target_fk_related_ids))
                )
                for pk in new_fk_related_ids:
                    # And there shouldn't be any new ones
                    self.assertIn(pk, all_fk_related_ids)

                # Arrays should have been merged
                for val in source_array:
                    self.assertIn(val, target.array_field)
                for val in target_array:
                    self.assertIn(val, target.array_field)

                # Make sure other reverse foreign key relations were forwarded to target
                for pk in related_fk_uniques:
                    self.assertEqual(
                        SecondTestModel.objects.get(pk=pk).foreign_key_unique, target
                    )

                # Finally, any cascades that required SecondTestModel objects to be merged
                # should have been properly consolidated (source objects shouldn't exist)
                for old, new in related_id_updates.items():
                    self.assertEqual(SecondTestModel.objects.filter(pk=old).count(), 0)
                    self.assertEqual(SecondTestModel.objects.filter(pk=new).count(), 1)

    def test_cache_handler(self):

        from django_pewtils import CacheHandler

        h = CacheHandler("cache", use_database=True, hash=True)
        h.write("test", "test", timeout=2)
        time.sleep(2)
        self.assertIsNone(h.read("test"))
        h.write("test", "test", timeout=60)
        self.assertEqual(h.read("test"), "test")
        h.clear_key("test")
        self.assertIsNone(h.read("test"))
        h.write("test", "test", timeout=60)
        h.clear()
        self.assertIsNone(h.read("test"))

        h = CacheHandler("cache", use_database=True, hash=False)
        h.write("test", "test", timeout=2)
        time.sleep(2)
        self.assertIsNone(h.read("test"))
        h.write("test", "test", timeout=60)
        self.assertEqual(h.read("test"), "test")
        h.clear_key("test")
        self.assertIsNone(h.read("test"))
        h.write("test", "test", timeout=60)
        h.clear()
        self.assertIsNone(h.read("test"))

        h = CacheHandler("cache", use_database=False, hash=True)
        h.write("test", "test", timeout=2)
        time.sleep(2)
        self.assertIsNone(h.read("test"))
        h.write("test", "test", timeout=60)
        self.assertEqual(h.read("test"), "test")
        h.clear_key("test")
        self.assertIsNone(h.read("test"))
        h.write("test", "test", timeout=60)
        h.clear()
        self.assertIsNone(h.read("test"))

        h = CacheHandler("cache", use_database=True, hash=False)
        h.write("test", "test", timeout=2)
        time.sleep(2)
        self.assertIsNone(h.read("test"))
        h.write("test", "test", timeout=60)
        self.assertEqual(h.read("test"), "test")
        h.clear_key("test")
        self.assertIsNone(h.read("test"))
        h.write("test", "test", timeout=60)
        h.clear()
        self.assertIsNone(h.read("test"))

    def test_get_app_settings_folders(self):

        from django_pewtils import get_app_settings_folders

        result = get_app_settings_folders("TEST_SETTINGS_FOLDERS")
        self.assertEqual(len(result), 2)
        self.assertIn("testapp", result)
        self.assertIn("testapp_installed", result)

    def test_run_partial_postgres_search(self):

        from django_pewtils import run_partial_postgres_search

        results = run_partial_postgres_search(TestModel, "film*", ["text_field"])
        for result in results:
            self.assertTrue("film" in result.text_field)

    def tearDown(self):
        from django.conf import settings
        import shutil
        import os

        cache_path = os.path.join(settings.BASE_DIR, settings.LOCAL_CACHE_ROOT)
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
