import pandas as pd
import numpy as np


"""
Mock data generators
"""

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
