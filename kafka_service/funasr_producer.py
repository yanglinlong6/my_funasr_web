import json
import uuid

from log.logger import log
from kafka import KafkaProducer
from config.config import ConfigInfo
from mysql_service import funasr_db

# 创建Kafka生产者
producer = KafkaProducer(bootstrap_servers=ConfigInfo.kafka_consumer_bootstrap_servers)  # Kafka集群的地址


# key = b"funasr-key"  # 消息的键（可选）
# 关闭生产者
# producer.close()

def send_message_analysis(message):
    message = json.dumps(message).encode('utf-8')
    log.info(f"funasr_task_send_success:{message}")
    producer.send(ConfigInfo.kafka_consumer_analysis_topic, message)
    # 等待所有消息发送完成
    producer.flush()

def send_wait_task():
    res = funasr_db.select_ali_asr_model_wait()
    if res is None or isinstance(res, bool) or len(res) < 1:
        return
    json_res = json.loads(res)
    print(f"服务启动推送等待任务：{json_res}")
    for item in json_res:
        task_id = item['task_id']
        data = {"task_id": task_id}
        message = json.dumps(data).encode('utf-8')
        producer.send(ConfigInfo.kafka_consumer_analysis_topic, message)
        print(f"send success{task_id}")
        # 等待所有消息发送完成
        producer.flush()