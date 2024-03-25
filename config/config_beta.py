class Config:
    DEBUG = False
    env = 'beta'
    # 数据库连接配置
    host='common.db.glsx.com'
    port = 3306
    user = 'biz_dj_smartcarlife'
    password = 'YiukxTcp'
    database = 'dj_smartcarlife'
    # Kafka consumer配置
    kafka_consumer_bootstrap_servers = 'biz.kafka.zk.glsx.com:9092'
    kafka_consumer_group_id = 'funasr_beta'
    kafka_consumer_auto_offset_reset = 'earliest'
    kafka_consumer_analysis_topic = 'funasr_analysis_topic'
    charset = 'utf8'
#
