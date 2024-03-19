import time
import traceback

from log.logger import log
from mysql_service import funasr_db
from mysql_service import MysqlHelper
from config import DbConect

consuming_start_time = time.perf_counter()

db = MysqlHelper.MysqlHelper(
    DbConect.ali_asr_model
)

task_id = str("63764ce2-e5cb-11ee-928c-b083fec01e48")
url = "https://smartcard-1253080096.cos.ap-guangzhou.myqcloud.com/audio/4827E2F0CD24_1709084561_4827E2F0CD24-1709084561.MP3"
# res = funasr_db.insert_ali_asr_model_res(task_id, url)
# print(f"res:{res}")


sql = "INSERT INTO dj_smartcarlife.ali_asr_model_res (task_id,file_url,task_status) VALUES (" \
      "'47f9402c-e5cc-11ee-928c-b083fec01e48','https://img01.glsx.com.cn/weapp/resource/wav/122m4a.wav',0);"
res = db.execute_modify(sql)
print(res)
try:
    time.sleep(2)
    execute_time = time.perf_counter() - consuming_start_time
    log.info(
        f"Function create_upload_file executed in {execute_time} s"
    )
    funasr_db.update_ali_asr_model_res(task_id, task_id, int((execute_time * 1000)))
    if res is None or isinstance(res, bool) or len(res) < 1:
        print("======")
except Exception as e:
    print(f"e:{traceback.format_exc()}")
    funasr_db.update_ali_asr_model_res_fail(task_id, str(traceback.format_exc()))
