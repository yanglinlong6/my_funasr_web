from mysql_service import MysqlHelper
from config import DbConect

db = MysqlHelper.MysqlHelper(
    DbConect.ali_asr_model
)


def insert_ali_asr_model_res(task_id: str, url: str):
    insert_sql = (
        f"INSERT INTO dj_smartcarlife.ali_asr_model_res (task_id,file_url,task_status) VALUES ('{task_id}','{url}',0);")
    return db.execute_modify(insert_sql)


def update_ali_asr_model_res(task_id: str, json_output: str):
    update_sql = (
        f"update ali_asr_model_res t set t.output_data = '{json_output}',t.task_status = 1 where t.task_id = '{task_id}';")
    return db.execute_modify(update_sql)


def update_ali_asr_model_res_fail(task_id: str):
    update_sql = (
        f"update ali_asr_model_res t set t.task_status = 2 where t.task_id = '{task_id}';")
    return db.execute_modify(update_sql)


def select_ali_asr_model_res(task_id: str):
    select_sql = (
        f"select id,task_id,file_url,task_status,output_data from ali_asr_model_res aamr where del_flag = 0 and "
        f"task_id = '{task_id}';")
    return db.execute_select(select_sql)


def select_ali_asr_model_wait():
    select_sql = (
        f"select id,task_id,file_url,task_status,output_data from ali_asr_model_res aamr where aamr.del_flag = 0 and aamr.output_data  is null;")
    return db.execute_select(select_sql)
