import requests
from flask import Flask, render_template, request, session, redirect, url_for
import os


app = Flask(__name__)
app.secret_key = 'chickenwing2024'

NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

# List of countries and their corresponding flags
countries = [
    ('us', 'United States', '🇺🇸'),
    ('au', 'Australia', '🇦🇺'),
    ('no', 'Norway', '🇳🇴'),
    ('it', 'Italy', '🇮🇹'),
    ('sa', 'Saudi Arabia', '🇸🇦'),
    ('de', 'Germany', '🇩🇪'),
    ('br', 'Brazil', '🇧🇷'),
    ('ca', 'Canada', '🇨🇦'),
    ('gb', 'United Kingdom', '🇬🇧'),
    ('fr', 'France', '🇫🇷'),
    ('in', 'India', '🇮🇳'),
    ('ru', 'Russia', '🇷🇺'),
    ('ar', 'Argentina', '🇦🇷'),
    ('ac', 'All countries', '🌍'),
]

# Country-specific sources for fallback when no headlines are found
COUNTRY_SOURCES = {
    'us': ['abc-news', 'bbc-news', 'cnn', 'fox-news', 'the-washington-post'],
    'au': ['abc-news-au', 'news-com-au'],
    'no': ['aftenposten', 'nrk'],
    'it': ['ansa-it', 'football-italia', 'il-sole-24-ore'],
    'sa': ['argaam', 'google-news-sa'],
    'de': ['bild', 'die-zeit', 'der-tagesspiegel', 'spiegel-online', 'handelsblatt'],
    'br': ['globo', 'blasting-news-br', 'infobae'],
    'ca': ['google-news-ca', 'financial-post', 'cbc-news'],
    'gb': ['bbc-news', 'the-guardian', 'the-times'],
    'fr': ['le-monde', 'les-echos', 'liberation'],
    'in': ['the-times-of-india', 'the-hindu'],
    'ru': ['ria', 'lenta', 'rbk'],
    'ar': ['la-nacion', 'infobae', 'clarin'],
    'ac': ['abc-news', 'bbc-news', 'cnn', 'fox-news', 'the-washington-post', 'abc-news-au', 'news-com-au', 'aftenposten', 'nrk', 'ansa-it', 'football-italia', 'il-sole-24-ore', 'argaam', 'google-news-sa', 'bild', 'die-zeit', 'der-tagesspiegel', 'spiegel-online', 'handelsblatt', 'globo', 'blasting-news-br', 'infobae', 'google-news-ca', 'financial-post', 'cbc-news', 'bbc-news', 'the-guardian', 'the-times', 'le-monde', 'les-echos', 'liberation', 'the-times-of-india', 'the-hindu', 'ria', 'lenta', 'rbk', 'la-nacion', 'infobae', 'clarin'],
}

NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

import re

def fetch_news(api_key, country, interests):
    url = f"{NEWS_API_URL}?apiKey={api_key}"

    # Start by trying to fetch top headlines
    if country != 'ac':
        url += f"&country={country}"

    if interests:
        url += f"&category={','.join(interests)}"
    
    print("Request URL:", url)  # Debugging URL

    # Attempt to fetch top headlines
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        news_data = response.json()
        articles = news_data.get('articles', [])

        # Regular expression to filter out URLs containing 'removed' or suspicious patterns
        removed_pattern = re.compile(r'removed|removed\.com|example\.com', re.IGNORECASE)

        # Filter out articles that have '[REMOVED]' in their title/content or unwanted domains in URL
        filtered_articles = [
            article for article in articles
            if '[removed]' not in article.get('title', '').lower() and
               '[removed]' not in article.get('content', '').lower() and
               not removed_pattern.search(article.get('url', ''))
        ]

        # If no articles are found, try fetching news from a specific source
        if not filtered_articles:
            print(f"No top headlines found for {country}, attempting to fetch news from sources...")
            fallback_sources = COUNTRY_SOURCES.get(country, [])
            if fallback_sources:
                valid_sources = []
                # Check each source for validity
                for source in fallback_sources:
                    source_url = f"https://newsapi.org/v2/sources?apiKey={api_key}&sources={source}"
                    source_response = requests.get(source_url)
                    if source_response.status_code == 200:
                        valid_sources.append(source)
                    else:
                        print(f"Source '{source}' is invalid for {country}")
                
                # Try again with valid sources
                if valid_sources:
                    source_str = ','.join(valid_sources)
                    url = f"https://newsapi.org/v2/everything?apiKey={api_key}&sources={source_str}"
                    response = requests.get(url)
                    response.raise_for_status()
                    news_data = response.json()
                    filtered_articles = news_data.get('articles', [])
        
        return filtered_articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    api_key = session.get('api_key', '')
    dark_mode = session.get('dark_mode', False)

    if request.method == 'POST':
        # Get the API key, country, and interests from the form
        api_key = request.form.get('api_key')
        country = request.form.get('country')
        interests = request.form.getlist('interests')
        dark_mode = 'dark_mode' in request.form
        
        # Save API key and dark mode preference to session
        session['api_key'] = api_key
        session['dark_mode'] = dark_mode
        
        if not api_key:
            return render_template('index.html', error="API Key is required!", countries=countries)

        # Fetch news articles based on user input
        articles = fetch_news(api_key, country, interests)
        
        # Render the result to the template
        return render_template('index.html', articles=articles, countries=countries, selected_country=country, api_key=api_key, dark_mode=dark_mode)

    return render_template('index.html', countries=countries, api_key=api_key, dark_mode=dark_mode)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))

