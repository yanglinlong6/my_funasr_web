from mysql_service import DbConect, MysqlHelper

db = MysqlHelper.MysqlHelper(
    DbConect.ali_asr_model
)


def insert_ali_asr_model_res(task_id: str, url: str):
    insertSql = (
        f"INSERT INTO dj_smartcarlife.ali_asr_model_res (task_id,file_url,task_status) VALUES ('{task_id}','{url}',0);")
    return db.execute_modify(insertSql)


def update_ali_asr_model_res(task_id: str, json_output: str):
    updateSql = (
        f"update ali_asr_model_res t set t.output_data = '{json_output}',t.task_status = 1 where t.task_id = '{task_id}';")
    db.execute_modify(updateSql)


def update_ali_asr_model_res_fail(task_id: str):
    updateSql = (
        f"update ali_asr_model_res t set t.task_status = 2 where t.task_id = '{task_id}';")
    db.execute_modify(updateSql)
