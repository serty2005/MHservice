import os
import json
import sqlite3
import time
import traceback
import requests
import sys
from dateutil import parser
from datetime import datetime
import schedule
# from dotenv import load_dotenv

# load_dotenv()

def exception_handler(exc_type, exc_value, exc_traceback):
    try:
        error_message = f"ERROR: An exception occurred + "
        error_message += ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print('timestamp'+error_message)
    except:
        pass

old_f = sys.stdout
class F:
    def write(self, x):
        old_f.write(x.replace("timestamp", "[%s] " % str(datetime.now())))
sys.stdout = F()

def post(url, params):
    response = requests.post(url, params=params)
    
    if response.status_code == 201:
        return print('timestamp'+"Успешно добавлено\n")
    elif response.status_code == 200:
        return response.text
    elif response.status_code == 500:
        print('timestamp'+"Ошибка подключения: " + str.strip(response.text) + '\n')
        response.raise_for_status()


def create_table(tablename):
    #Создаём пустую таблицу
    db_path = os.getenv("BDPATH")
    db_file = "fiscals.db"
    conn = sqlite3.connect(db_path + db_file)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS %s (
            serialNumber TEXT PRIMARY KEY,
            modelName TEXT,
            RNM TEXT,
            organizationName TEXT,
            fn_serial TEXT,
            datetime_reg TEXT,
            dateTime_end TEXT,
            ofdName TEXT,
            bootVersion TEXT,
            ffdVersion TEXT,
            fnExecution TEXT,
            INN TEXT,
            UUID TEXT,
            owner_uuid TEXT
        )""" % tablename)
    conn.commit()
    conn.close()
    print('timestamp'+f"Таблица {tablename} создана")


def importFromJSON(file_path):
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        path = os.getenv("BDPATH") + 'fiscals.db'
        conn = sqlite3.connect(path)
        c = conn.cursor()
        if 'serialNumber' in data:
            print('timestamp'+f'SN Атола: {data.get("serialNumber")}')
            if data.get('teamviewer_id') and data.get('teamviewer_id') != 'None':
                print('timestamp'+'Teamviewer: ' + data.get('teamviewer_id'))
            elif data.get('anydesk_id') and data.get('anydesk_id') != 'None':
                print('timestamp'+'AnyDesk: ' + data.get('anydesk_id'))

            if data.get('RNM') == '':
                print('timestamp'+'Регномер не найден. Ставлю 0000000000000000')
                data['RNM'] = '0000000000000000'
                data['fn_serial'] = '0000000000000000'
                       
            table_exists = c.execute(
                '''SELECT name FROM sqlite_master WHERE type='table' AND name='pos_fiscals' '''
            ).fetchone()
            if not table_exists:
                create_table('pos_fiscals')

            c.execute('''INSERT OR REPLACE INTO pos_fiscals 
                        (modelName, serialNumber, RNM, organizationName, fn_serial, datetime_reg, 
                        dateTime_end, ofdName, bootVersion, ffdVersion, fnExecution, INN)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (data['modelName'], data['serialNumber'], data['RNM'], data['organizationName'],
                        data['fn_serial'], data['datetime_reg'], data['dateTime_end'], data['ofdName'],
                        data['bootVersion'], data['ffdVersion'], data['fnExecution'], data['INN']))
            conn.commit()
            conn.close()
            print('*****')


def process_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            print('timestamp'+f'Обработка файла {filename}')
            try:
                importFromJSON(os.path.join(directory, filename))
            except Exception as e:
                exception_handler(type(e), e, e.__traceback__)
            # time.sleep(1)


def importFromServiceDesk(sd_data):
    conn = sqlite3.connect(os.getenv("BDPATH") + 'fiscals.db')
    parsed=json.loads(sd_data)
    c = conn.cursor()
    for data in parsed:
        owner_uuid = data['owner']['UUID'] if data.get('owner') and data['owner'].get('UUID') else None
        modelName = data['ModelKKT']['title']
        ofdName = data['OFDName']['title'] if data.get('OFDName') else None
        ffdVersion = data['FFD']['title'] if data.get('FFD') else None
        table_exists = c.execute(
            '''SELECT name FROM sqlite_master WHERE type='table' AND name='sd_fiscals' '''
        ).fetchone()
        if not table_exists:
            create_table('sd_fiscals')
        c.execute('''INSERT OR REPLACE INTO sd_fiscals 
                     (modelName, serialNumber, RNM, organizationName, fn_serial, datetime_reg, 
                     dateTime_end, ofdName, bootVersion, ffdVersion, owner_uuid, UUID)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (modelName, data['FRSerialNumber'], data['RNKKT'], data['LegalName'],
                      data['FNNumber'], data['KKTRegDate'], data['FNExpireDate'], ofdName,
                      data['FRDownloader'], ffdVersion, owner_uuid, data['UUID']))
    conn.commit()
    conn.close()


def update_sd_table():
    url = 'https://myhoreca.itsm365.com/sd/services/rest/find/objectBase$FR'
    params = {'accessKey': os.getenv('SDKEY'), 'attrs': 'UUID,FRSerialNumber,RNKKT,KKTRegDate,FNExpireDate,FNNumber,owner,FRDownloader,LegalName,OFDName,ModelKKT,FFD'}
    try:
        response = post(url, params)
        print('timestamp'+'Получен ответ от сервиса')
    except Exception as e:
        exception_handler(type(e), e, e.__traceback__)
    if response:
        importFromServiceDesk(response)


def compare_and_update():
    conn_sd = sqlite3.connect(os.getenv("BDPATH") + 'fiscals.db')
    conn_pos = sqlite3.connect(os.getenv("BDPATH") + 'fiscals.db')
    c_pos = conn_pos.cursor()
    c_sd = conn_sd.cursor()

    c_sd.execute('''SELECT modelName, serialNumber, RNM, organizationName, fn_serial, datetime_reg, 
                     dateTime_end, ofdName, bootVersion, ffdVersion, fnExecution, owner_uuid, UUID
                    FROM sd_fiscals''')
    sd_data = c_sd.fetchall()

    c_pos.execute('''SELECT modelName, serialNumber, RNM, organizationName, fn_serial, datetime_reg, 
                     dateTime_end, ofdName, bootVersion, ffdVersion, fnExecution, INN
                      FROM pos_fiscals''')
    pos_data = c_pos.fetchall()

    for sd_entry in sd_data:
        for pos_entry in pos_data:
            if sd_entry[1] == pos_entry[1]:
                sd_date = parser.parse(sd_entry[6])
                pos_date = parser.parse(pos_entry[6])

                if sd_date != pos_date:
                    print('timestamp'+f"Объект с UUID {sd_entry[12]} будет изменен.")
                    formatted_date = pos_date.strftime('%Y.%m.%d %H:%M:%S')
                    if 'ИНН:' not in sd_entry[3] and pos_entry[2] != '0000000000000000':
                        legalName = pos_entry[3] + ' ' + 'ИНН:' + pos_entry[11]
                    elif pos_entry[2] == '0000000000000000':
                        legalName = 'ЗАКОНЧИЛСЯ ФН'
                    else:
                        legalName = pos_entry[3]
                    edit_url = f'https://myhoreca.itsm365.com/sd/services/rest/edit/{sd_entry[12]}'
                    params = {'accessKey': os.getenv('SDKEY'), 'FNNumber': pos_entry[4], 'FNExpireDate': formatted_date, 'LegalName': legalName, 'RNKKT': pos_entry[2], 'FRDownloader': pos_entry[8]}
                    try:
                        post(edit_url, params)
                        print('timestamp'+f'Объект c UUID {sd_entry[12]} успешно изменен.')
                    except Exception as e:
                        exception_handler(type(e), e, e.__traceback__)
                        continue
    else:
        print('timestamp'+'Все объекты проверены.')


    conn_pos.close()
    conn_sd.close()

def run_tasks():
    schedule.every(3).minutes.do(update_sd_table)
    schedule.every(3).minutes.do(process_json_files, os.getenv('JSONPATH'))
    schedule.every(3).minutes.do(compare_and_update)

    while True:
        schedule.run_pending()
        time.sleep(5)

if __name__ == '__main__':
    create_table('pos_fiscals')
    create_table('sd_fiscals')
    process_json_files(os.getenv('JSONPATH'))

    run_tasks()
    