The system is going to answer to these questions
* Which zones will have the highest demand in the next hour?
* When should be more vehicles available in a specific zone?
* Which routes or time periods have unusually long trip durations?
* How do weather, day of week, holidays, and events affect demand?
* What percentage of trips have suspicious fares, distances, or durations?
* How much revenue and demand vary by zone and hour?

The system is going to have some logs and metrics as
* Pipeline duration
* Number of records processed
* Number of invalid records
* Freshness of the latest partition.
* Failure rate
* Query or job cost

The ETL should be scaling up increamentally
1. One month locally
2. One year locally partitioned with parquet
3. Several years with pySpark
4. Scheduled incremental processing in the cloud
5. A small ML service and monitoring dashboard


## First draft of SQL schema
