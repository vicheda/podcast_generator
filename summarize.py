import boto3
import json
from fetch_article import fetch_guardian_articles

"""
Summarizes articles and turns them into a podcast script using Cohere Command R via Amazon Bedrock.
params: articles: string of concatenated article text
returns: podcast_script: string of podcast script
""" 
def summarize_articles(articles):
    modelId = "meta.llama3-3-70b-instruct-v1:0"
    contentType = "application/json"
    accept = "application/json"
    
    bedrock_client = boto3.client("bedrock-runtime")
    
    try:
        response = bedrock_client.invoke_endpoint(
            modelId=modelId,
            contentType=contentType,
            accept=accept,
            body=json.dumps({"prompt":articles,"max_gen_len":512,"temperature":0.5,"top_p":0.9})
        )
        podcast_script = response['body']
        return podcast_script
    except Exception as e:
        print("summarize_articles() failed:")
        print(str(e))
        raise

# test the summarize_articles function
articles = fetch_guardian_articles('climate')
podcast_script = summarize_articles(articles)
print(podcast_script)