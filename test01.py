import time
from funasr import AutoModel

import funasr_service

# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need
model = AutoModel(
    # model="paraformer-zh",
    # model="paraformer-zh-spk",
    model="c:/Users/chizw/.cache/modelscope/hub/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-Common-vocab8404-pytorch",
    # model="c:/Users/chizw/.cache/modelscope/hub/iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-Common-vocab8404-pytorch",
    # model_revision="v2.0.4",
    vad_model="fsmn-vad",
    # punc_model="ct-punc-c",
    punc_model="ct-punc",
    # spk_model="cam++",
    spk_model="iic/speech_eres2net_sv_zh-cn_16k-common",
    # spk_model="cam++",
    # spk_model_revision="v1.0.0",
    # spk_model="iic/speech_eres2net-large_speaker-diarization_common",
    # openai_model="Whisper-large-v3",
    ncpu=2,
    device="cpu",
    batch_size=1,
)


def write_text(text):
    with open("audio.txt", "a+", encoding="utf8") as fw:
        fw.write(text.strip())
        fw.write("\n")


consuming_start_time = time.perf_counter()
# res = model.generate(input="asr_example.wav", batch_size_s=300, hotword="魔搭")
# res = model.generate(input="123456.wav", batch_size_s=300, hotword="魔搭")
res = model.generate(
    input="https://glsk-oss.oss-cn-shenzhen.aliyuncs.com/quality/7cf068ad-2592-4033-93c0-02c9b2735189.mp3",
    batch_size_s=1,
    batch_size_threshold_s=60 * 60,
    hotword="问界 100\n质保经理 100\n易损易耗件 100\n电瓶 100\nM5 100\nM7 100\nM9 100\n石子 100"
            "\n橡胶棒 100\n电子助力泵 100\n电子真空助力泵 100\n充电桩 100\n密封圈 100\n4S店 100\n老化 100"
            "\n打死 100\n油车 100\n电车 100\n备忘录 100\n自费 100\n胶套求成密封圈 100\n安信无忧 100"
            "\n全车易损耗件 100\n厂家 100\n喷漆 100\n封釉 100\n雾化 100\n里程 100\n延保 100\n外地牌 100"
            "\n轮胎 100\n胶条 100\n漆面 100\n充电接口 100\n车衣 100\n传动车身 100\n喜提新车 100",
)
print(f"res:{res}")
sentence_info = res[0]["sentence_info"]
print(f"res_sentence_info:{sentence_info}")
# print(res[0]["sentence_info"])
spk = 0
total_time = 0
content = ""
for one in sentence_info:
    # print(one)
    # print(one["end"] - one["start"])
    # print(one["text"])
    # print(one["spk"])
    # print(f'{one["end"] - one["start"]}; {one["text"]}; {one["spk"]}')
    total_time = total_time + (one["end"] - one["start"])
    if spk == one["spk"]:
        content = content + one["text"]
    else:
        text = f"角色{spk + 1} : {content} -- 时长:{total_time}ms"
        print(text)
        write_text(text)
        total_time = 0
        content = one["text"]
        spk = one["spk"]

if content is not None:
    text = f"角色{spk + 1} : {content} -- 时长:{total_time}ms"
    print(text)
    write_text(text)

res = funasr_service.fine_grained_transform_output(sentence_info)
print(res)

consuming_end_time = time.perf_counter()
print(
    f"Function transform_file executed in {(consuming_end_time - consuming_start_time)} 秒"
)
