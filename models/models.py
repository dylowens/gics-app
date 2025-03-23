from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

load_dotenv()

class Sector(Base):
    __tablename__ = 'sectors'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    industry_groups = relationship("IndustryGroup", back_populates="sector")


class IndustryGroup(Base):
    __tablename__ = 'industry_groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    sector_id = Column(Integer, ForeignKey('sectors.id'))
    sector = relationship("Sector", back_populates="industry_groups")
    industries = relationship("Industry", back_populates="industry_group")


class Industry(Base):
    __tablename__ = 'industries'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    industry_group_id = Column(Integer, ForeignKey('industry_groups.id'))
    industry_group = relationship("IndustryGroup", back_populates="industries")
    sub_industries = relationship("SubIndustry", back_populates="industry")


class SubIndustry(Base):
    __tablename__ = 'sub_industries'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    industry_id = Column(Integer, ForeignKey('industries.id'))
    industry = relationship("Industry", back_populates="sub_industries")


def create_tables_if_not_exist(database_url):
    print(f"Connecting to database: {database_url}")
    engine = create_engine(database_url)
    print("Creating tables (if not exist)...")
    Base.metadata.create_all(engine)
    print("Tables ensured.")
    return engine

