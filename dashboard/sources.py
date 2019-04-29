import pickle
import pandas as pd
import numpy as np
from cassandra.cluster import Cluster
from kafka import KafkaConsumer


cluster = None
session = None


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def connect_to_cassandra(cluster_ips, port):
    global cluster, session
    cluster = Cluster(cluster_ips, port)
    session = cluster.connect()
    session.row_factory = pandas_factory
    session.default_fetch_size = None


def value_deserializer(v):
    return pickle.loads(v.decode('ascii'))


def create_kafka_consumer(cluster_ips):
    consumer = KafkaConsumer(
        'rltest',
        value_deserializer=value_deserializer,
        bootstrap_servers=cluster_ips)


def visitors(time_window):
    index = pd.date_range(start='1/1/2019', end='30/1/2019')
    values = np.random.random_integers(4000, 10000, len(index))
    return index, values


def http_status_codes(time_window):
    index = [200, 300, 400, 500]
    values = np.random.random_integers(1, 1000, 4)
    return index, values


def requested_urls(time_window):
    index = [
        '/gatitos.gif', '/index.html', '/mancala/league.html',
        '/flask-tutorial.pdf', '/pandoc.html', '/webmailest.html',
        '/flask-tutorial2.pdf', '/pandoc2.html', '/webmailest2.html',
        '/flask-tutorial3.pdf', '/pandoc3.html', '/webmailest3.html'
        '/flask-tutorial4.pdf', '/pandoc4.html', '/webmailest5.html',
        '/flask-tutorial5.pdf', '/pandoc5.html', '/webmailest5.html'
        '/flask-tutorial6.pdf', '/pandoc6.html', '/webmailest6.html',
        '/flask-tutorial7.pdf', '/pandoc7.html', '/webmailest7.html'
    ]
    values = np.random.random_integers(1, 1000, len(index))
    return index, values


def requested_files(time_window):
    pass


def get_summary():
    index = ['Total Requests', 'Log Size', 'Requested Files', 'Not Found']
    values = np.random.random_integers(10, 10000, len(index))
    values = values.astype(np.object)
    values[1] = str(values[1]) + ' MiB'
    return index, values
