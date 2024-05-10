from sqlalchemy import create_engine, String, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, Mapped, mapped_column, DeclarativeBase
from typing import List
from datetime import datetime

class Base(DeclarativeBase):
    pass

engine = create_engine('postgresql://postgres:994525@10.25.1.250:5432/mhtest', echo=True)
session_instance = sessionmaker(engine)


class Company(Base):
    __tablename__ = 'companies'

    uuid: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(250))
    additional_name: Mapped[str | None] = mapped_column(String(150))
    lastmodify: Mapped[datetime]
    # equipinuse: Mapped[List['Server','Workstation','Fiscalnik']] = relationship(back_populates="owner")

    servers: Mapped[List["Server"]] = relationship(back_populates="owner")
    workstations: Mapped[List["Workstation"]] = relationship(back_populates="owner")
    fiscals: Mapped[List["Fiscalnik"]] = relationship(back_populates="owner")

    def __repr__(self):
        return f'{self.title}'
    

        

class Server(Base):
    __tablename__ = 'servers'
    
    uuid: Mapped[str] = mapped_column(primary_key=True)
    UniqueID: Mapped[str | None] = mapped_column(String(50))
    Teamviewer: Mapped[str | None] = mapped_column(String(100))
    AnyDesk: Mapped[str | None] = mapped_column(String(100))
    rdp: Mapped[str | None] = mapped_column(String(100))
    ip: Mapped[str | None] = mapped_column(String(100))
    CabinetLink: Mapped[str | None] = mapped_column(String(100))
    DeviceName: Mapped[str | None] = mapped_column(String(100))
    lastmodify: Mapped[datetime]

    company_uuid: Mapped[str] = mapped_column(ForeignKey('companies.uuid'))
    owner: Mapped["Company"] = relationship(back_populates="servers")

    def __repr__(self):
        return f'{self.DeviceName}'

class Workstation(Base):
    __tablename__ = 'workstations'

    uuid: Mapped[str] = mapped_column(primary_key=True)
    AnyDesk: Mapped[str | None] = mapped_column(String(100))
    Teamviewer: Mapped[str | None] = mapped_column(String(100))
    DeviceName: Mapped[str | None] = mapped_column(String(100))
    lastmodify: Mapped[datetime]

    company_uuid: Mapped[str] = mapped_column(ForeignKey('companies.uuid'))
    owner: Mapped["Company"] = relationship(back_populates="workstations")

    def __repr__(self):
        return f'{self.DeviceName}'

class Fiscalnik(Base):
    __tablename__ = 'fiscals'

    uuid: Mapped[str] = mapped_column(primary_key=True)
    rnkkt: Mapped[str | None] = mapped_column(String(50))
    LegalName: Mapped[str] = mapped_column(String(150))
    FNNumber: Mapped[int]
    KKTRegDate: Mapped[datetime]
    FNExpireDate: Mapped[datetime]
    FRSerialNumber: Mapped[int]
    lastmodify: Mapped[datetime]

    company_uuid: Mapped[str] = mapped_column(ForeignKey('companies.uuid'))
    owner: Mapped["Company"] = relationship(back_populates="fiscals")

    ofd_uuid: Mapped[str] = mapped_column(ForeignKey('ofd_names.uuid'))
    ofd: Mapped["OFDName"] = relationship()
    model_kkt_uuid: Mapped[str] = mapped_column(ForeignKey('model_kkts.uuid'))
    model_kkt: Mapped["ModelKKT"] = relationship()
    srok_fn_uuid: Mapped[str] = mapped_column(ForeignKey('sroki_fns.uuid'))
    srok_fn: Mapped["SrokFN"] = relationship()

    def __repr__(self):
        return f'{self.FRSerialNumber}'

class OFDName(Base):
    __tablename__ = 'ofd_names'

    uuid: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    code: Mapped[str]

    def __repr__(self):
        return f'{self.title}'

class ModelKKT(Base):
    __tablename__ = 'model_kkts'

    uuid: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    code: Mapped[str]

    def __repr__(self):
        return f'{self.title}'

class SrokFN(Base):
    __tablename__ = 'sroki_fns'

    uuid: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    code: Mapped[str]

    def __repr__(self):
        return f'{self.title}'

Base.metadata.create_all(engine)
