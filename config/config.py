import sys
from log.logger import log

environment = sys.argv[1] if len(sys.argv) > 1 else "default"
# environment = os.environ.get('ENV')
if environment == 'pro':
    from config_release import Config

    log.info(vars(Config))
elif environment == 'test':
    from config_test import Config

    log.info(vars(Config))
else:
    from config_dev import Config

    log.info(vars(Config))


class ConfigInfo:
    DEBUG = Config.DEBUG
    env = Config.env
    # 数据库连接配置
    host = Config.host
    port = Config.port
    user = Config.user
    password = Config.password
    database = Config.database
    # Kafka Config
    kafka_consumer_bootstrap_servers = Config.kafka_consumer_bootstrap_servers
    kafka_consumer_group_id = Config.kafka_consumer_group_id
    kafka_consumer_auto_offset_reset = Config.kafka_consumer_auto_offset_reset
    kafka_consumer_topic = Config.kafka_consumer_topic
    charset = Config.charset
