from urllib.parse import urljoin
import requests
import json
from fake_useragent import UserAgent
from lxml import html
import re
from pymongo import MongoClient

ua = UserAgent()
movie_records = []
first = True
base_url = "https://www.imdb.com/"
url = "https://www.imdb.com/search/title/?genres=drama&groups=top_250&sort=user_rating,desc&ref_=adv_prv"
def scrape(url):
    global first
    resp = requests.get(url = url,headers={'User-Agent':ua.random})
    tree = html.fromstring(resp.content)
    movie_data = tree.xpath("//div[@class = 'lister-item-content']")
    for movie in movie_data:
        p = {
        'name':movie.xpath(".//h3/a/text()")[0],
        'year' : re.findall('\d+',movie.xpath(".//h3/span[@class='lister-item-year text-muted unbold']/text()")[0])[0],
        'duration' : re.findall('\d+',movie.xpath(".//p/span[@class='runtime']/text()")[0])[0],
        'rating' : movie.xpath(".//div[@class='ratings-bar']/div[contains(@class,'inline-block ratings-imdb-rating')]/@data-value")[0]
        }
        movie_records.append(p)
    if first:
        next_page = tree.xpath("//div[@class = 'desc']/a/@href")
        first  = False
    else:
        next_page = tree.xpath("//div[@class='desc']/a[2]/@href")

    if len(next_page) != 0:
        
        surl = urljoin(base = base_url,url=next_page[0])
        print(surl)
        scrape(surl)

def insert_to_db(list_records):
    client = MongoClient("mongodb://<user_name>:<pwd>@cluster0-shard-00-00.rsxac.mongodb.net:27017,cluster0-shard-00-01.rsxac.mongodb.net:27017,cluster0-shard-00-02.rsxac.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-3xsr69-shard-0&authSource=admin&retryWrites=true&w=majority")
    db = client['imdb_movies']
    collection = db['movies']
    for m in movie_records:
        exists = collection.find_one({'name': m['name']})
        if exists:
            if exists['year'] != m['year'] :
                collection.replace_one({'name': exists['name']}, m)
                print(f"Old item: {exists} New Item: {m}")
        else:
            collection.insert_one(m)
    client.close()

scrape(url)
insert_to_db(movie_records)
print('number of movies ',len(movie_records))