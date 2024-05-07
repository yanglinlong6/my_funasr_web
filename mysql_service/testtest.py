from funasr import AutoModel
import soundfile as sf
from mysql_service import funasr_db

# # 初始化VAD模型和流式ASR模型
# vad_model = AutoModel(model="fsmn-vad")
# asr_model = AutoModel(model="paraformer-zh-streaming", chunk_size=[0, 10, 5])
#
# # 读取长音频文件
# long_audio_path = "D:/software/python/project/funasr_web/字节-安静环境.mp3"
# speech, sample_rate = sf.read(long_audio_path)
#
# # 使用VAD模型分割音频
# vad_segments = vad_model.generate(input=long_audio_path)
#
# # 对每个VAD分割的片段应用流式ASR模型
# for segment_start, segment_end in vad_segments:
#     # 根据VAD分割结果获取音频片段
#     segment = speech[int(segment_start * sample_rate):int(segment_end * sample_rate)]
#     # 流式处理音频片段
#     total_chunk_num = int(len(segment) / asr_model.chunk_size[1] * 960) + 1
#     for i in range(total_chunk_num):
#         speech_chunk = segment[i * asr_model.chunk_size[1] * 960:(i + 1) * asr_model.chunk_size[1] * 960]
#         is_final = i == total_chunk_num - 1
#         res = asr_model.generate(input=speech_chunk, is_final=is_final)
#         print(res)
#

