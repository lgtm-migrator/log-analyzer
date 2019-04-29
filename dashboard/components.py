from copy import deepcopy
from itertools import cycle

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

DEFAULT_FIGURE_LAYOUT = {
    'title': {
        'font': {
            'size': 24
        }
    },
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'font': {
        'color': '#ffffff'
    },
    'xaxis': {
        'gridcolor': '#5b5b5b',
        'showgrid': True,
        'tickcolor': 'rgb(127,127,127)',
        'tickfont': {
            'size': 10
        }
    },
    'yaxis': {
        'gridcolor': '#5b5b5b',
        'showgrid': True,
        'tickcolor': 'rgb(127,127,127)'
    },
    'showlegend': True,
    'margin': go.layout.Margin(l=40, r=0, t=50, b=35)
}

LINE_PLOT = {
    'type': 'scatter',
    'mode': 'lines+markers',
    'fill': 'tozeroy',
    'fillcolor': 'rgba(30, 105, 255, 0.3)',
    'marker': {
        'opacity': 1,
        'size': 7,
        'color': 'rgb(35, 185, 255)'
    },
    'line': {
        'color': 'rgb(30, 105, 255)'
    },
    'hoverlabel': {
        'bgcolor': 'rgba(200, 15, 15, 0.7)'
    }
}

BAR_PLOT = {
    'type': 'bar',
    'color': 'rgb(30, 105, 255)',
    'marker': {
        'color': 'rgb(30, 105, 255)',
        'line': {
            'color': 'rgb(35, 185, 255)',
            'width': 1.5
        }
    }
}

TRACES = {'bar': BAR_PLOT, 'line': LINE_PLOT}

CARD_STYLE = {'font-size': 28}

COLOR_PALETTE = [
    "#9b59b6",
    "#3498db",
    "#e74c3c",
    "#2ecc71"
]

def create_figure_layout(title):
    layout = deepcopy(DEFAULT_FIGURE_LAYOUT)
    layout['title']['text'] = title
    return layout


def create_figure(kind, x, y, label, title):
    trace = deepcopy(TRACES[kind])
    trace['x'] = x
    trace['y'] = y
    #trace['text'] = x
    trace['name'] = label
    layout = create_figure_layout(title)
    figure = {'data': [trace], 'layout': layout}
    return figure


def summary_card(title, value, border_color):
    style = {'border-top': '4px solid ' + border_color}
    header = dbc.CardHeader([
        html.I(className='fas fa-chart-bar icon-2x'),
        " " + title
    ], style=style)
    body = dbc.CardBody(
        [dbc.CardTitle(str(value), className='text-center', style=CARD_STYLE)])
    return dbc.Card([header, body], color='secondary', inverse=True)


def summary(labels, values):
    cards = map(summary_card, labels, values, cycle(COLOR_PALETTE))
    cards = list(cards)
    return dbc.CardDeck(cards)


def navbar(title):
    navbrand = dbc.NavbarBrand([
        dbc.Row([
            dbc.Col(html.Div(title)),
            dbc.Col(html.I(className='fas fa-tachometer-alt'))
        ])
    ])
    return dbc.Navbar([html.A(navbrand, href='#')],
                      sticky='top',
                      color="primary",
                      dark=True)


def dropdown(id, labels, values=None, default_idx=0):
    if not values:
        values = labels
    options = [{'label': l, 'value': v} for l, v in zip(labels, values)]
    return dcc.Dropdown(
        id=id,
        options=options,
        value=values[default_idx],
        clearable=False,
        style={'background-color': '#ffffff'})


def graphic(id, figure):
    options = dropdown(id + '-dropdown', ['Hourly', 'Daily', 'Monthly'])
    options = html.Div([dbc.Row(dbc.Col(options, width=3), justify='end')])
    graph = dcc.Graph(
        id=id,
        figure=figure,
        config={'displayModeBar': False},
        style={'height': 300})
    return dbc.Card([dbc.CardHeader(options), dbc.CardBody([graph])])


def interval_component(interval_in_secs):
    return dcc.Interval(
        id='interval-component',
        interval=interval_in_secs * 1000,
        n_intervals=0)
