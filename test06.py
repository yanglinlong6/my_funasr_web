import time
from funasr import AutoModel

import funasr_service

# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need

model = AutoModel(
    # model="iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    model="iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
    # model="iic/speech_conformer_asr_nat-zh-cn-16k-aishell2-vocab5212-pytorch",
    vad_model="iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
    # punc_model="iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
    punc_model="iic/punc_ct-transformer_cn-en-common-vocab471067-large",
    spk_model="iic/speech_campplus_sv_zh-cn_16k-common",
)


def write_text(text):
    with open("audio.txt", "a+", encoding="utf8") as fw:
        fw.write(text.strip())
        fw.write("\n")


consuming_start_time = time.perf_counter()
# res = model.generate(input="asr_example.wav", batch_size_s=300, hotword="魔搭")
# res = model.generate(input="123456.wav", batch_size_s=300, hotword="魔搭")
res = model.generate(
    # input="asr_train_example.mp3",
    input="https://glsk-oss.oss-cn-shenzhen.aliyuncs.com/quality/merged_17198870994551719886349986.mp3",
    batch_size_s=300,
    hotword="问界 80\n电瓶 100\n保修 100\n问界店 100\nM7\nM5\nM9",
    # return_raw_text=True,     # return raw text recognition results splited by space of equal length with timestamp
    preset_spk_num=2,         # preset speaker num for speaker cluster model
    # sentence_timestamp=True,  # return sentence level information when spk_model is not given
    decoding_ctc_weight=0.0,
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
