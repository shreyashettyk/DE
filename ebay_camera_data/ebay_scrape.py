import requests
from lxml import html
import json
import sys
try:
    resp = requests.get(url = 'https://www.ebay.com/globaldeals/tech/cameras-photo',headers={'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"})
    tree = html.fromstring(html = resp.text)
    camera_sales = []
    items = tree.xpath("//div[@class='dne-itemtile-detail']")
    
    for item in items:
        item_name = item.xpath(".//a/h3/span/span[@class='ebayui-ellipsis-2']/text()")[0]
        # print(item_name)
        item_price = item.xpath(".//div[@itemscope='itemscope']/span[1]/text()")[0]
        # print(item_price)
        prev_price = item.xpath(".//div[@class='dne-itemtile-original-price']/span/span[@class='itemtile-price-strikethrough']/text()")
        if len(prev_price) == 0:
            prev_price = item_price
        else:
            prev_price  = prev_price[0]
        

        hotness = item.xpath(".//span/span[@class='dne-itemcard-hotness itemcard-hotness-red ']/text()")
        if len(hotness) == 0:
            hotness = 'Many More'
        else:
            hotness = hotness[0]
        
        item_info = {
            'item_name' : item_name,
            'item_price' : item_price,
            'prev_price' : prev_price,
            'hotness' : hotness
        }
        camera_sales.append(item_info)
    print(camera_sales[0:3],len(camera_sales))
    with open('camera_data.json','w') as json_file:
        json.dump(camera_sales,json_file)
        print('Successfully written to the file ...')
except Exception as e:
    print(sys.exc_info()[0])
    print(sys.exc_info()[1])
    print(sys.exc_info()[2])

#xpath reference    
# //div[@class='dne-itemtile-detail']/a/h3[@class='dne-itemtile-title ellipse-2']/span/span[@class='ebayui-ellipsis-2']/text()
# //div[@class='dne-itemtile-detail']/div[@itemscope='itemscope']/span[1]/text()
# //div[@class='dne-itemtile-detail']/div[@class='dne-itemtile-original-price']/span/span[@class='itemtile-price-strikethrough']/text()
# //div[@class='dne-itemtile-detail']/span/span[@class='dne-itemcard-hotness itemcard-hotness-red ']/text()

# //div[@class='dne-itemtile-detail']/div[@class='dne-itemtile-original-price']/span/span[@class='itemtile-price-strikethrough']/text()