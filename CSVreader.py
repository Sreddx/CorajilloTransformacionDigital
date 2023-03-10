import gspread
import pandas as pd
import psycopg2

gc = gspread.oauth(
    credentials_filename='Credentials.json'
)
#SH es la hoja en la que estamos trabajando
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1m0qPA23PW2tQL1rrStTBrN9H1SpMvPg-Y-HiWd0FLcE/edit?usp=sharing")
data = sh.sheet1.get_all_records()
df = pd.DataFrame(data)
worksheet_name = "Materia Prima" #Se debe cambiar a que lea el nombre de la hoja que esta siendo leida

#Quitamos los signos de dinero para facilitar manipulacion de datos
df['COSTO'] = df['COSTO'].str.replace('$', '').str.replace(',', '')
df['TOTAL ($)'] = df['TOTAL ($)'].str.replace('$', '').str.replace(',', '')

#Convertirmos columnas de dinero a float
df['COSTO'] = df['COSTO'].astype(float)
df['TOTAL ($)'] = df['TOTAL ($)'].astype(float)

#print(df)
worksheet_list = sh.worksheets()
print(worksheet_list)
#Cambiamos el nombre de las columnas del Df para que al insertar a la base de datos sea mas sencillo.
df = df.rename(columns={
    'GAMA': 'Gama',
    'ARTICULO-DESCRIPCION': 'Articulo_Descripcion',
    'FOTO': 'Foto',
    'COSTO': 'Costo',
    'PIEZAS': 'Piezas',
    'TOTAL ($)': 'Total'
})



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
cur.execute("DROP TABLE IF EXISTS inventario;")

# Creamos el esquema
cur.execute('''
    CREATE TABLE inventario (
        id SERIAL PRIMARY KEY,
        Tipo VARCHAR(20), 
        Gama VARCHAR(255),
        Articulo_Descripcion VARCHAR(255),
        Foto VARCHAR(255),
        Costo DECIMAL(10,2),
        Piezas INTEGER,
        Total DECIMAL(10,2)
    );
''')
# AÑADIR ESTO A TIPO YA QUE SE PUEDA LEER EL NOMBRE DE LA HOJA NOT NULL CHECK (Tipo IN ('MATERIA PRIMA', 'PROCESO', 'SABORES Y COLORES', 'PRODUCTO TERMINADO'))
# Rellenamos la base de datos 

for i, row in df.iterrows():
    cur.execute("""
        INSERT INTO inventario (Gama, Articulo_Descripcion, Foto, Costo, Piezas, Total)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (row['Gama'], row['Articulo_Descripcion'], row['Foto'], row['Costo'], row['Piezas'], row['Total']))

# Subir los cambios a la base de datos
conn.commit()

# Extraer los datos de la base de datos
cur.execute("SELECT * FROM inventario")

# extraemos los datos del objeto cur
dfB = pd.read_sql('SELECT * FROM Inventario', conn)

conn.close()


