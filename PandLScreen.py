"""
Created by Sundar on 19-10-2020.email tksrajan@gmail.com
"""

from kivy.metrics import dp
from kivy.properties import ListProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import *
from kivymd.uix.datatables import MDDataTable

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
    for pf in pf_data:
        print(pf)


def get_table(data):
    row_data = []
    for item in data:
        if item.nav == 0:
            continue
        row = [item.name[:40], item.quantity, item.price, item.nav]
        row_data.append(row)

    table = MDDataTable(
        size_hint=(0.6, 0.8),
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
        #use_pagination=True,
        rows_num=50,
        check=False,
        column_data=[
            ("Name", dp(20)),
            ("Quantity", dp(20)),
            ("Price", dp(20)),
            ("NAV", dp(20)),
        ],
        row_data=row_data,
    )

    return table


class PnLScreen(Screen):
    data = ListProperty(defaultvalue=[])
    processing = BooleanProperty(defaultvalue=False)

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager: ScreenManager = screen_manager
        self.pf_data = list(tryout.product_dict.values())
        self.name = kwargs['name']
        app = MDApp.get_running_app().name
        if app == 'UPDATE':
            tryout.get_nse_prices()
            tryout.get_bse_prices()
            tryout.get_isin_to_symbol_map()
            tryout.make_product_dict_from_csv(csv_file='csv/pandb.csv')
            self.pf_data = list(tryout.product_dict.values())

        pf_nav = 0
        for pi in self.pf_data:
            pf_nav += pi.nav
        self.pf_nav = round(pf_nav, 2)
        sort("nav", self.pf_data)

        print("Running app is " + MDApp.get_running_app().name)
        self.add_widgets()

    def go_home(self, instance):
        self.screen_manager.current = "Main"

    def gain_loss(self, instance):
        print("gain loss")
        self.screen_manager.current = "GainLoss"

    def analysis(self, instance):
        print("analysis")

    def add_widgets(self):
        self.processing = True
        floatLayout = FloatLayout()
        button: Button = Button(text="Portfolio NAV is " + str(self.pf_nav),
                                pos_hint=({'center_x': .5, 'center_y': .95}),
                                size_hint=(1, .08), )
        button.background_color = (.2, .2, .2, 1)
        button.bind(on_press=self.go_home)
        floatLayout.add_widget(button)
        table = get_table(self.pf_data)
        floatLayout.add_widget(table)
        input_btn = MDRaisedButton(text="Add/Delete", size_hint=(None, None), size=(100, 50),
                                   pos_hint={'center_x': 0.4, 'center_y': 0.05}, elevation=10)
        input_btn.md_bg_color = (.2, .2, .2, 1)
        input_btn.bind(on_press=self.go_home)
        floatLayout.add_widget(input_btn)
        gain_btn = MDRaisedButton(text="Performance", size_hint=(None, None), size=(100, 50),
                                  pos_hint={'center_x': 0.6, 'center_y': 0.05}, elevation=10)
        gain_btn.md_bg_color = (.2, .2, .2, 1)
        gain_btn.bind(on_press=self.gain_loss)
        floatLayout.add_widget(gain_btn)

        # analysis_btn = MDRaisedButton(text="Sectoral Analysis", size_hint=(None, None), size=(100, 50),
        #                               pos_hint={'center_x': 0.9, 'center_y': 0.05}, elevation=10)
        # analysis_btn.md_bg_color = (.2, .2, .2, 1)
        # analysis_btn.bind(on_press=self.analysis)
        # floatLayout.add_widget(analysis_btn)
        self.add_widget(floatLayout)
    #
    # def build(self):
    #     button: Button = Button(text="Portfolio NAV is " + str(self.pf_nav),
    #                             pos_hint=({'center_x': .5, 'center_y': .95}),
    #                             size_hint=(1, .08), )
    #     button.background_color = (.2, .2, .2, 1)
    #     button.bind(on_press=self.go_home)
    #     self.add_widget(button)
    #     return self
