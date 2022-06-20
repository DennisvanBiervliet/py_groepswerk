import Lib_db.db_emo
from Lib_db import db_emo
from datetime import datetime
import pandas as pd


# Nieuwe user toevoegen
def db_insert_user(username):
    sql = f"INSERT IGNORE INTO users SET usr_name = '{username}'"
    db_emo.db_insert(sql)  # dit is de functie die ervoor zorgt dat sql statement uitgevoerd wordt id DB
    print('user in database')
    return True


# User id opvragen
def db_get_user_id(username):
    sql = f"SELECT usr_id FROM users WHERE usr_name = '{username}'"
    usr_id = Lib_db.db_emo.db_get_id(sql)
    return usr_id


# Nieuwe detectie toevoegen
def db_insert_capture(usr_id, score):
    now = datetime.now()
    sql = f"INSERT INTO detections SET det_datetime = NOW(), det_usr_id='{usr_id}', det_score='{score}'"
    det_id = db_emo.db_insert(sql)
    return det_id, now
