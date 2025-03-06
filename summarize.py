import boto3
import json
from fetch_article import fetch_guardian_articles

"""
Summarizes articles and turns them into a podcast script using Cohere Command R via Amazon Bedrock.
params: articles: string of concatenated article text
returns: podcast_script: string of podcast script
""" 
def call_lambda_summarize(articles):
    payload = {
        "prompt": f"Summarize the following articles and turn them into a podcast script:\n{articles}",
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9,
    }
    
    try:
        # Call the Lambda function
        response = lambda_client.invoke(
            FunctionName='summarizeText',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)  # pass the prompt as JSON payload
        )

        # read and parse the response
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        return response_payload['body']
    
    except Exception as e:
        # Handle errors
        print(f"Error: {e}")
        return None


if __name__ == '__main__':
    text = fetch_guardian_articles('technology')
    script = call_lambda_summarize(text)
    
    if script:
        print("Generated Text: ")
        print(script)  # Output the generated text
    else:
        print("Error generating text.")