import gspread
import pandas as pd

gc = gspread.oauth(
    credentials_filename='Credentials.json'
)

sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1m0qPA23PW2tQL1rrStTBrN9H1SpMvPg-Y-HiWd0FLcE/edit?usp=sharing")
dataframe = pd.DataFrame(sh.sheet1.get_all_records())
print(dataframe)


