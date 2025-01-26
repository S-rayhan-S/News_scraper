from fastapi import FastAPI
from scraper import scrape_news
import requests
from bs4 import BeautifulSoup
from database import get_database_connection

# Azure OpenAI settings
AZURE_OPENAI_ENDPOINT = ""
AZURE_API_KEY = ""

app = FastAPI()

# Function to generate a summary using Azure OpenAI
def generate_summary_with_azure_openai(news_details):
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_API_KEY
    }
    data = {
        "messages": [{"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
                     {"role": "user", "content": f"Summarize this article in one line :\n{news_details}"}],
        "max_tokens": 150,
        "temperature": 0.5
    }
    try:
        response = requests.post(AZURE_OPENAI_ENDPOINT, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        summary = result["choices"][0]["message"]["content"]
        return summary
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Endpoint to scrape and provide news links
@app.get("/news")
def get_news():
    news = scrape_news()
    return news

# Endpoint to fetch detailed content from a given link
@app.get("/details")
def get_details_and_save(link: str):
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Target the <article> tag with the specific id
        article_tag = soup.find('article', id='main-single-post')

        if article_tag:
            # Extract all the paragraphs within the article tag
            paragraphs = article_tag.find_all('p')
            full_content = " ".join(p.get_text(strip=True) for p in paragraphs)

            # Generate a summary using Azure OpenAI
            summary = generate_summary_with_azure_openai(full_content)

            # Extract the heading (for example, from the <h1> or <h3> tag)
            heading_tag = soup.find('h1') or soup.find('h3')
            heading = heading_tag.get_text(strip=True) if heading_tag else "No Heading Found"

            # Save the details and summary to the database
            conn = get_database_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO news (news_heading, news_details, details_summary) VALUES (%s, %s, %s)",
                    (heading, full_content, summary)
                )
                conn.commit()
                return {
                    "message": "Details and summary saved to the database successfully!",
                    "link": link,
                    "news_heading": heading,
                    "news_details": full_content,
                    "details_summary": summary
                }
            except Exception as e:
                conn.rollback()
                return {"message": f"Failed to save details and summary to the database. Error: {str(e)}"}
            finally:
                cursor.close()
                conn.close()
        else:
            return {"message": "Article content not found.", "link": link}
    else:
        return {"message": f"Failed to fetch the page. Status code: {response.status_code}", "link": link}
