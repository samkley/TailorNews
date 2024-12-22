from flask import Flask, render_template, request, redirect, url_for, session
import requests

# Initialize the Flask application
app = Flask(__name__)


app.secret_key = 'chickenwing2024'

# News API Key 
NEWS_API_KEY = '5021852e3eb3499390165ebc4e44d1f9'

# Function to fetch news based on category, source, or country
def get_news_by_category(category=None, sources=None, country=None):
    url = f'https://newsapi.org/v2/top-headlines?apiKey={NEWS_API_KEY}'

    if category:
        url += f'&category={category}'  # Add category filter
    if sources:
        url += f'&sources={sources}'  # Add sources filter
    if country and country != 'all':  # Only add country filter if it's not 'all'
        url += f'&country={country}'  # Add country filter

    # Log the request URL to debug
    print("Request URL:", url)

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching news: {response.status_code}")
        return []

    news_data = response.json()
    articles = news_data.get('articles', [])
    
    # Debugging: print the articles
    print(f"Fetched {len(articles)} articles.")
    
    return articles


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        interests = request.form.getlist('interests')
        country = request.form.get('country')
        session['interests'] = interests
        session['country'] = country
        return redirect(url_for('index'))
    
    if 'interests' in session and 'country' in session:
        interests = session['interests']
        country = session['country']
        news = []
        
        category_news = {}
        for interest in interests:
            category_news[interest] = get_news_by_category(category=interest, country=country)

        news.extend(get_news_by_category(sources="bbc-news", country=country))
        news.extend(get_news_by_category(country=country))

        # Handle the case where no news articles are available for the selected categories
        mixed_news = []
        max_len = 0
        if category_news:  # Check if the category_news dictionary is not empty
            max_len = max(len(articles) for articles in category_news.values())
        
        for i in range(max_len):
            for interest in interests:
                if i < len(category_news.get(interest, [])):  # Ensure the list exists
                    mixed_news.append(category_news[interest][i])

        news = mixed_news

        # Debugging: Check if any news was fetched
        if not news:
            print("No news articles found.")

    else:
        news = []

    countries = [
        ('au', 'Australia', '🇦🇺'),
        ('be', 'Belgium', '🇧🇪'),
        ('bg', 'Bulgaria', '🇧🇬'),
        ('br', 'Brazil', '🇧🇷'),
        ('ca', 'Canada', '🇨🇦'),
        ('ch', 'Switzerland', '🇨🇭'),
        ('cn', 'China', '🇨🇳'),
        ('co', 'Colombia', '🇨🇴'),
        ('cu', 'Cuba', '🇨🇺'),
        ('cz', 'Czech Republic', '🇨🇿'),
        ('de', 'Germany', '🇩🇪'),
        ('eg', 'Egypt', '🇪🇬'),
        ('fr', 'France', '🇫🇷'),
        ('gb', 'United Kingdom', '🇬🇧'),
        ('gr', 'Greece', '🇬🇷'),
        ('hk', 'Hong Kong', '🇭🇰'),
        ('hu', 'Hungary', '🇭🇺'),
        ('id', 'Indonesia', '🇮🇩'),
        ('ie', 'Ireland', '🇮🇪'),
        ('il', 'Israel', '🇮🇱'),
        ('in', 'India', '🇮🇳'),
        ('it', 'Italy', '🇮🇹'),
        ('jp', 'Japan', '🇯🇵'),
        ('kr', 'South Korea', '🇰🇷'),
        ('lt', 'Lithuania', '🇱🇹'),
        ('lv', 'Latvia', '🇱🇻'),
        ('ma', 'Morocco', '🇲🇦'),
        ('mx', 'Mexico', '🇲🇽'),
        ('my', 'Malaysia', '🇲🇾'),
        ('ng', 'Nigeria', '🇳🇬'),
        ('nl', 'Netherlands', '🇳🇱'),
        ('no', 'Norway', '🇳🇴'),
        ('nz', 'New Zealand', '🇳🇿'),
        ('ph', 'Philippines', '🇵🇭'),
        ('pl', 'Poland', '🇵🇱'),
        ('pt', 'Portugal', '🇵🇹'),
        ('ro', 'Romania', '🇷🇴'),
        ('rs', 'Serbia', '🇷🇸'),
        ('ru', 'Russia', '🇷🇺'),
        ('sa', 'Saudi Arabia', '🇸🇦'),
        ('se', 'Sweden', '🇸🇪'),
        ('sg', 'Singapore', '🇸🇬'),
        ('si', 'Slovenia', '🇸🇮'),
        ('sk', 'Slovakia', '🇸🇰'),
        ('th', 'Thailand', '🇹🇭'),
        ('tr', 'Turkey', '🇹🇷'),
        ('tw', 'Taiwan', '🇹🇼'),
        ('ua', 'Ukraine', '🇺🇦'),
        ('us', 'United States', '🇺🇸'),
        ('ve', 'Venezuela', '🇻🇪'),
        ('za', 'South Africa', '🇿🇦')
    ]
    
    return render_template('index.html', news=news, countries=countries)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)





