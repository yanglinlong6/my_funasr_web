from mysql_service import MysqlHelper
from config import DbConect
from config.config import ConfigInfo
from mysql_service import mysql_utils
from mysql_service.mysql_pool import ConnPool

# db = MysqlHelper.MysqlHelper(
#     DbConect.ali_asr_model
# )

config = {
    "host": ConfigInfo.host,
    "port": ConfigInfo.port,
    "user": ConfigInfo.user,
    "password": ConfigInfo.password,
    "database": ConfigInfo.database
}

pool = ConnPool(
    **config
)


def insert_ali_asr_model_res(task_id: str, url: str):
    insert_sql = (
        "INSERT INTO dj_smartcarlife.ali_asr_model_res (task_id,file_url,task_status) VALUES (%s,%s,%s);")
    return pool.insert_one(insert_sql, (task_id, url, 0,))


def update_ali_asr_model_res(task_id: str, json_output: str, execute_time: int):
    update_sql = (
        "update ali_asr_model_res t set t.output_data = %s,t.task_status = 1, t.execute_time = %s where t.task_id = %s;")
    return pool.update_one(update_sql, (json_output, execute_time, task_id,))


def update_ali_asr_model_res_fail(task_id: str, exception: str):
    update_sql = (
        f"update ali_asr_model_res t set t.task_status = 2, t.exception_log = %s where t.task_id = %s;")
    return pool.update_one(update_sql, (exception, task_id,))


def select_ali_asr_model_res(task_id: str):
    select_sql = (
        f"select id,task_id,file_url,task_status,output_data from ali_asr_model_res aamr where del_flag = 0 and "
        f"task_id = %s;")
    return pool.select_all(select_sql, (task_id,))


def select_ali_asr_model_wait():
    select_sql = (
        f"select id,task_id,file_url,task_status,output_data from ali_asr_model_res aamr where aamr.del_flag = 0 and "
        f"aamr.output_data is null and aamr.task_status = %s;")
    return pool.select_all(select_sql, 0)
