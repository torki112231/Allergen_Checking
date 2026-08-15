import sqlite3
import hashlib


DB_NAME = 'mosabb.db'


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_allergies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            allergy TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            relation TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS allergies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            allergy TEXT NOT NULL,
            FOREIGN KEY (member_id) REFERENCES family_members(id)
        )
    ''')

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def register_user(name, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
            ''',
            (
                name,
                email,
                hash_password(password)
            )
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT id, name, email
        FROM users
        WHERE email = ?
        AND password = ?
        ''',
        (
            email,
            hash_password(password)
        )
    )

    user = cursor.fetchone()

    conn.close()

    return user


def save_user_allergies(user_id, allergies):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        DELETE FROM user_allergies
        WHERE user_id = ?
        ''',
        (user_id,)
    )

    for allergy in allergies:
        cursor.execute(
            '''
            INSERT INTO user_allergies
            (user_id, allergy)
            VALUES (?, ?)
            ''',
            (
                user_id,
                allergy
            )
        )

    conn.commit()
    conn.close()


def get_user_allergies(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT allergy
        FROM user_allergies
        WHERE user_id = ?
        ''',
        (user_id,)
    )

    allergies = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return allergies


def add_family_member(
    user_id,
    name,
    relation,
    allergies
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO family_members
        (user_id, name, relation)
        VALUES (?, ?, ?)
        ''',
        (
            user_id,
            name,
            relation
        )
    )

    member_id = cursor.lastrowid

    for allergy in allergies:
        cursor.execute(
            '''
            INSERT INTO allergies
            (member_id, allergy)
            VALUES (?, ?)
            ''',
            (
                member_id,
                allergy
            )
        )

    conn.commit()
    conn.close()


def get_family_members(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT id, name, relation
        FROM family_members
        WHERE user_id = ?
        ''',
        (user_id,)
    )

    members = cursor.fetchall()

    family = []

    for member in members:

        member_id = member[0]
        name = member[1]
        relation = member[2]

        cursor.execute(
            '''
            SELECT allergy
            FROM allergies
            WHERE member_id = ?
            ''',
            (member_id,)
        )

        member_allergies = [
            row[0]
            for row in cursor.fetchall()
        ]

        family.append({
            'id': member_id,
            'name': name,
            'relation': relation,
            'allergies': member_allergies
        })

    conn.close()

    return family


def delete_family_member(member_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        DELETE FROM allergies
        WHERE member_id = ?
        ''',
        (member_id,)
    )

    cursor.execute(
        '''
        DELETE FROM family_members
        WHERE id = ?
        ''',
        (member_id,)
    )

    conn.commit()
    conn.close()
