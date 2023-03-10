from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

import os
from . import config

settings = config.Settings()
astra_db_keyspace = settings.db_keyspace

# List view -> Detail view
class Product(Model):
    __keyspace__ = astra_db_keyspace
    asin = columns.Text(primary_key=True, required=True)
    title = columns.Text()
    price_str = columns.Text(default="-100")

# Detail View for main
class ProductScrapeEvent(Model):
    __keyspace__ = astra_db_keyspace
    uuid = columns.UUID(primary_key=True)
    asin = columns.Text(index=True)
    title = columns.Text()
    price_str = columns.Text(default="-100")
