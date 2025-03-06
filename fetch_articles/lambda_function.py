import json
import os
import boto3
import requests
import uuid
import datatier
from bs4 import BeautifulSoup
from configparser import ConfigParser
import html


def text_from_html(body):
    soup = BeautifulSoup(body, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return html.unescape(text)

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

        if "pathParameters" in event and 'query' in event["pathParameters"]:
            query = event["pathParameters"]['query']
        else:
            raise Exception("requires query parameter in pathParameters in event")

        print("query:", query)
        print("Sending api request to Guardian...")
        search_endpoint = 'https://content.guardianapis.com/search'
        response = requests.get(
            f'{search_endpoint}?q={query}&show-fields=body,headline,trailText&api-key={API_KEY}'
        )
        response.raise_for_status()
        data = response.json()
        if data.get('response') and data['response'].get('results'):
            articles = data['response']['results']
            if len(articles)>0:
                combined_article_text = ""
                print("Combining articles' contents")
                for article in articles[:6]: #only get text of 5 articles
                    combined_article_text +=text_from_html(article['fields']['body'])
            else:
                print('No articles found.')
                return {
                    'statusCode': 400,
                    'body': json.dumps('No articles found')
                }
        else:
            raise Exception("No articles found")
        local_results_file = "/tmp/combinedarticles.txt"
        outfile = open(local_results_file, "w")
        outfile.write(combined_article_text)
        outfile.close()

        bucketkey = "combinedarticles/" + str(uuid.uuid4()) + ".txt"
        bucket.upload_file(local_results_file, 
                        bucketkey, 
                        ExtraArgs={
                            'ACL': 'public-read',
                            'ContentType': 'text/plain'
                        })
        print ("Uploaded txt file with combined articles' text")
        sql = """
        INSERT INTO queries(querytext, status, textkey)
                  VALUES(%s, %s, %s);
        """
        datatier.perform_action(dbConn, sql, [query, 'gathered articles', bucketkey])
        print("Inserted query into database")
        sql = "SELECT LAST_INSERT_ID();"

        row = datatier.retrieve_one_row(dbConn, sql)
        
        queryid = row[0]
        
        print("queryid:", queryid)

        return {
            'statusCode': 200,
            'body': json.dumps(queryid)
        }
    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
        'statusCode': 500,
        'body': json.dumps(str(err))
        }