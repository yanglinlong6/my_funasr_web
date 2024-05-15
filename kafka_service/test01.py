from kafka import KafkaConsumer
import funasr_service
from mysql_service import funasr_db

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

datas = ['88d4ac0e-11ea-11ef-8a60-b083fec01e48']


def not_insert_run():
    for task_id in datas:
        out_put: str
        if task_id.find("/") != -1:
            output_res = funasr_service.FunasrService(task_id).transform()
        else:
            sql_res = funasr_db.select_ali_asr_model_res(task_id)
            url = sql_res[0]["file_url"]
            output_res = funasr_service.FunasrService(url).transform()
        res = funasr_service.simple_transform_output(output_res[0]["sentence_info"])
        print(res)


def insert_run():
    for task_id in datas:
        funasr_service.deal_worker(task_id)


def run():
    url = 'https://glsk-oss.oss-cn-shenzhen.aliyuncs.com/quality/7cf068ad-2592-4033-93c0-02c9b2735189.mp3'
    res = funasr_service.FunasrService(url).transform
    print(f"res:{str(res)}")
    # print(f"sentence_info:{funasr_service.fine_grained_transform_output(res[0]['sentence_info'])}")


insert_run()
