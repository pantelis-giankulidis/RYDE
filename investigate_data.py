from pyarrow import parquet
import os
import pandas as pd

parquet_file = "/Users/pantelisgiankoulidis/Documents/nycity_cabs/ryde_transformer/data/bronze/yellow_tripdata_2026-01.parquet"

file = parquet.ParquetFile(parquet_file)
df = file.read().to_pandas()

metadata = file.metadata

print(metadata.schema.names)
print(df['extra'].head(10))

'''
'VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'passenger_count', 'trip_distance', 'RatecodeID', 'store_and_fwd_flag', 'PULocationID', 'DOLocationID', 'payment_type', 
'fare_amount', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge', 'total_amount', 'congestion_surcharge', 'Airport_fee', 'cbd_congestion_fee']
'''
