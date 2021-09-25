import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# Send request & Load the page
headers = {
  'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
}
url = 'https://www.amazon.com/Best-Sellers-Kindle-Store/zgbs/digital-text'
content = requests.get(url, headers=headers).text
soup = BeautifulSoup(content, 'html.parser')

# Load each card
cards = soup.select('.zg-item-immersion')
cards_arr = []
for card in cards:
  card_obj = {}
  # Handle title
  title_html = card.select('.p13n-sc-truncate')[0]
  title = title_html.text.strip()
  title = re.sub(r"\\(.*?\\)", "", title)
  card_obj['title'] = title

  # Handle rating
  try:
    rate_html = card.select('.a-icon-alt')[0]
    rate = rate_html.text
    rate = re.sub(r" out of.*?$", "", rate)
    card_obj['rate'] = rate
  except Exception as e:
    print(e)
  


  # Handle rank
  rank_html = card.select('.zg-badge-text')[0]
  rank = rank_html.text
  card_obj['rank'] = rank

  # Handle price
  price_html = card.select('.p13n-sc-price')[0]
  price = price_html.text.strip('$')
  card_obj['price'] = price
  
  cards_arr.append(card_obj)

cards_pd = pd.DataFrame(cards_arr)
print(cards_pd)

  

