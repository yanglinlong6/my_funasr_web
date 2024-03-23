import logging
import json
import traceback
from mysql.connector import pooling
from config.config import ConfigInfo
from log.logger import log

logger = logging.getLogger()

# 创建连接池对象
connection_pool = pooling.MySQLConnectionPool(
    pool_name="funasr_pool",
    pool_size=1,
    pool_reset_session=True,
    host=ConfigInfo.host,
    port=ConfigInfo.port,
    database=ConfigInfo.database,
    user=ConfigInfo.user,
    password=ConfigInfo.password,
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
        return cursor.fetchall()
    except Exception as msg:
        logger.error("sql执行Exception: " + str(msg))
    finally:
        cursor.close()
        conn.close()


def select_sql(sql):
    try:
        log.info("execute_select sql:%s" % sql)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        # 获取字段名
        field_names = [i[0] for i in cursor.description]
        rows = cursor.fetchall()
        if rows is None or len(rows) < 1:
            return None
        res = json.dumps([dict(zip(field_names, row)) for row in rows], ensure_ascii=False)
        conn.commit()
        log.info("execute_select result:%s" % res)
        return res
    except Exception as msg:
        log.error("sql执行Exception: " + str(traceback.format_exc()))
    finally:
        cursor.close()
        conn.close()


