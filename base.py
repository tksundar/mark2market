"""
Created by Sundar on 08-11-2020.email tksrajan@gmail.com
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDIconButton


class TableScreen(Screen):

    def __init__(self, widget, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(widget)
        self.widget = widget



class BaseGrid(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screens = []
        self.screen_index = 0
        self.right_nav_btn = None
        self.left_nav_btn = None
        self.layout = FloatLayout()

    def go_next(self, instance):
        if self.right_nav_btn.disabled:
            return
        self.layout.remove_widget(self.screens[self.screen_index])
        self.screen_index += 1
        self.layout.add_widget(self.screens[self.screen_index])
        self.add_nav_buttons()

    def go_prev(self, instance):
        if self.left_nav_btn.disabled:
            return
        self.layout.remove_widget(self.screens[self.screen_index])
        self.screen_index -= 1
        self.layout.add_widget(self.screens[self.screen_index])
        self.add_nav_buttons()

    def add_nav_buttons(self):
        self.right_nav_btn = MDIconButton(icon='chevron-right')
        self.right_nav_btn.md_bg_color = (1,1,1,1)
        self.right_nav_btn.disabled = False if self.screen_index + 1 < len(self.screens) else True
        self.right_nav_btn.pos_hint = {'center_x': .6, 'center_y': .15}
        self.right_nav_btn.bind(on_press=self.go_next)
        self.layout.add_widget(self.right_nav_btn)

        self.left_nav_btn = MDIconButton(icon='chevron-left')
        self.left_nav_btn.md_bg_color = (1,1,1,1)
        self.left_nav_btn.disabled = True if self.screen_index == 0 else False
        self.left_nav_btn.pos_hint = {'center_x': .4, 'center_y': .15}
        self.left_nav_btn.bind(on_press=self.go_prev)
        self.layout.add_widget(self.left_nav_btn)
