"""
Created by Sundar on 29-10-2020.email tksrajan@gmail.com
"""
import platform

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.button import *
from kivymd.uix.datatables import MDDataTable

import tryout
from base import BaseGrid, TableScreen


def get_gain_loss(pf_data):
    pf_cost = 0
    pf_nav = round(tryout.get_pf_nav(), 2)
    for pf in pf_data:
        pf_cost += pf.cost * pf.quantity
    gain_loss = round(pf_nav - round(pf_cost, 2), 2)
    gain_loss_pct = round((gain_loss / pf_cost) * 100, 2)
    return pf_nav, gain_loss, gain_loss_pct


class GainLossScreen(BaseGrid):

    def __init__(self, screen_manager: ScreenManager, **kwargs):
        self.updated = False
        if 'updated' in kwargs:
            self.updated = kwargs.pop('updated')
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.add_widgets()

    def add_widgets(self):
        tryout.init(updated=self.updated)
        pf_data = list(tryout.product_dict.values())
        if len(pf_data) > 0:
            pf_nav, gain_loss, gain_loss_percent = get_gain_loss(pf_data)
            n = str(pf_nav)
            g = str(gain_loss)
            if gain_loss_percent < 0:
                gp = '[color=FF0000]' + str(abs(gain_loss_percent)) + '%[/color]'
            elif gain_loss_percent > 0:
                gp = '[color=00FF00]' + str(abs(gain_loss_percent)) + '%[/color]'
            else:
                gp = str(gain_loss_percent) + '%'
            text_string = "Nav = " + n + "    Gain = " + g + "( " + gp + ")"
            labl = Label(text=text_string, markup=True, pos_hint=({'center_x': .5, 'center_y': .95}),
                         size_hint=(1, .09), )
            button: Button = MDRaisedButton(
                pos_hint=({'center_x': .5, 'center_y': .95}),
                size_hint=(1, .09), )
            button.background_color = (0.2, .6, 1, 1)
            button.bind(on_press=self.go_home)
            button.add_widget(labl)
            self.layout.add_widget(button)

            self.add_table_screens(pf_data)
            self.layout.add_widget(self.screens[0])
            self.add_nav_buttons()

            home_btn = MDIconButton(icon='home',
                                    pos_hint={'center_x': 0.5, 'center_y': 0.05})
            home_btn.md_bg_color = (1, 1, 1, 1)
            home_btn.bind(on_press=self.go_home)
            self.layout.add_widget(home_btn)

            self.add_widget(self.layout)

    # def events(self, instance, keyboard, keycode, text, modifiers):
    #     """Called when buttons are pressed on the mobile device."""
    #     if keyboard in (1001, 27):
    #         self.screen_manager.current = 'Main'
    #     return True

    def add_table_screens(self, data):
        c_data = [data[i:i + 7] for i in range(0, len(data), 7)]
        plt = platform.system()
        if plt == 'Windows':
            font_size = '[size=10]'
        else:
            font_size = '[size=30]'
        for index, fragment in enumerate(c_data):
            row_data = []
            for item in fragment:
                if item.nav == 0:
                    continue
                cost = round(item.cost * item.quantity, 2)
                gain_loss = item.gain
                if gain_loss < 0:
                    gain_loss = "[color=#FF0000]" + font_size + str(abs(round(gain_loss, 2))) + "[/size][/color]"
                else:
                    gain_loss = "[color=#448d08]" + font_size + str(round(gain_loss, 2)) + "[/size][/color]"
                sym_str = font_size + item.symbol + '[/size]'
                cost_str = font_size + str(cost) + '[/size]'
                nav_str = font_size + str(item.nav) + '[/size]'
                if plt == 'Windows':
                    row = [sym_str, cost_str, nav_str, gain_loss]
                else:
                    row = [sym_str, cost_str, gain_loss]
                row_data.append(row)
            if len(fragment) == 1:
                row_data.append(['', '', '', ''])  # hack. MDDatatable breaks if there just one row

            table = MDDataTable(
                size_hint=(1, 0.8),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                use_pagination=False,
                background_color=(0.2, .2, .2, 1),
                rows_num=7,
                check=False,
                column_data=[
                    ("Symbol", dp(20)),
                    ("Cost", dp(20)),
                    ("Gain", dp(20)),
                ] if plt == 'Linux' else [
                    ("Symbol", dp(45)),
                    ("Cost", dp(45)),
                    ("NAV", dp(45)),
                    ("Gain", dp(45)),
                ],
                row_data=row_data
            )
            table.md_bg_color = (0.2, .2, .2, 1)
            table.bind(on_row_press=tryout.on_row_press)
            tableScreen = TableScreen(table, name='table_g' + str(index))
            self.screens.append(tableScreen)

    def go_home(self, instance):
        self.screen_manager.current = 'Main'
