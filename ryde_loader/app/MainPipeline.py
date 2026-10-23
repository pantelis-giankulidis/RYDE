from dotenv import load_dotenv
from Logger import logger
import polars as pl
import pyodbc

load_dotenv()

CONN_STR = os.getenv("CONN_STR", default = None)

class MainPipeline:
    def __init__(self, df: pl.DataFrame):
        self.df = df

    def query(self):
        return """
            INSERT INTO FAIRS()
        """

    def load(self):
        with pyodbc.connect(CONN_STR) as conn:
            cursor = conn.cursor()
            cursor.fast_executemany = False 
            cursor.execute("SET IDENTITY_INSERT DAILY_ZONE_REVENUE ON")
            conn.commit()
            for chunk in self.df.iter_slices(n_rows = 10000):
                rows = chunk.rows()
                cursor.executemany(self.query(), rows)
                conn.commit() 
            cursor.execute("SET IDENTITY_INSERT DAILY_ZONE_REVENUE OFF")
            conn.commit()
        logger.info(f"Daily Zone Revenue loaded into postgres")

    def execute(self):
        if CONN_STR is not None:
            #self.load()
            logger.info(self.df.schema.names)
