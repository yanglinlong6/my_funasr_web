from mysql.connector import pooling

from config.config import ConfigInfo
from log.logger import log

# 创建连接池对象
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=32,
    pool_reset_session=True,
    host=ConfigInfo.host,
    port=ConfigInfo.port,
    database=ConfigInfo.database,
    user=ConfigInfo.user,
    password=ConfigInfo.password,
    autocommit=True,
)

log.info("启动3")
# 从连接池获取连接
def get_connection():
    log.info("connection_pool size:" + str(connection_pool._cnx_queue.qsize()))
    # 从连接池获取连接
    return connection_pool.get_connection()


def execute_sql(sql):
    try:
        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        result = cursor.execute(sql)
        # conn.commit()
        log.info("sql 执行结束")
        print(result)
        return result
    except Exception as msg:
        log.error("sql执行Exception: " + str(msg))
    # finally:
        # cursor.close()
        # conn.close()

if __name__ == "__main__":
    selectSql = ("select * from ali_asr_model_res;")
    print("execute sql:%s" %selectSql)
    res = execute_sql(selectSql)
    print(res)
