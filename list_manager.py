import mysql.connector
from mysql.connector import Error
import os
import random
import string
import hashlib
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    pool_size=16,
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)


def random_id(chars=string.ascii_uppercase + string.digits + string.ascii_lowercase + "-_=+.>,<|*^@!"):
    return ''.join(random.choice(chars) for _ in range(12))


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)


async def create_list(password):
    new_id = random_id()
    salt = os.urandom(32)
    password_hash = hash_password(password, salt)

    sql = "INSERT INTO wishlists (id, password, salt) VALUES (%s, %s, %s)"
    val = (new_id, password_hash, salt)

    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()
    db.close()

    return new_id


async def check_password(password_to_check, list_id) -> bool:
    print(list_id)
    cursor = db.cursor()
    try:
        sql = "SELECT password, salt FROM wishlists where id = %s;"
        val = (list_id,)
        cursor.execute(sql, val)
        records = cursor.fetchall()

        password = None
        salt = None

        for row in records:
            password = row[0]
            salt = row[1]

        if password is None:
            return False
        if salt is None:
            return False

        if password == hash_password(password_to_check, salt):
            return True

        return False

    except Error as e:
        return False
    finally:
        cursor.close()


async def add_entry(url, list_id):
    sql = "INSERT INTO entries (list_id, url) VALUES (%s, %s)"
    val = (list_id, url)

    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()

    cursor.close()


async def remove_entry(list_id, entry_id):
    sql = "DELETE FROM entries WHERE list_id = %s AND id = %s"
    val = (list_id, entry_id)
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()
    cursor.close()


async def get_entries(list_id):
    sql = "SELECT id, url FROM entries WHERE list_id = %s;"
    val = (list_id,)
    cursor = db.cursor()
    cursor.execute(sql, val)
    records = cursor.fetchall()

    entries = []

    for row in records:
        print(row)
        entries.append({
            "id": row[0],
            "url": row[1]
        })

    return entries


async def count_entries(list_id):
    sql = "SELECT COUNT(*) FROM entries WHERE list_id = %s;"
    val = (list_id,)
    cursor = db.cursor()
    cursor.execute(sql, val)
    records = cursor.fetchone()

    for row in records:
        return row
