import requests
import pandas as pd
import os
import json
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account

gcp_json_credentials_dict = json.loads(os.environ['creds'])
credentials = service_account.Credentials.from_service_account_info(gcp_json_credentials_dict)
cmc_creds = os.environ['cmc']

# Creds are supplied through Airflow's environment variables

class extractLoad:

    # Fetch prices from Binance API

    """
    Fetches all information on every available pairs on Binance 
    (cryptocurrency trading platform) as json
    Converts to DataFrame with pandas built-in read_json

    Input : None
    Output : DataFrame
    """

    def fetch_api(self):
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
          'start':'1',
          'limit':'5000',
          'convert':'USD'
        }
        headers = {
          'Accepts': 'application/json',
          'X-CMC_PRO_API_KEY': cmc_creds,
        }
        r = requests.get(url, headers=headers, params=parameters)
        r_json = r.json()
        json_data = r_json['data']
        df = pd.json_normalize(json_data, max_level=2)
        df = df[df['name'].notnull()]
        df.columns = df.columns.str.replace(".", "_")
        return df
    
    # Add datetime column - Minor Transformation

    """
    Adds an additional datetime column for the entire batch of data
    Format YYYY-MM-DD HH:MM:SS

    Input : DataFrame
    Output : DataFrame
    """

    def add_datetime(self, dataframe):
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dataframe['datetime'] = dt
        return dataframe

    # Load to Database

    """
    Loads DataFrame to BigQuery as a table

    Input : DataFrame
    Output : None
    """

    def load_bigquery(self, dataframe):
        print("Data Loaded")
        table_id = 'final-347314.main.cmcap_api'
        client = bigquery.Client(credentials=credentials)
        client.load_table_from_dataframe(dataframe, table_id)
