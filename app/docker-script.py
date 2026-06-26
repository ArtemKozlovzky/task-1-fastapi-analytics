import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def connect_source():
    return psycopg2.connect(
        host=os.getenv("DOCKER_SOURCE_HOST"),
        port=os.getenv("TARGET_PORT"), #source port, dbname ec.
        dbname=os.getenv("TARGET_DBNAME"),
        user=os.getenv("TARGET_USER"),
        password=os.getenv("TARGET_PASSWORD"),
        cursor_factory=RealDictCursor
    )

def connect_target():
    return psycopg2.connect(
        host=os.getenv("DOCKER_TARGET_HOST"),
        port=os.getenv("DOCKER_TARGET_PORT"),
        dbname=os.getenv("DOCKER_TARGET_DBNAME"),
        user=os.getenv("DOCKER_TARGET_USER"),
        password=os.getenv("DOCKER_TARGET_PASSWORD"),
        cursor_factory=RealDictCursor
    )

TABLES_IN_ORDER = [
    "make",
    "model",
    "color",
    "body_type",
    "engine_type",
    "publication_type",
    "seller_type",
    "transmission_type",
    "seller",
    "offer"
]

def migrate():
    print("Connecting to SOURCE...")
    src = connect_source()
    src_cur = src.cursor()

    print("Connecting to TARGET...")
    tgt = connect_target()
    tgt.autocommit = True
    tgt_cur = tgt.cursor()

    try:
        print("Clearing TARGET tables...")
        for table in reversed(TABLES_IN_ORDER):
            tgt_cur.execute(f"DELETE FROM {table};")

        print("Copying data...")
        for table in TABLES_IN_ORDER:
            print(f"  → {table}")

            src_cur.execute(f"SELECT * FROM {table};")
            rows = src_cur.fetchall()

            if not rows:
                continue

            columns = rows[0].keys()
            col_list = ", ".join(columns)
            placeholders = ", ".join([f"%({c})s" for c in columns])

            insert_sql = f"""
                INSERT INTO {table} ({col_list})
                VALUES ({placeholders});
            """

            for row in rows:
                tgt_cur.execute(insert_sql, row)

        print("Migration completed successfully!")

    except Exception as e:
        print("ERROR:", e)

    finally:
        src_cur.close()
        tgt_cur.close()
        src.close()
        tgt.close()


if __name__ == "__main__":
    migrate()
