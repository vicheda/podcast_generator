import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('GUARDIAN_API_KEY')
ENDPOINT = 'https://content.guardianapis.com/search'

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
