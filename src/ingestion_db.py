# Use this script to save CSV files into the database with their filename as table name.
import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time

logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

engine = create_engine("sqlite:///inventory.db")

def ingest_db(df, table_name, engine):
    """Ingest a dataframe into a database table."""
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)

def load_raw_data():
    """Load CSV files from data/ and ingest them into the database."""
    start = time.time()
    for file in os.listdir("data"):
        if file.lower().endswith(".csv"):
            df = pd.read_csv(os.path.join("data", file))
            logging.info("Ingesting %s into database", file)
            ingest_db(df, file[:-4], engine)
    total_time = (time.time() - start) / 60
    logging.info("-------------- Ingestion Complete ------------")
    logging.info("Total time taken: %.2f minutes", total_time)

if __name__ == "__main__":
    load_raw_data()
