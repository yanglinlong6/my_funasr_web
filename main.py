import argparse
import traceback
from datetime import timedelta
from logger import log
import json
import os
import random
import shutil
import threading
import time
import requests
import uuid
import MysqlHelper
import DbConect
from funasr import AutoModel
import pydantic
import uvicorn
from fastapi import Body, FastAPI, File, UploadFile
from funasr_service import FunasrService
from pydantic import BaseModel
from funasr.download.file import download_from_url
import multiprocessing

app = FastAPI()
# 全局进程池
pool = multiprocessing.Pool(processes=1)

db = MysqlHelper.MysqlHelper(
    DbConect.ali_asr_model
)

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
    log.info(f"Function transform_file executed in {(consuming_end_time - consuming_start_time)} 秒")
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
        log.info(f"Function create_file executed in {(consuming_end_time - consuming_start_time)} 秒")
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
        log.info(
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


class model_output():
    def __init__(self, role, offset, duration, content):
        self.role = role
        self.offset = offset
        self.duration = duration
        self.content = content

    def to_dict(self):
        return {
            'role': self.role,
            'offset': self.offset,
            'duration': self.duration,
            'content': self.content
        }


def deal_worker(url: str, task_id: str):
    """
    要执行的函数，在子进程中运行
    """
    try:
        # 获取当前进程的名字
        name = multiprocessing.current_process().name
        log.info(f"Worker {task_id} is running...进程名字 {name}")
        consuming_start_time = time.perf_counter()
        # 解析音频
        res = FunasrService(url).transform()
        log.info("res: %s" % res)
        if len(res) < 1:
            updateSql = (
                f"update ali_asr_model_res t set t.output_data = '{res}',t.task_status = 1 where t.task_id = '{task_id}';")
            db.execute_modify(updateSql)
            return
        output = []
        content = ""
        spk = 0
        duration = 0
        offset = 0
        for one in res[0]["sentence_info"]:
            duration = duration + (one["end"] - one["start"])
            offset = one["start"]
            if spk == one["spk"]:
                content = content + one["text"]
            else:
                output.append(model_output(spk, offset, duration, content).to_dict())
                duration = 0
                content = one["text"]
                spk = one["spk"]

        if content != "":
            output.append(model_output(spk, offset, duration, content).to_dict())
        json_output = json.dumps(output, ensure_ascii=False)
        log.info(f"output:{json_output}")
        updateSql = (
            f"update ali_asr_model_res t set t.output_data = '{json_output}',t.task_status = 1 where t.task_id = '{task_id}';")
        db.execute_modify(updateSql)
        log.info(
            f"Function create_upload_file executed in {(time.perf_counter() - consuming_start_time)} s"
        )
        log.info(f"Worker {task_id} finished.")
    except Exception as e:
        updateSql = (f"update ali_asr_model_res t set t.task_status = 2 where t.task_id = '{task_id}';")
        db.execute_modify(updateSql)
        log.error(f"Worker error{e}")
        traceback.print_exc()
        return {"Worker error": str(e)}

class UrlParam(BaseModel):
    url: str


@app.post("/funasr/url/")
async def create_url(param: UrlParam):
    try:
        task_id = uuid.uuid1()
        url = param.url
        insertSql = (
            f"INSERT INTO dj_smartcarlife.ali_asr_model_res (task_id,file_url,task_status) VALUES ('{task_id}','{url}',0);")
        res = db.execute_modify(insertSql)
        # process = multiprocessing.Process(target=deal_worker, args=(url, task_id,))
        # log.info(f"process:{process}")
        # process.start()
        # multiprocessing.freeze_support()
        pool.apply(deal_worker, (url, task_id))
        # 关闭进程池，不再接受新的任务
        pool.close()

        response = BaseResponse(
            code=200,
            msg="success",
            data={"task_id": str(task_id)}
        )
        log.info(f"response：{response}")
        return response
    except Exception as e:
        log.error(f"error：{e}")
        traceback.print_exc()
        return {"error": str(e)}


if __name__ == "__main__":
    multiprocessing.freeze_support()
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
