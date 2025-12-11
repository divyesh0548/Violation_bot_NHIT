import psycopg2

# Database configuration variables (set these with your values)
DB_HOST = "db-1.c2n44a20y9k5.us-east-1.rds.amazonaws.com"
DB_PORT = 5432
DB_NAME = "snt_form"
DB_USER = "postgres"
DB_PASSWORD = "postgres1234"

def get_db_connection():
    """Create and return a PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_testing_table():
    """Create table 'testing' with an extra integer column 'file_status'"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS testing (
        id SERIAL PRIMARY KEY,
        entity_name character varying(100) NOT NULL,
        name character varying(100) NOT NULL,
        email character varying(120) NOT NULL,
        date date NOT NULL,
        shift character varying(20) NOT NULL,
        vrn_file_url character varying(500) NULL,
        etc_file_url character varying(500) NULL,
        created_at timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP,
        file_status INT
    );
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(create_table_query)
                conn.commit()
                print("Table 'testing' created successfully (or already exists)")
        except psycopg2.Error as e:
            print(f"Error creating table: {e}")
        finally:
            conn.close()
    else:
        print("Connection to database failed. Table NOT created.")

def insert_data(records):
    """
    Insert multiple records into the 'testing' table.
    records: list of tuples with values in order:
        (entity_name, name, email, date, shift, vrn_file_url, etc_file_url, file_status)
    """
    insert_query = """
        INSERT INTO testing (
            entity_name, name, email, date, shift, vrn_file_url, etc_file_url, file_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.executemany(insert_query, records)
                conn.commit()
                print(f"Inserted {cursor.rowcount} records into 'testing' table.")
        except psycopg2.Error as e:
            print(f"Error inserting data: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to database.")

sample_records = [
    ("bankapur", "John Doe", "john@example.com", "2025-11-25", "Shift A", "https://snt-nhit-data.s3.us-east-1.amazonaws.com/bankapur/VRN/4_12/20251124_073201_Transaction_Detail_Report_23.11.2025_C.csv", "http://example.com/etc1", 0),
    ("odhaki_paipkhar", "Jane Smith", "jane@example.com", "2025-11-25", "Shift B", "https://snt-nhit-data.s3.us-east-1.amazonaws.com/odhaki_paipkhar/VRN/12_8/20251124_073251_All_Transaction_Report_Shift_A.xlsx", None, 0),
]

if __name__ == "__main__":
    # create_testing_table()
    insert_data(sample_records)
