import json

from kafka import KafkaProducer

# 创建Kafka生产者
producer = KafkaProducer(bootstrap_servers="192.168.3.131:9092")  # Kafka集群的地址

# 发送消息
topic = "funasr_topic"  # Kafka主题名称
key = b"my-key"  # 消息的键（可选）
data = {'orderId': 1234, 'fileId': 31,'filePath':'https://bhg.didihu.com.cn/group1/M00/22/05/wKgFDWWnocCAZllpAADp9tDJibY696.jpg','sns':'96312110851','vin':'VIN654321','fileType':1}
message = json.dumps(data).encode('utf-8')
producer.send(topic,message)

# 等待所有消息发送完成
producer.flush()

# 关闭生产者
producer.close()
