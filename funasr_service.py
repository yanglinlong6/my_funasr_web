import time
from funasr import AutoModel
from logger import log

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
    def __init__(self,path):
        self.path = path

    @timeit
    def transform(self):
        res = model.generate(input=self.path, batch_size_s=300, hotword="魔搭")
        # print(res)
        return res
