import gspread
import pandas as pd
import psycopg2

def get_spreadsheet_data(credentials_filename, url):
    gc = gspread.oauth(credentials_filename='Credentials.json')
    sh = gc.open_by_url(url)
    sheets = sh.worksheets()

    dfs = {}
    for sheet in sheets:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Limpiamos los datos de la hoja
        clean_dataframe(df)

        dfs[sheet.title] = df
    
    return dfs

def clean_dataframe(df):
    # Cambiamos el nombre de las columnas para que hagan match con la base de datos
    if 'PIEZAS' in df.columns:
        df.rename(columns={
            'GAMA': 'Gama',
            'ARTICULO-DESCRIPCION': 'Articulo_Descripcion',
            'FOTO': 'Foto',
            'COSTO': 'Costo',
            'PIEZAS': 'Piezas',
            'TOTAL ($)': 'Total'
        }, inplace=True)
    else:
        df.rename(columns={
            'GAMA': 'Gama',
            'ARTICULO-DESCRIPCION': 'Articulo_Descripcion',
            'FOTO': 'Foto',
            'COSTO': 'Costo',
            'TARIMAS': 'Tarimas',
            'TOTAL ($)': 'Total'
        }, inplace=True)
    
    # Quitamos los signos de dinero para facilitar manipulacion de datos
    if df['Costo'].dtype == 'object':
        df['Costo'] = df['Costo'].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    if df['Total'].dtype == 'object':
        df['Total'] = df['Total'].str.replace('$', '',regex=False).str.replace(',', '', regex=False)

    #Convertimos columnas de dinero a float
    df['Costo'] = df['Costo'].astype(float)
    df['Total'] = df['Total'].astype(float)

    

def create_database_table(conn):
    cur = conn.cursor()

    # Antes de crear la base de datos, borramos la tabla en caso de que exista
    cur.execute("DROP TABLE IF EXISTS inventario;")

    # Creamos la tabla
    cur.execute('''
        CREATE TABLE inventario (
            id SERIAL PRIMARY KEY,
            Tipo VARCHAR(20),
            Gama VARCHAR(255),
            Articulo_Descripcion VARCHAR(255),
            Foto VARCHAR(255),
            Costo DECIMAL(10,2),
            Piezas INTEGER,
            Tarimas FLOAT,
            Total DECIMAL(10,2)
        );
    ''')

    conn.commit()
    cur.close()

def populate_database_table(conn, df,tipo):
    cur = conn.cursor()

    for _, row in df.iterrows():
        if 'Tarimas' not in df.columns:
            cur.execute("""
                INSERT INTO inventario (Tipo, Gama, Articulo_Descripcion, Foto, Costo, Piezas, Total)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (tipo, row['Gama'], row['Articulo_Descripcion'], row['Foto'], row['Costo'], row['Piezas'], row['Total']))
        else:
            cur.execute("""
                INSERT INTO inventario (Tipo, Gama, Articulo_Descripcion, Foto, Costo, Tarimas, Total)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (tipo, row['Gama'], row['Articulo_Descripcion'], row['Foto'], row['Costo'], row['Tarimas'], row['Total']))

    conn.commit()
    cur.close()

def read_database_table(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventario")
    df = pd.read_sql('SELECT * FROM Inventario', conn)
    cur.close()

    return df

def main():
    credentials_filename = 'Credentials.json'
    url = 'https://docs.google.com/spreadsheets/d/1m0qPA23PW2tQL1rrStTBrN9H1SpMvPg-Y-HiWd0FLcE/edit?usp=sharing'
    
    #Obtenemos informacion del Google Sheet
    dfs = get_spreadsheet_data(credentials_filename, url)
    #Limpiamos los datos
    for df in dfs:
        clean_dataframe(dfs[df])
    
    #print(dfs['Materia Prima'])
    #Conectamos a la base de datos
    conn = psycopg2.connect(
        host="pg.pg4e.com",
        port=5432,
        database="pg4e_d5cf41ba12", 
        user="pg4e_d5cf41ba12",
        password="pg4e_p_34432ea43bce4f4"
    )

    #Creamos la tabla en la base de datos
    create_database_table(conn)

    #Llenamos la tabla con los datos del Google Sheet
    for df in dfs:
        #add name of data frame to third argument

        populate_database_table(conn, dfs[df],df)
    
    #Leemos la tabla de la base de datos
    df = read_database_table(conn)
    print(df.head())

if __name__ == '__main__':
    main()
    
    