"""
Created by Sundar on 11-11-2020.email tksrajan@gmail.com
"""
import platform

from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.metrics import dp, cm
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


class DataGrid(GridLayout):

    def __init__(self, colData, rowData, colWidth, **kwargs):
        cols = 0
        rows = 0
        if 'rows' in kwargs:
            rows = kwargs.pop('rows')
        if 'cols' in kwargs:
            cols = kwargs.pop('cols')
        super().__init__(**kwargs)
        plt = platform.system()
        if plt == 'Windows':
            self.padding = [100, 100, 100, 100]
            self.pos_hint = {'center_x': .6, 'center_y': .5}
        else:
            self.padding = [200, 200, 200, 200]
            self.pos_hint = {'center_x': .5, 'center_y': .5}
        if rows > 0 and cols > 0 or rows == 0:
            self.cols = cols
        elif rows > 0:
            self.rows = rows

        for col in colData:
            col.size_hint = None, None
            if plt == 'Windows':
                 col.height = dp(40)
                 col.width = dp(colWidth)
            else:
                col.height = dp(80)
                col.width = dp(15)
            self.add_widget(col)

        for rows in rowData:
            for index, row in enumerate(rows):
                row.size_hint = None, None
                row.height = 40
                row.width = dp(colWidth)
                row.line_height = 2
                row.halign = 'center'
                if row.text.isnumeric():
                    row.halign = 'right'
                row.valign = 'middle'
                self.add_widget(row)
        self.row_data = rowData
        self.col_data = colData
        # with self.canvas.before:
        #     Color(1, 1, 1, 1)
        #     self.rect = Rectangle(size=self.size,
        #                           pos=self.pos)
        # self.bind(pos=self.update_rect, size=self.update_rect)


    # def update_rect(self):
    #     self.rect.pos = self.pos
    #     self.rect.size = self.size
#
# class TestApp(App):
#
#     def build(self):
#         label1 = Label(text='[b][size=20]Name[/size][/b]', markup=True)
#
#         label2 = Label(text='[b][size=20]Quantity[/size][/b]', markup=True)
#
#         label3 = Label(text='[b][size=20]Price[/size][/b]', markup=True)
#
#         label4 = Label(text='[b][size=20]NAV[/size][/b]', markup=True)
#
#         colData = [label1, label2, label3, label4]
#
#         import tryout
#         tryout.init(updated=True)
#         data = list(tryout.product_dict.values())
#         row_data = []
#         for p in data:
#             nl = Label(text='[size=10]'+p.symbol+'[/size]', markup=True)
#             ql = Label(text='[size=10]'+str(p.quantity)+'[/size]', markup=True)
#             nav = str(p.nav)
#             price = str(p.price)
#
#             if p.symbol in tryout.nse_price_data:
#                 #price = str(tryout.get_live_price(p.symbol))
#                 close = float(tryout.nse_price_data.get(p.symbol))
#                 pre_close = float(tryout.nse_prev_price_data.get(p.symbol))
#                 if close > pre_close:
#                     nav = '[color=00FF00][size=15]' + nav + '[/size][/color]'
#
#                 else:
#                     nav = '[color=FF0000][size=15]' + nav + '[/size][/color]'
#
#                 if p.price > close:
#                     price = '[color=00FF00][size=15]' + price + '[/size][/color]'
#                 else:
#                     price = '[color=FF0000][size=15]' + price + '[/size][/color]'
#
#             pl = Label(text=price, markup=True)
#             nal = Label(text=nav, markup=True)
#             row = [nl, ql, pl, nal]
#             row_data.append(row)
#
#
#         datagrid = DataGrid(colData, row_data, 100, cols=4, )
#
#         return datagrid
#
#
# if __name__ == '__main__':
#     TestApp().run()
