import boto3
import json
from fetch_article import fetch_guardian_articles

"""
Summarizes articles and turns them into a podcast script using Cohere Command R via Amazon Bedrock.
params: articles: string of concatenated article text
returns: podcast_script: string of podcast script
""" 

# # {
# #  "modelId": "meta.llama3-3-70b-instruct-v1:0",
# #  "contentType": "application/json",
# #  "accept": "application/json",
# #  "body": "{\"prompt\":\"this is where you place your input text\",\"max_gen_len\":512,\"temperature\":0.5,\"top_p\":0.9}"
# # }

modelId = "meta.llama3-3-70b-instruct-v1:0"
contentType = "application/json"
accept = "application/json"

bedrock_client = boto3.client("bedrock-runtime")

def lambda_handler(event, context):
    # print("Received event:", json.dumps(event))

    if 'body' in event:
        body = json.loads(event['body'])
        # print("Received body:", body)
    else:
        # if the body is not found in the event, return an error response
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "'body' key is missing in the event"})
        }

    # extract the prompt from the body
    prompt = body.get("prompt", None)
    if not prompt:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "No 'prompt' found in the body"})
        }

    body_to_llm = {
        "prompt": f"Summarize the following articles and turn them into a podcast script:\n{prompt}",
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        # invoke the Bedrock model
        response = bedrock_client.invoke_model(
            modelId=modelId,
            contentType=contentType,
            accept=accept,
            body=json.dumps(body_to_llm)
        )

        # read the response body
        res_bytes = response['body'].read()
        res_json = json.loads(res_bytes)

        # print("Response:", res_json)

        # extract the generated text from the response
        res_text = res_json['generation']

        return {
            'statusCode': 200,
            'body': json.dumps(res_text)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
