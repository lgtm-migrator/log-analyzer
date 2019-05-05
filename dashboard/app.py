# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from components import summary, navbar, create_figure
from components import graphic, interval_component, TIME_WINDOWS
import sources

external_stylesheets = [
    dbc.themes.SLATE,
    {
        'href':
        'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
        'rel':
        'stylesheet',
        'integrity':
        'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
        'crossorigin':
        'anonymous'
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Apache Dashboard'

PLOT_CONFIG = [{
    'title': 'HTTP Response codes',
    'label': 'Response code',
    'kind':  'bar',
    'source': sources.http_response_codes
}, {
    'title': 'Requested URLs',
    'label': 'URL',
    'kind':  'bar',
    'source': sources.requested_urls
}, {
    'title': 'Visitors',
    'label': 'Visitors count',
    'kind':  'line',
    'source': sources.visitors
}, {
    'title': 'Visitor country',
    'label': 'Visitor country',
    'kind':  'geo',
    'source': sources.visitor_countries
}]


def create_figure_from_config(config, time_window):
    x, y = config['source'](time_window)
    fig = create_figure(config['kind'], x, y, config['label'], config['title'])
    return fig


def create_graphics():
    time_window = TIME_WINDOWS[0]
    graphics = [
        graphic('g' + str(i), create_figure_from_config(config, time_window))
        for i, config in enumerate(PLOT_CONFIG)
    ]
    return graphics


def create_summary_layout():
    labels, values = sources.get_summary()
    return [
        dbc.Row([dbc.Col(summary(labels, values))],
                style={'margin-top': '40px'})
    ]


def create_graphics_layout(graphics):
    return [
        dbc.Row([dbc.Col(g1, md=6), dbc.Col(g2, md=6)],
                style={'margin-top': '40px'})
        for g1, g2 in zip(graphics[0::2], graphics[1::2])
    ]


def create_interval_components(num):
    return [interval_component(i, 60) for i in range(num)]


def serve_layout():
    body_header = create_summary_layout()
    graphics = create_graphics()
    body_main = create_graphics_layout(graphics)
    int_components = create_interval_components(len(graphics))
    body = dbc.Container(body_header + body_main + int_components)
    return html.Div([navbar('Dashboard'), body])


def create_updating_function(config):
    def update(_, time_window):
        return create_figure_from_config(config, time_window)
    return update


def update_interval_component(time_window):
    return 5 * 1000 if time_window == 'Realtime' else 60 * 1000


app.layout = serve_layout

for i, conf in enumerate(PLOT_CONFIG):
    graph_output = Output('g' + str(i), 'figure')
    interval_output = Output('interval_component-' + str(i), 'interval')
    timer = Input('interval-component' + str(i), 'n_intervals')
    dropdown = Input('g' + str(i) + '-dropdown', 'value')
    app.callback(graph_output, [timer, dropdown])(create_updating_function(conf))
    app.callback(interval_output, [dropdown])(create_updating_function(conf))

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
