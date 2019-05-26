import pickle
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime
from cassandra.cluster import Cluster
from kafka import KafkaConsumer
import geoip2.database

cluster = None
session = None
num_requests = 0

TIMEDELTAS = {
    'Realtime': relativedelta(seconds=10),
    'Hour': relativedelta(hours=1),
    'Day': relativedelta(days=1),
    'Month': relativedelta(months=1)
}

FRECUENCIES = {
    'Realtime': 'S',
    'Hour': '1Min',
    'Day': '1H',
    'Month': 'D'
} 

GEOIP_DATABASE = geoip2.database.Reader('./dashboard/data/cities.mmdb')


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def connect_to_cassandra():
    global cluster, session
    cluster = Cluster()
    session = cluster.connect('logs_keyspace')
    session.row_factory = pandas_factory
    session.default_fetch_size = None


def time_window_to_dates(time_window):
    end = datetime.now()
    start = end - TIMEDELTAS[time_window]
    return start.isoformat(timespec='seconds'), end.isoformat(timespec='seconds')


def build_cassandra_query(time_window, select_clause, where_clause=None):
    start, end = time_window_to_dates(time_window)
    where_clause = (where_clause + ' and') if where_clause else ''
    query = """SELECT %s FROM logs WHERE user_id = '-' and  %s date_time > '%s' and
            date_time < '%s';""" % (select_clause, where_clause, start, end)
    return query


def get_data(time_window, select, where=None):
    if not session:
        connect_to_cassandra()
    query = build_cassandra_query(time_window, select, where)
    result = session.execute(query)
    result = result._current_rows
    if 'date_time' in result.columns:
        result['date_time'] = pd.to_datetime(result['date_time'])
        result.set_index('date_time', inplace=True)
    return result


def visitors(time_window):
    df = get_data(time_window, 'date_time, endpoint')
    freq = FRECUENCIES[time_window]
    result = df.resample(freq).count()
    return result.index, result.iloc[:, 0].values


def http_response_codes(time_window):
    df = get_data(time_window, 'response_code')
    result = df['response_code'].value_counts()
    return result.index, result.values


def requested_urls(time_window):
    df = get_data(time_window, 'endpoint')
    result = df['endpoint'].value_counts()
    return result.index, result.values


def get_country(ip):
    try:
        result = GEOIP_DATABASE.city(ip).country.name
    except:
        result = None
    finally:
        return result


def visitor_countries(time_window):
    df = get_data(time_window, 'ip_address')
    result = df['ip_address'].apply(get_country).value_counts()
    return result.index, result.values


def get_summary():
    index = ['Total Requests', 'Visitors']
    df = get_data(time_window, 'date_time, endpoint')
    freq = FRECUENCIES[time_window]
    result = df.resample(freq).count()
    return result.index, result.iloc[:, 0].values


def http_response_codes(time_window):
    df = get_data(time_window, 'response_code')
    result = df['response_code'].value_counts()
    return result.index, result.values


def requested_urls(time_window):
    df = get_data(time_window, 'endpoint')
    result = df['endpoint'].value_counts()
    return result.index, result.values


def get_country(ip):
    try:
        result = GEOIP_DATABASE.city(ip).country.name
    except:
        result = None
    finally:
        return result


def visitor_countries(time_window):
    df = get_data(time_window, 'ip_address')
    result = df['ip_address'].apply(get_country).value_counts()
    return result.index, result.values


def get_summary():
    df = get_data('Realtime', 'ip_address')
    requests = len(df)
    visitors = len(df['ip_address'].unique())
    index = ['Requests (Realtime)', 'Visitors (Realtime)']
    values = [requests, visitors]
    return index, values
