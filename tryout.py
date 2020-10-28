import os
import urllib
from urllib.error import HTTPError
from urllib.request import Request
from datetime import datetime
import csv
from zipfile import ZipFile
import tabula
from shutil import copyfile

d = datetime.now()
dd = str(int(d.strftime('%d')))
mm = d.strftime('%m')
yyyy = d.strftime('%y')

hrs = d.hour
if 0 < hrs < 17:
    dd = str(int(d.strftime('%d')) - 1)
date = dd + mm + yyyy

nse_equities_list_url = 'https://www1.nseindia.com/content/equities/EQUITY_L.csv'
nse_url = 'https://www1.nseindia.com/products/content/sec_bhavdata_full.csv'
bse_url = 'https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE_' + date + '.zip'
bse_csv_file = 'EQ_ISINCODE_' + date + '.CSV'
bse_canonical_file = "bse.csv"
bse_zip_file = 'bse.zip'
nse_isin_to_symbol_map: dict = {}
bse_isin_to_symbol_map: dict = {}
symbol_to_exchange_map: dict = {}
isin_to_name_map: dict = {}
nse_price_data: dict = {}
bse_price_data: dict = {}
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }

product_dict = {}


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


def convert_to_csv():
    csv_data = product_dict.values()
    a_dict = []
    for pf in csv_data:
        a_dict.append(pf.__dict__)

    with open('pandb.csv', 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file, fieldnames=a_dict[0].keys(), )
        fc.writeheader()
        fc.writerows(a_dict)


def make_product_dict(product_array):
    for pi in product_array:
        product_dict.update({pi.isin: pi})


def create_portfolio_item_dict(df):
    for row in df:
        pi = PortfolioItem()
        pi.isin = row["isin"]
        sym = nse_isin_to_symbol_map.get(pi.isin)
        pi.symbol = sym if sym else bse_isin_to_symbol_map.get(pi.isin)
        pi.name = isin_to_name_map.get(pi.isin)
        pi.quantity = float(row["quantity"])
        px = nse_price_data.get(pi.symbol)
        if px:
            pi.price = float(px)
        else:
            pi.price = float(bse_price_data.get(pi.isin))
            pi.exchange = "BSE"
        pi.cost = float(row["price"])
        nav, gain, percent = calculate_gain(pi.quantity, pi.cost, pi.price)
        pi.nav = nav
        pi.gain = gain
        pi.percent = percent
        product_dict.update({pi.isin: pi})
        convert_to_csv()


def read_pdf(input_file, password):
    product_array = []
    dfs = tabula.read_pdf(input_file, output_format='json', password=password, pages='all')
    for item in dfs:
        array_of_array = []
        list_items = item['data']
        for data in list_items:
            data_array = []
            for map_item in data:
                if len(map_item['text']) > 0:
                    data_array.append(map_item['text'])
            array_of_array.append(data_array)
        for prod in array_of_array:
            product = PortfolioItem()
            if prod[0].__contains__('ISINI'):
                product.isin = prod[0][4:]
                product.name = prod[1]
                product_array.append(product)
            elif len(prod) > 1 and prod[0].__contains__('Closing Balance'):
                product = product_array.pop()
                product.quantity = prod[1]
                product_array.append(product)
            elif len(prod) > 2 and prod[1].__contains__('Closing Balance'):
                product = product_array.pop()
                product.quantity = prod[2]
                product_array.append(product)

    for pi in product_array:
        symbol = nse_isin_to_symbol_map.get(pi.isin)
        if not symbol:
            symbol = bse_isin_to_symbol_map.get(pi.isin)
            pi.exchange = 'BSE'
        pi.symbol = symbol
        # price and nav
        if pi.exchange == 'NSE':
            price = float(nse_price_data.get(pi.symbol))
        else:
            print(pi.symbol)
            pr = bse_price_data.get(pi.isin)
            print(pi.symbol, pr, pi.isin)
            price = float(bse_price_data.get(pi.isin))

        nav = price * float(pi.quantity)
        pi.price = price
        pi.nav = round(nav, 2)
    make_product_dict(product_array)
    convert_to_csv()


def make_product_dict_from_csv(**kwargs):
    csvFile = kwargs['csv_file']
    usecols = ["isin", "quantity", "side", "price", "name"]
    df = read_csv(csvFile, usecols=usecols)
    for row in df:
        isin = row["isin"]
        if product_dict:
            pitem = product_dict[isin]
            if pitem:
                update_portfolio_item(row, pitem)
            else:
                make_new_portfolio_item(row)
        else:
            create_portfolio_item_dict(df)


def update_portfolio_item(row, pi):
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
    pi.cost = float(row["price"])
    net, gain, percent = calculate_gain(pi.quantity, pi.cost, pi.price)
    pi.nav = net
    pi.gain = gain
    pi.percent = percent
    convert_to_csv()


def make_new_portfolio_item(row):
    isin = row["isin"]
    pi = PortfolioItem()
    pi.isin = isin
    sym = nse_isin_to_symbol_map.get(isin)
    pi.symbol = sym if sym else bse_isin_to_symbol_map.get(isin)
    pi.symbol = isin_to_name_map.get(isin)
    pi.quantity = float(row["quantity"])
    pi.cost = float(row["price"])
    px = nse_price_data.get(pi.symbol)
    pi.price = float(px) if px else float(bse_price_data.get(pi.symbol))
    net, gain, percent = calculate_gain(pi.quantity, pi.cost, pi.price)
    pi.nav = net
    pi.gain = gain
    pi.percent = percent
    product_dict.update({isin: pi})
    convert_to_csv()


def calculate_gain(qty, cost, px):
    nav1 = cost * qty
    nav2 = px * qty
    gain = nav2 - nav1 if nav1 > 0 else 0
    percent = gain / nav1 if nav1 > 0 else 0
    return round(nav2, 2), gain, percent


def create_isin_to_symbol_map(df, isin_header, symbol_header, name_header, isin_symbol_map):
    for row in df:
        isin = row[isin_header]
        symbol = row[symbol_header]
        isin_symbol_map.update({isin: symbol})
        if not (isin in isin_to_name_map):
            isin_to_name_map.update({isin: row[name_header]})


def get_isin_to_symbol_map():
    if not os.path.exists('EQUITY_L.csv'):
        r = Request(nse_equities_list_url, None, headers)
        response = urllib.request.urlopen(r)
        with open('EQUITY_L.csv', "wb") as f:
            f.write(response.read())
    isin_header = ' ISIN NUMBER'
    symbol_header = 'SYMBOL'
    name_header = 'NAME OF COMPANY'
    df = read_csv('EQUITY_L.csv', usecols=['SYMBOL', ' ISIN NUMBER', 'NAME OF COMPANY'])
    create_isin_to_symbol_map(df, isin_header, symbol_header, name_header, nse_isin_to_symbol_map)
    if not os.path.exists('Equity.csv'):
        pass
        # get this dynamically
    df = read_csv('Equity.csv', usecols=['Security Id', 'ISIN No', 'Issuer Name'])
    symbol_header = 'Security Id'
    isin_header = 'ISIN No'
    name_header = 'Issuer Name'
    create_isin_to_symbol_map(df, isin_header, symbol_header, name_header, bse_isin_to_symbol_map)


def get_nse_prices():
    """Return a dict of Symbol to Close_Price"""
    # Fetch the csv file from NSE
    if os.path.exists('nse.csv'):
        os.remove('nse.csv')
    r = urllib.request.Request(nse_url, None, headers)
    response = urllib.request.urlopen(r)
    with open('nse.csv', "wb") as f:
        f.write(response.read())
    df = read_csv('nse.csv', usecols=['SYMBOL', ' CLOSE_PRICE'])
    for row in df:
        symbol = row["SYMBOL"]
        price = row[" CLOSE_PRICE"]
        nse_price_data.update({symbol: price})


def get_bse_prices():
    print(bse_url)
    msg = ''
    r = urllib.request.Request(bse_url, None, headers=headers)
    try:
        response = urllib.request.urlopen(r)
        # if os.path.exists(bse_csv_file):
        #     os.remove(bse_csv_file)
        # if os.path.exists(os.path.basename(bse_url)):
        #     os.remove(os.path.basename(bse_url))
        with open('bse.zip', "wb") as f:
            f.write(response.read())
        with ZipFile('bse.zip', 'r') as bse_zip:
            bse_zip.printdir()
            bse_zip.extractall()
            copyfile(bse_csv_file, bse_canonical_file)
            os.remove(bse_csv_file)
    except HTTPError:
        msg = 'BSE price file not available now. Using last available price file'
        print(msg)
    df = read_csv(bse_canonical_file, usecols=['ISIN_CODE', 'LAST'])
    print("Getting prices for symbols")
    for row in df:
        isin = row["ISIN_CODE"]
        price = row["LAST"]
        bse_price_data.update({isin: price})
    os.remove('bse.zip')
    return msg


def read_csv(fileName, **kwargs):
    """return a list of dictionaries  keyed by the header """
    df = []
    usecols = kwargs["usecols"]

    with open(fileName, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data = {}
            for header in usecols:
                if header in row:
                    data[header] = row[header]
            df.append(data)

    return df
