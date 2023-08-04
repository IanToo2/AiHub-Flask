import psycopg2
import json

def get_database_connection():
    with open('config.json') as f:
        config = json.load(f)

    return psycopg2.connect(
        database=config["database"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"],
    )