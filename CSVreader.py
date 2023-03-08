# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# # Define the scope of the credentials
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# # Set up the credentials
# creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

# # Authenticate with the Google Sheets API
# client = gspread.authorize(creds)

# # Open the Google Sheets file by its name
# sheet = client.open("Example Spreadsheet").sheet1

# # Get all values from the sheet
# data = sheet.get_all_values()
data = "Hola mundo"
# Print the data
print(data)