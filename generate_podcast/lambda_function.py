import json
import boto3
import os
import uuid
import datatier
import base64
from configparser import ConfigParser


# Initialize AWS Polly and S3 clients
polly_client = boto3.client("polly")
s3_client = boto3.client("s3")


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
        print("Getting scriptkey from database")
        sql = "SELECT querytext, status, scriptkey, audiokey from queries where queryid = %s;"

        row = datatier.retrieve_one_row(dbConn, sql, [queryid])

        if row == ():
            return {
            'statusCode': 400,
            'body': json.dumps({"error": "No script available"})
            }
        
        querytext = row[0]
        status = row[1]
        scriptkey = row[2]
        audiokey = row[3]

        print("querytext:", querytext)
        print("status:", status)
        print("scriptkey:", scriptkey)

        if status not in ["generated script", "generated audio"]:
            return {
            'statusCode': 400,
            'body': json.dumps({"error": "No script available, status: " + status})
            }
        if status == "generated audio":
            print("Audio already generated")
            audio_local_file = "/tmp/audio.mp3"
            bucket.download_file(audiokey, audio_local_file)

            infile = open(audio_local_file, "rb")
            bytes = infile.read()
            infile.close()
            data = base64.b64encode(bytes)
            datastr = data.decode()

            return {
            'statusCode': 200,
            "body": json.dumps({"audiokey": audiokey, "audiodata": datastr, "querytext": querytext})
            }
        script_local_filename = "/tmp/script.txt"
        #
        print("Downloading combined articles text from S3")
        #
        bucket.download_file(scriptkey, script_local_filename)
        #
        infile = open(script_local_filename, "r")
        script_text = infile.read()
        infile.close()

        if script_text == "":
            return {
            'statusCode': 400,
            'body': json.dumps({"error": "No script available"})
            }
        
        # Convert text to speech using Polly
        response = polly_client.synthesize_speech(
            Text=script_text,
            OutputFormat="mp3",
            VoiceId="Joanna",
            Engine="standard" # Change to your preferred voice
        )

        audio_local_file = "/tmp/audio.mp3"

        with open(audio_local_file, "wb") as audio_file:
            audio_file.write(response["AudioStream"].read())

        print ("Uploading podcast script txt file to S3")

        audiokey = "podcasts/" + str(uuid.uuid4()) + ".mp3"
        bucket.upload_file(audio_local_file, 
                        audiokey, 
                        ExtraArgs={
                            'ACL': 'public-read',
                            'ContentType': 'audio/mpeg'
                        })
        print ("Uploaded mp3 file with podcast")
        print ("audiokey:", audiokey)

        print ("Reading audio file as data string")
        infile = open(audio_local_file, "rb")
        bytes = infile.read()
        infile.close()
        data = base64.b64encode(bytes)
        datastr = data.decode()

        print ("Updating database with podcast script key and new status")
        sql = "UPDATE queries SET status = %s, audiokey = %s WHERE queryid = %s;"
        datatier.perform_action(dbConn, sql, ["generated audio", audiokey, queryid])

        
        return {
            "statusCode": 200,
            "body": json.dumps({"audiokey": audiokey, "audiodata": datastr, "querytext": querytext})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
