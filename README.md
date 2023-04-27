# Django Pewtils

`django_pewtils` is a Python package that provides general-purpose Django-related tools that make it easier to 
interact with data stored in databases using the Django ORM. If you’re using Django to manage a database, Django 
Pewtils can help you do things that Django can’t do out-of-the-box, like: consolidate duplicate database records with 
complicated relations that need to be resolved; view all of the relations an object has in the database; inspect all 
of the objects that will be deleted BEFORE you run a delete query (useful for avoiding unexpected cascades); 
efficiently loop over extremely large tables; run complex text searches and compute text similarities using efficient 
built-in database functions.


## Installation 

Install with pip: 

    pip install https://github.com/pewresearch/django_pewtils#egg=django_pewtils

Install from source: 

    python setup.py install


## Overview

Django Pewtils provides a variety of useful functions that help extend the capabilities of Django and that are 
broadly applicable in any Django application. The following is a selection of highlights worth knowing about:

#### `reset_django_connection`
Provides an easy way to reset your Django database connection. Useful when multiprocessing.

#### `consolidate_objects`
Takes two objects from the same model and merges them together; very useful for de-duplicating. 

#### `BasicExtendedModel`
An abstract model that provides additional functionality, like:
 - `inspect_delete()`: tells you all of the objects that would be cascade deleted if a particular object on your model 
 were to be deleted
- `related_objects()`: returns all of a particular object's relations across your database

#### `BasicExtendedManager`
A manager class that can be added to any model like so:
```python
class MyModel(BasicExtendedModel):
    objects = BasicExtendedManager().as_manager()
```
Provides a variety of helper functions like:
- `chunk()`: loops over a QuerySet more efficiently by breaking the list of IDs into chunks and evaluating the 
QuerySet one chunk at a time
- `chunk_update(my_field="my_value")`: uses `chunk` to apply updates to a QuerySet more efficiently
- `chunk_delete()`: uses `chunk` to delete objects in a QuerySet more efficiently
- `inspect_delete()`: tells you all of the objects that would be cascade deleted if your QuerySet were to be deleted
- `get_if_exists()`: lets you use JSON-style querying to select an existing object
    ```python
    result = MyModel.objects.get_if_exists(
        {"field": "value", "second_field": "second_value", "third_field": False, "fourth_field": []},
        match_any=True,
        search_nulls=False,
        empty_lists_are_null=True
    )
    ```
- `create_or_update()`: lets you use JSON-style querying to create or retrieve an object
    ```python
    result = MyModel.objects.create_or_update(
        {"field": "value"},
        update_data={"second_field": "second_value", "third_field": None},
        save_nulls=False
    )
    ```
    
#### Text search and comparison functions
Both `BasicExtendedModel` and `BasicExtendedManager` also provide a variety of functions for searching text fields 
and making text comparison. These include:
- `BasicExtendedModel.fuzzy_ratio`
- `BasicExtendedModel.similar_by_fuzzy_ratios`
- `BasicExtendedModel.levenshtein_difference`
- `BasicExtendedModel.similar_by_levenshtein_differences`
- `BasicExtendedModel.tfidf_similarity`
- `BasicExtendedModel.similar_by_tfidf_similarity`
- `BasicExtendedModel.trigram_similarity`
- `BasicExtendedModel.similar_by_trigram_similarity`
- `BasicExtendedManager.fuzzy_ratios`
- `BasicExtendedManager.fuzzy_ratio_best_match`
- `BasicExtendedManager.levenshtein_differences`
- `BasicExtendedManager.levenshtein_difference_best_match`
- `BasicExtendedManager.tfidf_similarities`
- `BasicExtendedManager.tfidf_similarity_best_match`
- `BasicExtendedManager.trigram_similarities`
- `BasicExtendedManager.trigram_similarity_best_match`
- `BasicExtendedManager.postgres_search`


## Acknowledgements

Pew Research Center is a subsidiary of The Pew Charitable Trusts, its primary funder. 

## Use Policy 

In addition to the [license](https://github.com/pewresearch/django_pewtils/blob/master/LICENSE), Users must abide by the following conditions:

- User may not use the Center's logo
- User may not use the Center's name in any advertising, marketing or promotional materials.
- User may not use the licensed materials in any manner that implies, suggests, or could otherwise be perceived as attributing a particular policy or lobbying objective or opinion to the Center, or as a Center endorsement of a cause, candidate, issue, party, product, business, organization, religion or viewpoint.


# About Pew Research Center

Pew Research Center is a nonpartisan fact tank that informs the public about the issues, attitudes and trends shaping the world. It does not take policy positions. The Center conducts public opinion polling, demographic research, content analysis and other data-driven social science research. It studies U.S. politics and policy; journalism and media; internet, science and technology; religion and public life; Hispanic trends; global attitudes and trends; and U.S. social and demographic trends. All of the Center's reports are available at [www.pewresearch.org](http://www.pewresearch.org). Pew Research Center is a subsidiary of The Pew Charitable Trusts, its primary funder.


## Contact

For all inquiries, please email info@pewresearch.org. Please be sure to specify your deadline, and we will get back to you as soon as possible. This email account is monitored regularly by Pew Research Center Communications staff.


# Test data

Test data was downloaded from NLTK on 9/12/19:
```
import nltk
nltk.download("movie_reviews")
reviews = [{"fileid": fileid, "text": nltk.corpus.movie_reviews.raw(fileid)} for fileid in nltk.corpus.movie_reviews.fileids()]
reviews = pd.DataFrame(reviews)
reviews.to_csv("test_data.csv", encoding="utf8")
```
