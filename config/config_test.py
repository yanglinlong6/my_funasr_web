class Config:
    DEBUG = False
    env = 'dev'
    # 数据库连接配置
    host='192.168.3.227'
    port = 3306
    user = 'dev_user'
    password = 'df234fl'
    database = 'glsx_car_service'
    # Kafka consumer配置
    kafka_consumer_bootstrap_servers = '192.168.3.131:9092'
    kafka_consumer_group_id = 'ocr_consumer_dev'
    kafka_consumer_auto_offset_reset = 'earliest'
    kafka_consumer_topic = 'ocr_topic'
    charset = 'utf8'
#
