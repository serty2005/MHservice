import os
import json
import sqlite3
import time
import requests
from dateutil import parser
import schedule

def get(url, params):
    response = requests.get(url)
    if response.ok:
        return json.loads(response.text)
    else:
        print("Ошибка при загрузке данных:", response.status_code)
        return None


def post(url, params):
    response = requests.post(url, params=params)
    if response.ok:
        return json.loads(response.text)
    else:
        print("Ошибка при загрузке данных:", response.status_code)
        return None
    

def create_json_table():

    path = os.getenv("BDPATH") + 'fiscal_registers_fromPOS.db'
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fiscal_registers
                 (modelName TEXT, serialNumber TEXT PRIMARY KEY, RNM TEXT, organizationName TEXT,
                  fn_serial TEXT, datetime_reg TEXT, dateTime_end TEXT, ofdName TEXT,
                  bootVersion TEXT, ffdVersion TEXT, fnExecution TEXT, INN TEXT)''')
    conn.commit()
    conn.close()


# Функция для вставки данных из файла .json в базу данных SQLite
def importFromJSON(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        path = os.getenv("BDPATH") + 'fiscal_registers_fromPOS.db'
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO fiscal_registers 
                     (modelName, serialNumber, RNM, organizationName, fn_serial, datetime_reg, 
                     dateTime_end, ofdName, bootVersion, ffdVersion, fnExecution, INN)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (data['modelName'], data['serialNumber'], data['RNM'], data['organizationName'],
                      data['fn_serial'], data['datetime_reg'], data['dateTime_end'], data['ofdName'],
                      data['bootVersion'], data['ffdVersion'], data['fnExecution'], data['INN']))
        conn.commit()
        conn.close()


# Функция для обхода всех файлов .json в заданной директории и чтения данных из них
def process_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            importFromJSON(file_path)


# Функция для создания таблицы в базе данных SQLite
def create_sd_table():
    path = os.getenv('BDPATH') + 'fiscal_registers_fromSD.db'
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fiscal_registers
                 (RNKKT TEXT, FNNumber TEXT, KKTRegDate TEXT, UUID TEXT PRIMARY KEY,
                  FRSerialNumber TEXT, FNExpireDate TEXT)''')
    conn.commit()
    conn.close()


# Функция для вставки данных из JSON объекта в базу данных SQLite
def importFromServiceDesk(sd_data):
    path = os.getenv("BDPATH") + 'fiscal_registers_fromSD.db'
    conn = sqlite3.connect(path)
    c = conn.cursor()
    for entry in sd_data:
            RNKKT = entry['RNKKT']
            FNNumber = entry['FNNumber']
            KKTRegDate = entry['KKTRegDate']
            UUID = entry['UUID']
            FRSerialNumber = entry['FRSerialNumber']
            FNExpireDate = entry['FNExpireDate']
            c.execute('''INSERT OR REPLACE INTO fiscal_registers 
                         (RNKKT, FNNumber, KKTRegDate, UUID, FRSerialNumber, FNExpireDate)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                         (RNKKT, FNNumber, KKTRegDate, UUID, FRSerialNumber, FNExpireDate))
    conn.commit()
    conn.close()


# Функция для получения данных по указанной ручке и обновления базы данных
def update_database():
    url = 'https://myhoreca.itsm365.com/sd/services/rest/find/objectBase$FR'
    params = {'accessKey': os.getenv('SDKEY'), 'attrs': 'UUID,FRSerialNumber,RNKKT,KKTRegDate,FNExpireDate,FNNumber'}
    response = post(url, params)
    if response:
        create_sd_table()
        importFromServiceDesk(response)
        print("База данных обновлена успешно.")
    else:
        print("Ошибка при получении данных:", response.status_code)


def compare_and_update():

    pathbd = os.getenv("BDPATH") + 'fiscal_registers_fromSD.db'
    conn_sd = sqlite3.connect(pathbd)
    path = os.getenv("BDPATH") + 'fiscal_registers_fromPOS.db'
    conn_json = sqlite3.connect(path)
    c_json = conn_json.cursor()
    c_sd = conn_sd.cursor()

    # Выбираем данные для сравнения из базы данных SD
    c_sd.execute('''SELECT FRSerialNumber, FNNumber, FNExpireDate, UUID
                    FROM fiscal_registers''')
    sd_data = c_sd.fetchall()

    # Выбираем данные для сравнения из базы данных JSON
    c_json.execute('''SELECT serialNumber, fn_serial, dateTime_end
                      FROM fiscal_registers''')
    json_data = c_json.fetchall()

    # Сравниваем данные и отправляем запросы на обновление при несоответствии
    for sd_entry in sd_data:
        for json_entry in json_data:
            # Проверяем совпадение по FRSerialNumber и serialNumber
            if sd_entry[0] == json_entry[0]:
                # Преобразуем даты из строкового формата в объекты datetime для корректного сравнения
                sd_date = parser.parse(sd_entry[2])
                json_date = parser.parse(json_entry[2])

                if sd_date != json_date:  # Сравниваем даты
                    
                    print(f"Объект с UUID {sd_entry[3]} будет изменен.") # Выводим UUID объекта для тестирования
                    formatted_date = json_date.strftime('%Y.%m.%d %H:%M:%S')

                    # Отправляем запрос на редактирование объекта в SD
                    edit_url = f'https://myhoreca.itsm365.com/sd/services/rest/edit/{sd_entry[3]}/'
                    params = {'accessKey': os.getenv('SDKEY'), 'FNNumber': json_entry[1], 'FNExpireDate': formatted_date}
                    post(edit_url, params)
                    
    conn_json.close()
    conn_sd.close()



def run_tasks():
    # Задание для работы с папкой с JSON файлами каждый час
    schedule.every().hour.do(process_json_files, os.getenv('JSONPATH'))

    # Задание для выгрузки данных из SD каждые 2 часа
    schedule.every(2).hours.do(importFromServiceDesk)

    # Задание для сравнения и обновления данных каждые 2 часа
    schedule.every(2).hours.do(compare_and_update)
 
    # Запускаем бесконечный цикл для выполнения задач с периодичностью
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    run_tasks()