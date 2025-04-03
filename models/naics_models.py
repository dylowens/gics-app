from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Sector(Base):
    __tablename__ = "sectors"
    code = Column(String, primary_key=True)  # 👈 ADD THIS
    name = Column(String, nullable=False)
    industry_groups = relationship("IndustryGroup", back_populates="sector")


class IndustryGroup(Base):
    __tablename__ = "industry_groups"
    code = Column(String, primary_key=True)  # 👈 ADD THIS
    name = Column(String, nullable=False)
    sector_code = Column(String, ForeignKey("sectors.code"))
    sector = relationship("Sector", back_populates="industry_groups")
    industries = relationship("Industry", back_populates="industry_group")


class Industry(Base):
    __tablename__ = "industries"
    code = Column(String, primary_key=True)  # 👈 ADD THIS
    name = Column(String, nullable=False)
    industry_group_code = Column(String, ForeignKey("industry_groups.code"))
    industry_group = relationship("IndustryGroup", back_populates="industries")
    sub_industries = relationship("SubIndustry", back_populates="industry")


class SubIndustry(Base):
    __tablename__ = "sub_industries"
    code = Column(String, primary_key=True)  # 👈 ADD THIS
    name = Column(String, nullable=False)
    industry_code = Column(String, ForeignKey("industries.code"))
    industry = relationship("Industry", back_populates="sub_industries")

def create_tables_if_not_exist(database_url: str):
    print(f"Connecting to database: {database_url}")
    engine = create_engine(database_url)
    print("Creating tables (if not exist)...")
    Base.metadata.create_all(engine)
    print("Tables ensured.")
    return engine