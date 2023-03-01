## Title
Store Monitoring system

## Solution Approach

The solution approach for this project involves the following steps:

- Load the CSV data into a PostgreSQL database using the pandas library.
- Create three tables in the database, one for each CSV data source.
- Join the tables using the store_id column.
- Convert the timestamp_utc to the local timezone of the store using the timezone_str column.
- Calculate the uptime and downtime for each store within business hours.
- Use interpolation to fill the entire business hours interval with uptime and downtime from the available observations.
- Create two APIs, one for triggering report generation and another for getting the report status or the CSV file.
