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