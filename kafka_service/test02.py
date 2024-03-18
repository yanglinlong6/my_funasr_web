from kafka import KafkaProducer
from config.config import ConfigInfo

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

