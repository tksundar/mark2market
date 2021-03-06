import os
import time

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager, ScreenManagerException
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDIconButton
from kivymd.uix.filemanager import MDFileManager

import tryout
from PandLScreen import PnLScreen
from analysis import Analysis
from gainloss import GainLossScreen
from help import HelpScreen

hint_center = {'center_x': .5, 'center_y': .5}


class MainScreen(Screen):
    pass


class TransactionUploadScreen(Screen):
    pass


class TransactionEntryScreen(Screen):
    pass


class TradingScreen(Screen):
    pass


class SpinnerScreen(Screen):
    pass


def addMainScreen(sm, self):
    sm.add_widget(MainScreen(name="Main"))
    sm.add_widget(TransactionUploadScreen(name="Upload"))
    sm.add_widget(TransactionEntryScreen(name="Entry"))
    sm.add_widget(TradingScreen(name="Trade"))


def spruce_val(val):
    if val.__contains__('LTD'):
        val = val.replace("LTD", "LIMITED")
    if val.__contains__('Ltd'):
        val = val.replace("Ltd", "LIMITED")
    if val.__contains__("Limited"):
        val = val.replace("Limited", "LIMITED")
    return val


def convert_to_csv(filePath):
    import pandas as pd
    df = pd.read_excel(filePath)
    df.to_csv('holdings.csv', header=True)
    return 'holdings.csv'


class Mark2MarketApp(MDApp):
    processing = BooleanProperty(defaultValue=False)
    analytics = BooleanProperty(defaultValue=True)
    stock_fetch = BooleanProperty(defaultValue=True)
    color = (0, 0, 0, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        start = time.time()
        self.updated = False
        self.processing = True
        self.screen_manager = ScreenManager()
        self.current = "Main"
        self.manager_open = False
        self.filePath = ""
        self.symbol = []
        self.qty = []
        self.cost = []
        self.side = []
        Window.bind(on_keyboard=self.events)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )

        self.file_manager.ext = ['.csv', '.CSV', '.xlsx', '.XLSX']
        self.popup = self.get_popup()
        self.no_data_popup = self.no_data_popup()
        end = time.time()
        print('elapsed time for startup is %d seconds ' % (end - start))
        self.processing = False

    def on_processing(self, instance, value):
        pass

    def on_analytics(self, instance, value):
        pass

    def on_stock_fetch(self, instance, value):
        pass

    def help(self):
        HelpScreen().open()

    def exit(self):
        Window.close()

    def on_state(self, instance, value):
        pass

    def get_popup(self):
        pop = Popup(title='Transaction status', auto_dismiss=False)
        lbl = Label()
        lbl.text = 'Update successful'
        btn = MDIconButton()
        lbl.pos_hint = {'center_x': .5, 'center_y': .5}
        btn.icon = 'home'
        btn.bind(on_press=self.go_home)
        btn.md_bg_color = (1, 1, 1, 1)
        btn.pos_hint = {'center_x': .5, 'center_y': 0.1}
        from kivy.uix.floatlayout import FloatLayout
        layout = FloatLayout()
        layout.add_widget(lbl)
        layout.add_widget(btn)
        pop.content = layout
        pop.size_hint = .6, .6
        return pop

    def no_data_popup(self):
        pop = Popup(title='Data status', auto_dismiss=False)
        lbl = Label()
        lbl.text = 'No Data!. Add some transactions'
        btn = MDIconButton()
        lbl.pos_hint = {'center_x': .5, 'center_y': .5}
        btn.icon = 'home'
        btn.bind(on_press=self.go_home)
        btn.md_bg_color = (1, 1, 1, 1)
        btn.pos_hint = {'center_x': .5, 'center_y': 0.1}
        layout = FloatLayout()
        layout.add_widget(lbl)
        layout.add_widget(btn)
        pop.content = layout
        pop.size_hint = .8, .6
        return pop

    def go_nav(self):
        if not os.path.exists('csv/pandb.csv'):
            self.no_data_popup.open()
            return
        self.processing = True
        Clock.schedule_once(self.nav_delegate, 1)

    def add_nav_widget(self):
        pnl = PnLScreen(self.screen_manager, name='NAV', updated=self.updated)
        self.updated = False
        self.screen_manager.add_widget(pnl)

    def nav_delegate(self, dt):
        try:
            pnl = self.screen_manager.get_screen('NAV')
            if self.updated or len(tryout.product_dict) == 0:
                self.screen_manager.remove_widget(pnl)
                self.add_nav_widget()
        except ScreenManagerException:
            self.add_nav_widget()
            print('prod dict length = ', len(tryout.product_dict))
        if len(tryout.product_dict) == 0:
            self.no_data_popup.open()
        else:
            self.screen_manager.current = "NAV"
        self.processing = False

    def upload_screen(self):
        self.screen_manager.current = 'Upload'

    def entry_screen(self):
        self.screen_manager.current = 'Entry'

    def trading_screen(self):
        self.screen_manager.current = 'Trade'

    def gain_loss(self):
        if not os.path.exists('csv/pandb.csv'):
            self.no_data_popup.open()
            return
        self.processing = True
        Clock.schedule_once(self.gain_loss_delegate, 1)

    def gain_loss_delegate(self, dt):
        self.processing = True
        try:
            self.screen_manager.get_screen('GainLoss')
        except ScreenManagerException:
            gl = GainLossScreen(self.screen_manager, name='GainLoss', updated=self.updated)
            self.screen_manager.add_widget(gl)
        if len(tryout.product_dict) == 0:
            self.no_data_popup.open()
        else:
            self.screen_manager.current = 'GainLoss'
        self.processing = False

    def charts(self):
        if not os.path.exists('csv/pandb.csv'):
            self.no_data_popup.open()
            return
        self.processing = True
        Clock.schedule_once(self.chart_delegate, 3)

    def chart_delegate(self, dt):
        try:
            analysis = self.screen_manager.get_screen('Charts')
        except ScreenManagerException:
            analysis = Analysis(self.screen_manager, name='Charts', updated=self.updated)
            # analysis.add_widgets()
            self.screen_manager.add_widget(analysis)
        if len(tryout.product_dict) > 0:
            self.screen_manager.current = 'Charts'
        else:
            self.no_data_popup.open()

        self.processing = False

    def on_text(self):
        symbol = self.root.get_screen("Entry").ids.symbol.text
        self.symbol.append(symbol)
        qty = self.root.get_screen("Entry").ids.quantity.text
        self.qty.append(qty)
        cost = self.root.get_screen("Entry").ids.cost.text
        self.cost.append(cost)
        side = self.root.get_screen("Entry").ids.side.text
        self.side.append(side)

    def open_url(self, instance):
        tryout.open_url(instance.text)

    def on_submit(self):
        self.processing = True
        Clock.schedule_once(self.submit_delegate, 1)

    def submit_delegate(self, dt):
        symbol = self.symbol.pop().upper()
        qty = float(self.qty.pop().upper())
        cost = float(self.cost.pop().upper())
        side = self.side.pop().upper()
        print(symbol, qty, cost, side)
        success = tryout.update_portfolio(symbol, qty, cost, side)
        if success:
            self.screen_manager.get_screen('Entry').ids.symbol.text = ''
            self.screen_manager.get_screen('Entry').ids.quantity.text = ''
            self.screen_manager.get_screen('Entry').ids.cost.text = ''
            self.screen_manager.get_screen('Entry').ids.side.text = ''
            self.updated = True
            self.processing = False
            self.popup.open()

    def home(self):
        self.screen_manager.current = 'Main'

    def go_home(self, instance):
        self.screen_manager.current = 'Main'
        self.popup.dismiss()
        self.no_data_popup.dismiss()

    def file_manager_open(self):
        self.file_manager.show('/')  # output manager to the screen
        self.manager_open = True

    def process_file(self, instance):
        self.processing = True
        Clock.schedule_once(self.process_file_delegate, 1)

    def process_file_delegate(self, dt):
        if len(self.filePath) == 0:
            toast('You must select a transaction file')
            return

        csvFile = self.filePath
        extn = self.filePath[-4:].upper()
        if extn.__contains__('XLS'):
            csvFile = convert_to_csv(self.filePath)
        tryout.init()
        tryout.make_product_dict_from_csv(csv_file=csvFile)
        self.go_nav()
        tryout.nav_name = 'NAV'
        self.processing = False
        self.root.get_screen(self.root.current).ids.file_chooser.text = 'Choose a transaction file'

    def select_path(self, path):
        """It will be called when you click on the file name
        or the catalog selection button.
        :type path: str;
        :param path: path to the selected directory or file;
        """
        self.exit_manager()
        self.root.get_screen(self.root.current).ids.file_chooser.text = path
        self.filePath = path
        # self.process_file()

    def set_error_message(self, instance_textfield):
        name = self.screen_manager.current
        screen = self.root.get_screen(name)
        screen.ids.input = True

    def back(self):
        self.screen_manager.current = 'Main'

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
            elif self.screen_manager.current == 'Main':
                self.exit()
            else:
                self.screen_manager.current = 'Main'
        return True

    def build(self):
        Builder.load_file('RootWidget.kv')
        addMainScreen(self.screen_manager, self)
        self.screen_manager.current = "Main"
        return self.screen_manager


if __name__ == '__main__':
    Mark2MarketApp().run()
