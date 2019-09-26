from __future__ import print_function
from builtins import object
import shutil, re, importlib, pkgutil, os, imp

from itertools import chain
from collections import defaultdict

from pewtils import is_null
from pewtils.internal import try_once_again
from pewtils.io import FileHandler

from django.core.exceptions import ImproperlyConfigured

try:
    from django.contrib.admin.utils import NestedObjects
    from django.db import DEFAULT_DB_ALIAS
    from django.apps import apps
    from django.db import IntegrityError
    from django.core.cache import cache
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Case, When
    from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
except ImproperlyConfigured:
    pass


def load_app(app_name, path=None, env=None):
    if not env:
        env = {}
    import os, django

    for k, v in env.items():
        os.environ[k] = v
    if path:
        import sys

        sys.path.insert(0, path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{}.settings".format(app_name))
    django.setup()


def get_model(name, app_name=None):
    """
    Returns a Django model class via a string lookup
    :param name: Name of the model
    :param app_name: Name of the app
    :return: Django model class
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
    else:
        return model


def django_multiprocessor(app_name):
    def _django_multiprocessor(func, *args):
        reset_django_connection(app_name)
        return func(*args)

    return _django_multiprocessor


def reset_django_connection_wrapper(app_name):
    def _reset_django_connection_wrapper(handle):
        def wrapper(self, *args, **options):
            reset_django_connection(app_name)
            return handle(self, *args, **options)

        return wrapper

    return _reset_django_connection_wrapper


def reset_django_connection(app_name=None):
    if not app_name:
        from django.conf import settings

        app_name = settings.SITE_NAME
    load_app(app_name)
    from django.db import connection

    connection.close()


def inspect_delete(items, counts=False):
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


def get_fields_with_model(model):
    return [
        (f, f.model if f.model != model else None)
        for f in model._meta.get_fields()
        if not f.is_relation or f.one_to_one or (f.many_to_one and f.related_model)
    ]


def get_all_field_names(model):
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


def consolidate_objects(
    source=None, target=None, overwrite=False, merge_one_to_ones=False
):
    if source and target and source._meta.model == target._meta.model:

        fields = source._meta.get_fields()
        for f in fields:
            if not f.is_relation:
                if isinstance(getattr(target, f.name), list) and isinstance(
                    getattr(source, f.name), list
                ):
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
                    is_null(getattr(target, f.name), empty_lists_are_null=True)
                    or overwrite
                ):
                    val = getattr(source, f.name)
                    if f.unique:
                        setattr(source, f.name, None)
                        source.save()
                    setattr(target, f.name, val)
            elif f.one_to_one or f.many_to_one:

                if hasattr(target, f.name) and (
                    is_null(getattr(target, f.name), empty_lists_are_null=True)
                    or overwrite
                ):

                    if f.concrete:
                        setattr(target, f.name, getattr(source, f.name))
                        if f.one_to_one:
                            setattr(source, f.name, None)
                            source.save()
                    else:

                        related_object = getattr(source, f.name)
                        setattr(related_object, f.remote_field.name, target)
                        related_object.save()

            elif f.one_to_many:

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
                    other_unique_fields = []
                    for other in f.remote_field.model._meta.get_fields():
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
                        source_objs = getattr(source, f.name).all()
                        for other in other_unique_fields:
                            source_objs = source_objs.filter(
                                **{other: getattr(t, other)}
                            )
                        for s in source_objs:
                            t = consolidate_objects(s, t)

                if hasattr(f, "object_id_field_name"):  # it's a generic relation
                    pk_field = f.object_id_field_name
                    for related_object in getattr(source, f.name).all():
                        setattr(related_object, pk_field, target.pk)
                        related_object.save()
                else:
                    for related_object in getattr(source, f.name).all():
                        setattr(related_object, f.remote_field.name, target)
                        related_object.save()

            elif f.many_to_many:

                try:
                    merged_objects = (
                        getattr(source, f.name).all() | getattr(target, f.name).all()
                    )
                    setattr(target, f.name, merged_objects)
                except AttributeError:
                    pass

        if hasattr(source, "history"):
            for h in source.history.all():
                h.id = target.pk
                h.save()

        try:
            # attempt to save the target before deleting the source, just to be safe
            # but if there's a unique constraint collision, the source needs to go before the target is saved
            target.save()
            source.delete()
        except IntegrityError:
            source.delete()
            target.save()

    return target


class CacheHandler(object):
    def __init__(self, path, use_database=False, hash=True, **options):

        self.path = path
        self.file_handler = FileHandler(self.path, **options)
        self.use_database = use_database
        self.hash = hash
        if self.use_database:
            self.cached_keys = []

    def write(self, key, value, timeout=5 * 60):

        if self.use_database:
            k = "/".join([self.path, key])
            if self.hash:
                k = self.file_handler.get_key_hash(k)
            self.cached_keys.append(k)
            cache.set(k, value, timeout)
        else:
            self.file_handler.write(key, value, hash_key=self.hash)

    @try_once_again
    def read(self, key):

        if self.use_database:
            if self.hash:
                key = self.file_handler.get_key_hash(key)
            return cache.get("/".join([self.path, key]))
        else:
            return self.file_handler.read(key, hash_key=self.hash)

    def clear(self):

        if self.use_database:
            print(
                "Warning: only keys that have been set by this CacheHandler instance will be cleared"
            )
            for k in self.cached_keys:
                cache.set("/".join([self.path, k]), None)
        else:
            if not self.file_handler.use_s3:
                try:
                    shutil.rmtree(self.file_handler.path)
                except OSError:
                    pass
            else:
                bucket_list = self.file_handler.s3.list(prefix=self.path)
                result = self.file_handler.s3.delete_keys(
                    [key.name for key in bucket_list]
                )


def get_app_settings_folders(settings_dir_list_var):
    command_dirs = []
    for appconf in apps.get_app_configs():
        try:
            settings_module = imp.load_source(
                "{}.settings".format(appconf.name),
                os.path.join(appconf.path, "settings.py"),
            )
            dirs = getattr(settings_module, settings_dir_list_var)
        except (AttributeError, IOError):
            dirs = []
        command_dirs.extend(dirs)
    from django.conf import settings

    if hasattr(settings, settings_dir_list_var):
        command_dirs.extend(getattr(settings, settings_dir_list_var))
    return list(set(command_dirs))


def run_partial_postgres_search(model, text, fields, max_results=250, min_rank=0.0):
    """
    Example usage: run_partial_postgres_search(ATPQuestion, text, ("description", "name", "response_options__label"), max_results=250)
    :param model: the model you want to search
    :param text: the search query
    :param fields: tuple of fields to search
    :param max_results: top N results you want to return
    :return:
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


# def extract_site_module_attributes(path, site_name, attribute_name):
#
#     from django.conf import settings
#     name_split = path.split(site_name)
#     name_split = site_name.join(name_split[1:])
#     name = settings.SITE_NAME + re.sub(r"[/\\]", '.', name_split)
#     path = [path]
#     attributes = {}
#     path = pkgutil.extend_path(path, name)
#     for importer, modname, ispkg in pkgutil.walk_packages(path=path, prefix=name + '.'):
#         if not ispkg:
#             module = importlib.import_module(modname)
#             if hasattr(module, attribute_name):
#                 attribute = getattr(module, attribute_name)
#                 attributes[modname.split(".")[-1]] = attribute
#
#     return attributes
#
#
# def extract_attributes_from_folder(folder_path, attribute_name):
#
#     attributes = {}
#     if os.path.exists(folder_path):
#         #try:
#         for file in os.listdir(folder_path):
#             import pdb
#             pdb.set_trace()
#             if file.endswith(".py") and not file.startswith("__init__"):
#                 full_path_to_module = os.path.join(folder_path, file)
#                 module_dir, module_file = os.path.split(full_path_to_module)
#                 module_name, module_ext = os.path.splitext(module_file)
#                 save_cwd = os.getcwd()
#                 import pdb
#                 pdb.set_trace()
#                 os.chdir(module_dir)
#                 module_obj = __import__(module_name)
#                 module_obj.__file__ = full_path_to_module
#                 if hasattr(module_obj, attribute_name):
#                     attributes[module_name] = getattr(module_obj, attribute_name)
#                 os.chdir(save_cwd)
#         #except:
#         #    raise ImportError
#     return attributes
