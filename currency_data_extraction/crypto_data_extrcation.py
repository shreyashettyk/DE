import requests
import json
from lxml import html
from urllib.parse import urljoin
import sys
from pymongo import MongoClient

# sys.setrecursionlimit(10**6)

url = "http://web.archive.org/web/20190312000208/https://coinmarketcap.com/"
data = []
flag = False
next_page = []
def get(list_items):
    try:
        return list_items.pop(0).strip()
    except:
        return ''

def scrape(surl):
    global flag
    global url
    global next_page

    resp = requests.get(url = surl,headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"})
    tree = html.fromstring(html = resp.content)
    bitcoin_data = tree.xpath("//tbody/tr[contains(@id,'id')]")
    
    for coin in bitcoin_data:
        c = {
            '_id' : int(get(coin.xpath(".//td[1]/text()"))),
            'name' : get(coin.xpath(".//td[2]/a/text()")),
            'market_cap' : get(coin.xpath(".//td[3]/text()")),
            'price': get(coin.xpath(".//td[4]/a/@data-usd")),
            'volume(24h)': get(coin.xpath(".//td[5]/a/@data-usd"))
        }
        data.append(c)
        
    # if flag == False:
    #     next_page = tree.xpath("//ul[@class='pagination bottom-paginator']/li[1]/a/@href")
    #     flag = True 
    # else:
    #     next_page = tree.xpath("//ul[@class='pagination bottom-paginator']/li[2]/a/@href")

        

    # if len(next_page) != 0:
    #     recursive_url = urljoin(base= surl,url = next_page[0])
    #     print(recursive_url)
    #     scrape(recursive_url)
        

def insert_to_db(coin_list):
    client = MongoClient("mongodb://<xyz>:<password>@cluster0-shard-00-00.rsxac.mongodb.net:27017,cluster0-shard-00-01.rsxac.mongodb.net:27017,cluster0-shard-00-02.rsxac.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-3xsr69-shard-0&authSource=admin&retryWrites=true&w=majority")
    # client = MongoClient("mongodb://127.0.0.1:27017/")
    db = client["currencies"]
    collection = db["price"]
    for currency in coin_list:
        exists = collection.find_one({'_id':currency['_id']})
        if exists:
            if exists['name'] == currency['name'] and ((exists['market_cap'] != currency['market_cap']) or 
            (exists['price'] != currency['price']) or (exists['volume(24h)'] != currency['volume(24h)'])):
                print('old item ',exists)
                print('new item ',currency)
                collection.replace_one({'_id':exists['_id']},currency)
        else:
            collection.insert_one(currency)

    
    client.close()

scrape(url)
insert_to_db(data)
# with open('conis.json','w') as json_file:
#     json.dump(data,json_file)
#     print('written to file....')
    
