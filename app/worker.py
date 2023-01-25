from celery import Celery
from celery.signals import beat_init, worker_process_init
from . import config, db, models
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table

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
def random_task(name):
    print(f"Who throws shows {name}")


@celery_app.task
def list_products():
    q = Products.objects().all().values_list("asin", flat=True)
    print(list(q))


@celery_app.task
def scrape_asin(asin):
    print(asin)

@celery_app.task
def scrape_product():
    print("To do scraping")
    q = Products.object().all().value_list("asin", flat=True)
    for asin in q:
        scrape_asin.delay(asin)
