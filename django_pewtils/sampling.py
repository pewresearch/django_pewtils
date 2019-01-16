from __future__ import print_function
import pandas, numpy, random

from pewanalytics.stats.sampling import SampleExtractor


class DatabaseSampleExtractor(SampleExtractor):

    def __init__(self, model, filter_dict=None, exclude_dict=None, *args, **kwargs):

        self.model = model
        self.filter_dict = filter_dict
        self.exclude_dict = exclude_dict
        super(DatabaseSampleExtractor, self).__init__(*args, **kwargs)

    def extract(self, df, sample_size):

        print("Extracting {}s".format(self.model._meta.model_name))
        if self.stratify_by:
            if type(self.stratify_by) is not list:
                stratify_by=[self.stratify_by]
            qset = self.model.objects.filter(**self.filter_dict).exclude(**self.exclude_dict).values(self.id_col, *stratify_by)
        else:
            qset = self.model.objects.filter(**self.filter_dict).exclude(**self.exclude_dict).values(self.id_col)

        docs = pandas.DataFrame(list(qset))

        return super(DatabaseSampleExtractor, self).extract(docs, sample_size)


# import pandas, importlib, itertools
#
# from logos.utils.database import get_model
# from logos.utils.io import CacheHandler
# from logos.utils.data import compute_boolean_column_proportions
# from logos.utils import is_null
# from logos.sampling.utils import SampleExtractor
#
#
# class DocumentSampleHandler(object):
#
#     def __init__(self, name, *args, **options):
#
#         self.name = name
#         module = importlib.import_module("logos.sampling.samples.{}".format(name))
#         if hasattr(module, "get_sample"):
#             for k, v in getattr(module, "get_sample")().iteritems():
#                 setattr(self, k, v)
#
#         self.options = options
#         self.cache = CacheHandler("learning/document_samples/{}".format(self.name))
#         self.sample = get_model("DocumentSample").objects.get_or_create(name=self.name)[0]
#
#
#     def _add_search_flags(self, df, text_col="text"):
#
#         if len(self.sampling_searches.keys()) > 0:
#             df['none'] = ~df[text_col].str.contains(r"|".join([s['pattern'] for s in self.sampling_searches.values()]))
#             for search_name, params in self.sampling_searches.items():
#                 df[search_name] = df[text_col].str.contains(params['pattern'])
#
#         return df
#
#     def extract_sample_frame(self, refresh=False):
#
#         df = None
#         if not refresh:
#
#             df = self.cache.read("sample_frame")
#
#         if is_null(df, empty_lists_are_null=True):
#
#             print "Refreshing sample frame"
#
#             objs = get_model("Document").objects
#             if self.filter_dict: objs = objs.filter(**self.filter_dict)
#             if self.exclude_dict: objs = objs.exclude(**self.exclude_dict)
#             df = pandas.DataFrame.from_records(
#                 objs.values("text", "pk")
#             )
#
#             df = self._add_sample_weights(df)
#             self.cache.write("sample_frame", df)
#
#         else:
#
#             print "Loaded sample frame from cache"
#
#         return df
#
#     def _add_sample_weights(self, df, text_col="text"):
#
#         df = self._add_search_flags(df, text_col=text_col)
#         search_columns = self.sampling_searches.keys()+['none']
#         search_proportions = compute_boolean_column_proportions(df, search_columns)
#         df['weight'] = df[search_columns].astype(int).dot(search_proportions)
#         # df.loc[df['weight']>1.0, "weight"] = 1.0
#
#         return df
#
#     def get_sample(self, refresh=False):
#
#         df = None
#         if not refresh:
#
#             df = self.cache.read("sample")
#
#         if is_null(df, empty_lists_are_null=True):
#
#             print "Refreshing sample '{}', {} rows".format(self.name, self.sample_size)
#
#             frame = self.extract_sample_frame(refresh=refresh)
#
#             if self.sample.documents.count() == 0 or refresh:
#
#                 sample_chunks = []
#                 non_search_sample_size = 1.0 - sum([s['proportion'] for s in self.sampling_searches.values()])
#                 sample_chunks.append(
#                     SampleExtractor(sampling_strategy=self.sampling_strategy, id_col="pk").extract(
#                         frame[frame['none']==1],
#                         sample_size=int(self.sample_size*non_search_sample_size)
#                     )
#                 )
#
#                 for search, params in self.sampling_searches.iteritems():
#                     sample_chunks.append(
#                         SampleExtractor(sampling_strategy=self.sampling_strategy, id_col="pk").extract(
#                             frame[frame[search]==1],
#                             sample_size=int(self.sample_size*params["proportion"])
#                         )
#                     )
#
#                 sample_ids = list(itertools.chain(*sample_chunks))
#                 self.sample.documents = get_model("Document").objects.filter(pk__in=sample_ids)
#                 self.sample.save()
#
#             df = pandas.DataFrame.from_records(
#                 self.sample.documents.values("pk", "text")
#             )
#             df = df.merge(frame[['pk', 'weight']], how='left', on='pk')
#
#             self.cache.write("sample", df)
#
#         else:
#
#             print "Loaded sample from cache"
#
#         return df
#
