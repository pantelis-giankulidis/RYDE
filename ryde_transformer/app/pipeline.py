import pandas as pd
import os
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.dataset as ds 
import pathlib 

BASE = pathlib.Path(__file__).resolve().parent
input_path = str(BASE / "../data/raw/yellow_tripdata_2026-01.parquet")
output_path = str(BASE / "../data/processed/yellow_tripdata_2026-01.parquet")

def extract_data(path):
    dataset = ds.dataset(path, format = "parquet")
    return dataset.scanner(batch_size = 10000)

def transform_data(scanner):
    writer = None 
    for batch in scanner.to_batches():
        df = batch.to_pandas()

        df = df.dropna(how="all")
        df = df.drop_duplicates()

        cleaned_batch = pa.RecordBatch.from_pandas(df)


        if writer is None:
            writer = pq.ParquetWriter(output_path, cleaned_batch.schema, compression="snappy")
            
        writer.write_batch(cleaned_batch)

def load_data():
    pass

def run_pipeline():
    raw_data_scanner = extract_data(input_path)
    transform_data(raw_data_scanner)
    print("Data pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()