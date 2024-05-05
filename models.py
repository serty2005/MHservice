from sqlalchemy import create_engine, Column, String, String, ForeignKey, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from typing import Optional, Annotated

c_uuid = Annotated[str, ForeignKey('companies.uuid')]

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'

    uuid = Column(String, primary_key=True)
    title = Column(String)
    address = Column(String)
    additional_name = Column(String)

    servers = relationship("Server", back_populates="owner")
    workstations = relationship("Workstation", back_populates="owner")
    fiscals = relationship("Fiscalnik", back_populates="owner")

class Server(Base):
    __tablename__ = 'servers'
    
    uuid = Column(String, primary_key=True)
    UniqueID = Column(String)
    Teamviewer = Column(String)
    AnyDesk = Column(String)
    rdp = Column(String)
    ip = Column(String)
    CabinetLink = Column(String)
    DeviceName = Column(String)

    company_uuid = c_uuid
    owner = relationship("Company", back_populates="servers")

class Workstation(Base):
    __tablename__ = 'workstations'

    uuid = Column(String, primary_key=True)
    AnyDesk = Column(String)
    Teamviewer = Column(String)
    DeviceName = Column(String)

    company_uuid = Column(String, ForeignKey('companies.uuid'))
    owner = relationship("Company", back_populates="workstations")

class Fiscalnik(Base):
    __tablename__ = 'fiscals'

    uuid = Column(String, primary_key=True)
    rnkkt = Column(String)
    LegalName = Column(String)
    FNNumber = Column(String)
    KKTRegDate = Column(String)
    FNExpireDate = Column(String)
    FRSerialNumber = Column(String)

    company_uuid = Column(String, ForeignKey('companies.uuid'))
    owner = relationship("Company", back_populates="fiscals")

    # Внешние ключи для связи с вспомогательными таблицами
    ofd_uuid = Column(String, ForeignKey('ofd_names.uuid'))
    ofd = relationship("OFDName")
    model_kkt_uuid = Column(String, ForeignKey('model_kkts.uuid'))
    model_kkt = relationship("ModelKKT")
    srok_fn_uuid = Column(String, ForeignKey('sroki_fns.uuid'))
    srok_fn = relationship("SrokFN")

class OFDName(Base):
    __tablename__ = 'ofd_names'

    uuid = Column(String, primary_key=True)
    title = Column(String)
    code = Column(String)
    def __repr__(self):
        return self.title

class ModelKKT(Base):
    __tablename__ = 'model_kkts'

    uuid = Column(String, primary_key=True)
    title = Column(String)
    code = Column(String)
    def __repr__(self):
        return self.title

class SrokFN(Base):
    __tablename__ = 'sroki_fns'

    uuid = Column(String, primary_key=True)
    title = Column(String)
    code = Column(String)
    def __repr__(self):
        return self.title
 
engine = create_engine('sqlite:///base.db')
session_factory = sessionmaker(bind=engine)
session_instance = session_factory()

Base.metadata.create_all(engine)
