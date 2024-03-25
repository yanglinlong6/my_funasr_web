import json
import multiprocessing
import threading
import time
import traceback
import funasr_service
from kafka import KafkaConsumer
from log.logger import log
from config.config import ConfigInfo
from concurrent.futures import ThreadPoolExecutor
from kafka.structs import TopicPartition
from mysql_service import funasr_db

# 配置 Kafka 消费者
consumer_new = KafkaConsumer(
    ConfigInfo.kafka_consumer_analysis_topic,
    bootstrap_servers=ConfigInfo.kafka_consumer_bootstrap_servers,  # Kafka broker 的地址
    group_id=ConfigInfo.kafka_consumer_group_id,  # 消费者组 ID
    auto_offset_reset=ConfigInfo.kafka_consumer_auto_offset_reset,  # 从最早的消息开始消费
)
log.info("启动2")


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
            log.error("funasr consumer Exception: " + str(traceback.format_exc()))

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
        # process_pool = multiprocessing.Pool(processes=1, initializer=consumer_process_init)
        for message in consumer_new:
            if message is None:
                continue
            log.info(f"Received message: {message}")
            # 处理逻辑
            funasr_service.handle_process(str(message.value.decode('utf-8')))
            # arg = str(message.value.decode('utf-8'))
            # log.info(f"arg:{arg},process_pool1:{process_pool}")
            # process_pool.apply_async(func=funasr_service.handle_process, args=(arg,),
            #                          callback=consumer_process_callback,
            #                          error_callback=consumer_process_error_callback)
            # process = multiprocessing.Process(target=funasr_service.handle_process, args=((str(message.value.decode('utf-8'))),),)
            # process.start()
            print("task handle")
        # process_pool.close()
        # process_pool.join()
    except Exception as e:
        log.error("funasr consumer Exception: " + str(traceback.format_exc()))


# 循环消费消息
# for message in consumer:
#     log.info(f"Received message: {message.value}")
#     if message is None:
#         continue
#     funasr_service.handle_process(str(message.value.decode('utf-8')))

def consumer_process_init():
    process_name = str(multiprocessing.current_process().name)
    log.info(f"consumer_process_init process_name:{process_name}")
    # try:
    #     res = funasr_db.select_process_fail_task(process_name)
    #     if res is not None:
    #         data = {"task_id": res[0]["task_id"]}
    #         message = json.dumps(data).encode('utf-8')
    #         funasr_service.handle_process(str(message))
    # except Exception as e:
    #     log.error(f"consumer_process_init_error process_name:{process_name}", e)


def consumer_process_callback(res):
    log.info(f"consumer_process_callback:{multiprocessing.current_process().name}, res:{res}")
    # count = funasr_db.select_process_all_end()
    # if count is not None and int(count) == 0:
    #     res = funasr_db.select_ali_asr_model_wait()
    #     if res is not None and len(res) > 0:
    #         data = {"task_id": res[0]["task_id"]}
    #         message = json.dumps(data).encode('utf-8')
    #         funasr_service.handle_process(str(message))


def consumer_process_error_callback(err):
    log.error(f"consumer_process_error_callback:{err}")
