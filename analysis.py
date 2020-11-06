"""
Created by Sundar on 30-10-2020.email tksrajan@gmail.com
"""
import os

import matplotlib.pyplot as plt
import pandas as pd
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager, ScreenManagerException
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton, MDTextButton

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
    fig.set_size_inches(12, 12)
    ax.pie(data, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, explode=ex)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('NAV Chart')
    plt.savefig(name, edgecolor="#04253a")


def get_nav_data():
    symbols = []
    labels = []
    navs = []
    pf_data = list(tryout.product_dict.values())
    tryout.sort('nav', pf_data)
    for index, pf in enumerate(pf_data):
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
    plt.figure(figsize=(12, 12))
    plt.bar(ticks, gains, color=colors)
    plt.title('Gain Loss Chart(in millions)')
    plt.xlabel("Stock Holdings (NAV ordered")
    plt.ylabel("Gain(Loss) millions")
    plt.grid(True, which='minor')
    for index, value in enumerate(gains):
        plt.text(index, value, names[index])
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
    fig.set_size_inches(12, 12)
    ax.pie(sector_data, labels=sector_labels, autopct='%1.1f%%', shadow=True, startangle=90, explode=explode)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Sectoral Exposure')
    plt.savefig(name, edgecolor="#04253a")


def make_day_gain_loss(name):
    global close
    import numpy as np
    date, prev_date = tryout.get_date_string()
    df = pd.read_csv('nse.csv', usecols=['SYMBOL', ' PREV_CLOSE', ' CLOSE_PRICE'])
    _, _, symbols = get_nav_data()
    up_down = {}

    sym_trend = {}
    for index, row in df.iterrows():
        symbol = row['SYMBOL']
        prev = float(row[' PREV_CLOSE'])
        last = row[' CLOSE_PRICE']
        try:
            close = float(last)
        except ValueError:
            print('bad price %s for symbol %s ' % (last, symbol))

        up_down_percent = ((close - prev) / prev) * 100
        print('%s, %f, %f %f' % (symbol, close, prev,up_down_percent))
        sym_trend.update({
            symbol: up_down_percent
        })
    filename = date + '_bse.csv'
    if not os.path.exists(filename):
        filename = prev_date + '_bse.csv'

    df = pd.read_csv(filename, usecols=['ISIN_CODE', 'PREVCLOSE', 'CLOSE'])
    for index, row in df.iterrows():
        isin = row['ISIN_CODE']
        symbol = tryout.bse_isin_to_symbol_map.get(isin)
        prev = float(row['PREVCLOSE'])
        close = float(row['CLOSE'])
        up_down_percent = 0
        if prev > 0:
            up_down_percent = ((close - prev) / prev) * 100
        if not (symbol in sym_trend):
            sym_trend.update({
                symbol: up_down_percent
            })
    for symbol in symbols:
        up_down.update({symbol: sym_trend[symbol]})

    labels = list(up_down.keys())
    data = list(up_down.values())
    colors = []
    for val in data:
        if val < 0:
            colors.append('red')
        else:
            colors.append('green')
    plt.clf()
    ticks = np.arange(0, len(labels))
    plt.figure(figsize=(12, 12))
    plt.bar(ticks, data, color=colors)
    plt.title('Stock Movement for the last trading session')
    plt.xlabel("Stock Holdings (NAV ordered)")
    plt.ylabel("Prev Day's Gain(Loss) in %")
    plt.grid(True, which='minor')
    for index, value in enumerate(data):
        if value < 0:
            value -= 0.1
        else:
            value += 0.1
        plt.text(index, value, labels[index])
    plt.savefig(name)


def add_home_btn(widget):
    home_btn = MDIconButton(icon='home', pos_hint={'center_x': 0.5, 'center_y': 0.05})
    home_btn.md_bg_color = (1, 1, 1, 1)
    home_btn.bind(on_press=widget.go_home)
    widget.add_widget(home_btn)


class NavScreen(Screen):

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager

    def add_widgets(self):
        make_nav_plot('nav.png')
        img = Image(source='nav.png')
        self.add_widget(img)
        add_home_btn(self)

    def go_home(self, instance):
        self.screen_manager.current = 'Charts'


class GLScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager

    def add_widgets(self):
        make_gains_plot('gains.png')
        img = Image(source='gains.png')
        self.add_widget(img)
        add_home_btn(self)

    def go_home(self, instance):
        self.screen_manager.current = 'Charts'


class SectorScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager

    def add_widgets(self):
        make_sectoral_plot('sectors.png')
        img = Image(source='sectors.png')
        self.add_widget(img)
        add_home_btn(self)

    def go_home(self, instance):
        self.screen_manager.current = 'Charts'


class TrendScreen(Screen):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager

    def add_widgets(self):
        make_day_gain_loss('day_gain_loss.png')
        img = Image(source='day_gain_loss.png')
        self.add_widget(img)
        add_home_btn(self)

    def go_home(self, instance):
        self.screen_manager.current = 'Charts'


def disable_spinner():
    MDApp.get_running_app().analytics = True


def enable_spinner(delegate):
    MDApp.get_running_app().analytics = False
    Clock.schedule_once(delegate, 1)


class Analysis(Screen):

    def __init__(self, screen_manager, **kwargs):
        self.updated = False
        if 'updated' in kwargs:
            self.updated = kwargs.pop('updated')
        super().__init__(**kwargs)
        self.screen_manager: ScreenManager = screen_manager
        Window.bind(on_keyboard=self.events)
        self.add_widgets()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""
        if keyboard in (1001, 27):
            self.screen_manager.current = 'Main'
        return True

    def add_widgets(self):
        tryout.init(updated=self.updated)
        floatLayout = FloatLayout(size_hint=(.9, .9))
        nav_btn = MDTextButton(text='NAV Plot', pos_hint={'center_x': 0.55, 'center_y': 0.7})
        nav_btn.bind(on_press=self.go_nav_plot)
        floatLayout.add_widget(nav_btn)

        gl_btn = MDTextButton(text='Gain Loss Plot', pos_hint={'center_x': 0.55, 'center_y': 0.6})
        gl_btn.bind(on_press=self.go_gl_plot)
        floatLayout.add_widget(gl_btn)

        sec_btn = MDTextButton(text='Sectoral Exposure Plot', pos_hint={'center_x': 0.55, 'center_y': 0.5})
        sec_btn.bind(on_press=self.go_sec_plot)
        floatLayout.add_widget(sec_btn)

        trend_btn = MDTextButton(text='Stock Movement plot', pos_hint={'center_x': 0.55, 'center_y': 0.4})
        trend_btn.bind(on_press=self.go_trend_plot)
        floatLayout.add_widget(trend_btn)
        self.add_widget(floatLayout)
        add_home_btn(self)

    def go_nav_plot(self, instance):
        enable_spinner(self.nav_plot_delegate)

    def nav_plot_delegate(self, dt):
        if len(tryout.product_dict) > 0:
            try:
                self.screen_manager.get_screen('NAV_PLOT')
            except ScreenManagerException:
                nav_plot = NavScreen(self.screen_manager, name='NAV_PLOT')
                nav_plot.add_widgets()
                self.screen_manager.add_widget(nav_plot)
        self.screen_manager.current = 'NAV_PLOT'
        disable_spinner()

    def go_gl_plot(self, instance):
        enable_spinner(self.gl_plot_delegate)

    def gl_plot_delegate(self, dt):
        try:
            self.screen_manager.get_screen('GL_PLOT')
        except ScreenManagerException:
            gl_plot = GLScreen(self.screen_manager, name='GL_PLOT')
            gl_plot.add_widgets()
            self.screen_manager.add_widget(gl_plot)
        self.screen_manager.current = 'GL_PLOT'
        disable_spinner()

    def go_sec_plot(self, instance):
        enable_spinner(self.sec_plot_delegate)

    def sec_plot_delegate(self, dt):
        try:
            self.screen_manager.get_screen('SEC_PLOT')
        except ScreenManagerException:
            sec_plot = SectorScreen(self.screen_manager, name='SEC_PLOT')
            sec_plot.add_widgets()
            self.screen_manager.add_widget(sec_plot)
        self.screen_manager.current = 'SEC_PLOT'
        disable_spinner()

    def go_trend_plot(self, instance):
        enable_spinner(self.trend_plot_delegate)

    def trend_plot_delegate(self, dt):
        try:
            self.screen_manager.get_screen('TREND_PLOT')
        except ScreenManagerException:
            trend_plot = TrendScreen(self.screen_manager, name='TREND_PLOT')
            trend_plot.add_widgets()
            self.screen_manager.add_widget(trend_plot)
        self.screen_manager.current = 'TREND_PLOT'
        disable_spinner()

    def go_home(self, instance):
        self.screen_manager.current = 'Main'


if __name__ == '__main__':
    Analysis(ScreenManager())
