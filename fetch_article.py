import requests
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

API_KEY = os.getenv('GUARDIAN_API_KEY')
ENDPOINT = 'https://content.guardianapis.com/search'

# AWS RDS MySQL configuration
DB_HOST = os.getenv('DB_HOST')  # RDS endpoint
DB_USER = os.getenv('DB_USER')  # RDS master username
DB_PASSWORD = os.getenv('DB_PASSWORD')  # RDS master password
DB_NAME = os.getenv('DB_NAME', 'articles_db')

# # initialize MySQL database connection
# def get_db_connection():
#     try:
#         conn = mysql.connector.connect(
#             host=DB_HOST,
#             user=DB_USER,
#             password=DB_PASSWORD,
#             database=DB_NAME
#         )
#         return conn
#     except mysql.connector.Error as e:
#         print(f"Error connecting to MySQL: {e}")
#         return None
    
# grab data from the guardian api
def fetch_guardian_articles(query):
    saved_articles = []

    try:
        response = requests.get(
            f'{ENDPOINT}?q={query}&api-key={API_KEY}'
        )
        data = response.json()

        if data.get('response') and data['response'].get('results'):
            # return data['response']['results']
            articles = data['response']['results']
            for article in articles[:5]:
                article_id = article['id'] 
                # make a new request to get the full article
                response = requests.get(
                    f'https://content.guardianapis.com/{article_id}?api-key={API_KEY}&show-fields=body,headline,trailText'
                )
                article_data = response.json()
                article_text = article_data['response']['content']['fields']['body']
                saved_articles.append(article_text)
            return saved_articles
        else:
            print('No results found.')
            return []
        

    except Exception as e:
        print(f'Error fetching articles: {e}')
        return []

# Example usage
if __name__ == '__main__':
    articles = fetch_guardian_articles('technology')
    for article in articles:
        print(article)
