import requests
import pandas as pd
import os
from functions import extractLoad
from datetime import datetime
from google.cloud import bigquery
from flask import Flask

app = Flask(__name__)

@app.route("/")
def el_job():
    el = extractLoad()
    df = el.fetch_api()
    final_df = el.add_datetime(df)
    el.load_bigquery(final_df)
    return "Job complete"

# Main
if __name__ == "__main__":
    print("Started")
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
 
