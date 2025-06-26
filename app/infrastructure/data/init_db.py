from dotenv import load_dotenv
from config.settings import Settings
import os
import pandas as pd
from sqlalchemy import create_engine

# cargar .env en runtime
load_dotenv(override=True)
# instancia (no uses Settings.database_url)
settings = Settings()

async def init_db():
    # usa la instancia
    db_url = settings.database_url
    db_path = db_url.split("///")[-1]
    if not os.path.exists(db_path):
        # crear la DB a partir del XLSX
        df = pd.read_excel(settings.raw_data_path)
        engine = create_engine(db_url)
        df.to_sql("raw_table", engine, index=False)
