import os
from mysql.connector.pooling import MySQLConnectionPool

# 從環境變量獲取數據庫配置
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'rootroot'),
    'database': os.getenv('DB_NAME', 'taipei_attractions'),
}


db_pool = MySQLConnectionPool(
    pool_name="mysql_pool",
    pool_size=30,
    pool_reset_session=True,
    **db_config
)

print("Connection pool created.")

def get_cursor():
    conn = db_pool.get_connection()
    cursor = conn.cursor()
    return cursor, conn

def conn_commit(conn):
    conn.commit()

def conn_close(conn):
    try:
        if conn.is_connected():
            conn.close()
    except Exception as event:
        print("Error closing connection:", event)