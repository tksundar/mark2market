"""
Created by Sundar on 24-12-2020.email tksrajan@gmail.com
"""
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager

kv = """MDRectangleFlatIconButton:
        id: file_chooser
        text: "Choose a transaction file"
        icon: "folder"
        size_hint: 0.8,0.1
        pos_hint: { 'center_x': 0.5,'center_y': 0.8 }
        on_release: app.file_manager_open()
"""


class FileApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )

        self.file_manager.ext = ['.csv', '.CSV', '.xlsx', '.XLSX']

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""
        self.manager_open = False
        self.file_manager.close()

    def select_path(self, path):
        """It will be called when you click on the file name
        or the catalog selection button.
        :type path: str;
        :param path: path to the selected directory or file;
        """
        self.exit_manager()
        self.root.get_screen(self.root.current).ids.file_chooser.text = path
        self.filePath = path

    def file_manager_open(self):
        self.file_manager.show('/')  # output manager to the screen
        self.manager_open = True

    def build(self):
        return Builder.load_string(kv)


if __name__ == '__main__':
    FileApp().run()
