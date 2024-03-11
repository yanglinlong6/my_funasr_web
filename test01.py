import time
from funasr import AutoModel
# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need
model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc-c",
    spk_model="cam++",
    ncpu=8,
)


def write_text(text):
    with open("audio.txt", "a+", encoding="utf8") as fw:
        fw.write(text.strip())
        fw.write("\n")


consuming_start_time = time.perf_counter()
# res = model.generate(input="asr_example.wav", batch_size_s=300, hotword="魔搭")
# res = model.generate(input="123456.wav", batch_size_s=300, hotword="魔搭")
res = model.generate(
    input="陕西西安店-陕西店1-2024-02-29_14.39.15-43.0.MP3",
    batch_size_s=300,
    hotword="华为问界 80",
)
print(res)
print(res[0]["sentence_info"])
print(res[0]["sentence_info"])
for one in res[0]["sentence_info"]:
    # print(one)
    # print(one["end"] - one["start"])
    # print(one["text"])
    # print(one["spk"])
    # print(f'{one["end"] - one["start"]}; {one["text"]}; {one["spk"]}')
    start_time=one['start']
    end_time = one["end"]
    text = f'{"角色1" if one["spk"] == 0 else "角色2"} : {one["text"]} -- 时长:{end_time-start_time}ms'
    print(text)
    write_text(text)

consuming_end_time = time.perf_counter()
print(
    f"Function transform_file executed in { (consuming_end_time - consuming_start_time)} 秒"
)
