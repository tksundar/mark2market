"""
Created by Sundar on 19-10-2020.email tksrajan@gmail.com
"""

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ListProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.button import *
from kivymd.uix.datatables import MDDataTable

import tryout
from base import BaseGrid, TableScreen

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


class PnLScreen(BaseGrid):
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

    def add_table_screens(self, data):
        c_data = [data[i:i + 7] for i in range(0, len(data), 7)]
        for index, fragment in enumerate(c_data):
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
            tableScreen = TableScreen(table, name='table' + str(index))
            self.screens.append(tableScreen)

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
        if len(self.pf_data) == 0:
            return
        pf_nav = 0
        for pi in self.pf_data:
            pf_nav += pi.nav
        self.pf_nav = round(pf_nav, 2)
        prev_nav = tryout.get_prev_pf_nav()
        print(pf_nav, prev_nav)
        percent = round(((self.pf_nav - prev_nav) / prev_nav) * 100, 2)
        mov_str = str(percent)
        if prev_nav > pf_nav:
            mov_str = '[color=FF0000]' + str(abs(percent)) + '%[/color]'
        elif prev_nav < pf_nav:
            mov_str = '[color=00FF00] ' + str(percent) + '%[/color]'
        text = "Portfolio NAV is " + str(self.pf_nav) + '(' + mov_str + ')'
        labl = Label(text=text, markup=True, pos_hint=({'center_x': .5, 'center_y': .95}),
                     size_hint=(1, .09), )
        labl.background_color = (0.2, .6, 1, 1)
        button: Button = MDRaisedButton(
                                        pos_hint=({'center_x': .5, 'center_y': .95}),
                                        size_hint=(1, .09), )

        button.background_color = (0.2, .6, 1, 1)
        button.bind(on_press=self.go_home)
        button.add_widget(labl)
        self.layout.add_widget(button)
        #self.layout.add_widget(labl)
        self.add_table_screens(self.pf_data)
        self.layout.add_widget(self.screens[0])

        self.add_nav_buttons()

        home_btn = MDIconButton(icon='home',
                                pos_hint={'center_x': 0.5, 'center_y': 0.05})
        home_btn.md_bg_color = (1, 1, 1, 1)
        home_btn.bind(on_press=self.go_home)
        self.layout.add_widget(home_btn)
        self.add_widget(self.layout)
