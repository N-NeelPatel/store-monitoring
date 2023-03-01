## Title
Store Monitoring system

## Solution Approach

The solution approach for this project involves the following steps:

1. Load the CSV data into a PostgreSQL database using the pandas library.
2. Create three tables in the database, one for each CSV data source.
3. Join the tables using the store_id column.
4. Convert the timestamp_utc to the local timezone of the store using the timezone_str column.
5. Calculate the uptime and downtime for each store within business hours.
6. Use interpolation to fill the entire business hours interval with uptime and downtime from the available observations.
7. Create two APIs, one for triggering report generation and another for getting the report status or the CSV file.


## API Endpoints
trigger_report
- URL: /trigger_report
- Method: POST
- Parameters: None
- Response: JSON object containing report_id
This API generates a random report_id and starts the report generation process in the background. It returns the report_id to the user.

get_report
- URL: /get_report
- Method: GET
- Parameters: report_id
- Response: CSV file with the following schema:
| store_id | report_date | uptime | downtime |
This API checks the status of the report generation process. If the process is still running, it returns "Running" as the output. If the process is complete, it returns "Complete" along with the CSV file.

## Code Structure
The code for this project is organized into the following files:

- `main.py`: This file contains the FastAPI application and the two APIs, trigger_report and get_report.
- `database.py`: This file contains functions to create the database tables and load the CSV data into the tables.
- `crud.py`: This file contains the SQL queries for joining the tables and calculating the uptime and downtime for each store.
- `utils.py`: This file contains utility functions for converting timestamps to local timezones, calculating the business hours interval, and interpolating the uptime and downtime for each store.
- `schema.py`: This file contains the schema for the models used.
