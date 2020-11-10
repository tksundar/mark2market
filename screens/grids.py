"""
Created by Sundar on 09-11-2020.email tksrajan@gmail.com
"""
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDIconButton, MDRaisedButton

import tryout


class TableScreen(Screen):

    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(screen)


class BaseTable(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screens = []
        self.screen_index = 0

    def go_next(self, instance):
        self.layout.remove_widget(self.screens[self.screen_index])
        self.screen_index += 1
        self.layout.add_widget(self.screens[self.screen_index])
        self.add_nav_buttons()

    def go_prev(self, instance):
        self.layout.remove_widget(self.screens[self.screen_index])
        self.screen_index -= 1
        print('len, index', len(self.screens), self.screen_index)
        self.layout.add_widget(self.screens[self.screen_index])
        self.add_nav_buttons()

    def add_nav_buttons(self):
        right_nav_btn = MDIconButton(icon='chevron-right')
        right_nav_btn.disabled = False if self.screen_index + 1 < len(self.screens) else True
        right_nav_btn.pos_hint = {'center_x': .6, 'center_y': .15}
        right_nav_btn.bind(on_press=self.go_next)
        self.layout.add_widget(right_nav_btn)

        left_nav_btn = MDIconButton(icon='chevron-left')
        left_nav_btn.disabled = True if self.screen_index == 0 else False
        left_nav_btn.pos_hint = {'center_x': .4, 'center_y': .15}
        left_nav_btn.bind(on_press=self.go_prev)
        self.layout.add_widget(left_nav_btn)


class NavScreen(BaseTable):

    def __init__(self, screen_manager, **kwargs):
        self.updated = False
        if 'updated' in kwargs:
            self.updated = kwargs.pop('updated')
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.pf_data = []
        self.pf_nav = 0
        self.layout = FloatLayout()
        self.add_widgets()

    def add_table_screens(self, pf_data):
        c_data = [pf_data[i:i + 7] for i in range(0, len(pf_data), 7)]

        for count in range(len(c_data)):
            float = FloatLayout()
            float.pos_hint = {'center_x': 0.5, 'center_y': 0.8}
            grid = GridLayout(cols=4)
            lab1 = Label(text='Symbol')
            grid.add_widget(lab1)
            lab2 = Label(text='Quantity')
            grid.add_widget(lab2)
            lab3 = Label(text='Price')
            grid.add_widget(lab3)
            lab4 = Label(text='Nav')
            grid.add_widget(lab4)

            for index, fragment in enumerate(c_data):
                for item in fragment:
                    sym = Label(text=item.symbol)
                    qty = Label(text=str(item.quantity))
                    price = Label(text=str(item.price))
                    nav_str = ''
                    if sym in tryout.nse_prev_price_data:
                        prev_close = tryout.nse_prev_price_data.get(sym)
                        prev_nav = prev_close * item.quantity
                        if prev_nav > item.nav:
                            nav_str = '[color=FF0000]' + str(item.nav) + '[/color]'
                        else:
                            nav_str = '[color=00FF00]' + str(item.nav) + '[/color]'
                    nav = Label(text=nav_str, markup=True)
                    grid.add_widget(sym)
                    grid.add_widget(qty)
                    grid.add_widget(price)
                    grid.add_widget(nav)
            float.add_widget(grid)
            tableScreen = TableScreen(float, name='table' + str(count))
            print(tableScreen)
            self.screens.append(tableScreen)

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
        self.add_table_screens(self.pf_data)
        self.layout.add_widget(self.screens[0])
        self.add_nav_buttons()

        home_btn = MDIconButton(icon='home',
                                pos_hint={'center_x': 0.5, 'center_y': 0.05})
        home_btn.md_bg_color = (1, 1, 1, 1)
        home_btn.bind(on_press=self.go_home)
        self.layout.add_widget(home_btn)
        self.add_widget(self.layout)

    def go_home(self, instance):
        self.screen_manager.current = "Main"
