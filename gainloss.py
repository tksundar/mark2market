"""
Created by Sundar on 29-10-2020.email tksrajan@gmail.com
"""

from kivy.metrics import dp
from kivy.properties import ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import *

import tryout


class GainLossScreen(Screen):

    def __init__(self, screen_manager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.pf_data = list(tryout.product_dict.values())
        self.add_widgets()

    def add_widgets(self):
        floatLayout = FloatLayout()
        button: Button = Button(text="Portfolio NAV is " + str(tryout.get_pf_nav()),
                                pos_hint=({'center_x': .5, 'center_y': .95}),
                                size_hint=(1, .08), )
        button.background_color = (.2, .2, .2, 1)
        button.bind(on_press=self.go_home)
        floatLayout.add_widget(button)
        table = self.get_table(self.pf_data)
        floatLayout.add_widget(table)
        input_btn = MDRaisedButton(text="Add Transactions", size_hint=(None, None), size=(100, 50),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.05}, elevation=10)
        input_btn.md_bg_color = (.2, .2, .2, 1)
        input_btn.bind(on_press=self.go_home)
        floatLayout.add_widget(input_btn)
        self.add_widget(floatLayout)

    def get_table(self, data):
        row_data = []
        for item in data:
            if item.nav == 0:
                continue

            cost = round(item.cost * item.quantity, 2)
            gain_loss = item.gain
            current_nav = item.nav
            if gain_loss < 0:
                gain_loss = '(' + str(round(gain_loss, 2))[1:] + ')'
            else:
                gain_loss = str(round(gain_loss, 2))

            row = [item.symbol, cost, current_nav, gain_loss]
            row_data.append(row)

        table = MDDataTable(
            size_hint=(0.9, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            use_pagination=True,
            rows_num=10,
            check=False,
            column_data=[
                ("Symbol", dp(30)),
                ("Avg.Cost", dp(30)),
                ("Curr.NAV", dp(30)),
                ("Gain/Loss", dp(30)),
            ],
            row_data=row_data
        )

        return table

    def go_home(self, instance):
        self.screen_manager.current = 'Main'
