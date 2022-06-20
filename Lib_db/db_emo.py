import mysql.connector as mysql
from mysql.connector.cursor_cext import CMySQLCursorDict as Cursor
from mysql.connector.connection_cext import CMySQLConnection as Connection
from mysql.connector import errorcode
import pandas as pd


# Functie met alle parameters om binnen te kunnen loggen in database (standaardwaarden ingevuld)
def get_config(user: str = 'py_dennis', password: str = 'LAJNVeXkMR0X', host: str = '185.115.218.166',
               database: str = 'py_dennis', raise_on_warnings: bool = True) -> dict:
    return {
        'user': user,
        'password': password,
        'host': host,
        'database': database,
        'raise_on_warnings': raise_on_warnings
    }


# Functie dat verbinding maakt met een database
def db_load() -> (Connection, Cursor):
    config = get_config()
    cnx = mysql.connect(**config)
    cursor = cnx.cursor(dictionary=True)

    return cnx, cursor


# Functie om de verbinding met database weer af te breken
def db_disconnect(cnx: Connection, cursor: Cursor) -> None:
    cursor.close()
    cnx.close()


# Verkrijg data opgevraagd via een query
def get_data(sql: str) -> list[dict]:
    cnx, cursor = db_load()
    cursor.execute(sql)
    data = [row for row in cursor]
    db_disconnect(cnx, cursor)

    return data


# Verkrijg de usr_id
def db_get_id(sql: str):
    cnx, cursor = db_load()
    cursor.execute(sql)
    result = cursor.fetchone()["usr_id"]
    db_disconnect(cnx, cursor)

    return result


# Insereer data in een database dmv een query
def db_insert(sql: str) -> int:
    cnx, cursor = db_load()
    cursor.execute(sql)
    cnx.commit()
    db_disconnect(cnx, cursor)

    return cursor.lastrowid


# Functie gebruikt om een tabel te updaten
def db_update(sql: str) -> bool:
    cnx, cursor = db_load()

    try:
        cursor.execute(sql)
        cnx.commit()
        aantal_records_geupdated = cursor.rowcount
        db_disconnect(cnx, cursor)
        return True
    except:
        return False


# Algemene functie om database-query uit te voeren
def execute_sql(sql: str):
    cnx, cursor = db_load()
    cursor.execute(sql)
    cnx.commit()
    db_disconnect(cnx, cursor)


# Functie om tabel te creëren. Deze wordt opgeslagen in een dictionary
def create_table(sql_dict: dict, key: str):
    try:
        print(f"Creating table \"{key}\": ")
        execute_sql(sql_dict[key])
    except mysql.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


# Zet tabel om naar een dataframe
def get_table_as_df(tablename: str) -> pd.DataFrame:
    query = f"""SELECT * from {tablename}"""

    config = get_config()
    cnx = mysql.connect(**config)

    sql_query = pd.read_sql_query(query, cnx)
    cnx.close()

    return sql_query


# Functie om iteratief tabel te vullen met data
def insert_into_table(data: dict, tablename: str):
    if tablename in data.keys():
        table = data[tablename]

        # Voor elk category {category: {"att1: "val1", "att2": "val",...}}
        for category, datas in table.items():
            sql = (
                f"INSERT INTO {tablename} SET"
            )
            # Voor elke data van dat categorie {"att1: "val1", "att2": "val",...}
            for att, value in datas.items():
                sql += f" {att} = \'{value}\',"

            sql = sql[:-1] + ";"
            print(sql)
            execute_sql(sql)

    else:
        print(f"{tablename} not found in data")
