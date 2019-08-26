# ## Step 2 - MongoDB and Flask Application
# Use MongoDB with Flask templating to create a new HTML page that displays all of the information that was scraped 
#from the URLs above.
# * Start by converting your Jupyter notebook into a Python script called `scrape_mars.py` with a function called 
#`scrape` that will execute all of your scraping code from above and return one Python dictionary containing 
#all of the scraped data.
# * Next, create a route called `/scrape` that will import your `scrape_mars.py` script and call your `scrape` function.
#   * Store the return value in Mongo as a Python dictionary.
# * Create a root route `/` that will query your Mongo database and pass the mars data into an HTML template to 
#display the data.
# * Create a template HTML file called `index.html` that will take the mars data dictionary and display all of the 
#data in the appropriate HTML elements. Use the following as a guide for what the final product should look like, 
#but feel free to create your own design.
# ![final_app_part1.png](Images/final_app_part1.png)
# ![final_app_part2.png](Images/final_app_part2.png)

from bs4 import BeautifulSoup as bs
from splinter import Browser
browser = Browser("chrome", headless=False)
import pandas as pd
from urllib.parse import urlsplit
import time

def scrape():
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    html = browser.html
    parsed = bs(html,"html.parser")

    news_title = parsed.find("div",class_="content_title").find("a").text
    news_p = parsed.find("div", class_="article_teaser_body").text

    jpl_image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_image_url)

    browser.click_link_by_partial_text('FULL IMAGE')

    time.sleep(4)
    browser.click_link_by_partial_text('more info')
    
    html = browser.html
    parsed = bs(html,"html.parser")
    
    img_src = parsed.find('img', class_='main_image').get('src')
    
    base_url = "{0.scheme}://{0.netloc}".format(urlsplit(jpl_image_url))
    
    featured_image_url=base_url + img_src
    
    tweet_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(tweet_url)
    
    tweet_xpath='//*[@id="stream-item-tweet-1164580766023606272"]/div[1]/div[2]/div[2]/p'
    mars_weather  = browser.find_by_xpath(tweet_xpath).text
    
    url = "https://space-facts.com/mars/"
    mars_table = pd.read_html(url)
    
    mars_facts=mars_table[1]
    mars_facts.set_index(0, inplace=True)
    mars_facts = mars_facts.to_html()

    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    base_url = "{0.scheme}://{0.netloc}".format(urlsplit(url))
    browser.visit(url)
    html = browser.html
    parsed = bs(html,"html.parser")

    hemisphere_image_urls = []
    hemisphere_image_urls_titles = []
    hemisphere_image_urls_images = []
    img_urls = []

    item_div = parsed.find_all('div', class_='item')

    for item in item_div: 

        title = item.find('h3').text

        img_urls.append(item.find('a', class_='product-item')['href'])
        hemisphere_image_urls_titles.append(title)

    for link in img_urls:
        browser.visit(base_url + link)
        img_html = browser.html
        parsed = bs(img_html, 'html.parser')

        full_img_url = base_url + parsed.find('img', class_='wide-image')['src']
        hemisphere_image_urls_images.append(full_img_url)
    for url, title in zip(hemisphere_image_urls_images, hemisphere_image_urls_titles):
        hemisphere_image_urls.append({"title" : title, "img_url" : url})

    mars_data={"news_title":news_title,
            "news_p":news_p,
            "featured_image_url":featured_image_url,
            "tweet_url":tweet_url,
            "mars_weather":mars_weather,
            "mars_facts":mars_facts,
            "hemisphere_image_urls":hemisphere_image_urls    
            }
    browser.quit()
    return mars_data
    