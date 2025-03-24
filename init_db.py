import pandas as pd
from models.models import Sector, IndustryGroup, Industry, SubIndustry, create_tables_if_not_exist
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///gics.db")
engine = create_tables_if_not_exist(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

df = pd.read_csv("sample_data/GICS.csv")

for _, row in df.iterrows():
    sector = session.query(Sector).filter_by(name=row['Sector']).first()
    if not sector:
        sector = Sector(name=row['Sector'])
        session.add(sector)

    ig = session.query(IndustryGroup).filter_by(name=row['Industry Group']).first()
    if not ig:
        ig = IndustryGroup(name=row['Industry Group'], sector=sector)
        session.add(ig)

    ind = session.query(Industry).filter_by(name=row['Industry']).first()
    if not ind:
        ind = Industry(name=row['Industry'], industry_group=ig)
        session.add(ind)

    sub = session.query(SubIndustry).filter_by(name=row['Sub-Industry']).first()
    if not sub:
        sub = SubIndustry(name=row['Sub-Industry'], industry=ind)
        session.add(sub)

session.commit()
session.close()