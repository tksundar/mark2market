"""
Created by Sundar on 19-10-2020.email tksrajan@gmail.com
"""

from kivy.metrics import dp
from kivy.properties import ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
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


def go_home(instance):
    print('called')


def get_table(data):
    row_data = []
    for item in data:
        if item.nav == 0:
            continue
        row = [item.name[:40], item.quantity, item.price, item.nav]
        row_data.append(row)

    table = MDDataTable(
        size_hint=(0.9, 0.9),
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
        use_pagination=True,
        rows_num=10,
        check=False,
        column_data=[
            ("Name", dp(30)),
            ("Quantity", dp(30)),
            ("Price", dp(30)),
            ("NAV", dp(30)),
        ],
        row_data=row_data
    )

    return table


class PnLScreen(Screen):
    data = ListProperty(defaultvalue=[])
    processing = BooleanProperty(defaultvalue=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(self.make_widget())

    def make_widget(self):
        self.processing = True
        pf_data = list(tryout.product_dict.values())
        pf_nav = 0
        for pi in pf_data:
            print(pi)
            pf_nav += pi.nav
        pf_nav = round(pf_nav, 2)
        sort("nav", pf_data)
        data = pf_data
        box = BoxLayout(orientation='vertical')
        button: Button = Button(text='Portfolio NAV is ' + str(pf_nav), size_hint_y=None, size=(1000, 50))
        button.background_color = (.2, .2, .2, 1)
        button.bind(on_press=go_home)
        box.add_widget(button)
        # ---------------- lambda x: self.go_home not working. Need more investigation!
        # toolbar = MDToolbar(title='Net Asset Value : INR ' + str(pf_nav))
        # toolbar.md_bg_color = (.2, .2, .2, 1)
        # #print(MDApp.get_running_app().go_home())
        # toolbar.left_action_items = [["home", lambda x: MDApp.get_running_app().go_home]]
        # box.add_widget(toolbar)
        floatLayout = FloatLayout()
        table = get_table(data)
        floatLayout.add_widget(table)
        box.add_widget(floatLayout)
        return box
