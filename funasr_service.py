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
    punc_model="ct-punc",
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
        res = model.generate(input=self.path, batch_size_s=200, hotword="问界 80")
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
        res = funasr_db.select_ali_asr_model_res(task_id)
        if res is None or isinstance(res, bool) or len(res) < 1:
            return
        output_data = json.loads(res)[0]["output_data"]
        if output_data is not None:
            return
        url = json.loads(res)[0]["file_url"]
        log.info(f"Worker {task_id} is running... url:{url}")
        consuming_start_time = time.perf_counter()
        # 解析音频
        res = FunasrService(url).transform()
        if len(res) < 1:
            log.info("res: %s" % res)
            funasr_db.update_ali_asr_model_res(task_id, res, 0)
            return
        sentence_info = res[0]["sentence_info"]
        log.info("res.sentence_info: %s" % sentence_info)
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
        log.info(f"output:{json_output}")
        execute_time = time.perf_counter() - consuming_start_time
        funasr_db.update_ali_asr_model_res(task_id, json_output, int((execute_time * 1000)))
        log.info(
            f"Function create_upload_file executed in {execute_time} s"
        )
        log.info(f"Worker {task_id} finished.")
    except Exception as e:
        funasr_db.update_ali_asr_model_res_fail(task_id)
        log.error(f"Worker error{e}")
        traceback.print_exc()
        return {"Worker error": str(e)}
