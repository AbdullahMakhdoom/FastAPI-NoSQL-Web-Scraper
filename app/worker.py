from celery import Celery
from celery.schedules import crontab
from celery.signals import beat_init, worker_process_init


from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table

from . import config, crud, db, models, scraper, schema

settings = config.get_settings()
REDIS_URL = settings.redis_url

celery_app = Celery(__name__)
celery_app.conf.broker_url = REDIS_URL
celery_app.conf.result_backend = REDIS_URL

def celery_on_startup(*args, **kwargs):
    if connection.cluster is not None:
        connection.cluster.shutdown()
    if connection.session is not None:
        connection.session.shutdown()
    cluster = db.get_cluster()
    session = cluster.connect()
    connection.register_connection(str(session), session=session)
    connection.set_default_connection(str(session))
    sync_table(Products)
    sync_table(ProductScrapeEvent)

Products = models.Product
ProductScrapeEvent = models.ProductScrapeEvent

beat_init.connect()
worker_process_init.connect(celery_on_startup)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, *args, **kwargs):
    sender.add_periodic_taks(
        crontab(minute="*/5"),
        scrape_products.s()
    )

@celery_app.task
def list_products():
    q = Products.objects().all().values_list("asin", flat=True)
    print(list(q))


@celery_app.task
def scrape_asin(asin):
    s = scraper.Scraper(asin=asin, endless_scroll=True)
    dataset = s.scrape()
    try:
        validated_data = schema.ProductListSchema(**dataset)
    except:
        valdiated_data = None
    if validated_data is not None:
        product, _ = crud.add_scrape_event(validated_data.dict())
        return asin, True
    return asin, False



@celery_app.task
def scrape_products():
    print("To do scraping")
    q = Products.object().all().value_list("asin", flat=True)
    for asin in q:
        scrape_asin.delay(asin)


