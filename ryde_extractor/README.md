# Ryde Extractor
This application  periodically scans the public available parquet files of the new york trip
record data, available online for free https://d37ci6vzurychx.cloudfront.net/trip-data

### Data crawling and storage
The project is a simple fastAPI server, that runs a scheduled job, every a pre-configured period of time (currently every 10 hours) and
checks in the public API , whether a new parquet file of the NYC taxi trip data, that hasn't been stored in our datalake yet, is available. It scans only for data from January 2026 until today.
When fresh data is available, it stores them in the project's datalake, under the /bronze folder. This folder conatins only the raw unporcessed data.
The **ryde_transformer** application does the cleanup of the data, this project simply stores whatever is available from the TLC trip data API.