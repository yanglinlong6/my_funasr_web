from kafka import KafkaConsumer
import funasr_service

# 创建Kafka消费者
# consumer = KafkaConsumer(
#     "my-yang-topic",  # Kafka主题名称
#     bootstrap_servers="192.168.3.131:9092",  # Kafka集群的地址
#     group_id="my-yang-group",  # 消费者组ID
# )

# 循环消费消息
# for message in consumer:
#     # 从消息中获取键和值
#     key = message.key
#     value = message.value
#     print(f"Key: {key}, Value: {value}")

datas = ['0f4ba9a0-e7f6-11ee-b77c-b083fec01e48' ]

for task_id in datas:
    funasr_service.deal_worker(task_id)
