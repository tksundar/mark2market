"""
Created by Sundar on 29-10-2020.email tksrajan@gmail.com
"""
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import *
from kivymd.uix.datatables import MDDataTable

import tryout


def get_gain_loss(pf_data):
    pf_cost = 0
    pf_nav = round(tryout.get_pf_nav(), 2)
    for pf in pf_data:
        pf_cost += pf.cost * pf.quantity
    gain_loss = round(pf_nav - round(pf_cost, 2), 2)
    gain_loss_pct = round((gain_loss / pf_cost) * 100, 2)
    return pf_nav, gain_loss, gain_loss_pct


def get_content():
    text = '''
           Coming soon...
           
           1. Exposure pie chart. Will show 
              which stocks are exposed to 
              what level
              
           2. Gain loss chart. Bar chart 
              showing gains and losses of 
              individual stocks
          '''
    label = Label(text=text)
    return label


class GainLossScreen(Screen):

    def __init__(self, screen_manager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        Window.bind(on_keyboard=self.events)
        self.pf_data = list(tryout.product_dict.values())
        self.pf_nav, self.gain_loss, self.gain_loss_percent = get_gain_loss(self.pf_data)
        self.popup = Popup()
        self.popup.title = 'Performance Charts'
        self.popup.content = get_content()
        self.popup.size_hint = (.9, .7)
        self.add_widgets()

    def add_widgets(self):
        floatLayout = FloatLayout()
        n = str(self.pf_nav)
        g = str(self.gain_loss)
        gp = str(self.gain_loss_percent)

        text_string = "Nav = " + n + "    Gain = " + g + "( " + gp + "% )"

        button: Button = Button(text=text_string,
                                pos_hint=({'center_x': .5, 'center_y': .95}),
                                size_hint=(1, .08), )
        button.background_color = (0, 0, 0, 1)
        button.bind(on_press=self.go_home)
        floatLayout.add_widget(button)

        table = self.get_table(self.pf_data)
        floatLayout.add_widget(table)
        home_btn = MDIconButton(icon='home', pos_hint={'center_x': 0.5, 'center_y': 0.05})
        home_btn.bind(on_press=self.go_home)
        floatLayout.add_widget(home_btn)
        self.add_widget(floatLayout)

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""
        if keyboard in (1001, 27):
            self.screen_manager.current = 'Main'
        return True

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
            size_hint=(.9, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            use_pagination=True,
            rows_num=7,
            pagination_menu_pos='auto',
            check=False,
            column_data=[
                ("Symbol", dp(15)),
                ("Cost", dp(15)),
                ("NAV", dp(15)),
                ("Gain", dp(15)),
            ],
            row_data=row_data
        )

        return table

    def go_home(self, instance):
        self.screen_manager.current = 'Main'
