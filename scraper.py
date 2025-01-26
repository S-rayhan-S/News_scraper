import requests
from bs4 import BeautifulSoup

BASE_URL = "https://thefinancialexpress.com.bd"

def scrape_news():
    url = f"{BASE_URL}/page/national/politics"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article')  # Locate all articles
        
        news_data = []

        for article in articles:
            # Extract the heading and link
            heading_tag = article.find('h3')
            if heading_tag and heading_tag.find('a'):
                heading = heading_tag.get_text(strip=True)
                link = heading_tag.find('a')['href']
                details_url = f"{BASE_URL}{link}"

                # Append heading and details link
                news_data.append({
                    "heading": heading,
                    "details_link": details_url
                })
        
        return news_data
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return []
