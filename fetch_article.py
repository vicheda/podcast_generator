import requests

API_KEY = '42160927-479f-46fd-90bd-ba61ced36638'
ENDPOINT = 'https://content.guardianapis.com/search'

def fetch_guardian_articles(query):
    try:
        response = requests.get(
            f'{ENDPOINT}?q={query}&api-key={API_KEY}'
        )
        data = response.json()
        if data.get('response') and data['response'].get('results'):
            return data['response']['results']
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
        print(f"Title: {article['webTitle']}")
        print(f"URL: {article['webUrl']}")
        print('---')
