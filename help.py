"""
Created by Sundar on 30-10-2020.email tksrajan@gmail.com
"""
from kivy.uix.label import Label
from kivy.uix.popup import Popup


def get_content():
    text = '''
          Upload only csv files.Use the following format for csv files.
       
          name,quantity,cost,side,
          ------------------------------------------------------------------------
          GRANULES INDIA LIMITED,4720,96.4095,BUY,
          IN9155A01020,3663,212.33,SELL,

          Or like this . This is preferred
          
          isin,quantity,cost,side,
          --------------------------------------------------------------------
          IN9155A01020,3663,212.33,SELL,
          
          Short sell is not supported and  will reduce quantity to zero

          cost is the price at which the stock is bought or sold.
          
          
          *press anywhere outside this screen to dismiss.
          '''
    label = Label(text=text)
    return label





class HelpScreen(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Instructions on Transaction file'
        self.content = get_content()
        self.size_hint = (.6,.8)


