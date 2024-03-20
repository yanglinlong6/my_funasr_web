import logging
import json
import traceback
from mysql.connector import pooling
from config.config import ConfigInfo
from log.logger import log


class MySQLConnectionPool:
    def __init__(self, pool_name, pool_size, **config):
        self.pool_name = pool_name
        self.pool_size = pool_size
        self.config = config
        self.cnxpool = None
        self.create_pool()

    def create_pool(self):
        try:
            self.cnxpool = pooling.MySQLConnectionPool(pool_name=self.pool_name, pool_size=self.pool_size,
                                                       **self.config)
        except Exception as e:
            log.info(f"创建连接池时出错: {e}")
            traceback.format_exc()
            raise

    def get_connection(self):
        if self.cnxpool is None:
            raise Exception("连接池尚未创建")
        try:
            return self.cnxpool.get_connection()
        except Exception as e:
            log.info(f"从连接池获取连接时出错: {e}")
            traceback.format_exc()
            raise

    def close(self):
        if self.cnxpool:
            self.cnxpool.close()


# config = {
#     "host": ConfigInfo.host,
#     "user": ConfigInfo.user,
#     "password": ConfigInfo.password,
#     "database": ConfigInfo.database,
# }

config = {
    "host" : '192.168.3.227',
    "port" : 3306,
    "user" : 'dev_user',
    "password" : 'df234fl',
    "database" : 'dj_smartcarlife'
}

pool = MySQLConnectionPool("funasr_pool", 1, **config)


def some_method():
    try:
        # 从连接池中获取连接
        conn = pool.get_connection()
        cursor = conn.cursor()
        # 执行SQL查询
        cursor.execute("select * from ali_asr_model_res aamr;")
        results = cursor.fetchall()
        for row in results:
            print(row)
        # 提交事务
        # conn.commit()
    except Exception as e:
        print(f"数据库操作出错: {e}")
        # 回滚事务
        conn.rollback()
    finally:
        # 关闭游标和连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()