import logging
from mysql.connector import pooling

logger = logging.getLogger()

# 创建连接池对象
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=32,
    pool_reset_session=True,
    host="",
    port="",
    database="",
    user="",
    password="",
    autocommit=True,
)

# 从连接池获取连接
def get_connection():
    logger.info("connection_pool size:" + str(connection_pool._cnx_queue.qsize()))
    # 从连接池获取连接
    return connection_pool.get_connection()


def execute_sql(sql):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        logger.info("sql 执行结束")
    except Exception as msg:
        logger.error("sql执行Exception: " + str(msg))
    finally:
        cursor.close()
        conn.close()
