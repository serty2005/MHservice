import mureq, os, sys, re


def req_all_from_sd(metaclass, attrs) -> dict | Exception:
    url = f'https://myhoreca.itsm365.com/sd/services/rest/find/{metaclass}'
    access_key = os.getenv('SDKEY')
    if access_key is None:
        sys.stderr.write("Ошибка: Не удалось получить доступный ключ для запроса\n")
        return Exception
    response = mureq.get(url, params={'accessKey': access_key, 'attrs': attrs})
    if response.status_code == 200:
        return response.json()
 
 
 
def req_by_uuid(metaclass, uuid) -> dict | Exception:
    url = f'https://myhoreca.itsm365.com/sd/services/rest/get/{uuid}'
    access_key = os.getenv('SDKEY')
    if access_key is None:
        sys.stderr.write("Ошибка: Не удалось получить доступный ключ для запроса\n")
        return Exception
    
    match metaclass:
        case 'objectBase$Workstation':
            attrs = 'UUID,AnyDesk,Teamviewer,DeviceName,owner,lastModifiedDate'   
        case 'ou$company':
            attrs = 'adress,title,UUID,KEsInUse,additionalName,childOUs,parent,lastModifiedDate'
        case 'objectBase$Server':
            attrs = 'UniqueID,UUID,Teamviewer,AnyDesk,RDP,IP,CabinetLink,DeviceName,owner,lastModifiedDate'
        case 'objectBase$FR':
            attrs = 'RNKKT,KKTRegDate,OFDName,UUID,FNExpireDate,LegalName,FRSerialNumber,ModelKKT,SrokFN,FNNumber,owner,lastModifiedDate'
        case _:
            attrs = False

    if attrs: response = mureq.get(url, params={'accessKey': access_key, 'attrs': attrs})        
    else: response = mureq.get(url, params={'accessKey': access_key})

    if response.status_code == 200:
        return response.json()
    else:
        return Exception


companys = req_by_uuid('objectBase$Workstation', 'objectBase$8203200')
print(companys)