import copy
from.db import get_session
from .models import Product, ProductScrapeEvent
import uuid



def create_entry(data: dict):
    return Product.create(**data)

def create_scrape_entry(data: dict):
    data['uuid'] = uuid.uuid1() # includes a timestamp
    return ProductScrapeEvent.create(**data)

def add_scrape_event(data: dict, fresh=False):
    if fresh:
        data = copy.deepcopy(data)
    product = create_entry(data)
    scrape_obj = create_scrape_entry(data)
    return product, scrape_obj
