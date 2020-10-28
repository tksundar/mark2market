from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDRectangleFlatIconButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.tooltip import MDTooltip
from PandLScreen import PnLScreen
import tryout
import os


class MainScreen(Screen):
    pass


def buildScreenManager():
    Builder.load_file("RootWidget.kv")
    sm = ScreenManager()
    sm.add_widget(MainScreen(name="Main"))
    return sm


class TooltipMDIconButton(MDRectangleFlatIconButton, MDTooltip):
    tooltip_text = 'Choose a PDF or CSV file. CSV file should have\n' \
                   'the following columns\n\n' \
                   'isin,                           quantity,         price,          side\n' \
                   'INE021A01026,            100,          2100,          BUY'


def on_processing(instance, value):
    print('instance, value', instance, value)


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
        self.file_manager.ext = ['.csv', '.CSV', '.pdf', '.PDF']
        self.processing = False
        self.characters = []
        self.screen_manager = buildScreenManager()
        if len(tryout.product_dict) > 0:
            pnl = PnLScreen(name="NAV")
            print(pnl)
            self.screen_manager.add_widget(pnl)
            self.screen_manager.current = "NAV"
        else:
            self.screen_manager.current = "Main"


    def on_text(self):
        name = self.screen_manager.current
        val = self.root.get_screen(name).ids.input.text
        print(val)
        self.characters.append(val.upper())

    def file_manager_open(self):
        self.file_manager.show('/')  # output manager to the screen
        self.manager_open = True
        if len(self.characters) > 0:
            self.root.get_screen("Main").ids.input.text = self.characters.pop()

    def process_file(self):
        if not hasattr(self, 'filePath'):
            toast('You must select a transaction file')
            return
        extn = self.filePath[self.filePath.index('.') + 1:len(self.filePath)].upper()
        if not (extn == 'PDF' or extn == 'CSV'):
            msg = extn + " not supported"
            toast(msg)
            return
        if len(self.characters) > 0:
            password = self.characters.pop()
            if extn == 'PDF':
                tryout.read_pdf(self.filePath, password)
            else:
                tryout.make_product_dict_from_csv(csv_file=self.filePath, password=password)
            self.screen_manager.add_widget(PnLScreen(name="NAV"))
            self.screen_manager.current = "NAV"
        else:
            toast('Document Password is required')

    def select_path(self, path):
        """It will be called when you click on the file name
        or the catalog selection button.
        :type path: str;
        :param path: path to the selected directory or file;
        """
        self.exit_manager()
        print(len(path))
        print(str(path))
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
        self.characters.append(str(text).upper())
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def build(self):
        return self.screen_manager


if __name__ == '__main__':
    Mark2MarketApp().run()
