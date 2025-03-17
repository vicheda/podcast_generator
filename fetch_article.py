import requests
import datatier
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

load_dotenv()

################################################
from configparser import ConfigParser

# setup AWS based on config file:
#
config_file = 'podcast-config.ini'
# os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

configur = ConfigParser()
configur.read(config_file)

# configure for RDS access
#
rds_endpoint = configur.get('rds', 'endpoint')
rds_portnum = int(configur.get('rds', 'port_number'))
rds_username = configur.get('rds', 'user_name')
rds_pwd = configur.get('rds', 'user_pwd')
rds_dbname = configur.get('rds', 'db_name')
API_KEY = configur.get('guardian','api_key')
################################################

dbConn = datatier.get_dbConn(rds_endpoint, int(rds_portnum), rds_username, rds_pwd, rds_dbname)

#helper function to convery html body into analyzable article text
def text_from_html(body):
    soup = BeautifulSoup(body, "html.parser")
    return soup.get_text(separator=" ", strip=True)

# grab data from the guardian api
def fetch_guardian_articles(query):
    search_endpoint = 'https://content.guardianapis.com/search'
    try:
        response = requests.get(
            f'{search_endpoint}?q={query}&show-fields=body,headline,trailText&api-key={API_KEY}'
        )
        data = response.json()

        if data.get('response') and data['response'].get('results'):
            articles = data['response']['results']
            if len(articles)>0:
                sql = """
                INSERT INTO queries(querytext, status, audiokey)
                            VALUES(%s, %s,'');
                """
                datatier.perform_action(dbConn, sql, [query, 'gathered articles'])

                sql = "SELECT LAST_INSERT_ID();"
    
                row = datatier.retrieve_one_row(dbConn, sql)
                
                queryid = row[0]
                
                print("queryid:", queryid)

            combined_article_text = ""
            for article in articles[:6]: #only get text of 5 articles
                combined_article_text +=text_from_html(article['fields']['body'])
            return combined_article_text

        else:
            print('No results found.')
            return ''
        

    except Exception as e:
        print(f'Error fetching articles: {e}')
        return 'ERROR'