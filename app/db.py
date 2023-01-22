import os
import json

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine.connection import register_connection, set_default_connection

from . import config

settings = config.get_settings()

def get_cluster():
    cloud_config = {
        'secure_connect_bundle': settings.connect_bundle_path
    }

    auth_provider = PlainTextAuthProvider(settings.db_client_id, settings.db_client_secret)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)

    return cluster

def get_session():
    cluster = get_cluster()
    session = cluster.connect()
    register_connection(str(session), session=session)
    set_default_connection(str(session))
    return session


if __name__ == "__main__":
    session = get_session()
    row = session.execute("select release_version from system.local").one()
    if row:
        print(row[0])
    else:
        print("An error occurred.")