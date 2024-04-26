本项目主要是提供接口给外部进行语音转文字
主要的功能类: main.py                            提供http协议接口
             funasr_service.py                   提供语音转文字模型功能
             kafka_service/funasr_consumer.py    提供kafka消费者功能
             kafka_service/funasr_producer.py    提供kafka生产者功能