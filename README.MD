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

This is still very rudimentary. I have not been able to package this for windows using pyinstaller or android using buildozer
pyinstaller doesnt package kivyMD dependency and buildozer has gotchas when it comes to packaging
pandas(actually it fails when applying some numpy patch while build). It is quite possible that these are problems due to 
my lack of understanding of the packaging process. I will update this page as and when there is progress.
