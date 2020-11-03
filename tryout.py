import csv
import os
import ssl
import urllib
import webbrowser
from datetime import datetime
from shutil import copyfile
from urllib.error import HTTPError
from urllib.request import Request
from zipfile import ZipFile

from kivy.uix.label import Label
from kivy.uix.popup import Popup


def get_date_string():
    d = datetime.now()
    dd = str(int(d.strftime('%d')))
    mm = d.strftime('%m')
    yyyy = d.strftime('%y')
    if d.day < 10:
        dd = '0' + dd
    hrs = d.hour

    if 0 < hrs < 17:
        dd = str(int(d.strftime('%d')) - 1)
        if d.day < 10:
            dd = '0' + dd
    return dd + mm + yyyy


date = get_date_string()

nse_equities_list_url = 'http://www1.nseindia.com/content/equities/EQUITY_L.csv'
nse_url = 'http://www1.nseindia.com/products/content/sec_bhavdata_full.csv'
bse_url = 'http://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE_' + date + '.zip'
bse_csv_file = 'EQ_ISINCODE_' + date + '.CSV'
bse_canonical_file = "bse.csv"
bse_zip_file = 'bse.zip'
nse_isin_to_symbol_map: dict = {}
bse_isin_to_symbol_map: dict = {}
bse_symbol_to_isin_map: dict = {}
nse_symbol_to_isin_map: dict = {}
symbol_to_exchange_map: dict = {}
isin_to_name_map: dict = {}
name_to_isin_map: dict = {}
nse_price_data: dict = {}
bse_price_data: dict = {}
product_dict = {}
symbol_product_dict = {}
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }
popup = None
nav_name = 'NAV'


class PortfolioItem:

    def __init__(self):
        self.isin = ''
        self.symbol = ''
        self.name = ''
        self.quantity = 0.0
        self.cost = 0.0
        self.price = 0.0
        self.nav = 0.0
        self.gain = 0.0
        self.percent = 0.0
        self.exchange = 'NSE'

    def __str__(self):
        return str(self.__dict__)


def init():
    if len(nse_price_data) == 0:
        get_nse_prices()
    if len(bse_price_data)  == 0:
        get_bse_prices()
    if len(nse_isin_to_symbol_map) == 0:
        get_isin_to_symbol_map()
    if os.path.exists('csv/pandb.csv'):
        if len(product_dict) == 0:
            make_product_dict_from_csv(csv_file='csv/pandb.csv')


def convert_to_csv():
    csv_data = product_dict.values()
    a_dict = []
    for pf in csv_data:
        a_dict.append(pf.__dict__)

    with open('csv/pandb.csv', 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file, fieldnames=a_dict[0].keys(), )
        fc.writeheader()
        fc.writerows(a_dict)


def get_pf_nav():
    pf_nav = 0
    for pi in list(product_dict.values()):
        pf_nav += pi.nav
    return pf_nav


def create_portfolio_item_dict(df, isin):
    for row in df:
        pi = PortfolioItem()
        pi.isin = isin
        sym = nse_isin_to_symbol_map.get(pi.isin)
        pi.symbol = sym if sym else bse_isin_to_symbol_map.get(pi.isin)
        pi.name = isin_to_name_map.get(pi.isin)
        q = row['quantity']
        pi.quantity = float(q)
        price = nse_price_data.get(pi.symbol)
        if not (price is None):
            pi.price = float(price)
        else:
            pi.price = float(bse_price_data.get(pi.isin))
            pi.exchange = "BSE"
        pi.cost = float(row["cost"])
        update_gain(pi)
        product_dict.update({pi.isin: pi})


def make_product_dict_from_csv(**kwargs):
    csvFile = kwargs['csv_file']
    usecols = ["isin", "quantity", "side", "cost", "price", "name"]
    df = read_csv(csvFile, usecols=usecols)
    for row in df:
        isin = ""
        if "isin" in row:
            isin = row["isin"]
        elif "name" in row:
            isin = name_to_isin_map.get(row['name'])
            if row['name'] in nse_isin_to_symbol_map or row['name'] in bse_isin_to_symbol_map:
                isin = row['name']
        if not isin:
            print(row)
            raise AttributeError("Could not find isin for %s", row["name"])
        if isin in product_dict:
            p_item = product_dict[isin]
            update_portfolio_item(row, p_item)
        else:
            make_new_portfolio_item(row, isin)

    convert_to_csv()


def update_portfolio_item(row, pi, **kwargs):
    if not (row is None):
        if 'name' in row:
            pi.name = row['name']
        else:
            pi.name = isin_to_name_map.get(row['isin'])
        qty = float(row["quantity"])
        if "side" in row:
            side = row["side"]
            if side == 'BUY':
                pi.quantity += qty
            else:
                if pi.quantity >= qty:
                    pi.quantity -= qty
                else:
                    pi.quantity = 0.0
        else:
            pi.quantity = qty
        pi.cost = float(row["cost"])
        update_price(pi)
        update_gain(pi)
    else:
        update_or_create_portfolio_item(**kwargs)


def update_price(pi: PortfolioItem):
    px = nse_price_data.get(pi.symbol)
    if not (px is None):
        pi.price = float(px)
    else:
        isn = pi.isin
        px = bse_price_data.get(isn)
        if px:
            pi.price = float(bse_price_data.get(isn))


def update_or_create_portfolio_item(**kwargs):
    symbol = kwargs['symbol']
    if symbol in symbol_product_dict:
        pi = symbol_product_dict.get(symbol)
        side = kwargs['side']
        quantity = float(kwargs['quantity'])
        cost = float(kwargs['cost'])
        if side == 'BUY':
            pi.cost = (pi.quantity * pi.cost + quantity * cost) / (pi.quantity + quantity)
            pi.quantity += quantity
        else:
            pi.cost = (pi.quantity * pi.cost - quantity * cost) / (pi.quantity + quantity)
            pi.quantity -= quantity
    else:
        pi = PortfolioItem()
        pi.symbol = symbol
        pi.quantity = float(kwargs['quantity'])
        pi.cost = float(kwargs['cost'])
        isin = nse_symbol_to_isin_map.get(pi.symbol)
        if isin is None:
            isin = bse_symbol_to_isin_map.get(pi.symbol)
        pi.isin = isin
        price = nse_price_data.get(pi.symbol)
        if price is None:
            price = bse_price_data.get(bse_symbol_to_isin_map.get(pi.symbol))
            if not (price is None):
                pi.price = float(price)
        else:
            pi.price = float(price)
        update_gain(pi)
        product_dict.update({pi.isin: pi})
        symbol_product_dict.update({pi.symbol: pi})
        print('processed %d symbols ' % len(symbol_product_dict))


def make_new_portfolio_item(row, isin, **kwargs):
    pi = PortfolioItem()
    if not (row is None):
        pi.isin = isin
        name = isin_to_name_map.get(isin)
        pi.name = name
        sym = nse_isin_to_symbol_map.get(isin)
        if not (sym is None):
            pi.symbol = sym
        else:
            pi.symbol = bse_isin_to_symbol_map.get(isin)
        pi.quantity = float(row["quantity"])
        pi.cost = float(row["cost"])
        update_price(pi)
        update_gain(pi)
        product_dict.update({isin: pi})
        symbol_product_dict.update({pi.symbol: pi})
    else:
        update_or_create_portfolio_item(**kwargs)


def update_gain(pi):
    nav1 = pi.cost * pi.quantity
    nav2 = pi.price * pi.quantity
    gain = nav2 - nav1 if nav1 > 0 else 0
    percent = gain / nav1 if nav1 > 0 else 0
    pi.nav = round(nav2, 2)
    pi.gain = round(gain, 2)
    pi.percent = round(percent, 2)


def create_isin_to_symbol_map(df, isin_header, symbol_header, name_header, isin_symbol_map, symbol_isin_map):
    for row in df:
        isin = row[isin_header]
        symbol = row[symbol_header]
        name = row[name_header].upper().replace('LTD', 'LIMITED')
        if name.__contains__('.-$'):
            ind = name.index('.-$')
            name = name[0:ind].strip()
        isin_symbol_map.update({isin: symbol})
        symbol_isin_map.update({symbol: isin})
        if not (isin in isin_to_name_map):
            isin_to_name_map.update({isin: name})
        name_to_isin_map.update({name: isin})


def get_isin_to_symbol_map():
    print('getting isin to symbol map...')
    context = ssl.SSLContext()
    if not os.path.exists('csv/EQUITY_L.csv'):
        r = Request(nse_equities_list_url, None, headers)
        response = urllib.request.urlopen(r, context=context)
        with open('csv/EQUITY_L.csv', "wb") as f:
            f.write(response.read())
    isin_header = ' ISIN NUMBER'
    symbol_header = 'SYMBOL'
    name_header = 'NAME OF COMPANY'
    df = read_csv('csv/EQUITY_L.csv', usecols=['SYMBOL', ' ISIN NUMBER', 'NAME OF COMPANY'])
    create_isin_to_symbol_map(df, isin_header, symbol_header, name_header, nse_isin_to_symbol_map,
                              nse_symbol_to_isin_map)
    if not os.path.exists('csv/Equity.csv'):
        pass
        # get this dynamically
    df = read_csv('csv/Equity.csv', usecols=['Security Id', 'ISIN No', 'Security Name'])
    symbol_header = 'Security Id'
    isin_header = 'ISIN No'
    name_header = 'Security Name'
    create_isin_to_symbol_map(df, isin_header, symbol_header, name_header, bse_isin_to_symbol_map,
                              bse_symbol_to_isin_map)

    print('finished getting isin to symbol map')


def get_delete_file(date_str, file_name):
    _30_day_months = {4: 4, 6: 5, 9: 9, 11: 11}
    _28_day_month = {2: 2}
    day = int(date_str[:2])
    month = int(date_str[2:4])
    year = date[-2:]
    dd = day - 1
    mm = month - 1
    if dd == 0:
        dd = 31
        if mm == 0:
            mm = 12
        if mm in _30_day_months:
            dd = 30
        elif mm in _28_day_month:
            dd = 28  # good for 4 years
    pre_date = str(dd) + str(mm) + year
    print(pre_date)
    return pre_date + '_' + file_name


def get_nse_prices():
    """Return a dict of Symbol to Close_Price"""
    # Fetch the csv file from NSE
    print('getting fresh nse price data')
    day = get_date_string()
    nse_path = day + "_nse.csv"
    file_date = nse_path[:6]
    if day != file_date or not (os.path.exists(nse_path)):
        print('date changed. getting fresh nse price data')
        delete_file = get_delete_file(day, 'nse.csv')
        if os.path.exists(delete_file):
            os.remove(delete_file)
        context = ssl.SSLContext()
        r = urllib.request.Request(nse_url, None, headers)
        response = urllib.request.urlopen(r, context=context)
        with open(nse_path, "wb") as f:
            f.write(response.read())
    df = read_csv(nse_path, usecols=['SYMBOL', ' CLOSE_PRICE'])
    for row in df:
        symbol = row["SYMBOL"]
        price = row[" CLOSE_PRICE"]
        nse_price_data.update({symbol: price})
    print('finished getting nse price data')


def get_content():
    global popup
    p = Popup()
    label = Label()
    text = '''
            BSE prices are not available now.
            Possibly b/c it is a holiday.
            
            Or may beb/c you are running 
            this app for the first time on 
            a market holiday
            
            If your holdings have BSE only 
            stocks, the NAV will be off. 
            
            This will resolve itself after
            17:00 hrs on the next trading
            day
    '''
    label.text = text
    p.content = label
    p.size_hint = (0.8, 0.8)
    popup = p


def get_bse_prices():
    print('getting bse prices')
    day = get_date_string()
    bse_file = day + "_bse.csv"
    file_date = bse_file[:6]
    if day != file_date or not (os.path.exists(bse_file)):
        print(' date changed. getting fresh bse prices')
        context = ssl.SSLContext()
        print(bse_url)
        r = urllib.request.Request(bse_url, None, headers=headers)
        try:
            response = urllib.request.urlopen(r, context=context)
            with open('bse.zip', "wb") as f:
                f.write(response.read())
            with ZipFile('bse.zip', 'r') as bse_zip:
                bse_zip.printdir()
                bse_zip.extractall()
                copyfile(bse_csv_file, bse_file)
                os.remove(bse_csv_file)
            delete_file = get_delete_file(day, 'bse_csv')
            if os.path.exists(delete_file):
                os.remove(delete_file)
        except HTTPError:
            msg = 'BSE price file not available now. Using last available price file'
            print(msg)

    df = read_csv(bse_file, usecols=['ISIN_CODE', 'LAST'])
    print("Getting prices for symbols")
    for row in df:
        isin = row["ISIN_CODE"]
        price = row["LAST"]
        bse_price_data.update({isin: price})

    if os.path.exists('bse.zip'):
        os.remove('bse.zip')
    print('finished getting bse price data')


def read_csv(fileName, **kwargs):
    """return a list of dictionaries  keyed by the header """
    df = []
    usecols = kwargs["usecols"]
    print(fileName)
    with open(fileName, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data = {}

            for header in usecols:
                if header in row:
                    val = row[header]
                    data[header] = val
            df.append(data)

    return df


def update_portfolio(symbol, qty, cost, side):
    if symbol in symbol_product_dict:
        update_portfolio_item(None, None, symbol=symbol, quantity=qty, cost=cost, side=side)
    else:
        # new symbol
        make_new_portfolio_item(None, None, symbol=symbol, quantity=qty, cost=cost, side=side)
    convert_to_csv()

    return True


def open_url(broker):
    url = ''
    if broker == 'HDFC Securities':
        url = 'https://ntrade.hdfcsec.com/?utm_source=netcore&utm_medium=emailer&utm_campaign=birthday&utm_content=manage'
    elif broker == 'ICICI Direct':
        url = 'https://secure.icicidirect.com/IDirectTrading/customer/login.aspx'
    webbrowser.open(url)
