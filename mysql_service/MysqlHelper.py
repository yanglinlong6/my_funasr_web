#import os,sys
import json
import traceback
import pymysql
from config import DbConect
from log.logger import log
#print(sys.path)


class MysqlHelper:

    _instance = None  # 本类的实例
    con = None  # 数据库conn
    cursor = None  # 游标

    def __init__(self, config) -> None:
        self.host = config['host']
        self.port = config["port"]
        self.user = config["user"]
        self.password = config["password"]
        self.db = config["db"]
        self.charset = config["charset"]
        self.con = None
        self.cursor = None

        try:
            self.con = pymysql.connect(
                    host=self.host, 
                    port=self.port, 
                    user=self.user, 
                    password=self.password,
                    database=self.db, charset='utf8'
                    # ,write_timeout=99999999
            )

            self.cursor = self.con.cursor()
            self._instance = MysqlHelper
        except Exception as e:
            print(e)
            return False

        

    # 创建连接
    def create_con(self):
        # try:
        #     self.con = pymysql.connect(
        #             host=self.host, 
        #             port=self.port, 
        #             user=self.user, 
        #             password=self.password,
        #             database=self.db, charset='utf8')
        #     self.cursor = self.con.cursor()
        #     return True
        # except Exception as e:
        #     print(e)
        #     return False
        pass

    # 关闭链接
    def close_con(self):
        if self.cursor:
            self.cursor.close()
        if self.con:
            self.con.close()

    # sql执行
    def execute_modify(self, sql):
        """
        执行插入/更新/删除语句
        """
        try:
            log.info("execute_modify sql:%s" % sql)
            res = self.cursor.execute(sql)
            self.con.commit()
            log.info("execute_modify result:%s" % res)
            result = True
        except Exception as e:
            log.error(e)
            traceback.print_exc()
            self.con.rollback
            result = False
        return result

    # sql执行 - return all
    def execute_select(self, sql):
        """
        执行查询语句
        """
        try:
            log.info("execute_select sql:%s" % sql)
            self.cursor.execute(sql)
            # 获取字段名
            field_names = [i[0] for i in self.cursor.description]
            rows = self.cursor.fetchall()
            if rows is None or len(rows) < 1:
                return None
            res = json.dumps([dict(zip(field_names, row)) for row in rows], ensure_ascii=False)
            log.info("execute_select result:%s" % res)
            return res
        except Exception as e:
            log.error(e)
            traceback.print_exc()
            return False
        finally:
            pass
    
    # sql执行 - return one
    def execute_selectOne(self, sql):
        """
        执行查询语句
        """
        try:
            log.info(sql)
            self.cursor.execute(sql)
            res = self.cursor.fetchone
            return res
        except Exception as e:
            log.error(e)
            traceback.print_exc()
            return False
        finally:
            pass

if __name__ == '__main__':
    db = MysqlHelper(DbConect.ali_asr_model)
    #添加
    # db.execute_sql("insert into user (username, password) values ('username4','password4')")
    #修改
    # db.execute_sql("update channellist set is_active=1 where id=2")
    #查询
    selectSql = ("select * from ali_asr_model_res;")
    print("execute sql:%s" %selectSql)
    res = db.execute_select(selectSql)
    print(res)
    print(len(res))
