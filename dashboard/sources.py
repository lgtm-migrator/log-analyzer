import json
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime
from cassandra.cluster import Cluster
from kafka import KafkaConsumer


cluster = None
session = None


TIMEDELTAS = {
    'Hour': relativedelta(minutes=1),
    'Day': relativedelta(days=1),
    'Month': relativedelta(months=1)
}


GROUP_RULES = {
    'Hour': '1Min',
    'Day': '1Day',
    'Month': '1Mon'
}


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def connect_to_cassandra():
    global cluster, session
    cluster = Cluster()
    session = cluster.connect('logs_keyspace')
    session.row_factory = pandas_factory
    session.default_fetch_size = None


def value_deserializer(v):
    return json.dumps(v).encode('utf-8')


def create_kafka_consumer(cluster_ips):
    consumer = KafkaConsumer(
        value_deserializer=value_deserializer, bootstrap_servers=cluster_ips)
    consumer.subscribe(['dashboard'])


def time_window_to_dates(time_window):
    end = datetime.now()
    start = end - TIMEDELTAS[time_window]
    return start.isoformat(timespec='seconds'), end.isoformat(timespec='seconds')


def group(time_window):
    pass


def cassandra_query(time_window, select):
    start, end = time_window_to_dates(time_window)
    query = """SELECT %s FROM logs
            WHERE date_time > '%s'
            and date_time < '%s' ALLOW FILTERING;""" % (select, start, end)
    if not session:
        connect_to_cassandra()
    result = session.execute(query)
    return result._current_rows


def visitors(time_window):
    df = cassandra_query(time_window, 'date_time')
    print(df)
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
