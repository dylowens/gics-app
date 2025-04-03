import pandas as pd
from models.naics_models import Sector, IndustryGroup, Industry, SubIndustry, create_tables_if_not_exist
from sqlalchemy.orm import sessionmaker
import os

# === Setup ===
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///naics.db")
engine = create_tables_if_not_exist(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# === Load and Clean CSV ===
df = pd.read_csv("2022_NAICS_Structure.csv", skiprows=2)
df.columns = ['change_indicator', 'code', 'title', 'col4', 'col5', 'col6']
df = df.dropna(subset=['code'])
df['code'] = df['code'].astype(str).str.strip().str.split('.').str[0]  # Ensure string
df['title'] = df['title'].str.replace('T', '', regex=False).str.strip()

# === In-Memory Code-to-Object Maps ===
code_map = {}

# === Load Hierarchy ===
for idx, row in df.iterrows():
    code = row['code']
    title = row['title']
    level = len(code)

    if level == 2:  # Sector
        sector = Sector(code=code, name=title)
        session.add(sector)
        session.flush()
        code_map[code] = sector

    elif level == 3:  # Subsector
        parent_code = code[:2]
        parent = code_map.get(parent_code)
        if parent:
            ig = IndustryGroup(code=code, name=title, sector=parent)
            session.add(ig)
            session.flush()
            code_map[code] = ig

    elif level == 4:  # Industry Group
        parent_code = code[:3]
        parent = code_map.get(parent_code)
        if parent:
            industry = Industry(code=code, name=title, industry_group=parent)
            session.add(industry)
            session.flush()
            code_map[code] = industry

    elif level == 5:  # Industry
        parent_code = code[:4]
        parent = code_map.get(parent_code)
        if parent:
            sub = SubIndustry(code=code, name=title, industry=parent)
            session.add(sub)
            session.flush()
            code_map[code] = sub

    elif level == 6:  # National Industry
        parent_code = code[:5]
        parent = code_map.get(parent_code)
        if parent:
            # Reuse SubIndustry model for now
            sub = SubIndustry(code=code, name=title, industry=parent.industry if hasattr(parent, 'industry') else parent)
            session.add(sub)
            session.flush()
            code_map[code] = sub

# === Finalize ===
session.commit()
session.close()
print("✅ NAICS data loaded into normalized hierarchy.")