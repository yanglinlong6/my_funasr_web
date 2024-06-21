import argparse
from funasr import AutoModel
import traceback
import os
import shutil
import uuid
import pydantic
import uvicorn
import json
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from log.logger import log
from kafka import KafkaConsumer

app = FastAPI()

consumer_new = KafkaConsumer(
    # ConfigInfo.kafka_consumer_analysis_topic,
    # bootstrap_servers=ConfigInfo.kafka_consumer_bootstrap_servers,  # Kafka broker 的地址
    # group_id=ConfigInfo.kafka_consumer_group_id,  # 消费者组 ID
    # auto_offset_reset=ConfigInfo.kafka_consumer_auto_offset_reset,  # 从最早的消息开始消费
)

class BaseResponse(BaseModel):
    code: int = pydantic.Field(200, description="HTTP status code")
    msg: str = pydantic.Field("success", description="HTTP status message")
    data: object = pydantic.Field([], description="HTTP return data")
    time_consuming: int = pydantic.Field(
        11, description="HTTP return data time consuming"
    )

class UrlParam(BaseModel):
    url: str

model = AutoModel(
    model="iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    vad_model="fsmn-vad",
    punc_model="ct-punc-c",
    spk_model="cam++",
    ncpu=2,
    ngpu=0,
    device="cpu",
    batch_size=1,
)
def handle_process(message: str):
    try:

        task_id = json.loads(message)["task_id"]
        # url = select_db(task_id) 查询数据库url todo
        url = "https://glsk-oss.oss-cn-shenzhen.aliyuncs.com/quality/merged_17177345226501717730109711.mp3"
        # 解析音频
        output_res = model.generate(input=url,
                                    batch_size_s=1,
                                    batch_size_threshold_s=60 * 60,
                                    hotword="")
        # update_db(task_id,output_res) 更新数据库 todo
    except Exception as e:
        log.error("funasr handle_process Exception: " + str(traceback.format_exc()))



@app.post("/funasr/url/")
async def create_url(param: UrlParam):
    try:
        log.info(f"funasr create_url api param:{param}")
        url = param.url
        if url is None:
            return BaseResponse(
                code=-1,
                msg="error",
                data="url is empty"
            )
        if url == "" or len(url) < 1 or not url.startswith("http"):
            return BaseResponse(
                code=-1,
                msg="error",
                data="url format error"
            )
        task_id = str(uuid.uuid1())
        # insert_db(task_id,url) 插入数据库 todo
        # task_id推送kafka todo
        response = BaseResponse(
            code=200,
            msg="success",
            data={"task_id": str(task_id)}
        )
        log.info(f"response：{response}")
        return response
    except Exception as e:
        log.error(f"error：{traceback.format_exc()}")
        return BaseResponse(
            code=-1,
            msg="error",
            data=str(e)
        )

if __name__ == "__main__":
    log.info("funasr main starting...")
    save_path = "./audio/"
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default="dev")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7888)
    args = parser.parse_args()
    uvicorn.run(
        app="main:app",
        host=args.host,
        port=args.port,
        workers=1,
        ws_ping_interval=600,
        ws_ping_timeout=600,
        timeout_keep_alive=600,
    )

def consume_kafka():
    # kafka消费消息并进行逻辑处理
    try:
        for message in consumer_new:
            if message is None:
                continue
            log.info(f"Received message: {message}")
            # 处理逻辑
            handle_process(str(message.value.decode('utf-8')))
            print("task handle")
    except Exception as e:
        log.error("funasr consumer Exception: " + str(traceback.format_exc()))