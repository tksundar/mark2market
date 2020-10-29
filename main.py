import os
from time import time

import openpyxl
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDRectangleFlatIconButton,MDIconButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.tooltip import MDTooltip

import tryout
from PandLScreen import PnLScreen
from gainloss import GainLossScreen


class MainScreen(Screen):
    pass


def buildScreenManager():
    Builder.load_file("RootWidget.kv")
    sm = ScreenManager()
    sm.add_widget(MainScreen(name="Main"))
    return sm


class TooltipMDIconButton(MDIconButton, MDTooltip):
    tooltip_text = 'Choose a CSV file.Press for more info'


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
    # opening the xlsx file
    xlsx = openpyxl.load_workbook(filePath)
    # opening the active sheet
    sheet = xlsx.active
    # getting the data from the sheet
    data = sheet.rows
    # creating a csv file
    csv = open("data.csv", "w+")
    count = 0
    for row in data:
        items = list(row)
        if (len(items)) < 4:
            continue
        count += 1
        for item in items:
            val = str(item.value)
            if not (val is None or val == 'None'):
                val = spruce_val(val)
                if count == 1:  # header row
                    csv.write(val.lower() + ',')
                else:
                    csv.write(val.upper() + ',')
        csv.write('\n')
    # close the csv file
    csv.close()
    return csv


class Mark2MarketApp(MDApp):
    processing = BooleanProperty(defaultValue=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tryout.get_nse_prices()
        tryout.get_bse_prices()
        tryout.get_isin_to_symbol_map()
        if os.path.exists('pandb.csv'):
            tryout.make_product_dict_from_csv(csv_file='pandb.csv')
        self.filePath = ""
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )
        self.file_manager.ext = ['.csv', '.CSV', '.xlsx', '.XLSX']
        self.processing = False
        # self.characters = []
        Builder.load_file("RootWidget.kv")
        self.screen_manager = ScreenManager(transition=FadeTransition())
        if len(tryout.product_dict) > 0:
            pnl = PnLScreen(self.screen_manager, name="NAV")
            print(pnl)
            self.screen_manager.add_widget(pnl)
            self.screen_manager.current = "NAV"
            self.current = "NAV"
            self.screen_manager.add_widget(MainScreen(name="Main"))
            self.screen_manager.add_widget(GainLossScreen(self.screen_manager,name="GainLoss"))
        else:
            self.screen_manager.add_widget(MainScreen(name="Main"))
            self.screen_manager.current = "Main"

    def go_nav(self):
        self.screen_manager.current = self.current

    # def on_text(self):
    #     name = self.screen_manager.current
    #     val = self.root.get_screen(name).ids.input.text
    #     print(val)
    #     self.characters.append(val.upper())

    def file_manager_open(self):
        self.file_manager.show('/')  # output manager to the screen
        self.manager_open = True
        # if len(self.characters) > 0:
        #     self.root.get_screen("Main").ids.input.text = self.characters.pop()

    def process_file(self):
        if not hasattr(self, 'filePath'):
            toast('You must select a transaction file')
            return
        extn = self.filePath[self.filePath.index('.') + 1:len(self.filePath)].upper()
        if not (extn == 'XLSX' or extn == 'CSV'):
            msg = extn + " not supported"
            toast(msg)
            return
        csvFile = self.filePath
        if extn == 'XLSX':
            convert_to_csv(self.filePath)
            csvFile = "data.csv"
        tryout.make_product_dict_from_csv(csv_file=csvFile)
        for item in list(tryout.product_dict.values()):
            print(item)
        screen_name = "UPDATE" + str(time())
        self.screen_manager.add_widget(PnLScreen(self.screen_manager, name=screen_name))
        self.screen_manager.add_widget(GainLossScreen(self.screen_manager, name="GainLoss"))
        self.screen_manager.current = screen_name
        self.current = screen_name

    def select_path(self, path):
        """It will be called when you click on the file name
        or the catalog selection button.
        :type path: str;
        :param path: path to the selected directory or file;
        """
        self.exit_manager()
        self.root.get_screen(self.root.current).ids.file_chooser.text = path
        self.filePath = path

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
        return True

    def build(self):
        return self.screen_manager


if __name__ == '__main__':
    Mark2MarketApp().run()
