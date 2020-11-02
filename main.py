import asyncio
import os
from time import time

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager, ScreenManagerException
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager

import tryout
from PandLScreen import PnLScreen
from analysis import Analysis
from gainloss import GainLossScreen
from help import HelpScreen


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


def addMainScreen(sm):
    sm.add_widget(MainScreen(name="Main"))
    sm.add_widget(TransactionUploadScreen(name="Upload"))
    sm.add_widget(TransactionEntryScreen(name="Entry"))
    sm.add_widget(TradingScreen(name="Trade"))
    sm.add_widget(SpinnerScreen(name="Spinner"))


def add_dep_screens(sm):
    pnl = PnLScreen(sm, name="NAV")
    sm.add_widget(pnl)
    sm.add_widget(GainLossScreen(sm, name="GainLoss"))
    analysis = Analysis(sm, name="Charts")
    sm.add_widget(analysis)


def on_processing(instance, value):
    print('instance, value', instance, value)


def spruce_val(val):
    if val.__contains__('LTD'):
        val = val.replace("LTD", "LIMITED")
    if val.__contains__('Ltd'):
        val = val.replace("Ltd", "LIMITED")
        print('replaced->', val)
    if val.__contains__("Limited"):
        val = val.replace("Limited", "LIMITED")
    return val


def convert_to_csv(filePath):
    import pandas as pd
    df = pd.read_excel(filePath)
    df.to_csv('holdings.csv', header=True)
    return 'holdings.csv'


def help():
    HelpScreen().open()


def exit():
    Window.close()


class Mark2MarketApp(MDApp):
    processing = BooleanProperty(defaultValue=False)
    state = StringProperty(defaultvalue='stop')


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        start = time()
        tryout.get_nse_prices()
        tryout.get_bse_prices()
        tryout.get_isin_to_symbol_map()

        if os.path.exists('csv/pandb.csv'):
            tryout.make_product_dict_from_csv(csv_file='csv/pandb.csv')


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
        # self.characters = []
        Builder.load_file("RootWidget.kv")
        self.screen_manager = ScreenManager()
        addMainScreen(self.screen_manager)
        if len(tryout.product_dict) > 0:
            print('have products.Opening nav screen')
            add_dep_screens(self.screen_manager)
            self.screen_manager.current = "NAV"
            self.current = "NAV"
        else:
            print('No products yet. Opening main screen')
            self.screen_manager.current = "Main"
            self.current = "Main"

        end = time()
        print('elapsed time for startup is %d seconds ' % (end - start))

    def on_state(self,instance,value):
        print(value)
        print(instance)
        # {
        #     "start": self.root.ids.progress.start,
        #     "stop": self.root.ids.progress.stop,
        # }.get(value)()
        #self.screen_manager.ids.progress.start()

    def get_popup(self):
        pop = Popup(auto_dismiss=False)
        lbl = Label()
        lbl.text = 'Transaction updated successfully'
        btn = Button()
        btn.text = 'Home'
        btn.bind(on_press=self.go_home)
        from kivy.uix.gridlayout import GridLayout
        layout = GridLayout(rows=2)
        layout.add_widget(lbl)
        layout.add_widget(btn)
        pop.content = layout
        pop.size_hint = .6, .6
        return pop

    def go_nav(self):
        self.screen_manager.current = self.current

    def upload_screen(self):
        self.screen_manager.current = 'Upload'

    def entry_screen(self):
        self.screen_manager.current = 'Entry'

    def trading_screen(self):
        self.screen_manager.current = 'Trade'

    def gain_loss(self):
        self.screen_manager.current = 'GainLoss'

    def charts(self):
        self.screen_manager.current = 'Charts'

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
        print(self.symbol, self.qty, self.cost, self.side)
        symbol = self.symbol.pop().upper()
        qty = float(self.qty.pop().upper())
        cost = float(self.cost.pop().upper())
        side = self.side.pop().upper()
        print(symbol, qty, cost, side)
        success = tryout.update_portfolio(symbol, qty, cost, side)
        if success:
            try:
                self.screen_manager.get_screen('NAV')
            except ScreenManagerException:
                self.screen_manager.add_widget(PnLScreen(self.screen_manager, name='NAV'))
                self.current = 'NAV'
            try:
                self.screen_manager.get_screen('GainLoss')
            except ScreenManagerException:
                self.screen_manager.add_widget(GainLossScreen(self.screen_manager, name='GainLoss'))
            try:
                self.screen_manager.get_screen('Charts')
            except ScreenManagerException:
                self.screen_manager.add_widget(Analysis(self.screen_manager, name='Charts'))
            self.popup.open()

    def home(self):
        self.screen_manager.current = 'Main'

    def go_home(self, instance):
        self.screen_manager.current = 'Main'
        self.popup.dismiss()

    def file_manager_open(self):
        self.file_manager.show('/')  # output manager to the screen
        self.manager_open = True
        # if len(self.characters) > 0:
        #     self.root.get_screen("Main").ids.input.text = self.characters.pop()

    def process_file(self):
        self.screen_manager.current = 'Spinner'
        if len(self.filePath) == 0:
            toast('You must select a transaction file')
            return

        csvFile = self.filePath
        extn = self.filePath[-4:].upper()
        if extn.__contains__('XLS'):
            csvFile = convert_to_csv(self.filePath)
        tryout.make_product_dict_from_csv(csv_file=csvFile)
        self.state = 'stop'
        # for item in list(tryout.product_dict.values()):
        #     print(item)
        screen_name = "UPDATE" + str(time())
        self.screen_manager.add_widget(PnLScreen(self.screen_manager, name=screen_name))
        self.screen_manager.add_widget(GainLossScreen(self.screen_manager, name="GainLoss"))
        analysis = Analysis(self.screen_manager, name="Charts")
        self.screen_manager.add_widget(analysis)
        self.screen_manager.current = screen_name
        self.current = screen_name
        tryout.nav_name = screen_name


    def select_path(self, path):
        """It will be called when you click on the file name
        or the catalog selection button.
        :type path: str;
        :param path: path to the selected directory or file;
        """
        self.exit_manager()
        self.root.get_screen(self.root.current).ids.file_chooser.text = path
        self.filePath = path
        #self.process_file()

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
            else:
                exit()
        return True

    def build(self):
        return self.screen_manager


if __name__ == '__main__':
    Mark2MarketApp().run()
