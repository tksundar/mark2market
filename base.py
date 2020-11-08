"""
Created by Sundar on 08-11-2020.email tksrajan@gmail.com
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDIconButton


class TableScreen(Screen):

    def __init__(self, screen, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(screen)


class BaseGrid(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screens = []
        self.screen_index = 0
        self.layout = FloatLayout()

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
        right_nav_btn.pos_hint = {'center_x': .5, 'center_y': .15}
        right_nav_btn.bind(on_press=self.go_next)
        self.layout.add_widget(right_nav_btn)

        left_nav_btn = MDIconButton(icon='chevron-left')
        left_nav_btn.disabled = True if self.screen_index == 0 else False
        left_nav_btn.pos_hint = {'center_x': .45, 'center_y': .15}
        left_nav_btn.bind(on_press=self.go_prev)
        self.layout.add_widget(left_nav_btn)
