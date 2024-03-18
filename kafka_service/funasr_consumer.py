import time
from kafka import KafkaConsumer

import funasr_service
from log.logger import log
from mysql.connector import pooling
from config.config import ConfigInfo


# 配置 Kafka 消费者
consumer = KafkaConsumer(
    ConfigInfo.kafka_consumer_analysis_topic,
    bootstrap_servers=ConfigInfo.kafka_consumer_bootstrap_servers,  # Kafka broker 的地址
    group_id=ConfigInfo.kafka_consumer_group_id,  # 消费者组 ID
    auto_offset_reset=ConfigInfo.kafka_consumer_auto_offset_reset,  # 从最早的消息开始消费
)
log.info("启动2")

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
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        log.info("sql 执行结束")
    except Exception as msg:
        log.error("sql执行Exception: " + str(msg))
    finally:
        cursor.close()
        conn.close()


# 循环消费消息
def consume_kafka():
    log.info("启动consume_kafka")
    # 消费消息并进行逻辑处理
    try:
        for message in consumer:
            if message is None:
                continue
            log.info(f"Received message: {message}")
            log.info(f"Received message value: {message.value}")
            # 处理逻辑
            start_time = time.time()
            funasr_service.handle_process(str(message.value.decode('utf-8')))
            print("task handle")
            end_time = time.time()
            log.info("handle_process耗时:" + str(end_time - start_time))
    except Exception as e:
        log.error("ocr consumer Exception: " + str(e))


# 循环消费消息
# for message in consumer:
#     log.info(f"Received message: {message.value}")
#     if message is None:
#         continue
#     funasr_service.handle_process(str(message.value.decode('utf-8')))