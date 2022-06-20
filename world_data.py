from choropleth_plotly import HappinessChoropleth
import pandas as pd
from Lib_db.db_emo import *
import os


TABLES = dict()

# Creatie van tabellen-queries: data voor Choropleth (countries, years en world-happiness)
TABLES['countries'] = (
    "CREATE TABLE countries ("
        "cou_id int NOT NULL AUTO_INCREMENT,"
        "cou_name varchar(255) NOT NULL,"
        "PRIMARY KEY (cou_id)"
        ") ENGINE=InnoDB;")

TABLES['years'] = (
    "CREATE TABLE years ("
        "yea_id int NOT NULL AUTO_INCREMENT,"
        "yea_year int NOT NULL,"
        "PRIMARY KEY (yea_id)"
        ") ENGINE=InnoDB;")

TABLES['world_happiness'] = (
    "CREATE TABLE world_happiness ("
        "hap_id int NOT NULL AUTO_INCREMENT,"
        "hap_country varchar(255) NOT NULL,"
        "hap_score float NOT NULL,"
        "hap_cou_id int,"
        "hap_yea_id int NOT NULL,"
        "PRIMARY KEY (hap_id)"
        ") ENGINE=InnoDB;")

# Deze functie creëert de tabellen in de database via de queries
create_table(sql_dict=TABLES, key='countries')
create_table(sql_dict=TABLES, key='years')
create_table(sql_dict=TABLES, key='world_happiness')


# Data invoegen in Choropleth-tabellen
DATA_INSERT = {"countries": {},
               "years": {},
               "world_happiness": {}
               }

years_df = static_db.get_table_as_df("years")
countries_df = static_db.get_table_as_df("countries")

path = os.path.join("input", "WHR_2021_data.xlsx")
whr_2021 = pd.read_excel(path)

# Data invoeg-functies: countries en years
insert_into_table(data=DATA_INSERT, tablename="countries")
insert_into_table(data=DATA_INSERT, tablename="years")

# Data voorbereiden om in te voeren in happiness score
for _, row in whr_2022.iterrows():
    country = row["Country name"]

    if country in countries_df['cou_name'].values:
        cou_id = countries_df.loc[countries_df['cou_name'] == country, "cou_id"].item()
    else:
        cou_id = 0

    DATA_INSERT["world_happiness"][row["Country name"]] = {"hap_country": row["Country name"],
                                                           "hap_score": row["Ladder score"],
                                                           "hap_cou_id": cou_id,
                                                           "hap_yea_id": 6,
                                                           }

insert_into_table(data=DATA_INSERT, tablename="world_happiness")
