import os
import json

from dotenv import load_dotenv

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


load_dotenv()

ASTRA_DB_SECRETS_JSON = os.environ.get("ASTRA_DB_SECRETS_PATH")
json_file = open(ASTRA_DB_SECRETS_JSON)
astra_db_credentials = json.load(json_file)


CLUSTER_BUNDLE = os.environ.get("ASTRA_DB_CONNECT_PATH")

def get_cluster():
    cloud_config = {
        'secure_connect_bundle': CLUSTER_BUNDLE
    }

    auth_provider = PlainTextAuthProvider(astra_db_credentials["clientId"], astra_db_credentials["secret"])
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)

    return cluster

def get_session():
    cluster = get_cluster()
    session = cluster.connect()
    return session


if __name__ == "__main__":
    session = get_session()
    row = session.execute("select release_version from system.local").one()
    if row:
        print(row[0])
    else:
        print("An error occurred.")