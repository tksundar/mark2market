"""
Created by Sundar on 19-10-2020.email tksrajan@gmail.com
"""
from kivy.core.window import Window
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


def get_table(data):
    row_data = []
    for item in data:
        if item.nav == 0:
            continue
        row = [item.symbol, item.quantity, item.price, item.nav]
        row_data.append(row)

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
        super().__init__(**kwargs)
        self.screen_manager: ScreenManager = screen_manager
        self.pf_data = list(tryout.product_dict.values())
        self.name = kwargs['name']
        app = MDApp.get_running_app().name
        if app == 'UPDATE':
            tryout.make_product_dict_from_csv(csv_file='csv/pandb.csv')
            self.pf_data = list(tryout.product_dict.values())
        Window.bind(on_keyboard=self.events)
        pf_nav = 0
        for pi in self.pf_data:
            pf_nav += pi.nav
        self.pf_nav = round(pf_nav, 2)
        sort("nav", self.pf_data)
        self.add_widgets()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""
        if keyboard in (1001, 27):
            self.screen_manager.current = 'Main'
        return True

    def go_home(self, instance):
        self.screen_manager.current = "Main"

    def add_widgets(self):
        self.processing = True
        floatLayout = FloatLayout()
        button: Button = Button(text="Portfolio NAV is " + str(self.pf_nav),
                                pos_hint=({'center_x': .5, 'center_y': .95}),
                                size_hint=(1, .08), )
        button.background_color = (0, 0, 0, 1)
        button.bind(on_press=self.go_home)
        floatLayout.add_widget(button)
        table = get_table(self.pf_data)
        floatLayout.add_widget(table)

        # input_btn = MDIconButton(icon='home',text="Home", size_hint=(None, None), size=(100, 50),
        #                            pos_hint={'center_x': 0.5, 'center_y': 0.05})

        home_btn = MDIconButton(icon='home',pos_hint={'center_x': 0.5, 'center_y': 0.05})
        home_btn.md_bg_color = (1, 1, 1, 1)
        home_btn.bind(on_press=self.go_home)
        floatLayout.add_widget(home_btn)


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
