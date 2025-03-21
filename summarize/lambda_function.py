import os
import uuid
from configparser import ConfigParser
import boto3
import json
import datatier

"""
Summarizes articles and turns them into a podcast script using Cohere Command R via Amazon Bedrock.
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
    try:
        config_file = 'podcast-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
        configur = ConfigParser()
        configur.read(config_file)

        print("configure for S3 access")
        s3_profile = 's3readwrite'
        boto3.setup_default_session(profile_name=s3_profile)
        
        bucketname = configur.get('s3', 'bucket_name')
        
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucketname)


        print("configure for RDS access")
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')
        API_KEY = configur.get('guardian','api_key')
        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        print ("Getting queryid from event")
        if "pathParameters" in event and 'queryid' in event["pathParameters"]:
            queryid = event["pathParameters"]['queryid']
        else:
            return {
            'statusCode': 400,
            'body': json.dumps({"error": "requires queryid parameter in pathParameters in event"})
            }
        
        print("queryid:", queryid)
        print("Getting textkey from database")
        sql = "SELECT querytext, status, textkey, scriptkey from queries where queryid = %s;"

        row = datatier.retrieve_one_row(dbConn, sql, [queryid])

        if row == ():  # no such query
            return {
            'statusCode': 400,
            'body': json.dumps({"error": "no such query" + queryid})
            }
        
        querytext = row[0]
        status = row[1]
        textkey = row[2]
        scriptkey = row[3]

        print("querytext:", querytext)
        print("status:", status)
        print("textkey:", textkey)
        print("scriptkey:", scriptkey)

        if status not in ["generated script", "gathered articles"]:
            return {
            'statusCode': 400,
            'body': json.dumps({"error": "No articles content available, status: " + status})
            }
        if status == "generated script":
            print("Script already generated")
            script_local_file = "/tmp/script.txt"
            bucket.download_file(scriptkey, script_local_file)

            infile = open(script_local_file, "r")
            script = infile.read()
            infile.close()
            return {
            'statusCode': 200,
            'body': json.dumps({"scriptkey": scriptkey, "script": script})
            }
        
        prompt_local_filename = "/tmp/combinedarticles.txt"
        #
        print("Downloading combined articles text from S3")
        #
        bucket.download_file(textkey, prompt_local_filename)
        #
        infile = open(prompt_local_filename, "r")
        prompt = infile.readlines()
        infile.close()

        if not prompt:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "No articles text was found in s3"})
            }

        body_to_llm = {
            # improved prompt
            "prompt": f"Generate a podcast script summarizing the provided articles in a natural and engaging style. The script should flow seamlessly without including meta text like 'Here's the podcast script' or section headers such as 'Segment 1'. Instead, transition smoothly between topics as a natural conversation or narration would. Keep it to 250 words max and professional, engaging, and structured without explicit labels\n{prompt}",
            "max_gen_len": 512,
            "temperature": 0.5,
            "top_p": 0.9
        }

        # invoke the Bedrock model
        print("Invoking Bedrock model")
        response = bedrock_client.invoke_model(
            modelId=modelId,
            contentType=contentType,
            accept=accept,
            body=json.dumps(body_to_llm)
        )

        print("Reading response from Bedrock model")
        # read the response body
        res_bytes = response['body'].read()
        res_json = json.loads(res_bytes)

        print("Response:", res_json)

        # extract the generated text from the response
        res_text = res_json['generation']

        print ("res_text:", res_text)

        print ("Writing podcast script to a local file")

        local_results_file = "/tmp/summary.txt"
        outfile = open(local_results_file, "w")
        outfile.write(res_text)
        outfile.close()

        print ("Uploading podcast script txt file to S3")

        scriptkey = "summaries/" + str(uuid.uuid4()) + ".txt"
        bucket.upload_file(local_results_file, 
                        scriptkey, 
                        ExtraArgs={
                            'ACL': 'public-read',
                            'ContentType': 'text/plain'
                        })
        print ("Uploaded txt file with podcast script")
        print ("scriptkey:", scriptkey)

        print ("Updating database with podcast script key and new status")
        sql = "UPDATE queries SET status = %s, scriptkey = %s WHERE queryid = %s;"
        datatier.perform_action(dbConn, sql, ["generated script", scriptkey, queryid])

        return {
            'statusCode': 200,
            'body': json.dumps({"scriptkey": scriptkey, "script": res_text})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
