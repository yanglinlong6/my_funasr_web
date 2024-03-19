import json

from kafka import KafkaProducer
from config.config import ConfigInfo
from mysql_service import funasr_db

# 创建Kafka生产者
producer = KafkaProducer(bootstrap_servers=ConfigInfo.kafka_consumer_bootstrap_servers)  # Kafka集群的地址

# 发送消息
topic = "my-yang-topic"  # Kafka主题名称
key = b"my-key"  # 消息的键（可选）
value = b'{"task_id": "7db1a2c8-e4eb-11ee-ac46-a0e70be87132"}'  # 消息的值
for item in range(1):
    producer.send(ConfigInfo.kafka_consumer_analysis_topic, key=key, value=value)

# 等待所有消息发送完成
producer.flush()
# 关闭生产者
producer.close()


res = funasr_db.select_ali_asr_model_wait()
json_res = json.loads(res)
# json_res = json_res.replace("'", "\"")
print(f"json_res{json_res}")
for item in json_res:
    print(f"item:{item}")
    task_id = item['task_id']
    data = {"task_id":task_id}
    message = json.dumps(data).encode('utf-8')
    producer.send(ConfigInfo.kafka_consumer_analysis_topic, message)
    print(f"success{task_id}")
    # 等待所有消息发送完成
    producer.flush()
# 关闭生产者
producer.close()

