# """
# Created by Sundar on 30-10-2020.email tksrajan@gmail.com
# """
# import os
#
# import matplotlib.pyplot as plt
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.image import Image
# from kivy.uix.screenmanager import Screen, ScreenManager
# from kivymd.uix.button import MDRaisedButton
#
# import tryout
#
#
# def get_plot_data():
#     labels = []
#     navs = []
#     for pf in list(tryout.product_dict.values()):
#         labels.append(pf.symbol)
#         navs.append(pf.nav)
#     return labels, navs
#
#
# def get_gains_data():
#     names = []
#     gains = []
#
#     for pf in list(tryout.product_dict.values()):
#         names.append(pf.symbol)
#         gains.append(round(pf.gain, 2))
#
#     return names, gains
#
#
# class Analysis(Screen):
#     def __init__(self, screen_manager, **kwargs):
#         super().__init__(**kwargs)
#         tryout.get_nse_prices()
#         tryout.get_bse_prices()
#         tryout.get_isin_to_symbol_map()
#         if os.path.exists('csv/pandb.csv'):
#             tryout.make_product_dict_from_csv(csv_file='csv/pandb.csv')
#
#         self.screen_manager = screen_manager
#         self.labels, self.data = get_plot_data()
#
#         fig, ax = plt.subplots()
#         ax.pie(self.data, labels=self.labels, autopct='%1.1f%%',
#                shadow=True, startangle=90)
#         ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
#
#         plt.savefig('nav.png')
#         layout = FloatLayout()
#         img = Image(source='nav.png')
#         layout.add_widget(img)
#
#
#         # back_btn = MDRaisedButton(text="Back", size_hint=(None, None), size=(100, 50),
#         #                           pos_hint={'center_x': 0.5, 'center_y': 0.05}, elevation=10)
#         # back_btn.md_bg_color = (.2, .2, .2, 1)
#         # back_btn.bind(on_press=self.go_back)
#         # layout.add_widget(back_btn)
#         #
#         # self.add_widget(layout)
#
#     def go_back(self,instance):
#         self.screen_manager.current = 'GainLoss'
#
#         # # names, gains = get_gains_data()
#         # names = ['GRANULES', 'CDSL', 'INDOCO', 'NUCLEUS', 'BAJAJCON', 'MAYURUNIQ', 'TIIL', 'EXPLEOSOL', 'GRAUWEIL']
#         #
#         # gains = [1347279.16, 446419.52, 126257.92, 181252.87, -264910.15, 17668.11, -113767.7, 24125.02, -96285.66]
#         # import numpy as np
#         # # Make a fake dataset:
#         # height = [3, 12, 5, 18, 45]
#         # bars = ('A', 'B', 'C', 'D', 'E')
#         # y_pos = np.arange(len(bars))
#         #
#         # # Create bars
#         # plt.bar(y_pos, height)
#         #
#         # # Create names on the x-axis
#         # plt.xticks(y_pos, bars)
#         #
#         # # Show graphic
#         # plt.show()
#
#
# if __name__ == '__main__':
#     Analysis(ScreenManager())
