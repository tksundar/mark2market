This project attempts to build a UI app to display net asset value of individual stocks in a portfolio and the total 
nav of the portfolio. Portfolio information can be entered by browsing to the path of a CSV file or XLSX
file of specified format. The format is as follows

isin/name,       quantity,       price,          side,

INE021A01026,            100,          2100,          BUY

If the ISIN is present, the portfolio is updated , else a new portfolio item is added and nav recalculated and displayed
If a name is given , its isin will be fetched.

In addition individual trade entry is also supported. View will refresh automatically when data changes. App restart is not required

I have not been able to package this for windows using pyinstaller. Packaging for android using buildozer has been completed.

In all, the following screens are available

1. Home : ![ScreenShot](/screenshots/home.jpg)
2. File upload : https://github.com/tksundar/mark2market/blob/master/screenshots/file_upload.jpg?raw=True
https://github.com/tksundar/mark2market/blob/master/screenshots/upload_popup.jpg?raw=True
3. Trade Entry : https://github.com/tksundar/mark2market/blob/master/screenshots/trade_entry.jpg?raw=True
4. Trade in markets
5. View Net Asset Value of portfolio and individual stocks
6. View gain loss of portfolio and individual stocks
7. View exposure chart with respect to net asset value
8. View exposure chart with respect to industry sectors
9. View  overall gain/loss of each stock 
10. View stock movement in the last trading session.

A few more enhancements are in the pipeline such as

1. Pressing a symbol on a datagrid will show live stock data of that symbol during trading hours
2. Add additional analytical charts, stock trends etc to enable trading.


