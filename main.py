import argparse
from datetime import timedelta
import json
import logging
import os
import random
import shutil
import threading
import time
import requests
import asyncio

import pydantic
import uvicorn
from fastapi import Body, FastAPI, File, UploadFile
from funasr_service import FunasrService
from pydantic import BaseModel
from funasr.download.file import download_from_url
import multiprocessing

logger = logging.getLogger()
app = FastAPI()


class BaseResponse(BaseModel):
    code: int = pydantic.Field(200, description="HTTP status code")
    msg: str = pydantic.Field("success", description="HTTP status message")
    data: object = pydantic.Field([], description="HTTP return data")
    time_consuming: int = pydantic.Field(
        11, description="HTTP return data time consuming"
    )

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": [],
                "time_consuming": 11,
            }
        }


def generate_random_filename():
    timestamp = int(time.time())  # 获取当前时间戳
    random_number = random.randint(1000, 9999)  # 生成一个随机数
    filename = f"file_{timestamp}_{random_number}"  # 创建文件名
    return filename + ".wav"


@app.get("/")
def hello_world():
    return "Hello World!"


@app.get("/funasr/")
async def transform_file():
    consuming_start_time = time.perf_counter()
    res = FunasrService("asr_example.wav").transform()
    # res = FunasrService("123456.wav").transform()
    answer = []
    print(str(res[0]["sentence_info"]))
    for one in res[0]["sentence_info"]:
        start_time = one['start']
        end_time = one['end']
        answer.append(
            f'{"角色1" if one["spk"] == 0 else "角色2"} : {one["text"]} -- 时长:{end_time - start_time}ms'
        )
    consuming_end_time = time.perf_counter()
    print(f"Function transform_file executed in {(consuming_end_time - consuming_start_time)} 秒")
    logger.info(f"Function transform_file executed in {(consuming_end_time - consuming_start_time)} 秒")
    return BaseResponse(
        code=200,
        msg=res[0]["text"],
        data=answer,
        time_consuming=int(consuming_end_time - consuming_start_time),
    )


@app.post("/funasr/file/")
async def create_file(file: bytes = File()):
    # 获取文件内容
    # 打开文件以写入模式
    try:
        consuming_start_time = time.perf_counter()
        save_path = f"./audio/"
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        save_path = f"./audio/{str(threading.current_thread().ident)}/"
        if not os.path.exists(save_path):
            os.mkdir(save_path)

        save_file = os.path.join(save_path, generate_random_filename())
        with open(save_file, "wb") as f:
            # 将接收到的文件内容写入文件中
            # while content := await file.read(1024):
            #     f.write(content)
            f.write(file)

        print({"file_size": len(file)})
        # 解析音频
        res = FunasrService(save_file).transform()
        answer = []
        print(str(res[0]["sentence_info"]))
        for one in res[0]["sentence_info"]:
            start_time = one['start']
            end_time = one['end']
            answer.append(
                f'{"角色1" if one["spk"] == 0 else "角色2"} : {one["text"]} -- 时长:{end_time - start_time}ms'
            )
        consuming_end_time = time.perf_counter()
        print(f"Function create_file executed in {(consuming_end_time - consuming_start_time)} 秒")
        logger.info(f"Function create_file executed in {(consuming_end_time - consuming_start_time)} 秒")
        os.remove(save_file)
        response = BaseResponse(
            code=200,
            msg=res[0]["text"],
            data=answer,
            time_consuming=int(consuming_end_time - consuming_start_time),
        )
        print(f"response：{response}")
        return response
    except Exception as e:
        os.remove(save_file)
        return {"error": str(e)}


@app.post("/funasr/uploadfile/")
async def create_upload_file(file: UploadFile):
    try:
        consuming_start_time = time.perf_counter()
        fn = file.filename
        save_path = f"./audio/"
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        save_path = f"./audio/{str(threading.current_thread().ident)}/"
        if not os.path.exists(save_path):
            os.mkdir(save_path)

        save_file = os.path.join(save_path, fn)
        with open(save_file, "wb") as f:
            # 将接收到的文件内容写入文件中
            while content := await file.read(1024):
                f.write(content)
        print({"filename": file.filename})
        # 解析音频
        res = FunasrService(save_file).transform()
        answer = []
        print(str(res[0]["sentence_info"]))
        for one in res[0]["sentence_info"]:
            start_time = one['start']
            end_time = one['end']
            answer.append(
                f'{"角色1" if one["spk"] == 0 else "角色2"} : {one["text"]} -- 时长:{end_time - start_time}ms'
            )
        consuming_end_time = time.perf_counter()
        print(f"Function create_upload_file executed in {(consuming_end_time - consuming_start_time)} 秒")
        logger.info(
            f"Function create_upload_file executed in {(consuming_end_time - consuming_start_time)} 秒"
        )
        os.remove(save_file)
        return BaseResponse(
            code=200,
            msg=res[0]["text"],
            data=answer,
            time_consuming=int(consuming_end_time - consuming_start_time),
        )
    except Exception as e:
        os.remove(save_file)
        return {"error": str(e)}


def deal_worker(url):
    """
    要执行的函数，在子进程中运行
    """
    print(f"Worker {url} is running...")
    # 解析音频
    res = FunasrService(url).transform()
    time.sleep(1)
    print(f"Worker {url} finished.")


class UrlParam(BaseModel):
    url: str

@app.post("/funasr/url")
async def create_url(param: UrlParam):
    try:
        process = multiprocessing.Process(target=deal_worker, args=(param.url))
        process.start()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    save_path = "./audio/"
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    parser = argparse.ArgumentParser()
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
