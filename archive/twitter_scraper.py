from playwright.sync_api import sync_playwright
import time
import re


def scrape_tweets(account, tweet_count=3):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = f'https://twitter.com/{account}'
        page.goto(url)

        tweets = {}
        last_height = page.evaluate("document.body.scrollHeight")

        while len(tweets) < tweet_count:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)  # wait for loading more tweets
            tweet_elements = page.query_selector_all('article')  # Locate tweet articles and extract text and date
            for tweet_element in tweet_elements:   
                tweet_text = tweet_element.query_selector('[data-testid="tweetText"]')  # Extract tweet text
                tweet_text = tweet_text.inner_text() if tweet_text else ""

                date_element = tweet_element.query_selector('time')  # Extract tweet date
                tweet_date = date_element.get_attribute("datetime") if date_element else "Unknown Date"

                if tweet_text and tweet_date:
                    tweets[tweet_date] = tweet_text

                if len(tweets) >= tweet_count:
                    break

            new_height = page.evaluate("document.body.scrollHeight")  # Break if the page height has not changed (end of scroll)
            if new_height == last_height:
                break
            last_height = new_height

        browser.close()
        
        return tweets



if __name__ == "__main__":
    account_name = "elonmusk"
    n_tweets = 10
    
    tweets = scrape_tweets(account_name, tweet_count=n_tweets)
    print(tweets)

    '''
    for i in tweets:
        print(f"Date: {i} \t Tweet: {tweets[i]}")
    '''
