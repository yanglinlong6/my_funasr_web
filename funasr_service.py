import multiprocessing
import threading
import time
from funasr import AutoModel
from kafka_service import funasr_producer
from log.logger import log
import json
import traceback
from mysql_service import funasr_db

# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need

model = AutoModel(
    # model='iic/speech_UniASR_asr_2pass-cantonese-CHS-16k-common-vocab1468-tensorflow1-online',
    # model='iic/speech_UniASR_asr_2pass-cantonese-CHS-16k-common-vocab1468-tensorflow1-offline',
    # model="damo/speech_UniASR_asr_2pass-cantonese-CHS-16k-common-vocab1468-tensorflow1-online",
    # decoding_model="offline",
    # model_revision="v2.0.4",
    # model="dengcunqin/speech_seaco_paraformer_large_asr_nat-zh-cantonese-en-16k-common-vocab11666-pytorch",
    model_revision="master",
    model="iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    # model="iic/speech_paraformer-large-vad-punc-spk_asr_nat-zh-cn",
    # model_revision='v1.0.1',
    vad_model="fsmn-vad",
    punc_model="ct-punc-c",
    spk_model="cam++",
    # spk_model="iic/speech_campplus_speaker-diarization_common",
    # spk_model="damo/speech_campplus_speaker-diarization_common",
    # spk_model="iic/speech_campplus_sv_zh-cn_16k-common",
    vad_model_revision="master",
    punc_model_revision="master",
    spk_model_revision="master",
    # spk_model_revision="v2.0.2",
    ncpu=2,
    device="cpu",
    batch_size=1,
    #     model="iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    #     vad_model="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
    #     punc_model="iic/punc_ct-transformer_cn-en-common-vocab471067-large",
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
        res = model.generate(input=self.path,
                             batch_size_s=1,
                             batch_size_threshold_s=60 * 60,
                             hotword="问界 100\n质保经理 100\n易损易耗件 100\n电瓶 100\nM5 100\nM7 100\nM9 100\n石子 100"
                                     "\n橡胶棒 100\n电子助力泵 100\n电子真空助力泵 100\n充电桩 100\n密封圈 100\n4S店 100\n老化 100"
                                     "\n打死 100\n油车 100\n电车 100\n备忘录 100\n自费 100\n胶套求成密封圈 100\n安信无忧 100"
                                     "\n全车易损耗件 100\n厂家 100\n喷漆 100\n封釉 100\n雾化 100\n里程 100\n延保 100\n外地牌 100"
                                     "\n轮胎 100\n胶条 100\n漆面 100\n充电接口 100\n车衣 100\n传动车身 100\n喜提新车 100")
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
        process = multiprocessing.current_process()
        log.info(
            f"handle_process_start process:{process},thread name:{threading.current_thread().name}，"
            f"Received task_id: {message}")
        # 处理逻辑
        start_time = time.time()
        task_id = json.loads(message)["task_id"]
        deal_worker(task_id)
        log.info(f"handle_process_end process:{process} task_id:{task_id} 耗时:" + str(time.time() - start_time))
    except Exception as e:
        log.error("funasr handle_process Exception: " + str(traceback.format_exc()))


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
        exception_msg = sql_res[0]["exception_msg"]
        if exception_msg is not None:
            if exception_msg == "list index out of range" \
                    or exception_msg == "Unspecified internal error." \
                    or exception_msg == "local variable 'raw_text' referenced before assignment":
                funasr_db.update_ali_asr_model_res_skip(task_id)
                return
        funasr_db.update_process_task(task_id, str(multiprocessing.current_process().name))
        url = sql_res[0]["file_url"]
        if url == "" or len(url) < 1 or not url.startswith("http"):
            funasr_db.update_ali_asr_model_res_skip(task_id)
            return
        log.info(f"Worker {task_id} is running... url:{url}")
        consuming_start_time = time.perf_counter()
        # 解析音频
        output_res = FunasrService(url).transform()
        if len(output_res) < 1:
            log.info("output_res: %s" % output_res)
            funasr_db.update_ali_asr_model_res(task_id, str(output_res), 0)
            return
        sentence_info = output_res[0]["sentence_info"]
        json_output = fine_grained_transform_output(sentence_info)
        # log.info("json_output: %s" % json_output)
        execute_time = time.perf_counter() - consuming_start_time
        funasr_db.update_ali_asr_model_res(task_id, json_output, int((execute_time * 1000)))
        log.info(
            f"Function create_upload_file executed in {execute_time} s"
        )
        log.info(f"Worker {task_id} finished.")
    except Exception as e:
        log.error(f"Worker error：{traceback.format_exc()}")
        funasr_db.update_ali_asr_model_res_fail(task_id, str(e), traceback.format_exc())
        # funasr_producer.send_task_id(task_id)
        return


def fine_grained_transform_output(sentence_info):
    output = []
    for one in sentence_info:
        duration = one["end"] - one["start"]
        output.append(model_output(one["spk"], one["start"], duration, one["text"]).to_dict())
    json_output = json.dumps(output, ensure_ascii=False)
    json_output = json_output.replace("m 五", "M5").replace("m 七", "M7").replace("m 九", "M9").replace("8年", "八年") \
        .replace("3个月", "三个月").replace("5千公里", "五千公里").replace("1年", "一年").replace("1万公里", "一万公里") \
        .replace("4年", "四年").replace("5年", "五年").replace("100000公里", "十万公里").replace("6年", "六年") \
        .replace("12万", "十二万").replace("16万", "十六万")
    return json_output


def simple_transform_output(sentence_info):
    output = []
    for one in sentence_info:
        output.append((str(one["spk"]) + ":" + one["text"] + '\n'))
    json_output = json.dumps(output, ensure_ascii=False)
    json_output = json_output.replace(" m 五", "M5").replace(" m 七", "M7").replace(" m 九", "M9")
    return json_output


def merge_spk_transform_output(sentence_info):
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
    return json_output


def task_compensate_send():
    try:
        log.info("task_compensate_send start")
        res = funasr_db.select_time_out_task()
        if res is not None and len(res) > 0:
            for item in res:
                funasr_producer.send_task_id(item["task_id"])
        log.info("task_compensate_send end")
    except Exception as e:
        log.error("task_compensate_send error", e)
