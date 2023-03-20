Django Pewtils
===================================================================

`django_pewtils` is a Python package that provides general-purpose Django-related tools that make it easier to
interact with data stored in databases using the Django ORM. If you’re using Django to manage a database, Django
Pewtils can help you do things that Django can’t do out-of-the-box, like: consolidate duplicate database records with
complicated relations that need to be resolved; view all of the relations an object has in the database; inspect all
of the objects that will be deleted BEFORE you run a delete query (useful for avoiding unexpected cascades);
efficiently loop over extremely large tables; run complex text searches and compute text similarities using efficient
built-in database functions.

.. toctree::
   :maxdepth: 1
   :caption: Table of Contents:

   Installation <installation>
   Basic functions <base>
   Abstract models <abstract_models>
   Managers <managers>
   Examples <examples>
