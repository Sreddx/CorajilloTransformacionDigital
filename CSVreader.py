import gspread
import pandas as pd
import psycopg2

gc = gspread.oauth(
    credentials_filename='Credentials.json'
)

sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1m0qPA23PW2tQL1rrStTBrN9H1SpMvPg-Y-HiWd0FLcE/edit?usp=sharing")
df = pd.DataFrame(sh.sheet1.get_all_records())
# Nos conectamos a la base de datos utilizando las credenciales.
# Connect to an existing database
conn = psycopg2.connect(
    host="pg.pg4e.com",
    port=5432,
    database="pg4e_d5cf41ba12", 
    user="pg4e_d5cf41ba12",
    password="pg4e_p_34432ea43bce4f4")

# Abrimos un cursor para realizar operaciones en la base de datos
cur = conn.cursor()


# Antes de crear la base de datos, borramos la base de datos en caso de que exista
try:
    cur.execute("DROP TABLE corajillo;")
except:
    pass

# Creamos el esquema
cur.execute(
    "CREATE TABLE corajillo(id INTEGER, nombre VARCHAR(128), cantidad VARCHAR(128), cliente VARCHAR(128));"
)

# Rellenamos la base de datos 

for i in range(len(df)):
    cur.execute("INSERT INTO corajillo (id, nombre, cantidad, cliente) VALUES (%s, %s, %s, %s)", 
                (int(df.iloc[i,0]), str(df.iloc[i,1]), int(df.iloc[i,2]), str(df.iloc[i,3])))

# Subir los cambios a la base de datos
conn.commit()

# Extraer los datos de la base de datos
cur.execute("SELECT * FROM corajillo")

# extraemos los datos del objeto cur
db_data = cur.fetchall()


print(db_data)


