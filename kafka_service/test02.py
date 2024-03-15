from kafka import KafkaProducer

# 创建Kafka生产者
producer = KafkaProducer(bootstrap_servers="192.168.3.131:9092")  # Kafka集群的地址

# 发送消息
topic = "my-yang-topic"  # Kafka主题名称
key = b"my-key"  # 消息的键（可选）
value = b"my-value"  # 消息的值
for item in range(10):
    producer.send(topic, key=key, value=value)

# 等待所有消息发送完成
producer.flush()

# 关闭生产者
producer.close()
