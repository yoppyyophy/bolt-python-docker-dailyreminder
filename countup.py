import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
    with conn.cursor() as cur:
        cur.execute('SELECT message_id FROM today_count')
        data = cur.fetchall()

    message_id = data[0][0]
    message_id += 1
    if message_id > 3:
        message_id = 1

    with conn.cursor() as cur:
        cur.execute(f"UPDATE today_count SET message_id = {str(message_id)}")

    conn.commit()
