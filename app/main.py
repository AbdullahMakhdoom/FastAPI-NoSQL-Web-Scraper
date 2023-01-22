from typing import List
from fastapi import FastAPI

from cassandra.cqlengine.management import sync_table
from . import db, models, schema, config, crud

settings = config.get_settings()
Product = models.Product
ProductScrapeEvent = models.ProductScrapeEvent


app = FastAPI()

@app.get("/")
def read_index():
    return {"hello": "world", "name": settings.name}

@app.get("/products", response_model=List[schema.ProductListSchema])
def products_list_view():
    return list(Product.objects().all())

@app.get("/products/{asin}")
def products_detail_view(asin):
    data = dict(Product.objects().get(asin=asin))
    events =  list(ProductScrapeEvent.objects().filter(asin=asin).limit(5))
    data['event'] = [schema.ProductScrapeEventDetailSchema(**x) for x in events]
    data['event_url'] = f"/products/{asin}/events" 
    return data

@app.get("/products/{asin}/events" , response_model=List[schema.ProductScrapeEventDetailSchema])
def products_scrapes_list_view(asin):
    return list(ProductScrapeEvent.objects().filter(asin=asin))

@app.post("/events/scrape")
def events_scrape_create_view(data: schema.ProductListSchema):
    product, _ = crud.add_scrape_event(data.dict())
    return product
    
session = None
@app.on_event("startup")
def on_startup():
    global session
    session = db.get_session()
    sync_table(models.Product)
    sync_table(models.ProductScrapeEvent)


