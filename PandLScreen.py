"""
Created by Sundar on 19-10-2020.email tksrajan@gmail.com
"""
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ListProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager
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


def get_table(data):
    row_data = []
    for item in data:
        if item.nav == 0:
            continue
        row = [item.symbol, item.quantity, item.price, item.nav]
        row_data.append(row)
    if len(row_data) == 1:
        row_data.append(['', '', '', ''])  # hack. MDDatatable breaks if there just one row

    table = MDDataTable(
        size_hint=(.9, 0.8),
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

    return table


class PnLScreen(Screen):
    data = ListProperty(defaultvalue=[])
    processing = BooleanProperty(defaultvalue=False)

    def __init__(self, screen_manager, **kwargs):
        self.updated = False
        if 'updated' in kwargs:
            self.updated = kwargs.pop('updated')
        super().__init__(**kwargs)
        self.screen_manager: ScreenManager = screen_manager
        self.name = kwargs['name']

        Window.bind(on_keyboard=self.events)

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""
        if keyboard in (1001, 27):
            self.screen_manager.current = 'Main'
        return True

    def go_home(self, instance):
        self.screen_manager.current = "Main"
        self.screen_manager.get_screen('Main').ids.spinner.active = False

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
                                        size_hint=(.9, .09), )
        button.background_color = (0.2, .6, 1, 1)
        button.bind(on_press=self.go_home)
        floatLayout.add_widget(button)
        table = get_table(self.pf_data)
        floatLayout.add_widget(table)
        home_btn = MDIconButton(icon='home',
                                pos_hint={'center_x': 0.5, 'center_y': 0.05})
        home_btn.md_bg_color = (0.2, .6, 1, 1)
        home_btn.bind(on_press=self.go_home)
        floatLayout.add_widget(home_btn)
        self.add_widget(floatLayout)
