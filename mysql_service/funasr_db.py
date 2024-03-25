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


def update_ali_asr_model_res_fail(task_id: str, exception_msg: str, exception: str):
    update_sql = (
        "update ali_asr_model_res t set t.task_status = 2, t.exception_msg = %s, t.exception_log = %s, "
        "exception_limit = exception_limit + 1 "
        "where t.task_id = %s;")
    return pool.update_one(update_sql, (exception_msg, exception, task_id,))


def update_ali_asr_model_res_skip(task_id: str):
    update_sql = (
        "update ali_asr_model_res t set t.task_status = 2,"
        "exception_limit = exception_limit + 1 "
        "where t.task_id = %s;")
    return pool.update_one(update_sql, (task_id,))


def select_ali_asr_model_res(task_id: str):
    select_sql = (
        "select id,task_id,file_url,task_status,output_data,exception_msg"
        " from ali_asr_model_res aamr"
        " where del_flag = 0 and "
        "task_id = %s and exception_limit < 3;")
    return pool.select_all(select_sql, (task_id,))


def select_ali_asr_model_wait():
    select_sql = (
        "select id,task_id,file_url,task_status,output_data from ali_asr_model_res aamr where aamr.del_flag = 0 and "
        "aamr.output_data is null and aamr.task_status != %s and exception_limit < 3;")
    return pool.select_all(select_sql, 1)


def select_process_fail_task(process_name: str):
    select_sql = (
        "select id,task_id,file_url,task_status from ali_asr_model_res aamr where aamr.del_flag = 0 "
        "and aamr.task_status = 0 and aamr.execute_process_name = %s;"
    )
    return pool.select_all(select_sql, (process_name))


def update_process_task(task_id: str, process_name: str):
    update_sql = (
        "update ali_asr_model_res t set t.execute_process_name = %s where task_id = %s;"
    )
    return pool.update_one(update_sql, (process_name, task_id))


def select_process_all_end():
    sql = (
        "select count(aamr.id) from ali_asr_model_res aamr where aamr.del_flag = 0 "
        "and aamr.execute_process_name is not null and aamr.task_status = %s;"
    )
    return pool.select_all(sql, (0))


def select_time_out_task():
    sql = (
        "select id,task_id,file_url,task_status from ali_asr_model_res aamr where aamr.del_flag = 0 "
        "and aamr.output_data is null and aamr.execute_process_name is not null and exception_limit < 3"
        "and aamr.updated_time < TIMESTAMPADD(MINUTE, -%s, NOW());"
    )
    return pool.select_all(sql, (30))
