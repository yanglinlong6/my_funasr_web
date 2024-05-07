import time
from funasr import AutoModel

# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need
model = AutoModel(
    model="paraformer-zh",
    # vad_model="fsmn-vad",
    # punc_model="ct-punc-c",
    # spk_model="cam++",
    # openai_model="Whisper-large-v3",
    # ncpu=8,
)


def write_text(text):
    with open("audio.txt", "a+", encoding="utf8") as fw:
        fw.write(text.strip())
        fw.write("\n")


consuming_start_time = time.perf_counter()

res = model.export(quantize=False)
print(res)
# res = model.generate(input="asr_example.wav", batch_size_s=300, hotword="魔搭")
# res = model.generate(input="123456.wav", batch_size_s=300, hotword="魔搭")
# res = model.generate(
#     input="北京店1-2024-02-29_14.58.11.MP3",
#     batch_size_s=300,
#     hotword="问界 80\n电瓶 100\n保修 100\n问界店 100\nM7\nM5\nM9",
# )
# res=model.export(input="北京店1-2024-02-29_14.58.11.MP3")
# print(f"res:{res}")
# sentence_info = res[0]["sentence_info"]
# print(f"res_sentence_info:{sentence_info}")
# # print(res[0]["sentence_info"])
# spk = 0
# total_time = 0
# content = ""
# for one in sentence_info:
#     # print(one)
#     # print(one["end"] - one["start"])
#     # print(one["text"])
#     # print(one["spk"])
#     # print(f'{one["end"] - one["start"]}; {one["text"]}; {one["spk"]}')
#     total_time = total_time + (one["end"] - one["start"])
#     if spk == one["spk"]:
#         content = content + one["text"]
#     else:
#         text = f'角色{spk + 1} : {content} -- 时长:{total_time}ms'
#         print(text)
#         write_text(text)
#         total_time = 0
#         content = one["text"]
#         spk = one["spk"]

# if content is not None:
#     text = f'角色{spk + 1} : {content} -- 时长:{total_time}ms'
#     print(text)
#     write_text(text)


# consuming_end_time = time.perf_counter()
# print(
#     f"Function transform_file executed in {(consuming_end_time - consuming_start_time)} 秒"
# )
