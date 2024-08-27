__author__ = "Shashank Katyayan"

import os

import psycopg2
import json
import pandas as pd

def fetch_data_from_db():
    # Connect to your database
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )
    cur = conn.cursor()

    query = f"""
    SELECT 
        date_part('year', CAST(lpd.month AS DATE)) AS order_year, 
        date_part('month', CAST(lpd.month AS DATE)) AS order_month, 
        lpd.domain, 
        SUM(lpd.order_count)/1000 AS total_orders_delivered
    FROM 
        {os.getenv('POSTGRES_SCHEMA')}.landing_page_data lpd 
    GROUP BY 
        order_year,
        order_month, 
        lpd.domain
    ORDER BY order_year, order_month asc, total_orders_delivered desc
    
    """

    cur.execute(query)
    # data = cur.fetchall()
    df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    cur.close()
    conn.close()

    return df


def top_chart_format(df):
    df['order_date'] = df['order_month'].astype(int).apply(lambda x: f"{x:02}") + '-' + df['order_year'].astype(
        int).astype(str)
    if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
        df['order_date'] = pd.to_datetime(df['order_date'])
    df['total_orders_delivered'] = pd.to_numeric(df['total_orders_delivered'], errors='coerce')

    formatted_data = {
        "series": [],
        "categories": df['order_date'].dt.strftime('%b-%y').unique().tolist()
    }

    # Prepare a dictionary to store total orders per domain per month
    domain_data = {}
    for index, row in df.iterrows():
        domain = row['domain']
        month_year = row['order_date'].strftime('%b-%y')
        total_orders = row['total_orders_delivered']

        if domain not in domain_data:
            domain_data[domain] = {}

        domain_data[domain][month_year] = total_orders

    # Prepare series data for each domain
    for domain in df['domain'].unique():
        if domain == '' or domain == 'Missing':
            continue

        domain_series = []
        for category in formatted_data['categories']:
            total_orders = domain_data.get(domain, {}).get(category, 0)
            domain_series.append(total_orders)

        state_data = {
            "name": domain,
            "data": domain_series
        }
        formatted_data["series"].append(state_data)

    return formatted_data

def update_json_with_db_data(json_data, db_data):

    json_data['series'] = db_data['series']
    json_data['xaxis']['categories'] = db_data['categories']

    return json_data
def read_json_from_file(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data


def write_json_to_file(json_data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)
    except Exception as e:
        print(e)
