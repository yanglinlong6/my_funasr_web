import json
import uuid

from log.logger import log
from kafka import KafkaProducer
from config.config import ConfigInfo

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
