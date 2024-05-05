import os
import sys
import requests

def req_from_sd(metaclass, attrs):
    url = f'https://myhoreca.itsm365.com/sd/services/rest/find/{metaclass}'
    access_key = os.getenv('SDKEY')
    if access_key is None:
        sys.stderr.write("Ошибка: Не удалось получить доступный ключ для запроса\n")
        sys.exit(1)
    
    params = {'accessKey': access_key, 'attrs': attrs}
    response = requests.post(url, params=params)
    
    if response.status_code == 201:
        sys.stdout.write("Успешно добавлено\n")
    elif response.status_code == 200:
        return response.text
    elif response.status_code == 500:
        sys.stderr.write("Ошибка подключения: " + str.strip(response.text) + '\n')
        sys.exit(1)
