import multiprocessing
import threading
import time
import traceback
import funasr_service
from kafka import KafkaConsumer
from log.logger import log
from mysql.connector import pooling
from config.config import ConfigInfo
from concurrent.futures import ThreadPoolExecutor
from kafka.structs import TopicPartition

# 配置 Kafka 消费者
consumer_new = KafkaConsumer(
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


class MultiThreadKafka(object):

    def __init__(self):
        self.seek = 0  # 偏移量
    def start_consumer(self, consumer):
        log.info(f"启动consume_kafka Thread name:{threading.current_thread().name}")
        # 消费消息并进行逻辑处理
        try:
            for message in consumer:
                if message is None:
                    continue
                log.info(f"Received message: {message}")
                log.info(
                    f"""process name:{multiprocessing.current_process()},thread name:{threading.current_thread().name}，
                            Received message value: {message.value}""")
                # 处理逻辑
                funasr_service.handle_process(str(message.value.decode('utf-8')))
                print("task handle")
        except Exception as e:
            traceback.print_exc()
            log.error("funasr consumer Exception: " + str(e))

    def operate(self):
        consumer = KafkaConsumer(
            # ConfigInfo.kafka_consumer_analysis_topic,
            bootstrap_servers=ConfigInfo.kafka_consumer_bootstrap_servers,  # Kafka broker 的地址
            group_id=ConfigInfo.kafka_consumer_group_id,  # 消费者组 ID
            auto_offset_reset=ConfigInfo.kafka_consumer_auto_offset_reset,  # 从最早的消息开始消费
        )
        tp = TopicPartition(ConfigInfo.kafka_consumer_analysis_topic, self.seek)
        consumer.assign([tp])
        # consumer.seek(tp, self.seek)
        self.seek += 1
        # consumer_data = next(consumer)
        self.start_consumer(consumer)

    def main(self):
        thread_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="funasr_")  # 我们使用线程池统一管理线程
        for i in range(2):
            thread_pool.submit(self.operate, )


def multi_thread_consumer():
    thread_kafka = MultiThreadKafka()
    thread_kafka.main()



# 循环消费消息
def consume_kafka():
    log.info(f"启动consume_kafka Thread name:{threading.current_thread().name}")
    # 消费消息并进行逻辑处理
    try:
        process_pool = multiprocessing.Pool(processes=2)
        for message in consumer_new:
            if message is None:
                continue
            log.info(f"Received message: {message}")
            # 处理逻辑
            # funasr_service.handle_process(str(message.value.decode('utf-8')))
            process_pool.apply_async(funasr_service.handle_process, ((str(message.value.decode('utf-8'))),))
            # process = multiprocessing.Process(target=funasr_service.handle_process, args=((str(message.value.decode('utf-8'))),),)
            log.info(f"process:{process_pool}")
            # process.start()
            print("task handle")
        # process_pool.close()
        # process_pool.join()
    except Exception as e:
        traceback.print_exc()
        log.error("funasr consumer Exception: " + str(e))

# 循环消费消息
# for message in consumer:
#     log.info(f"Received message: {message.value}")
#     if message is None:
#         continue
#     funasr_service.handle_process(str(message.value.decode('utf-8')))
