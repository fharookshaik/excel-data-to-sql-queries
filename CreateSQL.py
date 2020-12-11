import mysql.connector as mysqlc
from mysql.connector import Error
from python_mysql_dbconfig import read_db_config
import openpyxl
import shutil
import os
import time


def connect():
    print(f"[{time.ctime()}] STARTING PROCESS")
    print(f"[{time.ctime()}] CONNECTING TO MYSQL DATABASE")

    db_config = read_db_config()
    conn = None

    try:
        print(f"[{time.ctime()}]CONNECTING TO MYSQL...")
        conn = mysqlc.connect(**db_config)

        if conn.is_connected():
            print(f"[{time.ctime()}] CONNECTED TO MYSQL DATABASE")
            print(conn)
            return conn
        else:
            print('Connection failed')
    
    except Error as e:
        print(e)


def dataFromExcel(notebook):
    print(f"[{time.ctime()}] IMPORTING DATA FROM {notebook}")
    data = []

    excelFile = openpyxl.load_workbook(notebook)
    sheet = excelFile.active
    
    for row in sheet.rows:
        rowData = []
        for cell in row:
            rowData.append(cell.value)
        data.append(tuple(rowData))
    print(f"[{time.ctime()}] DATA IMPORTED SUCCESSFULLY FROM {notebook}")   
    return data


def typeconversion(attrType,values):
    values = list(values)
    for i in range(len(attrType)):
        if attrType[i] == b'date':
            temp = str(values[i])
            values[i] = temp[:-9]
        if values[i] == None:
            values[i] = ''
    return tuple(values)



if __name__ == "__main__":

    conn = connect()
    print(f"[{time.ctime()}] SETTING UP CURSOR")
    cursor = conn.cursor()

    # Excel files folder
    folderPath = os.getcwd() + r"\\attachments" 
    print(f"[{time.ctime()}] LOOKING FOR EXCEL SHEETS IN {folderPath}")
    
    # New folder for SQL files
    sqlPath = os.getcwd() + r"\\sqlfiles"

    if os.path.isdir(sqlPath):
        print(f"[{time.ctime()}] {sqlPath} FOUND. DELETING IT AND CREATING A NEW ONE")
        # os.rmdir(sqlPath) -> Linux
        shutil.rmtree(sqlPath)
        os.mkdir(sqlPath)
    else:
        print(f"[{time.ctime()}] {sqlPath} NOT FOUND. CREATING A NEW ONE")
        os.mkdir(sqlPath)

    fileNames = os.listdir(folderPath)

    for i in fileNames:
        # loading the excel file
        dataNotebook = folderPath + f"\\{i}"
        # new sql table name
        tableName = "g2" + f"{i[:-5].lower()}"
        print("\n\n")
        print(f"[{time.ctime()}] LOOKING INTO '{i}', CREATED A NEW TABLE NAMED '{tableName}' ")

        data = dataFromExcel(dataNotebook)

        sqlfile = open(f'{tableName}.sql','a')
        print(f"[{time.ctime()}] CREATING A NEW SQL FILE {tableName}.sql")

        
        attr = []
        attrType = []
        print(f"[{time.ctime()}] LOOKING FOR {tableName} IN MYSQL DATABASE")
        cursor.execute(f"DESC {tableName}")
        print(f"[{time.ctime()}] FOUND {tableName}. ACQUIRING ATTRIBUTE TYPES OF THE TABLE")
        for x in cursor:
            attr.append(x[0])
            attrType.append(x[1])

        # print(attr)
        # print(attrType)
        print(f"[{time.ctime()}] OPTIMIZING DATA FOR CREATING SQL QUERIES & GENERATING SQL QUERIES FOR {tableName} DATA IMPORTED FROM {dataNotebook}")
        for i in range(1,len(data)):
            values = data[i]
            finalvalues = typeconversion(attrType,values)
            # query = f"INSERT INTO {tableName} {tuple(attr)} VALUES {finalvalues} ;\n"
            query = f"INSERT INTO {tableName} VALUES {finalvalues} ;\n"
            sqlfile.write(query)
    
        sqlfile.close()
        print(f"[{time.ctime()}] SUCCESSFULLY CREATED {tableName}.sql in '{sqlPath}' ")
        originalPath = os.getcwd() + f"\\{tableName}.sql"
        finalPath = f"{sqlPath}" + f"\\{tableName}.sql"
        shutil.move(originalPath, finalPath)
        time.sleep(1)
    
    print(f"\n\n[{time.ctime()}] ALL DONE")
