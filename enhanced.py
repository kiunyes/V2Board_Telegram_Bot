from Modules.daily import getTimestemp
import bot
import os
from handler import MysqlUtils


def isExistTable(tableName):
    try:
        db = MysqlUtils()
        result = db.is_exist_table(tableName)
        return result
    finally:
        db.close()


def onQuery(sql):
    try:
        db = MysqlUtils()
        result = db.sql_query(sql)
    finally:
        db.close()
        return result


def onSqlExec(sql):
    try:
        db = MysqlUtils()
        result = db.execute_sql(sql)
        if result is not None:
            raise Exception(result)
    finally:
        db.close()


def initEnhanced():
    try:
        if not isExistTable('enhncd_config'):
            dbEnhanced('init')
    except Exception as err:
        print('增强模组初始化失败', err)
        bot.isEnhanced = False


enhancedName = ''


def dbEnhanced(enhancedName):
    enhancedSqlScripts = []

    if enhancedName != 'init':
        db = MysqlUtils()
        cur = db.cur
        sql = "SELECT enhanced,content FROM enhncd_config WHERE enhanced=%s"
        s = (enhancedName, )
        cur.execute(sql, s)
        result = cur.fetchone()
        db.close()
        if result is not None:
            return

    try:
        sqlScriptDir = "./Databases/" + enhancedName
        for root, dirs, files in os.walk(sqlScriptDir):
            files.sort()
            for file in files:
                fullname = os.path.abspath(os.path.join(root, file))
                enhancedSqlScripts.append(fullname)

        db = MysqlUtils()
        for enhancedSqlScript in enhancedSqlScripts:
            with open(enhancedSqlScript) as sqlFile:
                sqlScriptContents = sqlFile.read().splitlines()
                for sqlScriptContent in sqlScriptContents:
                    db.cur.execute(sqlScriptContent)
                    db.conn.commit()
    except Exception as err:
        print(err)
    finally:
        db.close()
