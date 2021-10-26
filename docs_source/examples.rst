*************************************
Examples
*************************************

Basic functions
===============

.. code:: ipython3

    from django_pewtils import get_model

.. code:: ipython3

    get_model("facebook page")


.. parsed-literal::

    logos.models.facebook.FacebookPage


.. code:: ipython3

    get_model("facebookpage")




.. parsed-literal::

    logos.models.facebook.FacebookPage



.. code:: ipython3

    get_model("Facebook_Page")




.. parsed-literal::

    logos.models.facebook.FacebookPage



.. code:: ipython3

    get_model("contenttype")




.. parsed-literal::

    django.contrib.contenttypes.models.ContentType



.. code:: ipython3

    get_model("document")




.. parsed-literal::

    django_learning.models.documents.Document



.. code:: ipython3

    from django_pewtils import reset_django_connection
    reset_django_connection(app_name="logos")

.. code:: ipython3

    from django_pewtils import get_all_field_names
    get_all_field_names(Politician)




.. parsed-literal::

    ['education_bachelors',
     'age',
     'votes_for',
     'staffers',
     'education_bachelors_institution',
     'twitter_profiles',
     'webpages',
     'votes_against',
     'military_service_branch',
     'press_releases',
     'facebook_pages',
     'ballotpedia_id',
     'has_press_release_scraper',
     'command_logs',
     'last_name',
     'education_associates',
     'education_md_institution',
     'contributions_donated',
     'ranking_member_committees',
     'military_service',
     'committees',
     'elections_won',
     'current_term_id',
     'cosponsored_bills',
     'current_term',
     'caucuses',
     'valid_wikipedia_id',
     'fec_ids',
     'education_jd_institution',
     'suffix',
     'image_src',
     'latest_term_id',
     'education_masters_institution',
     'profession',
     'education_jd',
     'military_service_years',
     'ballotpedia_page',
     'nickname',
     'icpsr_id',
     'chaired_committees',
     'personal_metrics',
     'birthday',
     'old_facebook_ids',
     'middle_initial',
     'twitter_ids',
     'incumbent_elections',
     'lis_id',
     'education_associates_institution',
     'in_office',
     'id',
     'campaigns',
     'wikipedia_id',
     'instagram_ids',
     'commands',
     'party',
     'education_phd',
     'hearings',
     'wikipedia_page',
     'old_twitter_ids',
     'committee_memberships',
     'party_id',
     'terms',
     'gender',
     'old_instagram_ids',
     'facebook_ids',
     'valid_ballotpedia_id',
     'govtrack_id',
     'sponsored_bills',
     'speeches',
     'latest_term',
     'capitol_words_speech_backfill',
     'bioguide_bio',
     'bioguide_id',
     'education_phd_institution',
     'education_md',
     'education_masters',
     'opensecrets_id',
     'contributions_received',
     'scrape_logs',
     'votes_abstained',
     'relevant_news_articles',
     'thomas_id',
     'first_name',
     'religion',
     'birthplace',
     'verifications']



The core of Django Pewtils: the ``BasicExtendedModel`` and ``BasicExtendedManager``
===================================================================================

Django Pewtils’ main purpose is to extend the Django ORM with useful
functions for working with records and queries in your database. The
overwhelming majority of these functions can be found on two classes.
The ``BasicExtendedModel`` extends Django’s base Model class with
additional row-level functions, and the ``BasicExtendedManager`` extends
Django’s base Manager class with additional table/query-level functions.
To use these extended classes, just swap out ``models.Model`` for
``BasicExtendedModel`` in your model definition. It uses
``BasicExtendedManager`` by default, so you don’t even have to worry
about that.

.. code:: python

       class TestModel(BasicExtendedModel):
           pass

Let’s start by taking a look at the Politician table, which contains
members of Congress, presidential candidates, and other politicians

.. code:: ipython3

    politicians = Politician.objects.all()

.. code:: ipython3

    politicians




.. parsed-literal::

    <PoliticianManager [<Politician: John Michael Fleig>, <Politician: James Berryhill>, <Politician: Joseph C Miechowicz>, <Politician: James Edgar Sr Md Lundeen>, <Politician: Daniel Cochcran 'Dc' Morrison>, <Politician: Mary Pallant>, <Politician: Charles Taylor Sutherland>, <Politician: Demetrios S Giannaros>, <Politician: Corinne Nicole Westerfield>, <Politician: Joseph M Kyrillos Jr>, <Politician: Paul Andrew Rundquist>, <Politician: Jim Bussler>, <Politician: Sona Mehring>, <Politician: William G. Barnes>, <Politician: Carol Ann Joyce Larosa>, <Politician: John R. Cox>, <Politician: >, <Politician: Go Vegan Go Vegan>, <Politician: Trish Causey>, <Politician: Christopher Alen Andrade>, '...(remaining elements truncated)...']>



.. code:: ipython3

    politicians.count()




.. parsed-literal::

    20673



If we wanted to quickly grab all of this data and start crunching
numbers, we can do that easily by using the ``.to_df`` function provided
by the ``BasicExtendedManager``, which converts any arbitrary Django
query into a Pandas DataFrame. Just watch your memory with big queries!

.. code:: ipython3

    politicians.to_df()




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }

        .dataframe tbody tr th {
            vertical-align: top;
        }

        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>id</th>
          <th>first_name</th>
          <th>middle_initial</th>
          <th>last_name</th>
          <th>nickname</th>
          <th>suffix</th>
          <th>has_press_release_scraper</th>
          <th>religion</th>
          <th>gender</th>
          <th>birthday</th>
          <th>...</th>
          <th>birthplace</th>
          <th>military_service</th>
          <th>military_service_years</th>
          <th>military_service_branch</th>
          <th>profession</th>
          <th>bioguide_bio</th>
          <th>current_term_id</th>
          <th>latest_term_id</th>
          <th>party_id</th>
          <th>in_office</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>49974</td>
          <td>John</td>
          <td>Michael</td>
          <td>Fleig</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>1</th>
          <td>62869</td>
          <td>James</td>
          <td></td>
          <td>Berryhill</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>2</th>
          <td>49987</td>
          <td>Joseph</td>
          <td>C</td>
          <td>Miechowicz</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>3</th>
          <td>50087</td>
          <td>James</td>
          <td>Edgar Sr Md</td>
          <td>Lundeen</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>4</th>
          <td>50108</td>
          <td>Daniel</td>
          <td>Cochcran</td>
          <td>Morrison</td>
          <td>Dc</td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>...</th>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <th>20668</th>
          <td>58883</td>
          <td>Julio</td>
          <td></td>
          <td>Castaneda</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>20669</th>
          <td>58884</td>
          <td>Samir</td>
          <td></td>
          <td>Jammal</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>20670</th>
          <td>58911</td>
          <td>Brian</td>
          <td></td>
          <td>Forde</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>20671</th>
          <td>58657</td>
          <td>Joshua</td>
          <td>A</td>
          <td>Mandel</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>20672</th>
          <td>58689</td>
          <td>Robert</td>
          <td></td>
          <td>Kennedy</td>
          <td></td>
          <td>Jr.</td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
      </tbody>
    </table>
    <p>20673 rows × 52 columns</p>
    </div>



We could also pull a random sample using ``.sample``

.. code:: ipython3

    politicians.sample(10)




.. parsed-literal::

    <PoliticianManager [<Politician: Gene Eugene Green>, <Politician: Michael C Hight>, <Politician: Jason Kander>, <Politician: Steven Edward Mirabella>, <Politician: Harold L Whitfield>, <Politician: Sheirl Lee Fletcher>, <Politician: Joe Manchik>, <Politician: Charles Wayne Dowdy>, <Politician: Nicholas Tutora>, <Politician: Matthew Caroll Hook>]>



.. code:: ipython3

    politicians.sample(10).to_df()




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }

        .dataframe tbody tr th {
            vertical-align: top;
        }

        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>id</th>
          <th>first_name</th>
          <th>middle_initial</th>
          <th>last_name</th>
          <th>nickname</th>
          <th>suffix</th>
          <th>has_press_release_scraper</th>
          <th>religion</th>
          <th>gender</th>
          <th>birthday</th>
          <th>...</th>
          <th>birthplace</th>
          <th>military_service</th>
          <th>military_service_years</th>
          <th>military_service_branch</th>
          <th>profession</th>
          <th>bioguide_bio</th>
          <th>current_term_id</th>
          <th>latest_term_id</th>
          <th>party_id</th>
          <th>in_office</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>5804</td>
          <td>Eric</td>
          <td>J. J.</td>
          <td>Massa</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>M</td>
          <td>1959-09-16</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>MASSA, Eric J.J., a Representative from New Yo...</td>
          <td>None</td>
          <td>9827.0</td>
          <td>26.0</td>
          <td>False</td>
        </tr>
        <tr>
          <th>1</th>
          <td>45570</td>
          <td>Peter</td>
          <td></td>
          <td>Vivaldi</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>2</th>
          <td>47758</td>
          <td>James</td>
          <td>A</td>
          <td>Hayden</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>3</th>
          <td>51324</td>
          <td>Clinton</td>
          <td></td>
          <td>Desjarlais</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>4</th>
          <td>54965</td>
          <td>Adam</td>
          <td>D</td>
          <td>Shaffer</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>5</th>
          <td>55248</td>
          <td>Myrtle</td>
          <td>Charlotte Montomery</td>
          <td>Carlyle</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>6</th>
          <td>57725</td>
          <td>Billy</td>
          <td></td>
          <td>Falling</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>7</th>
          <td>59130</td>
          <td>Angie</td>
          <td></td>
          <td>Chirino</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>8</th>
          <td>61854</td>
          <td>Wednesday</td>
          <td>Alexandra</td>
          <td>Green</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
        <tr>
          <th>9</th>
          <td>64080</td>
          <td>Chris</td>
          <td>B.</td>
          <td>Royal</td>
          <td></td>
          <td></td>
          <td>False</td>
          <td>None</td>
          <td>None</td>
          <td>NaT</td>
          <td>...</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>None</td>
          <td>NaN</td>
          <td>NaN</td>
          <td>None</td>
        </tr>
      </tbody>
    </table>
    <p>10 rows × 52 columns</p>
    </div>



The Politician table isn’t *super* large, but if it was, fully
evaluating the query could cause you problems - by default, Django will
try to load queries into memory, even if you’re just trying to loop over
each record and do something with it one at a time. To help with this,
the ``.chunk`` function will efficiently load the full list of primary
keys in your query and iterate over them in chunks, to keep things
light.

.. code:: ipython3

    for obj in politicians.chunk(size=1000):  # Behind the scenes, Django Pewtils will iterate over the records 1000 at a time
        pass  # do something

Similarly, if we want to make bulk changes to a set of records in a
table, we can use the ``chunk_update`` function. And if your query
stalls when trying to delete records in bulk (like
``politicians.delete()``), then the ``chunk_delete`` function can help
you delete your records en masse. (For obvious reasons, we won’t be
doing a live example of these here.)

.. code:: python

       politicians.chunk_update(first_name="Bob")

.. code:: python

       politicians.chunk_delete()

Anyway, let’s explore some of the other Django Pewtils functions with an
example. The records that we see in our Politician table didn’t come
from nowhere - we had to compile our database from a variety of
different data sources. The @unitedstates GitHub is a great place to
start - it has tons of information on members of Congress, including
their names, terms of office, social media accounts, and more. But there
are tons of other sources too: Wikipedia has extensive bios on Congress,
the FEC provides detailed campaign finance data, etc. To bring all of
this data together, we need to harmonize records from these various
sources - which can be difficult because different sources use different
unique identifiers, and not all of the data is perfectly clean.

Let’s see how Django Pewtils can help us with some of these challenges.
Let’s imagine that Dwayne “The Rock” Johnson decides to run for
President in 2024, but drops out of the race after losing to Oprah in
the primaries, runs for Senate, gets elected there instead. He first
shows up in our database via the record below:

.. code:: ipython3

    initial_record = {
        "bioguide_id": "J99999",
        "first_name": "Dwayne",
        "last_name": "Johnson"
    }
    Politician.objects.create(**initial_record)
    Politician.objects.get(bioguide_id="J99999")




.. parsed-literal::

    <Politician: Dwayne Johnson>



Now let’s say we download data from another source that has some
additional information on politicians - including the FEC ID for Senator
Rock’s failed presidential bid, and the ID for his campaign’s Instagram
account.

.. code:: ipython3

    new_record = {
        "bioguide_id": "J99999",
        "fec_ids": ["P99999"],
        "last_name": "Johnson",
        "nickname": "The Rock",
        "instagram_ids": ["1234567890"]
    }

Since we’ve been good database architects and we’ve specified that
``bioguide_id`` is a unique field, if we try to create a new record for
Mr. Rock, it’s going to fail because our first record already exists.

.. code:: ipython3

    Politician.objects.create(**new_record)


::


    ---------------------------------------------------------------------------

    UniqueViolation                           Traceback (most recent call last)

    ~/.local/lib/python3.7/site-packages/django/db/backends/utils.py in _execute(self, sql, params, *ignored_wrapper_args)
         83             else:
    ---> 84                 return self.cursor.execute(sql, params)
         85


    UniqueViolation: duplicate key value violates unique constraint "logos_politician_bioguide_id_317c4279_uniq"
    DETAIL:  Key (bioguide_id)=(J99999) already exists.



    The above exception was the direct cause of the following exception:


    IntegrityError                            Traceback (most recent call last)

    <ipython-input-22-4cfe6540bccd> in <module>
    ----> 1 Politician.objects.create(**new_record)


    ~/.local/lib/python3.7/site-packages/django/db/models/manager.py in manager_method(self, *args, **kwargs)
         83         def create_method(name, method):
         84             def manager_method(self, *args, **kwargs):
    ---> 85                 return getattr(self.get_queryset(), name)(*args, **kwargs)
         86             manager_method.__name__ = method.__name__
         87             manager_method.__doc__ = method.__doc__


    ~/.local/lib/python3.7/site-packages/django/db/models/query.py in create(self, **kwargs)
        445         obj = self.model(**kwargs)
        446         self._for_write = True
    --> 447         obj.save(force_insert=True, using=self.db)
        448         return obj
        449


    /apps/prod/logos/src/django_verifications/django_verifications/models.py in save(self, *args, **kwargs)
         90                         )
         91
    ---> 92         super(VerifiedModel, self).save(*args, **kwargs)
         93
         94     def get_verification_metadata(self):


    ~/.local/lib/python3.7/site-packages/django/db/models/base.py in save(self, force_insert, force_update, using, update_fields)
        752
        753         self.save_base(using=using, force_insert=force_insert,
    --> 754                        force_update=force_update, update_fields=update_fields)
        755     save.alters_data = True
        756


    ~/.local/lib/python3.7/site-packages/django/db/models/base.py in save_base(self, raw, force_insert, force_update, using, update_fields)
        790             updated = self._save_table(
        791                 raw, cls, force_insert or parent_inserted,
    --> 792                 force_update, using, update_fields,
        793             )
        794         # Store the database on which the object was saved


    ~/.local/lib/python3.7/site-packages/django/db/models/base.py in _save_table(self, raw, cls, force_insert, force_update, using, update_fields)
        893
        894             returning_fields = meta.db_returning_fields
    --> 895             results = self._do_insert(cls._base_manager, using, fields, returning_fields, raw)
        896             if results:
        897                 for value, field in zip(results[0], returning_fields):


    ~/.local/lib/python3.7/site-packages/django/db/models/base.py in _do_insert(self, manager, using, fields, returning_fields, raw)
        933         return manager._insert(
        934             [self], fields=fields, returning_fields=returning_fields,
    --> 935             using=using, raw=raw,
        936         )
        937


    ~/.local/lib/python3.7/site-packages/django/db/models/manager.py in manager_method(self, *args, **kwargs)
         83         def create_method(name, method):
         84             def manager_method(self, *args, **kwargs):
    ---> 85                 return getattr(self.get_queryset(), name)(*args, **kwargs)
         86             manager_method.__name__ = method.__name__
         87             manager_method.__doc__ = method.__doc__


    ~/.local/lib/python3.7/site-packages/django/db/models/query.py in _insert(self, objs, fields, returning_fields, raw, using, ignore_conflicts)
       1252         query = sql.InsertQuery(self.model, ignore_conflicts=ignore_conflicts)
       1253         query.insert_values(fields, objs, raw=raw)
    -> 1254         return query.get_compiler(using=using).execute_sql(returning_fields)
       1255     _insert.alters_data = True
       1256     _insert.queryset_only = False


    ~/.local/lib/python3.7/site-packages/django/db/models/sql/compiler.py in execute_sql(self, returning_fields)
       1395         with self.connection.cursor() as cursor:
       1396             for sql, params in self.as_sql():
    -> 1397                 cursor.execute(sql, params)
       1398             if not self.returning_fields:
       1399                 return []


    ~/.local/lib/python3.7/site-packages/django/db/backends/utils.py in execute(self, sql, params)
         96     def execute(self, sql, params=None):
         97         with self.debug_sql(sql, params, use_last_executed_query=True):
    ---> 98             return super().execute(sql, params)
         99
        100     def executemany(self, sql, param_list):


    ~/.local/lib/python3.7/site-packages/django/db/backends/utils.py in execute(self, sql, params)
         64
         65     def execute(self, sql, params=None):
    ---> 66         return self._execute_with_wrappers(sql, params, many=False, executor=self._execute)
         67
         68     def executemany(self, sql, param_list):


    ~/.local/lib/python3.7/site-packages/django/db/backends/utils.py in _execute_with_wrappers(self, sql, params, many, executor)
         73         for wrapper in reversed(self.db.execute_wrappers):
         74             executor = functools.partial(wrapper, executor)
    ---> 75         return executor(sql, params, many, context)
         76
         77     def _execute(self, sql, params, *ignored_wrapper_args):


    ~/.local/lib/python3.7/site-packages/django/db/backends/utils.py in _execute(self, sql, params, *ignored_wrapper_args)
         82                 return self.cursor.execute(sql)
         83             else:
    ---> 84                 return self.cursor.execute(sql, params)
         85
         86     def _executemany(self, sql, param_list, *ignored_wrapper_args):


    ~/.local/lib/python3.7/site-packages/django/db/utils.py in __exit__(self, exc_type, exc_value, traceback)
         88                 if dj_exc_type not in (DataError, IntegrityError):
         89                     self.wrapper.errors_occurred = True
    ---> 90                 raise dj_exc_value.with_traceback(traceback) from exc_value
         91
         92     def __call__(self, func):


    ~/.local/lib/python3.7/site-packages/django/db/backends/utils.py in _execute(self, sql, params, *ignored_wrapper_args)
         82                 return self.cursor.execute(sql)
         83             else:
    ---> 84                 return self.cursor.execute(sql, params)
         85
         86     def _executemany(self, sql, param_list, *ignored_wrapper_args):


    IntegrityError: duplicate key value violates unique constraint "logos_politician_bioguide_id_317c4279_uniq"
    DETAIL:  Key (bioguide_id)=(J99999) already exists.



So, traditionally, we’d write some code to catch the error, and if he
already exists, we update the existing record instead

.. code:: ipython3

    from django.db import IntegrityError

    try:
        Politician.objects.create(**new_record)
    except IntegrityError:
        pol = Politician.objects.get(bioguide_id=new_record['bioguide_id'])
        for fec_id in new_record["fec_ids"]:
            if fec_id not in pol.fec_ids:
                pol.fec_ids.append(fec_id)
        if not pol.last_name:
            pol.last_name = new_record['last_name']
        # ... and so on, and then we save the existing record:
        # pol.save()

We could even be fancier and skip that IntegrityError check

.. code:: ipython3

    pol, created = Politician.objects.get_or_create(bioguide_id=new_record['bioguide_id'])
    for fec_id in new_record["fec_ids"]:
        if fec_id not in pol.fec_ids:
            pol.fec_ids.append(fec_id)
    if not pol.last_name:
        pol.last_name = new_record['last_name']
    # ... and so on, and then we save the existing record:
    # pol.save()

But this is a royal pain. Often, when we’re trying to harmonize data
from multiple sources, we’re A) working with overlapping but incomplete
records and multiple potential IDs, and B) working with data that can be
easily represented as JSON/dictionary records. So wouldn’t it be nice if
we could just query Django directly with those records, and have it
search for existing records across multiple fields?

.. code:: ipython3

    new_record




.. parsed-literal::

    {'bioguide_id': 'J99999',
     'fec_ids': ['P99999'],
     'last_name': 'Johnson',
     'nickname': 'The Rock',
     'instagram_ids': ['1234567890']}



.. code:: ipython3

    pol = Politician.objects.get_if_exists(
        {"bioguide_id": new_record["bioguide_id"], "fec_ids": new_record['fec_ids']},
        match_any=True, search_nulls=False, empty_lists_are_null=True, allow_list_overlaps=False
    )

The ``BasicExtendedModel`` ``.json`` function can fetch a dictionary
representation of a particular record (the same way ``.values()`` does
for all of the objects in your query in vanilla Django).

.. code:: ipython3

    pol.json(exclude_nulls=True)




.. parsed-literal::

    {'id': 64716,
     'first_name': 'Dwayne',
     'last_name': 'Johnson',
     'has_press_release_scraper': False,
     'bioguide_id': 'J99999',
     'fec_ids': [],
     'facebook_ids': [],
     'old_facebook_ids': [],
     'twitter_ids': [],
     'old_twitter_ids': [],
     'instagram_ids': [],
     'old_instagram_ids': [],
     'capitol_words_speech_backfill': False}



Sweet, we found a match. Now, what if we could give Django some
guidelines, pass it our identifiers AND our new data, and have it
intelligently create or update records all at once?

.. code:: ipython3

    pol = Politician.objects.create_or_update(
        {"bioguide_id": new_record["bioguide_id"], "fec_ids": new_record["fec_ids"]},
        new_record,
        match_any=True, search_nulls=False, empty_lists_are_null=True, allow_list_overlaps=True,
        save_nulls=False, only_update_existing_nulls=False, return_object=True
    )

.. code:: ipython3

    pol.json(exclude_nulls=True)




.. parsed-literal::

    {'id': 64716,
     'first_name': 'Dwayne',
     'last_name': 'Johnson',
     'nickname': 'The Rock',
     'has_press_release_scraper': False,
     'bioguide_id': 'J99999',
     'fec_ids': ['P99999'],
     'facebook_ids': [],
     'old_facebook_ids': [],
     'twitter_ids': [],
     'old_twitter_ids': [],
     'instagram_ids': ['1234567890'],
     'old_instagram_ids': [],
     'capitol_words_speech_backfill': False}



Depending on the quality and completeness of our data source, we may
have a preference for preserving any existing data, or alternatively
overwriting it. We can control this behavior with some of those keyword
parameters - ``save_nulls`` (off by default) instructs django_pewtils to
preserve non-null values that are null in our new data;
``empty_lists_are_null`` (on by default) determines whether empty lists
should be treated like null values, and ``only_update_existing_nulls``
(off by default) is handy if you want to favor existing data and only
want to fill in what’s missing in any existing records.

Now let’s say we collect yet another new record. This time we don’t have
a Bioguide ID, but we do have FEC IDs - in fact, this new data source
has both Mr. Rock’s presidential FEC ID (which we know about) as well as
his Senate race FEC ID (which we don’t). Let’s pass all of the unique
identifiers we have and see what happens.

.. code:: ipython3

    new_record = {
        "icpsr_id": "12345",
        "fec_ids": ["S99999", "P99999"],
        "first_name": "Dwayne",
        "last_name": "Johnson",
        "nickname": None,
    }

.. code:: ipython3

    Politician.objects.get_if_exists(
        {"icpsr_id": new_record["icpsr_id"], "fec_ids": new_record["fec_ids"]},
        match_any=True, search_nulls=False, empty_lists_are_null=True, allow_list_overlaps=False
    )

Why didn’t we find anything? Because we were looking for an exact match
on the list of FEC IDs - by default, ``get_if_exists`` treats arrays
just like any other value. But if we pass ``allow_list_overlaps=True``,
we can tell django_pewtils to not only search for existing records that
overlap with our list, but also to update the existing record with the
*union* of the lists rather than overwrite what’s already there. (Note:
this only works with databases that support array fields, aka Postgres)

.. code:: ipython3

    Politician.objects.get_if_exists(
        {"icpsr_id": new_record["icpsr_id"], "fec_ids": new_record["fec_ids"]},
        match_any=True, search_nulls=False, empty_lists_are_null=True, allow_list_overlaps=True
    )




.. parsed-literal::

    <Politician: Dwayne 'The Rock' Johnson>



.. code:: ipython3

    mr_rock = Politician.objects.create_or_update(
        {"icpsr_id": new_record["icpsr_id"], "fec_ids": new_record["fec_ids"]},
        new_record,
        match_any=True, search_nulls=False, empty_lists_are_null=True, allow_list_overlaps=True,
        save_nulls=False, only_update_existing_nulls=False, return_object=True
    )

.. code:: ipython3

    mr_rock.json(exclude_nulls=True)




.. parsed-literal::

    {'id': 64716,
     'first_name': 'Dwayne',
     'last_name': 'Johnson',
     'nickname': 'The Rock',
     'has_press_release_scraper': False,
     'bioguide_id': 'J99999',
     'fec_ids': ['P99999', 'S99999'],
     'icpsr_id': '12345',
     'facebook_ids': [],
     'old_facebook_ids': [],
     'twitter_ids': [],
     'old_twitter_ids': [],
     'instagram_ids': ['1234567890'],
     'old_instagram_ids': [],
     'capitol_words_speech_backfill': False}



Boom - it found our existing record with an overlapping FEC ID, updated
it with the new ICPSR ID, update the FEC IDs to the union, and also
avoided overwriting the existing nickname.

Let’s try saving one more record, but this time we don’t have any unique
identifiers that overlap with our existing data. And there’s a typo in
the data. Great. This is going to cause some problems.

.. code:: ipython3

    new_record = {
        "opensecrets_id": "12345",
        "instagram_ids": ["0987654321"],
        "nickname": "Teh Rock",
        "last_name": "Johnson"
    }

.. code:: ipython3

    also_mr_rock = Politician.objects.create_or_update(
        {"opensecrets_id": new_record["opensecrets_id"]},
        new_record,
        match_any=True, search_nulls=False, empty_lists_are_null=True, allow_list_overlaps=True,
        save_nulls=False, only_update_existing_nulls=False, return_object=True
    )

Now we’ve unwittingly created two different records for Mr. Rock,
despite our best efforts to leverage all of the overlapping unique
identifiers from our various data sources.

.. code:: ipython3

    mr_rock.json(exclude_nulls=True)




.. parsed-literal::

    {'id': 64716,
     'first_name': 'Dwayne',
     'last_name': 'Johnson',
     'nickname': 'The Rock',
     'has_press_release_scraper': False,
     'bioguide_id': 'J99999',
     'fec_ids': ['P99999', 'S99999'],
     'icpsr_id': '12345',
     'facebook_ids': [],
     'old_facebook_ids': [],
     'twitter_ids': [],
     'old_twitter_ids': [],
     'instagram_ids': ['1234567890'],
     'old_instagram_ids': [],
     'capitol_words_speech_backfill': False}



.. code:: ipython3

    also_mr_rock.json(exclude_nulls=True)




.. parsed-literal::

    {'id': 64719,
     'last_name': 'Johnson',
     'nickname': 'Teh Rock',
     'has_press_release_scraper': False,
     'fec_ids': [],
     'opensecrets_id': '12345',
     'facebook_ids': [],
     'old_facebook_ids': [],
     'twitter_ids': [],
     'old_twitter_ids': [],
     'instagram_ids': ['0987654321'],
     'old_instagram_ids': [],
     'capitol_words_speech_backfill': False}



What can we do about this? We know about each copy right now - so in
this case, we could manually write some code to resolve the two records
and delete one of them - but in many cases, we aren’t even going to be
*aware* that a duplicate got created. So our first challenge is: how do
we check a massive database for possible duplicates, if we’ve already
checked all of the obvious unique indicators? And our second challenge
is: if we run into one of these duplicates, how do we resolve them
without having to do it manually every single time?

So let’s start with our original Mr. Rock, and see if we can find his
clone. In this case, the best shot we have at doing this is to look for
other Politician records with similar names. We have a few different
fields that might be useful - first name, last name, and nickname.
Fortunately, Django Pewtils’ ``BasicExtendedModel`` and
``BasicExtendedManager`` offer a variety of text similarity search
functions.

.. code:: ipython3

    mr_rock




.. parsed-literal::

    <Politician: Dwayne 'The Rock' Johnson>



.. code:: ipython3

    mr_rock.similar_by_fuzzy_ratios(['first_name', 'nickname', 'last_name'], min_ratio=.9)[:3]




.. parsed-literal::

    [{'pk': 64719,
      'first_name': '',
      'nickname': 'Teh Rock',
      'last_name': 'Johnson',
      'fuzzy_ratio': 80.0},
     {'pk': 55405,
      'first_name': 'Dan',
      'nickname': '',
      'last_name': 'Johnson',
      'fuzzy_ratio': 68.57142857142857},
     {'pk': 54070,
      'first_name': 'Daniel',
      'nickname': '',
      'last_name': 'Johnson',
      'fuzzy_ratio': 68.42105263157895}]



.. code:: ipython3

    mr_rock.similar_by_levenshtein_differences(['first_name', 'nickname', 'last_name'], max_difference=.5)[:3]




.. parsed-literal::

    <PoliticianManager [{'difference': 0.470588235294118, 'pk': 64719, 'first_name': '', 'nickname': 'Teh Rock', 'last_name': 'Johnson'}]>



.. code:: ipython3

    mr_rock.similar_by_tfidf_similarity(['first_name', 'nickname', 'last_name'], min_similarity=.5)[:3]




.. parsed-literal::

    [{'pk': 64719,
      'first_name': '',
      'nickname': 'Teh Rock',
      'last_name': 'Johnson',
      'similarity': 0.5351794382465026}]



.. code:: ipython3

    mr_rock.similar_by_trigram_similarity(['first_name', 'nickname', 'last_name'], min_similarity=.5)[:3]




.. parsed-literal::

    <PoliticianManager [{'similarity': 0.518519, 'pk': 64719, 'first_name': '', 'nickname': 'Teh Rock', 'last_name': 'Johnson'}]>



Okay, so now we’ve found our duplicate. Now what? Well, Django Pewtils’
``consolidate_objects`` function has the ability to collapse duplicate
records. Not only will it let us easily merge our records together the
way we’d like, it’ll also resolve database relations intelligently.
Values that are null in one record but filled in the other will be
filled in, many-to-many relationships and arrays will get merged into
their unions, and if our records have any unique one-to-one
relationships (e.g. each record has a unique “WikipediaPage” assigned to
it, and those are duplicates as well), we can instruct
``consolidate_objects`` to cascade to those records and consolidate them
as well. All we need to do is specify which record we want to keep: the
“source” is our duplicate, and we’ll merge it into the “target”, which
is the record that we’ll be keeping.

.. code:: ipython3

    from django_pewtils import consolidate_objects

    mr_rock = consolidate_objects(
        source=also_mr_rock,
        target=mr_rock,
        overwrite=False,  # False means that we'll prefer preserving the target's existing values if we encounter conflicts
        consolidate_related_uniques=False  # Unless we set this to True, the function will raise an error if there are conflicting relationships that can't be merged
    )

.. code:: ipython3

    mr_rock.json(exclude_nulls=True)




.. parsed-literal::

    {'id': 64716,
     'first_name': 'Dwayne',
     'last_name': 'Johnson',
     'nickname': 'The Rock',
     'has_press_release_scraper': False,
     'bioguide_id': 'J99999',
     'fec_ids': ['S99999', 'P99999'],
     'opensecrets_id': '12345',
     'icpsr_id': '12345',
     'facebook_ids': [],
     'old_facebook_ids': [],
     'twitter_ids': [],
     'old_twitter_ids': [],
     'instagram_ids': ['0987654321', '1234567890'],
     'old_instagram_ids': [],
     'capitol_words_speech_backfill': False}



You know, it would have been nice to avoid all of this in the first
place. What if we could have written some additional checks when we
first loaded in the duplicate Rock record, to search for existing
politicians with similar names? Our duplicate record had values for
``nickname`` and ``last_name``, so what if we had scanned the database
for matches using those?

.. code:: ipython3

    search_text = "Teh Rock Johnson"  # What we had in our duplicate record

.. code:: ipython3

    Politician.objects.fuzzy_ratios(['nickname', 'last_name'], search_text)[:3]




.. parsed-literal::

    [{'pk': 64716,
      'nickname': 'The Rock',
      'last_name': 'Johnson',
      'fuzzy_ratio': 93.75},
     {'pk': 55400,
      'nickname': '',
      'last_name': 'Johnson',
      'fuzzy_ratio': 66.66666666666666},
     {'pk': 52587,
      'nickname': '',
      'last_name': 'Johnson',
      'fuzzy_ratio': 66.66666666666666}]



.. code:: ipython3

    Politician.objects.fuzzy_ratio_best_match(['nickname', 'last_name'], search_text)




.. parsed-literal::

    (<Politician: Dwayne 'The Rock' Johnson>, 93.75)



.. code:: ipython3

    Politician.objects.levenshtein_differences(['nickname', 'last_name'], search_text)[:3]




.. parsed-literal::

    <PoliticianManager [{'difference': 0.125, 'pk': 64716, 'nickname': 'The Rock', 'last_name': 'Johnson'}, {'difference': 0.533333333333333, 'pk': 48661, 'nickname': '', 'last_name': 'Mcneal Johnson'}, {'difference': 0.533333333333333, 'pk': 59287, 'nickname': '', 'last_name': 'Roldan-Johnson'}]>



.. code:: ipython3

    Politician.objects.levenshtein_difference_best_match(['nickname', 'last_name'], search_text)




.. parsed-literal::

    (<Politician: Dwayne 'The Rock' Johnson>, 0.125)



.. code:: ipython3

    Politician.objects.tfidf_similarities(['nickname', 'last_name'], search_text)[:3]




.. parsed-literal::

    [{'pk': 64716,
      'nickname': 'The Rock',
      'last_name': 'Johnson',
      'similarity': 0.8116603660917949},
     {'pk': 55651,
      'nickname': '',
      'last_name': 'Johnson',
      'similarity': 0.5205634156460611},
     {'pk': 49912,
      'nickname': '',
      'last_name': 'Johnson',
      'similarity': 0.5205634156460611}]



.. code:: ipython3

    Politician.objects.tfidf_similarity_best_match(['nickname', 'last_name'], search_text)




.. parsed-literal::

    (<Politician: Dwayne 'The Rock' Johnson>, 0.8116603660917949)



.. code:: ipython3

    Politician.objects.trigram_similarities(['nickname', 'last_name'], search_text)[:3]




.. parsed-literal::

    <PoliticianManager [{'similarity': 0.7, 'pk': 64716, 'nickname': 'The Rock', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 55400, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 52587, 'nickname': '', 'last_name': 'Johnson'}]>



.. code:: ipython3

    Politician.objects.trigram_similarity_best_match(['nickname', 'last_name'], search_text)




.. parsed-literal::

    (<Politician: Dwayne 'The Rock' Johnson>, 0.7)



Some of these searches can take quite a while to run and/or will eat up
a lot of memory when you’ve got a large table. Postgres also has a
built-in search functionality that can more efficiently put the burden
on your database.

.. code:: ipython3

    Politician.objects.postgres_search(['nickname', 'last_name'], search_text)




.. parsed-literal::

    <PoliticianManager [<Politician: Dwayne 'The Rock' Johnson>, <Politician: William C Kortz II>, <Politician: Robert Michael Clark>, <Politician: Abel Maldonado>, <Politician: Doyel Shamley>, <Politician: Jamie Moore>, <Politician: James A Barnett>, <Politician: Thomas Catalano>, <Politician: Abel Gebre Laeke>, <Politician: Andrew Michael Decker>, <Politician: L. Mack Van Allen>, <Politician: Henry W Meers Jr>, <Politician: Darrel Ervin Miller>, <Politician: Robert W. Tucker>, <Politician: Oreta Tufaga-Mapu Crichton>, <Politician: Phat Nguyen>, <Politician: Justin Sung-Sup Kim>, <Politician: Lei Sharsh-Davis>, <Politician: Alan J.K. Yim>, <Politician: Shirlene D. (Shirl) Ostrov>, '...(remaining elements truncated)...']>



Equivalent functions also exist on ``BasicExtendedModel`` so you can
invoke them for specific records, too.

.. code:: ipython3

    mr_rock.trigram_similarity(['nickname', 'last_name'], search_text)




.. parsed-literal::

    0.7



.. code:: ipython3

    mr_rock.similar_by_trigram_similarity(['nickname', 'last_name'], min_similarity=.4)




.. parsed-literal::

    <PoliticianManager [{'similarity': 0.470588, 'pk': 52587, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 45952, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 46918, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 47003, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 48651, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 49075, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 63555, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 49386, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 49618, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 49836, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 49912, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 50417, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 53745, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 50703, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 53739, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 51020, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 51025, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 51223, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 51250, 'nickname': '', 'last_name': 'Johnson'}, {'similarity': 0.470588, 'pk': 51339, 'nickname': '', 'last_name': 'Johnson'}, '...(remaining elements truncated)...']>



Okay, goodbye Mr. Rock.

.. code:: ipython3

    mr_rock.delete()




.. parsed-literal::

    (1, {'logos.Politician': 1})



Django Pewtils also has a variety of functions for inspecting records in
your database. Let’s take a look at someone a bit more established than
Mr. Rock.

.. code:: ipython3

    bernie = Politician.objects.get(bioguide_id="S000033")

Let’s see what we’ve got on Bernie.

.. code:: ipython3

    bernie.related_objects()




.. parsed-literal::

    {'personal_metrics': <QueryModelManager [<PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2016, dw_nominate1: -0.526>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2015, comfortable_with_samesex_marriage: 2.0>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2015, privatize_social_security: -2.0>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2019, dw_nominate1: -0.526>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2019, dw_nominate2: -0.371>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2020, dw_nominate1: -0.526>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2020, dw_nominate2: -0.371>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2009, dw_nominate2: -0.296999990940094>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2010, dw_nominate1: -0.50900000333786>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2010, dw_nominate2: -0.296999990940094>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2011, dw_nominate2: -0.296999990940094>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2012, dw_nominate1: -0.50900000333786>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2012, dw_nominate2: -0.296999990940094>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2014, net_worth: 160000.0>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2014, assets: 190000.0>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2014, liabilities: 30000.0>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2015, dw_nominate1: -0.526>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2015, dw_nominate2: -0.371>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2016, dw_nominate2: -0.371>, <PoliticianPersonalMetric: Bernard 'Bernie' Sanders, 2017, dw_nominate1: -0.526>, '...(remaining elements truncated)...']>,
     'campaigns': <CampaignManager [<Campaign: Bernard 'Bernie' Sanders, campaign for 2020 race for President (winner None)>, <Campaign: Bernard 'Bernie' Sanders, campaign for 2018 race for Senator of Vermont, U.S. Senate (Class 1) (winner Bernard 'Bernie' Sanders)>, <Campaign: Bernard 'Bernie' Sanders, campaign for 2016 race for Senator of Vermont, U.S. Senate (Class 3) (winner Patrick Joseph Leahy)>, <Campaign: Bernard 'Bernie' Sanders, campaign for 2016 race for President (winner None)>, <Campaign: Bernard 'Bernie' Sanders, campaign for 2012 race for Senator of Vermont, U.S. Senate (Class 1) (winner Bernard 'Bernie' Sanders)>, <Campaign: Bernard 'Bernie' Sanders, campaign for 2006 race for Senator of Vermont, U.S. Senate (Class 1) (winner Bernard 'Bernie' Sanders)>, <Campaign: Bernard 'Bernie' Sanders, campaign for 2004 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>]>,
     'staffers': <QueryModelManager []>,
     'relevant_news_articles': <QueryModelManager [<NewsArticle: Gates of Vienna, 2015-05-21 00:00:00: Gates of Vienna News Feed 5/20/2015>, <NewsArticle: Gates of Vienna, 2015-05-02 00:00:00: Gates of Vienna News Feed 5/1/2015>, <NewsArticle: Gates of Vienna, 2015-05-22 00:00:00: Gates of Vienna News Feed 5/21/2015>, <NewsArticle: Gates of Vienna, 2015-05-04 00:00:00: Gates of Vienna News Feed 5/3/2015>, <NewsArticle: IHS Global Insight, 2015-05-21 00:00:00: Advocacy groups challenge patents for Gilead's HCV drug in Argentina, Brazil, China, Russia, and Ukraine>, <NewsArticle: Newstex Blogs
     SaintPetersBlog, 2015-05-27 00:00:00: Sunburn - The morning read of what's hot in Florida politics - May 27>, <NewsArticle: International Business Times News, 2015-05-19 00:00:00: Why Do Drugs Cost So Much?>, <NewsArticle: Betsy's Page, 2015-05-12 00:00:00: Cruising the Web>, <NewsArticle: DownWithTyranny, 2015-05-20 00:00:00: Democratic Congressional Candidate Jason Ritchie Makes The Case For Opposing TPP>, <NewsArticle: The Daily Dot, 2015-05-17 00:00:00: Du Vote, the tech that could make online voting safe>, <NewsArticle: Washington Post Blogs, 2015-05-19 00:00:00: Minorities and poor college students are shouldering the most student debt>, <NewsArticle: Atlantic Online, 2015-05-04 00:00:00: The Audacity of Ben Carson and Carly Fiorina>, <NewsArticle: Dissident Voice, 2015-05-13 00:00:00: Middle Class? What Middle Class?>, <NewsArticle: Washington Post Blogs, 2015-05-03 00:00:00: With little choice, O'Malley defends Baltimore tenure;  The former mayor plans to announce presidential campaign there despite critique of zero-tolerance policing.>, <NewsArticle: Washingtonpost.com, 2015-05-04 00:00:00: With little choice and under scrutiny, O'Malley embraces tenure as mayor>, <NewsArticle: Washington Post Blogs, 2015-05-11 00:00:00: Obama has harsh words for Warren on free trade>, <NewsArticle: Phil's Stock World, 2015-05-07 00:00:00: News You Can Use From Phil's Stock World>, <NewsArticle: Washington Post BlogsThe Plum Line, 2015-05-28 00:00:00: Morning Plum: Jeb Bush rips Republicans for 'bending with the wind' on immigration;  But Bush has not been as courageous on the issue as he suggests.>, <NewsArticle: ColoradoPols.com, 2015-05-05 00:00:00: Get More Smarter on Tuesday (May 5)>, <NewsArticle: AMERICAblog, 2015-05-18 00:00:00: The Blue Wall exists for a reason: The GOP built it>, '...(remaining elements truncated)...']>,
     'press_releases': <PressReleaseManager [<PressRelease: Bernard 'Bernie' Sanders, 2015-04-14 00:00:00: HHS to Probe Skyrocketing Generic Drug Prices>, <PressRelease: Bernard 'Bernie' Sanders, 2013-09-02 00:00:00: Vermont's 'age wave' brings jobs>, <PressRelease: Bernard 'Bernie' Sanders, 2013-07-26 00:00:00: Obama Said Not Ready to Decide on Fed Chief for Weeks>, <PressRelease: Bernard 'Bernie' Sanders, 2013-07-12 00:00:00: Vermont receives an additional $42M to help exchange>, <PressRelease: Bernard 'Bernie' Sanders, 2010-09-30 00:00:00: Release: Congress Steps Up to Protect Social Security>, <PressRelease: Bernard 'Bernie' Sanders, 2008-10-22 00:00:00: Rebuild America>, <PressRelease: Bernard 'Bernie' Sanders, 2015-03-17 00:00:00: Sanders: House Budget Plan is an Assault on the Middle Class and a Gift to Millionaires and Billionaires>, <PressRelease: Bernard 'Bernie' Sanders, 2013-07-23 00:00:00: Could job cuts hurt Vermont Yankee's case before PSB?>, <PressRelease: Bernard 'Bernie' Sanders, 2008-10-20 00:00:00: Rebuild America>, <PressRelease: Bernard 'Bernie' Sanders, 2009-01-11 00:00:00: Sanders: Why Not Fire Failed Tycoons?>, <PressRelease: Bernard 'Bernie' Sanders, 2013-11-21 00:00:00: SEN. SANDERS ISSUES STATEMENT ON MAJORITY RULE IN THE SENATE>, <PressRelease: Bernard 'Bernie' Sanders, 2008-05-27 00:00:00: Ike Was Right>, <PressRelease: Bernard 'Bernie' Sanders, 2015-08-26 00:00:00: Sanders Sends Letter to Postmaster General>, <PressRelease: Bernard 'Bernie' Sanders, 2009-08-20 00:00:00: Federal Grants for Vermont Communities to Counter Drug And Substance Abuse>, <PressRelease: Bernard 'Bernie' Sanders, 2014-04-22 00:00:00: Earth Day>, <PressRelease: Bernard 'Bernie' Sanders, 2007-11-14 00:00:00: A good, long look>, <PressRelease: Bernard 'Bernie' Sanders, 2008-01-15 00:00:00: Fire!>, <PressRelease: Bernard 'Bernie' Sanders, 2009-05-06 00:00:00: Encouraging Renewable Energy>, <PressRelease: Bernard 'Bernie' Sanders, 2010-01-08 00:00:00: Release: GE in Rutland Wins $12 Million Clean Energy Stimulus, Delegation Announces>, <PressRelease: Bernard 'Bernie' Sanders, 2013-08-27 00:00:00: Vermont Yankee Shutdown is 'Good News,' Sanders Says>, '...(remaining elements truncated)...']>,
     'ballotpedia_page': <QueryModelManager [<BallotpediaPage: BallotpediaPage object (599)>]>,
     'wikipedia_page': <QueryModelManager [<WikipediaPage: WikipediaPage object (1691)>]>,
     'speeches': <QueryModelManager [<Speech: Speech object (1255897)>, <Speech: Speech object (1255895)>, <Speech: Speech object (1255893)>, <Speech: Speech object (1255891)>, <Speech: Speech object (1255889)>, <Speech: Speech object (1255887)>, <Speech: Speech object (1255883)>, <Speech: Speech object (1255881)>, <Speech: Speech object (1248748)>, <Speech: Speech object (1248742)>, <Speech: Speech object (1248738)>, <Speech: Speech object (1248736)>, <Speech: Speech object (1241197)>, <Speech: Speech object (1238387)>, <Speech: Speech object (1238385)>, <Speech: Speech object (1238383)>, <Speech: Speech object (1238381)>, <Speech: Speech object (1235399)>, <Speech: Speech object (1235396)>, <Speech: Speech object (1235394)>, '...(remaining elements truncated)...']>,
     'twitter_profiles': <MergedTwitterProfileManager [<TwitterProfile: sensanders (Bernard 'Bernie' Sanders)>, <TwitterProfile: berniesanders (Bernard 'Bernie' Sanders)>, <TwitterProfile: senatorsanders (Bernard 'Bernie' Sanders)>]>,
     'incumbent_elections': <QueryModelManager [<Election: 2012 race for Senator of Vermont, U.S. Senate (Class 1) (winner Bernard 'Bernie' Sanders)>, <Election: 2004 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>]>,
     'elections_won': <QueryModelManager [<Election: 2018 race for Senator of Vermont, U.S. Senate (Class 1) (winner Bernard 'Bernie' Sanders)>, <Election: 2012 race for Senator of Vermont, U.S. Senate (Class 1) (winner Bernard 'Bernie' Sanders)>, <Election: 2006 race for Senator of Vermont, U.S. Senate (Class 1) (winner Bernard 'Bernie' Sanders)>, <Election: 2004 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>, <Election: 2002 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>, <Election: 2000 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>, <Election: 1998 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>, <Election: 1996 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>, <Election: 1994 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>, <Election: 1992 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>, <Election: 1990 race for Representative of Vermont, District At-Large (historical), U.S. House of Representatives (winner Bernard 'Bernie' Sanders)>]>,
     'contributions_donated': <QueryModelManager []>,
     'contributions_received': <QueryModelManager []>,
     'facebook_pages': <MergedFacebookPageManager [<FacebookPage: berniesanders (Bernard 'Bernie' Sanders)>, <FacebookPage: senatorsanders (Bernard 'Bernie' Sanders)>]>,
     'terms': <QueryModelManager [<Term: Bernard 'Bernie' Sanders term as Senator of Vermont, U.S. Senate (Class 1), 2019 - 2025>, <Term: Bernard 'Bernie' Sanders term as Senator of Vermont, U.S. Senate (Class 1), 2013 - 2019>, <Term: Bernard 'Bernie' Sanders term as Senator of Vermont, U.S. Senate (Class 1), 2007 - 2013>, <Term: Bernard 'Bernie' Sanders term as Representative of Vermont, District At-Large (historical), U.S. House of Representatives, 2005 - 2007>, <Term: Bernard 'Bernie' Sanders term as Representative of Vermont, District At-Large (historical), U.S. House of Representatives, 2003 - 2005>, <Term: Bernard 'Bernie' Sanders term as Representative of Vermont, District At-Large (historical), U.S. House of Representatives, 2001 - 2003>, <Term: Bernard 'Bernie' Sanders term as Representative of Vermont, District At-Large (historical), U.S. House of Representatives, 1999 - 2001>, <Term: Bernard 'Bernie' Sanders term as Representative of Vermont, District At-Large (historical), U.S. House of Representatives, 1997 - 1999>, <Term: Bernard 'Bernie' Sanders term as Representative of Vermont, District At-Large (historical), U.S. House of Representatives, 1995 - 1997>, <Term: Bernard 'Bernie' Sanders term as Representative of Vermont, District At-Large (historical), U.S. House of Representatives, 1993 - 1995>, <Term: Bernard 'Bernie' Sanders term as Representative of Vermont, District At-Large (historical), U.S. House of Representatives, 1991 - 1993>]>,
     'chaired_committees': <QueryModelManager []>,
     'ranking_member_committees': <QueryModelManager [<Committee: Senate Committee on Budget, <LegislatureManager [<Legislature: U.S. Senate>]>>, <Committee: Primary Health and Aging, <LegislatureManager [<Legislature: U.S. Senate>]>>]>,
     'committees': <QueryModelManager []>,
     'committee_memberships': <QueryModelManager [<CommitteeMembership: CommitteeMembership object (164934)>, <CommitteeMembership: CommitteeMembership object (150092)>, <CommitteeMembership: CommitteeMembership object (161558)>, <CommitteeMembership: CommitteeMembership object (165308)>, <CommitteeMembership: CommitteeMembership object (164893)>, <CommitteeMembership: CommitteeMembership object (161149)>, <CommitteeMembership: CommitteeMembership object (168701)>, <CommitteeMembership: CommitteeMembership object (165447)>, <CommitteeMembership: CommitteeMembership object (168757)>, <CommitteeMembership: CommitteeMembership object (168688)>, <CommitteeMembership: CommitteeMembership object (153618)>, <CommitteeMembership: CommitteeMembership object (164978)>, <CommitteeMembership: CommitteeMembership object (161133)>, <CommitteeMembership: CommitteeMembership object (149705)>, <CommitteeMembership: CommitteeMembership object (161709)>, <CommitteeMembership: CommitteeMembership object (168497)>, <CommitteeMembership: CommitteeMembership object (161526)>, <CommitteeMembership: CommitteeMembership object (161203)>, <CommitteeMembership: CommitteeMembership object (149883)>, <CommitteeMembership: CommitteeMembership object (164994)>, '...(remaining elements truncated)...']>,
     'caucuses': <QueryModelManager [<Caucus: Congressional Progressive Caucus>]>,
     'sponsored_bills': <QueryModelManager [<Bill: U.S. Senate s3044-114: Puerto Rico Humanitarian Relief and Reconstruction Act>, <Bill: U.S. Senate s2399-114: Climate Protection and Justice Act of 2015>, <Bill: U.S. Senate s2398-114: Clean Energy Worker Just Transition Act>, <Bill: U.S. Senate s2391-114: American Clean Energy Investment Act of 2015>, <Bill: U.S. Senate s2242-114: Save Oak Flat Act>, <Bill: U.S. Senate s2237-114: Ending Federal Marijuana Prohibition Act of 2015>, <Bill: U.S. Senate s2142-114: Workplace Democracy Act>, <Bill: U.S. Senate s2054-114: Justice is Not For Sale Act of 2015>, <Bill: U.S. Senate s2023-114: Prescription Drug Affordability Act of 2015>, <Bill: U.S. Senate s1970-114: Raising Enrollment with a Government Initiated System for Timely Electoral Registration (REGISTER) Act of 2015>, <Bill: U.S. Senate s1969-114: Democracy Day Act of 2015>, <Bill: U.S. Senate s1832-114: Pay Workers a Living Wage Act>, <Bill: U.S. Senate s1713-114: Low-Income Solar Act>, <Bill: U.S. Senate s1677-114: Responsible Estate Tax Act>, <Bill: U.S. Senate s1631-114: Keep Our Pension Promises Act>, <Bill: U.S. Senate s1564-114: Guaranteed Paid Vacation Act>, <Bill: U.S. Senate s1506-114: Employ Young Americans Now Act>, <Bill: U.S. Senate s1373-114: College for All Act>, <Bill: U.S. Senate s1371-114: Inclusive Prosperity Act of 2015>, <Bill: U.S. Senate s1366-114: None>, '...(remaining elements truncated)...']>,
     'cosponsored_bills': <QueryModelManager [<Bill: U.S. Senate sres640-114: None>, <Bill: U.S. Senate sres633-114: None>, <Bill: U.S. Senate sres632-114: None>, <Bill: U.S. Senate sres590-114: None>, <Bill: U.S. Senate sres581-114: No Vote No Recess Resolution>, <Bill: U.S. Senate sres561-114: None>, <Bill: U.S. Senate sres539-114: None>, <Bill: U.S. Senate sres530-114: None>, <Bill: U.S. Senate sres523-114: None>, <Bill: U.S. Senate sconres45-114: None>, <Bill: U.S. Senate s3491-114: Justice for Victims of Fraud Act of 2016>, <Bill: U.S. Senate s3476-114: National Guard Bonus Repayment and Financial Relief Act>, <Bill: U.S. Senate s3328-114: Department of Veterans Affairs Appeals Modernization Act of 2016>, <Bill: U.S. Senate s3321-114: Empowering States' Rights To Protect Consumers Act of 2016>, <Bill: U.S. Senate s3309-114: Voter Empowerment Act of 2015>, <Bill: U.S. Senate s3252-114: Automatic Voter Registration Act of 2016>, <Bill: U.S. Senate sres202-115: None>, <Bill: U.S. Senate sres201-115: None>, <Bill: U.S. Senate sres193-115: None>, <Bill: U.S. Senate sres184-115: None>, '...(remaining elements truncated)...']>,
     'votes_for': <QueryModelManager [<Vote: Vote On the Motion to Table H.R. 3326 on U.S. House of Representatives hr3326-111: Department of Defense Appropriations Act, 2010, 2009-12-19 00:00:00>, <Vote: Vote On the Motion (Motion To Concur In The House Amdt. To The Senate Amdt.) on U.S. House of Representatives hr3326-111: Department of Defense Appropriations Act, 2010, 2009-12-19 00:00:00>, <Vote: Vote On the Motion (Motion to Waive CBA and All Budget Resolutions Re: Motion to Concur in House Amdt. to H.R. 3326) on U.S. House of Representatives hr3326-111: Department of Defense Appropriations Act, 2010, 2009-12-19 00:00:00>, <Vote: Vote On the Cloture Motion on U.S. House of Representatives hr3590-111: Patient Protection and Affordable Care Act, 2009-12-21 00:00:00>, <Vote: Vote On the Motion to Table S.Amdt. 4309 to S.Con.Res. 70 (No short title on file) on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Cloture Motion on U.S. House of Representatives hr3326-111: Department of Defense Appropriations Act, 2010, 2009-12-18 00:00:00>, <Vote: Vote On the Motion (Motion to Waive Rule XXVIII Re: Conference Report to Accompany H.R. 3288) on U.S. House of Representatives hr3288-111: Consolidated Appropriations Act, 2010, 2009-12-11 00:00:00>, <Vote: Vote On the Motion to Proceed on U.S. House of Representatives hr3288-111: Consolidated Appropriations Act, 2010, 2009-12-10 00:00:00>, <Vote: Vote On the Motion to Table S.Amdt. 3278 to H.R. 3590 (Service Members Home Ownership Tax Act of 2009) on U.S. House of Representatives hr3590-111: Patient Protection and Affordable Care Act, 2009-12-22 00:00:00>, <Vote: Vote Call of the House by States on None, 2005-01-04 00:00:00>, <Vote: Vote On the Cloture Motion on None, 2014-07-15 00:00:00>, <Vote: Vote On the Nomination on None, 2014-07-09 00:00:00>, <Vote: Vote On the Nomination on None, 2014-06-26 00:00:00>, <Vote: Vote On the Nomination on None, 2014-06-24 00:00:00>, <Vote: Vote On the Cloture Motion on None, 2014-07-15 00:00:00>, <Vote: Vote On the Nomination on None, 2014-07-10 00:00:00>, <Vote: Vote On the Cloture Motion on None, 2014-06-23 00:00:00>, <Vote: Vote On the Nomination on None, 2014-07-07 00:00:00>, '...(remaining elements truncated)...']>,
     'votes_against': <QueryModelManager [<Vote: Vote On the Amendment on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Motion (Motion to Waive C.B.A. Cornyn Amdt. No. 4242) on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate sconres70-110: None, 2008-03-13 00:00:00>, <Vote: Vote On Consideration of the Resolution on U.S. House of Representatives hres5-109: None, 2005-01-04 00:00:00>, <Vote: Vote On the Amendment on U.S. House of Representatives hr2-114: Medicare Access and CHIP Reauthorization Act of 2015, 2015-04-14 00:00:00>, <Vote: Vote On the Amendment on U.S. House of Representatives hr2-114: Medicare Access and CHIP Reauthorization Act of 2015, 2015-04-14 00:00:00>, <Vote: Vote On Ordering the Previous Question on U.S. House of Representatives hres5-109: None, 2005-01-04 00:00:00>, <Vote: Vote On the Resolution on U.S. House of Representatives hres5-109: None, 2005-01-04 00:00:00>, <Vote: Vote On Agreeing to the Objection on None, 2005-01-06 00:00:00>, <Vote: Vote On the Amendment on U.S. House of Representatives hr2-114: Medicare Access and CHIP Reauthorization Act of 2015, 2015-04-14 00:00:00>, <Vote: Vote On the Cloture Motion on U.S. House of Representatives hr2029-114: Military Construction and Veterans Affairs and Related Agencies Appropriations Act, 2016, 2015-12-18 00:00:00>, <Vote: Vote On the Motion (Motion to Waive All Applicable Budgetary Discipline Re: Motion to Concur in the House Amendments to the Senate Amendment to H.R. 2029) on U.S. House of Representatives hr2029-114: Military Construction and Veterans Affairs and Related Agencies Appropriations Act, 2016, 2015-12-18 00:00:00>, <Vote: Vote On the Motion (Motion to Concur in the House Amendments to the Senate Amendment to H.R. 2029) on U.S. House of Representatives hr2029-114: Military Construction and Veterans Affairs and Related Agencies Appropriations Act, 2016, 2015-12-18 00:00:00>, <Vote: Vote On Passage of the Bill on U.S. House of Representatives hr54-109: Congressional Gold Medal Enhancement Act of 2005, 2005-01-26 00:00:00>, <Vote: Vote On the Resolution on U.S. House of Representatives hconres36-109: None, 2005-02-02 00:00:00>, '...(remaining elements truncated)...']>,
     'votes_abstained': <QueryModelManager [<Vote: Vote On the Nomination on None, 2016-01-11 00:00:00>, <Vote: Vote On the Nomination on None, 2016-01-19 00:00:00>, <Vote: Vote On the Cloture Motion on U.S. House of Representatives hr4038-114: American SAFE Act of 2015, 2016-01-20 00:00:00>, <Vote: Vote On the Cloture Motion on U.S. Senate sjres22-114: None, 2016-01-21 00:00:00>, <Vote: Vote On the Nomination on None, 2016-01-27 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-01-28 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-01-28 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-01-28 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-02-02 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-02-02 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-02-02 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-02-02 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-02-02 00:00:00>, <Vote: Vote On the Amendment on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-02-02 00:00:00>, <Vote: Vote On the Cloture Motion on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-02-04 00:00:00>, <Vote: Vote On the Cloture Motion on U.S. Senate s2012-114: Energy Policy Modernization Act of 2016, 2016-02-04 00:00:00>, <Vote: Vote On the Nomination on None, 2016-02-08 00:00:00>, <Vote: Vote On the Nomination on None, 2016-02-09 00:00:00>, <Vote: Vote On Passage of the Bill on U.S. House of Representatives hr757-114: North Korea Sanctions Enforcement Act of 2015, 2016-02-10 00:00:00>, <Vote: Vote On the Cloture Motion on U.S. House of Representatives hr644-114: Trade Facilitation and Trade Enforcement Act of 2015, 2016-02-11 00:00:00>, '...(remaining elements truncated)...']>,
     'hearings': <QueryModelManager [<LegislativeHearing: 72 CHRG-114shrg94051: [datetime.date(2015, 3, 19)]>, <LegislativeHearing: 14284 CHRG-110shrg36643: [datetime.date(2007, 4, 25)]>, <LegislativeHearing: 14291 CHRG-110shrg34335: [datetime.date(2007, 3, 14)]>, <LegislativeHearing: 14292 CHRG-110shrg40573: [datetime.date(2007, 9, 27)]>, <LegislativeHearing: 9563 CHRG-109hhrg29458: [datetime.date(2005, 6, 23)]>, <LegislativeHearing: 8663 CHRG-108hhrg94689: [datetime.date(2004, 3, 30)]>, <LegislativeHearing: 8665 CHRG-108hhrg95012: [datetime.date(2004, 5, 18)]>, <LegislativeHearing: 345 CHRG-114shrg96272: [datetime.date(2015, 8, 17)]>, <LegislativeHearing: 8677 CHRG-108hhrg96529: [datetime.date(2004, 7, 15)]>, <LegislativeHearing: 4084 CHRG-112shrg94198: [datetime.date(2012, 11, 15)]>, <LegislativeHearing: 7770 CHRG-108hhrg89409: [datetime.date(2003, 4, 10)]>, <LegislativeHearing: 8694 CHRG-108hhrg96545: [datetime.date(2004, 4, 28)]>, <LegislativeHearing: 8698 CHRG-108hhrg94688: [datetime.date(2004, 3, 25)]>, <LegislativeHearing: 7777 CHRG-108hhrg89633: [datetime.date(2003, 5, 22)]>, <LegislativeHearing: 8718 CHRG-108hhrg96546: [datetime.date(2004, 5, 3)]>, <LegislativeHearing: 9721 CHRG-109hhrg28102: [datetime.date(2005, 7, 19)]>, <LegislativeHearing: 7780 CHRG-108hhrg91543: [datetime.date(2003, 6, 17)]>, <LegislativeHearing: 8724 CHRG-108hhrg93841: [datetime.date(2004, 3, 18)]>, <LegislativeHearing: 2851 CHRG-113shrg94431: [datetime.date(2013, 3, 14)]>, <LegislativeHearing: 7797 CHRG-108hhrg91303: [datetime.date(2003, 10, 8)]>, '...(remaining elements truncated)...']>,
     'scrape_logs': <ScrapeLogManager [<ScrapeLog: ScrapeLog object (1083)>, <ScrapeLog: ScrapeLog object (1082)>, <ScrapeLog: ScrapeLog object (1081)>]>,
     'webpages': <WebpageManager [<Webpage: 232e6cb76ab068afb772f670b2e9a913>, <Webpage: 2ca773ae3bdd0c424b3672b5b9194208>, <Webpage: c1ac6146dfe6520a029c6cf0812561ad>, <Webpage: eec968dae00e21cd710860082c2bd82d>, <Webpage: 9018d1511cf46681a964719a346a654d>, <Webpage: edd9cdde8b570ebbbfbc70d0eec10c55>, <Webpage: 21d73276ff8ef92a17fe3d906376cd2e>, <Webpage: ad6ad2636640bd50f8317bc67c633116>, <Webpage: 25f0981e0ac67bda6ad06b55206af734>, <Webpage: 147f948c5defe278dc5d014205b379b1>, <Webpage: 7a416fda677ae1e7c4a4e284b6c54f86>, <Webpage: d2e5d410055e75dc072067d5aac18e57>, <Webpage: f10191506e6097a96886b32e7dbaa7c6>, <Webpage: 362cd980f72a5c9c02891bda27dfdad7>, <Webpage: 1485789318324a08f944b4e95c1db0db>, <Webpage: b8bc12cca78d8efdb8465cbef3006ea8>, <Webpage: c6a245a7bd66e04dc1f59cb6afca91d1>, <Webpage: 1cc70e7fbb725e103b45155c744b28af>, <Webpage: 7a980b3dbcf1aa618f2a1fb4ee28fd59>, <Webpage: 64d37b16892d4e32a9011b57114d2b73>, '...(remaining elements truncated)...']>,
     'current_term': <QueryModelManager [<Term: Bernard 'Bernie' Sanders term as Senator of Vermont, U.S. Senate (Class 1), 2019 - 2025>]>,
     'latest_term': <QueryModelManager [<Term: Bernard 'Bernie' Sanders term as Senator of Vermont, U.S. Senate (Class 1), 2019 - 2025>]>,
     'party': <PartyManager [<Party: Democratic Party>]>,
     'commands': <BasicExtendedManager [<Command: load_pew_data_labs_politician_social_media_accounts {}>, <Command: load_pew_data_labs_scraper_press_releases {'mode': 'reparse_existing'}>, <Command: load_united_states_github_congress_members {}>, <Command: load_united_states_github_congress_member_social_media {}>, <Command: load_pew_data_labs_mturk_politician_social_media_accounts {}>, <Command: load_sunlight_current_congress_members {}>, <Command: load_facebook_politician_pages {}>, <Command: load_twitter_politician_profiles {}>, <Command: load_pew_data_labs_scraper_press_releases {'mode': 'new'}>, <Command: load_wikipedia_politician_pages {}>, <Command: clean_remove_duplicate_politician_press_releases {}>, <Command: logos_load_facebook_politician_pages {}>, <Command: commands_load_twitter_politician_profiles {}>, <Command: commands_load_facebook_politician_pages {}>, <Command: commands_load_united_states_github_congress_members {}>, <Command: commands_load_united_states_github_congress_member_social_media {}>, <Command: load_bioguide_politician_bios {}>, <Command: politician_profiles {}>, <Command: data_labs_politician_social_media_accounts {}>, <Command: states_github_congress_members {}>, '...(remaining elements truncated)...']>,
     'command_logs': <BasicExtendedManager [<CommandLog: load_pew_data_labs_politician_social_media_accounts {} (pk=27787): COMPLETED>, <CommandLog: load_pew_data_labs_politician_social_media_accounts {} (pk=27790): COMPLETED>, <CommandLog: load_pew_data_labs_politician_social_media_accounts {} (pk=27792): COMPLETED>, <CommandLog: load_pew_data_labs_scraper_press_releases {'mode': 'reparse_existing'} (pk=28027): RUNNING>, <CommandLog: load_united_states_github_congress_members {} (pk=28113): COMPLETED>, <CommandLog: load_united_states_github_congress_members {} (pk=28115): COMPLETED>, <CommandLog: load_united_states_github_congress_members {} (pk=28116): COMPLETED>, <CommandLog: load_united_states_github_congress_members {} (pk=28117): FAILED>, <CommandLog: load_united_states_github_congress_members {} (pk=28118): RUNNING>, <CommandLog: load_united_states_github_congress_members {} (pk=28119): RUNNING>, <CommandLog: load_united_states_github_congress_members {} (pk=28120): RUNNING>, <CommandLog: load_united_states_github_congress_members {} (pk=28121): COMPLETED>, <CommandLog: load_united_states_github_congress_members {} (pk=28122): RUNNING>, <CommandLog: load_united_states_github_congress_members {} (pk=28123): RUNNING>, <CommandLog: load_united_states_github_congress_members {} (pk=28124): COMPLETED>, <CommandLog: load_united_states_github_congress_members {} (pk=28126): FAILED>, <CommandLog: load_united_states_github_congress_members {} (pk=28128): FAILED>, <CommandLog: load_united_states_github_congress_members {} (pk=28130): FAILED>, <CommandLog: load_united_states_github_congress_members {} (pk=28131): FAILED>, <CommandLog: load_united_states_github_congress_members {} (pk=28132): COMPLETED>, '...(remaining elements truncated)...']>,
     'verifications': <VerificationManager []>}



.. code:: ipython3

    bernie.related_objects(counts=True)




.. parsed-literal::

    {'personal_metrics': 47,
     'campaigns': 7,
     'staffers': 0,
     'relevant_news_articles': 96109,
     'press_releases': 3326,
     'ballotpedia_page': 1,
     'wikipedia_page': 1,
     'speeches': 2890,
     'twitter_profiles': 3,
     'incumbent_elections': 2,
     'elections_won': 11,
     'contributions_donated': 0,
     'contributions_received': 0,
     'facebook_pages': 2,
     'terms': 11,
     'chaired_committees': 0,
     'ranking_member_committees': 2,
     'committees': 0,
     'committee_memberships': 63,
     'caucuses': 1,
     'sponsored_bills': 235,
     'cosponsored_bills': 2638,
     'votes_for': 3320,
     'votes_against': 1918,
     'votes_abstained': 343,
     'hearings': 1059,
     'scrape_logs': 3,
     'webpages': 2193,
     'current_term': 1,
     'latest_term': 1,
     'party': 1,
     'commands': 21,
     'command_logs': 1108,
     'verifications': 0}



Looks like we’ve got a lot of data on Bernie. What would happen if we
deleted him? Deleting a record in a database can cause a lot of
unexpected cascade behavior if you aren’t careful! The
``inspect_delete`` function in Django Pewtils’ ``BasicExtendedModel``
can help you make sure you’re not going to do something you’ll regret.
(You can also run this on queries too.)

.. code:: ipython3

    bernie.inspect_delete(counts=True)




.. parsed-literal::

    defaultdict(list,
                {logos.models.agents.Politician: 1,
                 logos.models.agents.Politician_commands: 21,
                 logos.models.agents.Politician_command_logs: 1108,
                 logos.models.agents.PoliticianPersonalMetric: 47,
                 logos.models.agents.PoliticianPersonalMetric_commands: 27,
                 logos.models.agents.PoliticianPersonalMetric_command_logs: 167,
                 logos.models.media.NewsArticle_relevant_politicians: 96109,
                 logos.models.media.BallotpediaPage: 1,
                 logos.models.media.WikipediaPage: 1,
                 logos.models.media.WikipediaPage_commands: 1,
                 logos.models.media.WikipediaPage_command_logs: 1,
                 logos.models.government.CommitteeMembership: 63,
                 logos.models.government.CommitteeMembership_commands: 63,
                 logos.models.government.CommitteeMembership_command_logs: 63,
                 logos.models.government.Caucus_members: 1,
                 logos.models.government.Bill_cosponsors: 2638,
                 logos.models.government.Vote_votes_for: 3320,
                 logos.models.government.Vote_votes_against: 1918,
                 logos.models.government.Vote_votes_abstained: 343,
                 logos.models.government.LegislativeHearing_attendees: 1059})



So, let’s maybe *not* do that.

Anyway, that’s some of the handy stuff in Django Pewtils!

Let’s make sure we deleted all of our Rocks, just in case:

.. code:: ipython3

    for field, unique_id in [
        ("fec_ids", ["S99999", "P99999"]),
        ("fec_ids", ['P99999', 'H99999']),
        ("bioguide_id", "J99999"),
        ("icpsr_id", "12345"),
        ("opensecrets_id", "12345")
    ]:
        try: Politician.objects.get(**{field: unique_id}).delete()
        except Politician.DoesNotExist: pass
