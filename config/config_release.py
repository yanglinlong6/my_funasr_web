class Config:
    DEBUG = False
    env = 'release'
    # 数据库连接配置
    host='supplychain.db.glsx.com'
    port = 13306
    user = 'biz_dj_smartcarlife'
    password = '[已加密]204db0d16a54807b8822481c6612513a'
    database = 'dj_smartcarlife'
    # Kafka consumer配置
    kafka_consumer_bootstrap_servers = 'newbiz.kafka.zk.glsx.com:9094'
    kafka_consumer_group_id = 'funasr_release'
    kafka_consumer_auto_offset_reset = 'earliest'
    kafka_consumer_analysis_topic = 'funasr_analysis_topic'
    charset = 'utf8'
