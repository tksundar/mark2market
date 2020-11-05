This project attempts to build a UI app to display net asset value of individual stocks in a portfolio and the total 
nav of the portfolio. Portfolio information can be entered by browsing to the path of a CSV file or PDF
file of specified format. While pdf file support is currently available for a specific format that is
provided by M/S Integrated Enterprises (India) Private Limited - Depository Division, CSV file format is
generic as follows

isin,       quantity,       price,          side,

INE021A01026,            100,          2100,          BUY

If the ISIN is present, the portfolio is updated , else a new portfolio item is added and nav recalculated and displayed

kivy/kivyMD datatables do not seem to have auto refresh capability based on how the model changes So at present, the
app needs to be restarted for the changes to reflect.

This is still very rudimentary. I have not been able to package this for windows using pyinstaller. Packaging for
android using buildozer has been completed.

The application has 10 screens, displaying various aspects of a portfolio abd facilitating transaction inputs.
As of now, it is almost fully functional. A few more embellishments are required such as

1. Pressing a symbol on a datagrid will show live stock data of that symbol during trading hours
2. Add additional analytical charts, stock trends etc to enable trading.


