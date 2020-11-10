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

1. Home : <p><img src="/screenshots/home.jpg?raw=true" width="500" height="800" /></p>
2. File upload : <p><img src="/screenshots/file_upload.jpg?raw=true" width="500" height="800" /></p>
   a) File upload help : <p><img src="/screenshots/upload_popup.jpg?raw=true" width="500" height="800" /></p>
3. Trade Entry : <p><img src="/screenshots/trade_entry.jpg?raw=true" width="500" height="800" /></p>
4. Trade in markets: <p><img src="/screenshots/trade_markets.jpg?raw=true" width="500" height="800" /></p>
5. View Net Asset Value of portfolio and individual stocks:<p><img src="/screenshots/nav_screen.jpg?raw=true" width="500" height="800" /></p>
6. View gain loss of portfolio and individual stocks:<p><img src="/screenshots/gain_loss.jpg?raw=true" width="500" height="800" /></p>
7. View exposure chart with respect to net asset value:<p><img src="/screenshots/nav_plot.jpg?raw=true" width="500" height="800" /></p>
8. View exposure chart with respect to industry sectors:<p><img src="/screenshots/sector_plot.jpg?raw=true" width="500" height="800" /></p>
9. View  overall gain/loss of each stock: <p><img src="/screenshots/gain_loss_plot.jpg?raw=true" width="500" height="800" /></p>
10. View stock movement in the last trading session: <p><img src="/screenshots/movement.jpg?raw=true" width="500" height="800" /></p>
11. Real time data for a stock : <p><img src="/screenshots/real_time_price.jpg?raw=true" width="500" height="800" /></p>

A few more enhancements are in the pipeline such as

Add additional analytical charts, stock trends etc to enable trading.

The project is written in python 3.8. It uses the Kivy UI framework and also uses some components from the 
KivyMD project, notably the datagrid and filemanager. The datagrid is still evolving, so more features will be 
introduced as and when they are available( ability to stile the row cells  individually, adding widgets to
cells etc). In addition, the project uses pandas and matplotlib for generating charts.


