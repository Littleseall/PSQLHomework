
import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(100)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                phone VARCHAR(20)
            );
        """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id;
        """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        if phones:
            for phone in phones:
                add_phone(conn, client_id, phone)
        conn.commit()
        return client_id

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO phones (client_id, phone) VALUES (%s, %s);
        """, (client_id, phone))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("UPDATE clients SET first_name = %s WHERE id = %s;", (first_name, client_id))
        if last_name:
            cur.execute("UPDATE clients SET last_name = %s WHERE id = %s;", (last_name, client_id))
        if email:
            cur.execute("UPDATE clients SET email = %s WHERE id = %s;", (email, client_id))
        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phones WHERE client_id = %s AND phone = %s;
        """, (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM clients WHERE id = %s;", (client_id,))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = "SELECT * FROM clients"
        params = []
        conditions = []

        if first_name:
            conditions.append("first_name = %s")
            params.append(first_name)
        if last_name:
            conditions.append("last_name = %s")
            params.append(last_name)
        if email:
            conditions.append("email = %s")
            params.append(email)
        if phone:
            query += " INNER JOIN phones ON clients.id = phones.client_id"
            conditions.append("phones.phone = %s")
            params.append(phone)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cur.execute(query, params)
        return cur.fetchall()

def add_phone_to_existing_client(conn, client_id, phone):
    add_phone(conn, client_id, phone)

def delete_phone_from_existing_client(conn, client_id, phone):
    delete_phone(conn, client_id, phone)

if __name__ == "__main__":
    with psycopg2.connect(database="clients_db", user="postgres", password="SQLzadanie") as conn:
        create_db(conn)  # Функция, создающая структуру БД (таблицы).

        # Функция, позволяющая добавить нового клиента.
        client_id = add_client(conn, "Artem", "Ivanov", "ivanov@yandex.ru", ["123-456-7890"])
        print(f"Добавлен клиент: {client_id}")

        # Функция, позволяющая добавить телефон для существующего клиента.
        add_phone_to_existing_client(conn, client_id, "987-654-3210")
        print("Добавлен телефон для клиента.")

        # Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
        clients = find_client(conn, first_name="Artem")
        print("Найденные клиенты:", clients)

        # Функция, позволяющая удалить телефон для существующего клиента.
        delete_phone_from_existing_client(conn, client_id, "123-456-7890")
        print("Телефон удален у клиента.")

        # Функция, позволяющая изменить данные о клиенте.
        change_client(conn, client_id, email="new_email@yandex.ru")
        updated_client = find_client(conn, email="new_email@yandex.ru")
        print("Измененые данные у клиента:", updated_client)

        # Функция, позволяющая удалить существующего клиента.
        delete_client(conn, client_id)
        deleted_client = find_client(conn, first_name="Artem")
        print("Удаление клиента:", deleted_client)
