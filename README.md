# Membership platform
## Objective
1. Implement API that returns three most used benefits
for every venue during the last 180 days.
2. Implement API that returns available benefits for the
user for a specific venue at the given time (default=current time) based
on the benefit recurrence rules and user’s earlier benefit usage.
3. Implement API that lists all the inactivity periods of the
benefits for the specific venue which have had significant inactivity
periods during the last 180 days.

## Setup

Create docker image

```bash
docker build -t membership-platform .
```
Run docker image with environment variables. 
Please put ip address of the database instead domain to the PG_HOST.

```bash
docker run -e PG_USER='' \
-e PG_PASS='' \
-e PG_HOST='' \
-e PG_PORT='' \
-e PG_NAME='' \
-p 5000:5000 \
membership-platform
```

## Swagger
The project contains a swagger file. Please read it to be aware about how the platform API. 

