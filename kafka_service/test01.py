from kafka import KafkaConsumer

# 创建Kafka消费者
consumer = KafkaConsumer(
    "my-yang-topic",  # Kafka主题名称
    bootstrap_servers="192.168.3.131:9092",  # Kafka集群的地址
    group_id="my-yang-group",  # 消费者组ID
)

# 循环消费消息
# for message in consumer:
#     # 从消息中获取键和值
#     key = message.key
#     value = message.value
#     print(f"Key: {key}, Value: {value}")


datas = ["", "   ", "1111","https","1http",]
for data in datas:
    data.replace(" ", "")
    if data == "" or len(data) < 1 or not data.startswith("http"):
        print(False)
    else:
        print(True)
