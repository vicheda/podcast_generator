import boto3
import json
import os

from fetch_article import fetch_guardian_articles
client = boto3.client("bedrock", region_name="us-east-2")  # Use "bedrock" (not "bedrock-runtime")

response = client.list_foundation_models()

print(json.dumps(response, indent=2))

def summarize_articles(articles):
    """
    Summarizes articles and turns them into a podcast script using Cohere Command R via Amazon Bedrock.
    params: articles: string of concatenated article text
    returns: podcast_script: string of podcast script
    """ 
    client = boto3.client('bedrock-runtime', region_name='us-east-2')

    payload = {
        "prompt": f"Summarize the following articles into a podcast script:\n\n{articles}",
        "max_tokens": 500,
        "temperature": 0.7
    }

    response = client.invoke_model(
        modelId="cohere.command-r-plus",  # Confirm this ID using list_foundation_models()
        body=json.dumps(payload)
    )

    response_body = json.loads(response["body"].read())
    podcast_script = response_body.get("text", "Error generating summary.")

    return podcast_script

# Example Usage
if __name__ == '__main__':
    text = fetch_guardian_articles('technology')
    if text and text != 'ERROR':
        script = summarize_articles(text)
        print(script)