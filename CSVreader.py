import gspread

gc = gspread.oauth(
    credentials_filename='Credentials.json'
)

sh = gc.open("Example spreadsheet")

print(sh.sheet1.get('B1'))


