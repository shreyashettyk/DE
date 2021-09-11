from sqlite3.dbapi2 import OperationalError
import requests
import json
import pprint
from fake_useragent import UserAgent
from urllib.parse import urljoin
import sqlite3

ua = UserAgent()

url = "https://www.walgreens.com/productsearch/v3/products/search"
base_url = 'https://www.walgreens.com'
extracted_products = []
def scrape(pagenumber):
    global extracted_products
    payload = json.dumps({"p":pagenumber,"s":72,"view":"allView","geoTargetEnabled":False,"abtest":["tier2","showNewCategories"],"deviceType":"desktop","id":["350006"],"requestType":"tier3","sort":"Top Sellers","couponStoreId":"15196","storeId":"15196"})
    headers = {
    'Content-Type': 'application/json',
    'Cookie': '_abck=EC88A6F12306D824EDA570361AA950E3~-1~YAAQNCozao/1JRR7AQAARwj4xgYJV7I+yVgfs30uhGpki+Cl4oH2VUVOgFbhbBkwMol0d7BfKowCEBSIm5nC690z90PbIapUQ4nYU9BlGoqIyvvbJc7otpi3F4KgTSYJ8Xg8DxvLrky4YgwCE1Bi7kp8xlzfPpF3hcjAuhuNLDpejsUkTyOx2gE3xIJFLbavI/UFixF0wfnr70Uy1aNyoIYIkNKuoVZdAvF/PSn0lPIVG8sY6oqB2WWxlJ/QFtdBmW+XTG0elWxDmu9pl6QvqAiJGitJO/f0mxhIt0wzuD2Xyc+JOQkNYDMu+tlo9meaGutkIKyqnNNLB6ZuKXoXNDYkkhRbBG6jz5qMLjBSZ6RVyKfPJ86VKLZsyc8=~-1~-1~-1; bm_sz=B2C9DB7FBEE1BC4DFDB536FDB99AA56F~YAAQNCozapD1JRR7AQAARwj4xg38lfe/KUqXCWFdI/UW1DlfcdW6YyY2gY0Vpn1stlDt42zz4Sir4iMnmvJSz7F6TSusn0nNZl5UquliF+0qgPrgY/TJt9PAMN1msF6uKM5lHH4NzDfZq93XpHly58ioyQo9HBGVP+wTQWl9AxltHyfB5Hm5X6XDx396IOHskQ/4UhtVWCs/Ofdc3ogVSSk4it+sAw8omhWw8iy7/naIJgu3KpAamujkov26KUH1wB9VMO1N40ITblwzMJSeP5BBk8c8LE1lz5XSsTLeu3S9r+aL8yQ=~4470594~3223605; akavpau_walgreens=1631131391~id=b8f2fe07e44a243ecfc9a11c539f5373',
    'user-agent' : ua.random  
    }

    response = requests.post(url, headers=headers, data=payload)

    print(response.json)
    data = response.json()
    # pprint.pprint(data)
    #pprint.pprint(data['products'])
    try:
        #pprint.pprint(data['products'][0])
        for pr_info in data['products']:
            product = pr_info['productInfo']
            p = {
                'img': product['imageUrl'],
                'price' : product['priceInfo']['regularPrice'],
                'id' : product['prodId'],
                'name' : product['productName'],
                'size' :product['productSize'],
                'url' : urljoin(base=base_url,url=product['productURL'])

            }
            # print(p)
            extracted_products.append(p)
        pagenumber+=1
        scrape(pagenumber)
    except KeyError:
        return None

def insert_to_db(extracted_products):
    conn = sqlite3.connect('walgreens.db')
    c = conn.cursor()
    try:
        c.execute(
            '''
            create table products(
                id TEXT PRIMARY KEY,
                name TEXT,
                url TEXT,
                size TEXT,
                price TEXT,
                img TEXT
            )
            '''
        )
    except :
        print('creation excetion caught')


    for pr in extracted_products:
        try:
            c.execute(''' insert into products(id,name,url,size,price,img) values(?,?,?,?,?,?)''',(pr['id'],pr['name'],pr['url'],pr['size'],pr['price'],pr['img']))
        except :
            print('caught...for insert')
            
    conn.commit()
    conn.close()

scrape(pagenumber=1)
print(extracted_products)
print('number of products is ',len(extracted_products))

print('*'*20,end=' ')
print('insert to db',end=' ')
print('*'*20)
insert_to_db(extracted_products)