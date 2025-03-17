import requests
import json

"""
Summarizes articles and turns them into a podcast script using API Gateway.
params: queryid: ID of the query stored in RDS
returns: podcast_script: string of podcast script
""" 

#***************************************************************
# IGNORE THIS FUNCTION (already implemented in main)
#***************************************************************
def summarize_articles(queryid):
    api_url = "..."

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "pathParameters": {
            "queryid": queryid
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print("summarize_articles() failed:")
        print(str(e))
        raise