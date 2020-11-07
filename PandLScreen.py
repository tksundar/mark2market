"""
Created by Sundar on 19-10-2020.email tksrajan@gmail.com
"""
from functools import partial

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ListProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import *
from kivymd.uix.datatables import MDDataTable, CellRow
from nsetools.nse import Nse

import tryout

sort_param = ''


def get_sort_key(obj):
    if sort_param == 'symbol':
        return obj.symbol
    if sort_param == 'name':
        return obj.name
    if sort_param == 'quantity':
        return obj.quantity
    if sort_param == 'price':
        return obj.price
    if sort_param == 'nav':
        return obj.nav


def sort(param, pf_data):
    global sort_param
    sort_param = param
    pf_data.sort(key=get_sort_key, reverse=True if param == 'quantity' or param == 'price' or param == 'nav' else False)


class PnLScreen(Screen):
    data = ListProperty(defaultvalue=[])
    processing = BooleanProperty(defaultvalue=False)
    updated = False

    def __init__(self, screen_manager, **kwargs):
        self.updated = False
        if 'updated' in kwargs:
            self.updated = kwargs.pop('updated')
        super().__init__(**kwargs)
        self.screen_manager: ScreenManager = screen_manager
        self.name = kwargs['name']
        Window.bind(on_keyboard=self.events)
        self.add_widgets()

    def get_table(self, data):
        row_data = []
        for item in data:
            if item.nav == 0:
                continue
            row = [item.symbol, item.quantity, item.price, item.nav]
            row_data.append(row)
        if len(row_data) == 1:
            row_data.append(['', '', '', ''])  # hack. MDDatatable breaks if there just one row

        table = MDDataTable(
            size_hint=(1, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            use_pagination=True,
            pagination_menu_pos='center',
            rows_num=7,
            check=False,
            column_data=[
                ("Symbol", dp(15)),
                ("Quantity", dp(15)),
                ("Price", dp(15)),
                ("NAV", dp(15)),
            ],
            row_data=row_data,

        )
        table.bind(on_row_press=tryout.on_row_press)
        return table

    # def on_row_press(self, instance_table, instance_row: CellRow):
    #     """Called when a table row is clicked."""
    #
    #     print(instance_row.text)
    #     text: str = instance_row.text
    #     Clock.schedule_once(partial(tryout.get_stock_data, text), 0.5)

    # def get_nse_data(self, symbol, dt):
    #     nse = Nse()
    #     q = nse.get_quote(symbol)
    #     name = q['companyName']
    #     ltp = q['lastPrice']
    #     low = q['dayLow']
    #     high = q['dayHigh']
    #     high52 = q['high52']
    #     low52 = q['low52']
    #     c1 = Label(text='Symbol')
    #     c2 = Label(text=symbol)
    #     c3 = Label(text='Name')
    #     c4 = Label(text=name)
    #     c5 = Label(text='Last Traded Price')
    #     c6 = Label(text=str(ltp))
    #     c7 = Label(text='Day Low')
    #     c8 = Label(text=str(low))
    #     c9 = Label(text='Day High')
    #     c10 = Label(text=str(high))
    #     c11 = Label(text='52 week Low')
    #     c12 = Label(text=str(low52))
    #     c13 = Label(text='52 week High')
    #     c14 = Label(text=str(high52))
    #
    #     gridlayout = GridLayout(cols=2)
    #     gridlayout.add_widget(c1)
    #     gridlayout.add_widget(c2)
    #     gridlayout.add_widget(c3)
    #     gridlayout.add_widget(c4)
    #     gridlayout.add_widget(c5)
    #     gridlayout.add_widget(c6)
    #     gridlayout.add_widget(c7)
    #     gridlayout.add_widget(c8)
    #     gridlayout.add_widget(c9)
    #     gridlayout.add_widget(c10)
    #     gridlayout.add_widget(c11)
    #     gridlayout.add_widget(c12)
    #     gridlayout.add_widget(c13)
    #     gridlayout.add_widget(c14)
    #     popup = Popup()
    #     popup.content = gridlayout
    #     popup.title = 'Live data for ' + symbol + '. ( delayed by a minute)'
    #     popup.size_hint = (.8, .6)
    #     popup.pos_hint = {'center_x': .5, 'center_y': .5}
    #     popup.open()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""
        if keyboard in (1001, 27):
            self.screen_manager.current = 'Main'
        return True

    def go_home(self, instance):
        self.screen_manager.current = "Main"

    def add_widgets(self):
        tryout.init(updated=self.updated)
        self.pf_data = list(tryout.product_dict.values())
        pf_nav = 0
        for pi in self.pf_data:
            pf_nav += pi.nav
        self.pf_nav = round(pf_nav, 2)
        floatLayout = FloatLayout()
        button: Button = MDRaisedButton(text="Portfolio NAV is " + str(self.pf_nav),
                                        pos_hint=({'center_x': .5, 'center_y': .95}),
                                        size_hint=(1, .09), )
        button.background_color = (0.2, .6, 1, 1)
        button.bind(on_press=self.go_home)
        floatLayout.add_widget(button)
        table = self.get_table(self.pf_data)
        floatLayout.add_widget(table)
        home_btn = MDIconButton(icon='home',
                                pos_hint={'center_x': 0.5, 'center_y': 0.05})
        home_btn.md_bg_color = (1, 1, 1, 1)
        home_btn.bind(on_press=self.go_home)
        floatLayout.add_widget(home_btn)
        self.add_widget(floatLayout)
