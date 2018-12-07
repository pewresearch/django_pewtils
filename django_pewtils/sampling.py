import pandas, numpy, random

from pewtils import group_percentages


# TODO: does SampleExtractor have any actual django dependencies or can this be moved to pewtils/sampling.py?

class SampleExtractor(object):

    def __init__(self, stratify_by=None, id_col='document__pk', seed=None, sampling_strategy='guarantee_strata', logger=None):

        self.stratify_by = stratify_by
        self.id_col = id_col
        self.seed = seed
        self.sampling_strategy = sampling_strategy
        self.logger = logger

    def extract(self, df, sample_size):

        """
        :param df: dataframe
        :param sample_size:  integer (for sample size) or decimal (percentage of df)
        :param stratify_by: (column or list of columns in the dataframe to stratify on)
        :param id_col: column in the dataframe to be used as the record id
        :param seed: random seed ( optional )
        :param type: type of stratification to use . pass "even" if sample evenly from each strata. Otherwise strata-proportional sampling will be applied.
        :return:
        """

        if self.sampling_strategy:
            if self.stratify_by:
                # pass in a list or a single column to stratify by
                stratify_by = [self.stratify_by] if not isinstance(self.stratify_by, list) else self.stratify_by
                if self.logger:
                    self.logger.info("stratify on columns: {}".format(",".join(stratify_by)))
                # NOTE: use logos.utils.get_logger() and pass it to this class if you want logging
                frame_size = df.shape[0]
                # So you can pass in a decimal proportion of total dataframe or number of samples
                sample_n = sample_size if sample_size >= 1 else int(round(sample_size*frame_size))
                if not self.seed:
                    self.seed = int(round(1000*numpy.random.random()))

                if self.sampling_strategy == 'even':
                    doc_ids = self._stratify_sample_even(df, sample_n)
                elif self.sampling_strategy == 'guarantee_strata':
                    strata_one = self._take_one_per_strata(df, sample_n)
                    left_to_sample = sample_n - len(strata_one)
                    if left_to_sample > 0:
                        doc_ids = self._stratify_sample_final(df[~df[self.id_col].isin(strata_one)], left_to_sample)
                        doc_ids = list(doc_ids) + list(strata_one)
                    else:
                        print("Nothing left to sample, no stratification applied")
                        doc_ids = strata_one
                else:
                    doc_ids = self._stratify_sample_final(df, sample_n)

            else:
                # If no stratification at all
                if self.logger:
                    self.logger.info("Basic random sample")
                doc_ids =  self._basic_sample(df[self.id_col], sample_size).values

            print "Sample of %i extracted" % (len(doc_ids))
            return list(doc_ids)
        else:
            print "No sampling strategy specified; extracting entire frame"
            return df[self.id_col].values


    def _take_one_per_strata(self, df, sample_n):

        # Number of groups to stratify by must be less than the total sample size
        strata_groups = df.groupby(self.stratify_by)[self.id_col].count().count()
        print("strata groups ({}) & things to sample: {}".format(strata_groups, sample_n))
        if sample_n > strata_groups:
            print("sample one document per strata first")
            one_per = df.groupby(self.stratify_by).apply(lambda x: x.sample(1, random_state=self.seed))[self.id_col].values
            return one_per
        else:
            print("There are more strata groups ({}) than things to sample: {}".format(strata_groups, sample_n))
            one_per = df.groupby(self.stratify_by).apply(lambda x: x.sample(1, random_state=self.seed))[self.id_col].sample(sample_n).values
            return one_per

    def _stratify_sample_even(self, df, sample_size):

        """
        Sample evenly from each group that's stratified by.
        At least one document per group

        :param df: dataframe to sample from
        :param sample_size: sample size ( int )
        :param stratify_by: column name to stratify by ( or list of columns )
        :param id_col:
        :return: id column for the sample & stats about the sample
        """
        random.seed(self.seed)
        # This works for a list of strata-cols too
        docs_per_strata = float(sample_size)/ float(df.groupby(self.stratify_by)[self.id_col].count().count())
        print("Drawing even samples of {} across all stratification groups".format(docs_per_strata))
        all_strata = df[self.stratify_by].unique()
        random.shuffle(all_strata)
        doc_ids = []
        while len(doc_ids) < sample_size:
            for strata in all_strata:
                strata_data = df[df[self.stratify_by]==strata]
                # strata_sample_size = min([docs_per_strata, (sample_size - len(doc_ids))])
                # doc_ids.append(strata_data[self.id_col].sample(strata_sample_size))
                strata_doc_prob = docs_per_strata / float(len(strata_data[self.id_col]))
                for i, doc in strata_data.iterrows():
                    if random.random() <= strata_doc_prob:
                        doc_ids.append(doc[self.id_col])
                        if len(doc_ids) == sample_size: break
                if len(doc_ids) == sample_size: break

        return doc_ids

    def _stratify_sample_final(self, df, sample_n):

        """
            proportional stratification

            Method sourced from : Kish, Leslie. "Survey sampling." (1965).  Chapter 4.

        """
        print("Kish-style stratification")
        # Subset & copy cols that we care about
        data = df.copy()[[self.id_col] + [self.stratify_by]]
        frame_size = data.shape[0]

        # Shuffle the dataframe a
        if self.logger:
            self.logger.debug("Random seed: {}".format(self.seed))
        numpy.random.seed(self.seed)
        if self.logger:
            self.logger.debug("Dataframe before sorting:{}".format(data.head()))
        data.index = numpy.random.permutation(data.index)
        # re-sort grouped by strata
        data = data.groupby(self.stratify_by).apply(lambda x: x.sort_index())
        data.index = range(0, frame_size)
        if self.logger:
            self.logger.debug("Dataframe after shuffle & groupby sorting:{}".format(data.head()))

        skip_interval = float(frame_size)/float(sample_n)

        start_index = numpy.random.uniform(0,skip_interval) # index to start from
        if self.logger:
            self.logger.info("start index : {}".format(start_index))
        mysample_index = numpy.round((numpy.zeros(sample_n) + start_index) + (numpy.arange(sample_n) * skip_interval))

        # Return the real id column
        mysample_id = data[data.index.isin(mysample_index)][self.id_col].values

        return mysample_id

    def _stratify_sample_2(self, df, sample_size):
        """
        In stratified sampling, the overall proportion of each group is preserved

        :param df: dataframe to sample from
        :param sample_size: sample size ( int )
        :param stratify_by: column name to stratify by ( or list of columns )
        :param id_col:
        :return: id column for the sample & stats about the sample
        """
        print("New stratification method")
        docs_per_strata = {}
        if self.stratify_by:

            docs_per_strata = (group_percentages(df, self.stratify_by, self.id_col)).to_dict()
            doc_ids = []

            for strata, strata_data in df.groupby(self.stratify_by):
                sample_strata_ids = self._basic_sample(strata_data[self.id_col], docs_per_strata[strata]).values.tolist()
                doc_ids = doc_ids + sample_strata_ids

            print "Stratified sample of %i extracted" % (len(doc_ids))

        else:
            doc_ids = self._basic_sample(df[self.id_col], sample_size, seed=self.seed).values.tolist()

        return doc_ids, docs_per_strata

    def _basic_sample(self, df, size):

        if size >= 1:
            try:
                return df.sample(int(size), random_state=self.seed)
            except ValueError:
                return df
        else:
            return df.sample(frac=float(size), random_state=self.seed)


class DatabaseSampleExtractor(SampleExtractor):

    def __init__(self, model, filter_dict=None, exclude_dict=None, *args, **kwargs):

        self.model = model
        self.filter_dict = filter_dict
        self.exclude_dict = exclude_dict
        super(DatabaseSampleExtractor, self).__init__(*args, **kwargs)

    def extract(self, df, sample_size):

        print "Extracting {}s".format(self.model._meta.model_name)
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
