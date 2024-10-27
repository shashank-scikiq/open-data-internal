FROM python:3.11.9-slim

# ARG POSTGRES_SCHEMA='dev_v3'

WORKDIR /app
WORKDIR /app/Webapp

COPY APP/ /app/Webapp/
COPY APP/requirements.txt /app/Webapp/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# RUN python manage.py collectstatic --noinput

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8001"]