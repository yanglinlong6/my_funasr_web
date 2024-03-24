import json
import threading
import time

import pymysql
from DBUtils.PooledDB import PooledDB
from config.config import ConfigInfo
from log.logger import log


class ConnPool:

    def __init__(self, **config):
        self.pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            mincached=2,  # 初始化时，链接池中至少创建的链接，0表示不创建
            maxconnections=32,  # 连接池允许的最大连接数，0和None表示不限制连接数
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"]
        )

    def open(self):
        self.conn = self.pool.connection()
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)  # 表示读取的数据为字典类型
        return self.conn, self.cursor

    def close(self, cursor, conn):
        cursor.close()
        conn.close()
        print("close success")

    def select_one(self, sql, *args):
        """查询单条数据"""
        log.info(f"execute_select_one sql:{sql}" % args)
        conn, cursor = self.open()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        self.close(conn, cursor)
        log.info(f"execute_select_one result:{result}")
        return result

    def select_all(self, sql, args):
        """查询多条数据"""
        log.info(f"execute_select_all sql:{sql}" % args)
        conn, cursor = self.open()
        cursor.execute(sql, args)
        result = cursor.fetchall()
        self.close(conn, cursor)
        log.info(f"execute_select_all result:{result}")
        if str(result) == "()":
            return None
        else:
            return result

    def insert_one(self, sql, args):
        """插入单条数据"""
        print(sql)
        log.info(f"execute_insert_one sql:{sql}" % args)
        self.execute(sql, args, isNeed=True)
        return True

    def insert_all(self, sql, datas):
        """插入多条批量插入"""
        log.info(f"execute_insert_all sql:{sql},args:{datas}")
        conn, cursor = self.open()
        try:
            cursor.executemany(sql, datas)
            conn.commit()
            return {'result': True, 'id': int(cursor.lastrowid)}
        except Exception as err:
            conn.rollback()
            return {'result': False, 'err': err}

    def update_one(self, sql, args):
        """更新数据"""
        log.info(f"execute_update_one sql:{sql}" % args)
        self.execute(sql, args, isNeed=True)
        return True

    def delete_one(self, sql, *args):
        """删除数据"""
        log.info(f"execute_delete_one sql:{sql}" % args)
        self.execute(sql, args, isNeed=True)
        return True

    def execute(self, sql, args, isNeed=False):
        """
        执行
        :param isNeed 是否需要回滚
        """
        conn, cursor = self.open()
        if isNeed:
            try:
                cursor.execute(sql, args)
                conn.commit()
            except:
                conn.rollback()
        else:
            cursor.execute(sql, args)
            conn.commit()
        self.close(conn, cursor)


"""
CREATE TABLE `names` (
  `id` int(10) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` VARCHAR(30) DEFAULT NULL COMMENT '姓名',
  `sex` VARCHAR(20) DEFAULT NULL COMMENT '性别',
  `age` int(5) DEFAULT NULL COMMENT '年龄',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='数据导入mysql';

"""


# sql_insert_one = "insert into `names` (`name`, sex, age) values (%s,%s,%s)"
# mysql.insert_one(sql_insert_one, ('唐三', '男', 25))
#
# datas = [
#     ('戴沐白', '男', 26),
#     ('奥斯卡', '男', 26),
#     ('唐三', '男', 25),
#     ('小舞', '女', 100000),
#     ('马红俊', '男', 23),
#     ('宁荣荣', '女', 22),
#     ('朱竹清', '女', 21),
# ]
# sql_insert_all = "insert into `names` (`name`, sex, age) values (%s,%s,%s)"
# mysql.insert_all(sql_insert_all, datas)
#
# sql_update_one = "update `names` set age=%s where `name`=%s"
# mysql.update_one(sql_update_one, (28, '唐三'))
#
# sql_delete_one = 'delete from `names` where `name`=%s '
# mysql.delete_one(sql_delete_one, ('唐三',))
#
# sql_select_one = 'select * from `names` where `name`=%s'
# results = mysql.select_one(sql_select_one, ('唐三',))
# print(results)
#
# sql_select_all = 'select * from `names` where `name`=%s'
# results = mysql.select_all(sql_select_all, ('唐三',))
# print(results)

def test_sql():
    mysql = ConnPool()
    sql_select_all = 'select id,task_id,file_url,task_status,output_data from `ali_asr_model_res` where `task_id`=%s'
    results = mysql.select_all(sql_select_all, ('0bfa2d5c-e662-11ee-8b56-b083fec01e48',))
    print(results[0]["task_id"])
    json_res = json.dumps(results, ensure_ascii=False)
    print(json_res)
