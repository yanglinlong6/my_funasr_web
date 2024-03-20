import time
import traceback
from mysql_service import mysql_pool
from mysql.connector import pooling
from log.logger import log
from mysql_service import funasr_db
from mysql_service import MysqlHelper
from config import DbConect
from mysql_service import mysql_utils
from mysql_service.mysql_pool import MySQLConnectionPool
from config.config import ConfigInfo


consuming_start_time = time.perf_counter()

# db = MysqlHelper.MysqlHelper(
#     DbConect.ali_asr_model
# )

task_id = str("63764ce2-e5cb-11ee-928c-b083fec01e48")
url = "https://smartcard-1253080096.cos.ap-guangzhou.myqcloud.com/audio/4827E2F0CD24_1709084561_4827E2F0CD24-1709084561.MP3"
# res = funasr_db.insert_ali_asr_model_res(task_id, url)
# print(f"res:{res}")


sql = "INSERT INTO dj_smartcarlife.ali_asr_model_res (task_id,file_url,task_status) VALUES (" \
      "'47f9402c-e5cc-11ee-928c-b083fec01e48','https://img01.glsx.com.cn/weapp/resource/wav/122m4a.wav',0);"

# select_res = mysql_utils.execute_sql("select * from ali_asr_model_res aamr;")
# print(select_res)
for i in range(1):
    # res = mysql_pool.some_method()
    res = funasr_db.select_ali_asr_model_wait()
    print(res)
try:
    # time.sleep(2)
    execute_time = time.perf_counter() - consuming_start_time
    log.info(
        f"Function create_upload_file executed in {execute_time} s"
    )
    # funasr_db.update_ali_asr_model_res(task_id, task_id, int((execute_time * 1000)))
    # if res is None or isinstance(res, bool) or len(res) < 1:
    #     print("======")
except Exception as e:
    print(f"e:{traceback.format_exc()}")
    # funasr_db.update_ali_asr_model_res_fail(task_id, str(traceback.format_exc()))

import json

# 定义要执行的SQL语句
# SQL = """
#       select * from sys_order_file_ocr_sn sofon limit 5
# """
# # 执行SQL语句
# cursor_dev.execute(SQL)
#
# # 获取查询结果
# result = cursor_dev.fetchall()
#
# class Config:
#     DEBUG = False
#     env = 'dev'
#     # 数据库连接配置
#     host='192.168.3.227'
#     port = 3306
#     user = 'dev_user'
#     password = 'df234fl'
#     database = 'dj_smartcarlife'
#     # Kafka consumer配置
#     kafka_consumer_bootstrap_servers = '192.168.3.131:9092'
#     kafka_consumer_group_id = 'ocr_consumer_dev'
#     kafka_consumer_auto_offset_reset = 'earliest'
#     kafka_consumer_topic = 'ocr_topic'
#     charset = 'utf8'
#
#
# # 创建连接池对象
# connection_pool = pooling.MySQLConnectionPool(
#     pool_name="mypool",
#     pool_size=32,
#     pool_reset_session=True,
#     host=Config.host,
#     port=Config.port,
#     database=Config.database,
#     user=Config.user,
#     password=Config.password,
#     autocommit=True,
# )
#
# # 从连接池获取连接
# def get_connection():
#     log.info("connection_pool size:" + str(connection_pool._cnx_queue.qsize()))
#     # 从连接池获取连接
#     return connection_pool.get_connection()
#
#
# def execute_sql(sql):
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute(sql)
#         conn.commit()
#         log.info("sql 执行结束")
#     except Exception as msg:
#         log.error("sql执行Exception: " + str(msg))
#     finally:
#         cursor.close()
#         conn.close()
#
# SQL = "select * from sys_order_ocr_vin_result"
# res = execute_sql(SQL)
# print(res)
#






