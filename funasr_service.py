import time
from funasr import AutoModel
from log.logger import log
import json
import traceback

from mysql_service import funasr_db

# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need

model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc-c",
    spk_model="cam++",
    ncpu=8,
)


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Function {func.__name__} executed in {total_time} seconds.")
        log.info(f"Function {func.__name__} executed in {total_time} seconds.")
        return result

    return wrapper


class FunasrService(object):
    def __init__(self, path):
        self.path = path

    @timeit
    def transform(self):
        res = model.generate(input=self.path, batch_size_s=200, hotword="""问界\n质保经理 80\n易损易耗件 80\n电瓶 80\nM5 80
                \nM7 80\nM9 80\n石子 80\n橡胶棒 80\n电子助力泵 80\n电子真空助力泵 80\n充电桩 80\n密封圈 80\n4S店 80\n老化 80
                """)
        # print(res)
        return res


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


def handle_process(message: str):
    try:
        # 处理逻辑
        start_time = time.time()
        task_id = json.loads(message)["task_id"]
        deal_worker(task_id)
        log.info("funasr_handle_process耗时:" + str(time.time() - start_time))
    except Exception as e:
        traceback.print_exc()
        log.error("funasr consumer Exception: " + str(e))


def deal_worker(task_id: str):
    """
    要执行的函数，在子进程中运行
    """
    try:
        sql_res = funasr_db.select_ali_asr_model_res(task_id)
        if sql_res is None or isinstance(sql_res, bool) or len(sql_res) < 1:
            return
        output_data = sql_res[0]["output_data"]
        if output_data is not None:
            return
        url = sql_res[0]["file_url"]
        if url == "" or len(url) < 1 or not url.startswith("http"):
            return
        log.info(f"Worker {task_id} is running... url:{url}")
        consuming_start_time = time.perf_counter()
        # 解析音频
        output_res = FunasrService(url).transform()
        if len(output_res) < 1:
            log.info("output_res: %s" % output_res)
            funasr_db.update_ali_asr_model_res(task_id, output_res, 0)
            return
        sentence_info = output_res[0]["sentence_info"]
        log.info("output_res.sentence_info: %s" % sentence_info)
        output = []
        content = ""
        spk = 0
        duration = 0
        offset = 0
        for one in sentence_info:
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
        execute_time = time.perf_counter() - consuming_start_time
        funasr_db.update_ali_asr_model_res(task_id, json_output, int((execute_time * 1000)))
        log.info(
            f"Function create_upload_file executed in {execute_time} s"
        )
        log.info(f"Worker {task_id} finished.")
    except Exception as e:
        funasr_db.update_ali_asr_model_res_fail(task_id, traceback.format_exc())
        log.error(f"Worker error{e}")
        traceback.print_exc()
        return {"Worker error": str(e)}
