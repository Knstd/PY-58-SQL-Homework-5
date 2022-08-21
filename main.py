import psycopg2
import os
from dotenv import load_dotenv, find_dotenv


# Функция, создающая структуру БД (таблицы)
def create_db(conn):
    with conn.cursor() as curr:
        curr.execute('''
            CREATE TABLE IF NOT EXISTS clients(
            client_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            surname VARCHAR(50) NOT NULL,
            email VARCHAR(50) NOT NULL);''')
        curr.execute('''
            CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20) UNIQUE,
            client_id INTEGER REFERENCES clients(client_id));''')
        conn.commit()


# Функция, позволяющая добавить нового клиента
def add_client(conn, name, surname, email, phone_number=None):
    with conn.cursor() as curr:
        curr.execute('''
            INSERT INTO clients(name, surname, email)
            VALUES (%s, %s, %s)
            RETURNING client_id;''', (name, surname, email))
        id = curr.fetchone()
        curr.execute('''
            INSERT INTO phones(phone_number, client_id)
            VALUES (%s, %s);''', (phone_number, id))


# Функция, позволяющая добавить телефон для существующего клиента
def add_phone_number(conn, client_id, phone_number):
    with conn.cursor() as curr:
        try:
            curr.execute('''
                SELECT client_id
                FROM clients
                WHERE client_id = %s;''', (client_id,))
            id = curr.fetchone()[0]
            curr.execute('''
                INSERT INTO phones(phone_number, client_id)
                VALUES (%s, %s);''', (phone_number, id))
        except TypeError:
            print(f'Error - client_id {client_id} is missing')


# Функция, позволяющая изменить данные о клиенте
def update_client(conn, client_id, name=None, surname=None, email=None, new_phone_number=None):
    with conn.cursor() as curr:
        if name:
            curr.execute('''
                UPDATE clients
                SET name = %s
                WHERE client_id = %s;''', (name, client_id))
        if surname:
            curr.execute('''
                UPDATE clients
                SET surname = %s
                WHERE client_id = %s;''', (surname, client_id))
        if email:
            curr.execute('''
                UPDATE clients
                SET email = %s
                WHERE client_id = %s;''', (email, client_id))
        if new_phone_number:
            curr.execute('''
                SELECT c.client_id, p.phone_number
                FROM clients c
                LEFT JOIN phones p USING(client_id)
                WHERE client_id = %s;''', (client_id,))
            phone_list = curr.fetchall()
            print(f'Phones list for client_id {client_id}: ')
            for id, phone in enumerate(phone_list, 1):
                print(f'{id} - {phone[1]}')
            old_phone_number = input('Input phone number to replace: ')
            exist = False
            for phone in phone_list:
                if old_phone_number in phone:
                    exist = True
            if exist:
                curr.execute('''
                    UPDATE phones
                    SET phone_number = %s
                    WHERE phone_number = %s;''', (new_phone_number, old_phone_number))
            else:
                print('Input error')


# Функция, позволяющая удалить телефон для существующего клиента
def delete_phone(conn, client_id, phone_number):
    with conn.cursor() as curr:
        curr.execute('''
            SELECT client_id
            FROM clients
            WHERE client_id = %s;''', (client_id,))
        id = curr.fetchone()[0]
        curr.execute('''
            DELETE FROM phones
            WHERE client_id = %s AND phone_number = %s;''', (id, phone_number))


# Функция, позволяющая удалить существующего клиента
def delete_client(conn, client_id):
    with conn.cursor() as curr:
        curr.execute('''
            DELETE FROM phones
            WHERE client_id = %s;''', (client_id,))
        curr.execute('''
            DELETE FROM clients
            WHERE client_id = %s;''', (client_id,))


# Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)
def find_client(conn, name=None, surname=None, email=None, phone_number=None):
    with conn.cursor() as curr:
        curr.execute('''
            SELECT c.client_id, c.name, c.surname, c.email, p.phone_number 
            FROM clients c
            LEFT JOIN phones p USING(client_id)
            WHERE name=%s AND surname=%s AND email=%s OR phone_number=%s;''', (name, surname, email, phone_number))
        return curr.fetchall()


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    user = os.getenv('user')
    password = os.getenv('password')
    with psycopg2.connect(database='PD-58 Homework5', user=user, password=password, host='localhost') as conn:
        with conn.cursor() as curr:
            curr.execute('''
            DROP TABLE phones;
            DROP TABLE clients;
            ''')
        create_db(conn)
        add_client(conn, 'name_1', 'surname_1', '1@email.com', '123-456')
        add_client(conn, 'name_2', 'surname_2', '2@email.com', '234-567')
        add_client(conn, 'name_3', 'surname_3', '3@email.com', '345-678')
        add_client(conn, 'name_4', 'surname_4', '4@email.com', '456-789')
        add_client(conn, 'name_5', 'surname_5', '5@email.com', '567-890')
        add_phone_number(conn, 2, '654-321')
        add_phone_number(conn, 5, '543-210')
        delete_phone(conn, 1, '123-456')
        delete_client(conn, 4)
        print(find_client(conn, name='name_1', surname='surname_1', email='1@email.com'))
        print(find_client(conn, phone_number='345-678'))
        update_client(conn, 3, 'name_6', 'surname_6', '6@email.com', '678-901')
        update_client(conn, 2, new_phone_number='789-012')

    conn.close()
