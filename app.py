from scripts import req_from_sd as req
from models import Company, Server, Workstation, Fiscalnik, session_instance, OFDName, SrokFN, ModelKKT
import json

def fill_companies():
    metaclass = 'ou$company'
    attrs = 'adress,title,UUID,KEsInUse,additionalName,childOUs, parent'
    response = req(metaclass, attrs)

    if response:
        companies_json = json.loads(response)
        for company_json in companies_json:
            company = Company(
                uuid = company_json['UUID'],
                title = company_json['title'],
                address = company_json['adress'],
                additional_name = company_json['additionalName'] if 'additionalName' in company_json else None
            )
            try: 
                session_instance.add(company)
                session_instance.flush()
            except:
                session_instance.rollback()
                print(company_json['title'])
                continue
            kes_in_use = company_json['KEsInUse']
            for kes in kes_in_use:
                meta_class = kes['metaClass']
                equipment_uuid = kes['UUID']
                if meta_class == 'objectBase$Server':
                    server = Server(
                        uuid = equipment_uuid
                    )
                    company.servers.append(server)
                if meta_class == 'objectBase$Workstation':
                    workstation = Workstation(
                        uuid = equipment_uuid
                    )
                    company.workstations.append(workstation)
                if meta_class == 'objectBase$FR':
                    fiscal = Fiscalnik(
                        uuid = equipment_uuid
                    )
                    company.fiscals.append(fiscal)
        session_instance.commit()

def fill_servers():
    metaclass = 'objectBase$Server'
    attrs = 'UniqueID,UUID,Teamviewer,AnyDesk,RDP,IP,CabinetLink,DeviceName,owner'
    response = req(metaclass, attrs)

    if response:
        servers_json = json.loads(response)
        for server_json in servers_json:
            existing_server = session_instance.query(Server).filter_by(uuid=server_json['UUID']).first()
            if existing_server:
                existing_server.Teamviewer = server_json.get('Teamviewer') if 'Teamviewer' in server_json else None
                existing_server.UniqueID = server_json.get('UniqueID') if 'UniqueID' in server_json else None
                existing_server.AnyDesk = server_json.get('AnyDesk') if 'AnyDesk' in server_json else None
                existing_server.rdp = server_json.get('RDP') if 'RDP' in server_json else None
                existing_server.ip = server_json.get('IP') if 'IP' in server_json else None
                existing_server.CabinetLink = server_json.get('CabinetLink') if 'CabinetLink' in server_json else None
                existing_server.DeviceName = server_json.get('DeviceName') if 'DeviceName' in server_json else None
                if 'owner' in server_json and server_json['owner']:
                    owner_uuid = server_json['owner']['UUID']
                    if owner_uuid:
                        company = session_instance.query(Company).filter_by(uuid=owner_uuid).first()
                        if company:
                            existing_server.owner = company
                            session_instance.add(existing_server)
                session_instance.refresh(existing_server)
            else:
                server = Server(
                    uuid=server_json['UUID'],
                    UniqueID=server_json['UniqueID'],
                    Teamviewer=server_json['Teamviewer'] if 'Teamviewer' in server_json else None,
                    AnyDesk=server_json['AnyDesk'] if 'AnyDesk' in server_json else None,
                    rdp=server_json['RDP'] if 'RDP' in server_json else None,
                    ip=server_json['IP'] if 'IP' in server_json else None,
                    CabinetLink=server_json['CabinetLink'] if 'CabinetLink' in server_json else None,
                    DeviceName=server_json['DeviceName'] if 'DeviceName' in server_json else None
                )
                if 'owner' in server_json and server_json['owner']:
                    owner_uuid = server_json['owner']['UUID']
                    if owner_uuid:
                        company = session_instance.query(Company).filter_by(uuid=owner_uuid).first()
                        if company:
                            server.owner = company
                try:
                    session_instance.add(server)
                    session_instance.flush()
                except:
                    session_instance.rollback()
                    print(server_json['UniqueID'])
                    continue

        session_instance.commit()

def fill_workstations():
    metaclass = 'objectBase$Workstation'
    attrs = 'UUID,AnyDesk,Teamviewer,DeviceName,owner'
    response = req(metaclass, attrs)

    if response:
        workstations_json = json.loads(response)
        for workstation_json in workstations_json:
            existing_workstation = session_instance.query(Workstation).filter_by(uuid=workstation_json['UUID']).first()
            if existing_workstation:
                existing_workstation.AnyDesk = workstation_json.get('AnyDesk') if 'AnyDesk' in workstation_json else None
                existing_workstation.Teamviewer = workstation_json.get('Teamviewer') if 'Teamviewer' in workstation_json else None
                existing_workstation.DeviceName = workstation_json.get('DeviceName') if 'DeviceName' in workstation_json else None
                if 'owner' in workstation_json and workstation_json['owner']:
                    owner_uuid = workstation_json['owner']['UUID']
                    if owner_uuid:
                        company = session_instance.query(Company).filter_by(uuid=owner_uuid).first()
                        if company:
                            existing_workstation.owner = company
                            session_instance.add(existing_workstation)
                session_instance.refresh(existing_workstation)
            else:
                workstation = Workstation(
                    uuid = workstation_json['UUID'],
                    AnyDesk = workstation_json['AnyDesk'] if 'AnyDesk' in workstation_json else None,
                    Teamviewer = workstation_json['Teamviewer'] if 'Teamviewer' in workstation_json else None,
                    DeviceName = workstation_json['DeviceName'] if 'DeviceName' in workstation_json else None
                )
                if 'owner' in workstation_json and workstation_json['owner']:
                    owner_uuid = workstation_json['owner']['UUID']
                    if owner_uuid:
                        company = session_instance.query(Company).filter_by(uuid=owner_uuid).first()
                        if company:
                            workstation.owner = company
                try:
                    session_instance.add(workstation)
                    session_instance.flush()
                except:
                    session_instance.rollback()
                    print(workstation_json['DeviceName'])
                    continue
        session_instance.commit()

def fill_fiscals():
    metaclass = 'objectBase$FR'
    attrs = 'RNKKT,KKTRegDate,OFDName,UUID,FNExpireDate,LegalName,FRSerialNumber,ModelKKT,SrokFN,FNNumber,owner'
    response = req(metaclass, attrs)

    if response:
        fiscals_json = json.loads(response)
        for fiscal_json in fiscals_json:
            existing_fiscal = session_instance.query(Fiscalnik).filter_by(uuid=fiscal_json['UUID']).first()
            if existing_fiscal:
                existing_fiscal.rnkkt = fiscal_json.get('RNKKT')
                existing_fiscal.KKTRegDate = fiscal_json.get('KKTRegDate')
                existing_fiscal.FNExpireDate = fiscal_json.get('FNExpireDate')
                existing_fiscal.LegalName = fiscal_json.get('LegalName')
                existing_fiscal.FRSerialNumber = fiscal_json.get('FRSerialNumber')
                existing_fiscal.FNNumber = fiscal_json.get('FNNumber')
                if 'owner' in fiscal_json and fiscal_json['owner']:
                    owner_uuid = fiscal_json['owner']['UUID']
                    if owner_uuid:
                        company = session_instance.query(Company).filter_by(uuid=owner_uuid).first()
                        if company:
                            existing_fiscal.owner = company
                            session_instance.add(existing_fiscal)
                if 'OFDName' in fiscal_json and fiscal_json['OFDName'] is not None:
                    ofd_name_uuid = fiscal_json['OFDName']['UUID']
                    if ofd_name_uuid:
                        ofd_name = session_instance.query(OFDName).filter_by(uuid=ofd_name_uuid).first()
                        if ofd_name:
                            existing_fiscal.ofd = ofd_name
                model_kkt_uuid = fiscal_json['ModelKKT']['UUID']
                if model_kkt_uuid:
                    model_kkt = session_instance.query(ModelKKT).filter_by(uuid=model_kkt_uuid).first()
                    if model_kkt:
                        existing_fiscal.model_kkt = model_kkt
                srok_fn_uuid = fiscal_json['SrokFN']['UUID']
                if srok_fn_uuid:
                    srok_fn = session_instance.query(SrokFN).filter_by(uuid=srok_fn_uuid).first()
                    if srok_fn:
                        existing_fiscal.srok_fn = srok_fn
                session_instance.refresh(existing_fiscal)
            else:
                fiscal = Fiscalnik(
                    uuid=fiscal_json['UUID'],
                    rnkkt=fiscal_json['RNKKT'],
                    KKTRegDate=fiscal_json['KKTRegDate'],
                    FNExpireDate=fiscal_json['FNExpireDate'],
                    LegalName=fiscal_json['LegalName'],
                    FRSerialNumber=fiscal_json['FRSerialNumber'],
                    FNNumber=fiscal_json['FNNumber']
                )
                if 'owner' in fiscal_json and fiscal_json['owner']:
                    owner_uuid = fiscal_json['owner']['UUID']
                    if owner_uuid:
                        company = session_instance.query(Company).filter_by(uuid=owner_uuid).first()
                        if company:
                            fiscal.owner = company
                if 'OFDName' in fiscal_json and fiscal_json['OFDName'] is not None:
                    ofd_name_uuid = fiscal_json['OFDName']['UUID']
                    if ofd_name_uuid:
                        ofd_name = session_instance.query(OFDName).filter_by(uuid=ofd_name_uuid).first()
                        if ofd_name:
                            fiscal.ofd = ofd_name
                model_kkt_uuid = fiscal_json['ModelKKT']['UUID']
                if model_kkt_uuid:
                    model_kkt = session_instance.query(ModelKKT).filter_by(uuid=model_kkt_uuid).first()
                    if model_kkt:
                        fiscal.model_kkt = model_kkt
                srok_fn_uuid = fiscal_json['SrokFN']['UUID']
                if srok_fn_uuid:
                    srok_fn = session_instance.query(SrokFN).filter_by(uuid=srok_fn_uuid).first()
                    if srok_fn:
                        fiscal.srok_fn = srok_fn
                try:
                    session_instance.add(fiscal)
                    session_instance.flush()
                except:
                    session_instance.rollback()
                    print(fiscal_json['LegalName'])
                    continue
        session_instance.commit()

def fill_ofd_names():
    metaclass = 'OFD'
    attrs = 'title,code,UUID'
    response = req(metaclass, attrs)

    if response:
        ofd_names_json = json.loads(response)
        for ofd_name_json in ofd_names_json:
            ofd_name = OFDName(
                uuid=ofd_name_json['UUID'],
                title=ofd_name_json['title'],
                code=ofd_name_json['code']
            )
            try:
                session_instance.add(ofd_name)
                session_instance.flush()
            except:
                session_instance.rollback()
                print(ofd_name_json['title'])
                continue

        session_instance.commit()


def fill_model_kkts():
    metaclass = 'ModeliFR'
    attrs = 'title,code,UUID'
    response = req(metaclass, attrs)

    if response:
        model_kkts_json = json.loads(response)
        for model_kkt_json in model_kkts_json:
            model_kkt = ModelKKT(
                uuid=model_kkt_json['UUID'],
                title=model_kkt_json['title'],
                code=model_kkt_json['code']
            )
            try:
                session_instance.add(model_kkt)
                session_instance.flush()
            except:
                session_instance.rollback()
                print(model_kkt_json['title'])
                continue

        session_instance.commit()


def fill_sroki_fns():
    metaclass = 'SrokiFN'
    attrs = 'title,code,UUID'
    response = req(metaclass, attrs)

    if response:
        sroki_fns_json = json.loads(response)
        for srok_fn_json in sroki_fns_json:
            srok_fn = SrokFN(
                uuid=srok_fn_json['UUID'],
                title=srok_fn_json['title'],
                code=srok_fn_json['code']
            )
            try:
                session_instance.add(srok_fn)
                session_instance.flush()
            except:
                session_instance.rollback()
                print(srok_fn_json['title'])
                continue

        session_instance.commit()


if __name__ == '__main__':
    fill_companies()
    fill_servers()
    fill_workstations()
    fill_ofd_names()
    fill_model_kkts()
    fill_sroki_fns()
    fill_fiscals()
