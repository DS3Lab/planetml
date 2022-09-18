import os
import typesense

client = None

def get_typesense_client():
    global client
    if client is None:
        MYSQL_PASS = os.getenv("TOMA_TYPESENSE_TOKEN", default="mysql")
        client = typesense.Client({
            'nodes': [{
                'host': '35.88.240.80',
                'port': '8108',
                'protocol': 'http'
            }],
            'api_key': MYSQL_PASS,
            'connection_timeout_seconds': 2
        })
    return client