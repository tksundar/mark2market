"""
Created by Sundar on 30-10-2020.email tksrajan@gmail.com
"""
import os

import matplotlib.pyplot as plt
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDTextButton, MDIconButton
import pandas as pd

import tryout


def make_nav_plot(name):
    labels, data, symbols = get_nav_data()
    ex = []

    for index, item in enumerate(labels):
        if index == 0:
            ex.append(0.1)
        else:
            ex.append(0)

    plt.clf()
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, explode=ex)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('NAV Chart')
    plt.savefig(name, edgecolor="#04253a")


def get_nav_data():
    symbols = []
    labels = []
    navs = []
    for index, pf in enumerate(list(tryout.product_dict.values())):
        symbols.append(pf.symbol)
        labels.append(pf.symbol + '(' + str(index + 1) + ')')
        navs.append(pf.nav)
    return labels, navs, symbols


def get_gains_data():
    names = []
    gains = []

    for pf in list(tryout.product_dict.values()):
        names.append(pf.symbol)
        gains.append(round(pf.gain, 2))

    return names, gains


def make_gains_plot(name):
    names, gains = get_gains_data()
    ticks = []
    colors = []
    for i, n in enumerate(gains):
        ticks.append(i + 1)
        if n < 0:
            colors.append('red')
        else:
            colors.append('green')
    plt.clf()
    fig, axes = plt.subplots()
    axes.bar(ticks, gains, color=colors)
    axes.xaxis.grid(True, which='minor')
    plt.title('Gain Loss Chart(in millions)')
    plt.savefig(name)


def make_sectoral_plot(name):
    df = pd.read_excel('csv/sector.xlsx', usecols=['Symbol', 'Sector'])
    sec_map = {}
    for index, row in df.iterrows():
        symbol = row['Symbol'].upper()
        sec_map[symbol] = row['Sector']
    sectors = {'CDSL': 'Business Services', 'BAJAJCON': 'Consumer Non-Durables', 'SPAL': 'Textiles',
               'EQUITAS': 'Banking', 'EXPLEOSOL': 'Computers', 'GRAUWEIL': 'Chemicals', 'SPECIALITY': 'Hotels',
               'KDDL': 'Misc'}

    label, nav, symbols = get_nav_data()

    for symbol in symbols:
        if not (symbol in sectors):
            sectors.update({symbol: sec_map.get(symbol)})
    from collections import defaultdict
    grouped = defaultdict(list)

    for symbol, sector in sorted(sectors.items()):
        grouped[sector].append(symbol)

    sector_labels = []
    sector_data = []
    for key in grouped.keys():
        stocks = grouped.get(key)
        total = 0
        for stock in stocks:
            pi = tryout.symbol_product_dict.get(stock)
            if not (pi is None):
                total += pi.nav
        sector_labels.append(key)
        sector_data.append(total)

    index = sector_data.index(max(sector_data))
    explode = []
    for i, val in enumerate(sector_data):
        if i == index:
            explode.append(.1)
        else:
            explode.append(0)

    plt.clf()
    fig, ax = plt.subplots()
    ax.pie(sector_data, labels=sector_labels, autopct='%1.1f%%', shadow=True, startangle=90, explode=explode)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Sectoral Exposure')
    plt.savefig(name, edgecolor="#04253a")


def make_day_gain_loss(name):
    import numpy as np
    df = pd.read_csv('nse.csv', usecols=['SYMBOL', ' PREV_CLOSE', ' CLOSE_PRICE'])
    _, _, symbols = get_nav_data()
    up_down = {}

    for index, row in df.iterrows():
        symbol = row['SYMBOL']
        if symbol in symbols:
            prev = float(row[' PREV_CLOSE'])
            close = float(row[' CLOSE_PRICE'])
            up_down.update({symbol: close - prev})

    df = pd.read_csv('bse.csv', usecols=['ISIN_CODE', 'PREVCLOSE', 'CLOSE'])
    for index, row in df.iterrows():
        isin = row['ISIN_CODE']
        symbol = tryout.bse_isin_to_symbol_map.get(isin)
        if symbol in symbols:
            prev = float(row['PREVCLOSE'])
            close = float(row['CLOSE'])
            up_down.update({symbol: close - prev})

    labels = list(up_down.keys())
    data = list(up_down.values())
    colors = []
    for val in data:
        if val < 0:
            colors.append('red')
        else:
            colors.append('green')
    plt.clf()
    fig, axes = plt.subplots()
    ticks = np.arange(0, len(labels))
    axes.bar(ticks, data, color=colors)
    axes.xaxis.grid(True, which='minor')
    plt.title('Stock Movement for the last trading session')
    plt.savefig(name)


class Analysis(Screen):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        make_nav_plot('nav.png')
        make_gains_plot('gains.png')
        make_sectoral_plot('sectors.png')
        make_day_gain_loss('day_gain_loss.png')

        layout = GridLayout(cols=2, size_hint=(.9, .8), pos_hint={'center_x': .5, 'center_y': 0.5})


        img = Image(source='nav.png')
        layout.add_widget(img)  # 1

        img = Image(source='gains.png')
        layout.add_widget(img)  # 2

        img = Image(source='sectors.png')
        layout.add_widget(img)  # 3

        img = Image(source='day_gain_loss.png')
        layout.add_widget(img)

        self.add_widget(layout)

        home_btn = MDIconButton(icon='home', pos_hint={'center_x': 0.5, 'center_y': 0.02})
        home_btn.md_bg_color = (1, 1, 1, 1)
        home_btn.bind(on_press=self.go_home)
        self.add_widget(home_btn)

    def go_home(self, instance):
        self.screen_manager.current = 'Main'


if __name__ == '__main__':
    Analysis(ScreenManager())
