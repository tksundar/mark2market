"""
Created by Sundar on 19-10-2020.email tksrajan@gmail.com
"""

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ListProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import *
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.spinner import MDSpinner

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

    def get_carousel(self, data):
        carousel = Carousel(direction='right')
        c_data = [data[i:i + 7] for i in range(0, len(data), 7)]
        for fragment in c_data:
            row_data = []
            for item in fragment:
                if item.nav == 0:
                    continue
                row = [item.symbol, item.quantity, item.price, item.nav]
                row_data.append(row)
                if len(fragment) == 1:
                    row_data.append('')
            table = MDDataTable(
                size_hint=(1, 0.8),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                use_pagination=False,
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
            carousel.add_widget(table)

        return carousel

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
        carousel = self.get_carousel(self.pf_data)
        floatLayout.add_widget(carousel)

        spinner = MDSpinner()
        MDApp.get_running_app().stock_fetch = False
        spinner.active = MDApp.get_running_app().stock_fetch
        spinner.size_hint = None, None
        spinner.size = dp(30), dp(30)
        spinner.pos_hint = {'center_x': .5, 'center_y': .8}

        floatLayout.add_widget(spinner)

        home_btn = MDIconButton(icon='home',
                                pos_hint={'center_x': 0.5, 'center_y': 0.05})
        home_btn.md_bg_color = (1, 1, 1, 1)
        home_btn.bind(on_press=self.go_home)
        floatLayout.add_widget(home_btn)
        self.add_widget(floatLayout)
