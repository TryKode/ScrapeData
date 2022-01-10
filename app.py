# 1. Importing Libraries
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from bs4 import BeautifulSoup as bs
import requests
import re
import json

# 2. Create Class for taking Data in
class database_scrape(BaseModel):
    product_url: str 

# 3. Create the app and model objects
app = FastAPI()

# 4. API Base page
@app.get('/')
def index():
    return {'message': 'Hello, This API is used to Scrape the data from Amazon Product page and to use BERT-Transformer for question-answering system.'}

# 5. API to Scrape data
@app.get('/scrape')
def scrape_data(database_scrape:database_scrape):
    productURL = database_scrape.product_url
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    productPage = requests.get(productURL, headers=headers)
    productSoup = bs(productPage.content,'html.parser')

    productNames = productSoup.find_all('span', id='productTitle')
    if len(productNames) > 0:
        productNames = productNames[0].get_text().strip()
        
    ids = ['priceblock_dealprice', 'priceblock_ourprice', 'tp_price_block_total_price_ww', 'apexPriceToPay']
    for ID in ids:
        productDiscountPrice = productSoup.find_all('span', id=ID)
        if len(productDiscountPrice) > 0 :
            break
    if len(productDiscountPrice) > 0:
        productDiscountPrice = productDiscountPrice[0].get_text().strip()
        productDiscountPriceArr = productDiscountPrice.split('.')
        productDiscountPrice = 'Product Price after Discount is '+productDiscountPriceArr[0]

    classes = ['priceBlockStrikePriceString', 'a-text-price']
    for CLASS in classes:
        productActualPrice = productSoup.find_all('span', class_=CLASS)
        if productActualPrice != [] :
            break
    if len(productActualPrice) > 0 :
        productActualPrice = productActualPrice[0].get_text().strip()
        productActualPriceArr = productActualPrice.split('.')
        productActualPrice = 'Product Actual Price is ' + productActualPriceArr[0]

    productRating = productSoup.find_all('span', class_="a-icon-alt")
    if len(productRating) > 0:
        productRating = productRating[0].get_text().strip()

    productImg = productSoup.find_all('img', alt=productNames)
    if len(productImg) > 0:
        productImg = productImg[0]['data-a-dynamic-image']
        productImg = json.loads(productImg)

    productFeatures = productSoup.find_all('div', id='feature-bullets')
    if len(productFeatures) > 0:
        productFeatures = productFeatures[0].get_text().strip()
        productFeatures = re.split('\n|  ',productFeatures)
        temp = []
        for i in range(len(productFeatures)):
            if productFeatures[i]!='' and productFeatures[i]!=' ' :
                temp.append( productFeatures[i].strip() )
        productFeatures = temp
    
    productSpecs = productSoup.find_all('table', id='productDetails_techSpec_section_1')
    if len(productSpecs) > 0:
        productSpecs = productSpecs[0].get_text().strip()
        productSpecs = re.split('\n|\u200e|  ',productSpecs) 
        temp = []
        for i in range(len(productSpecs)):
            if productSpecs[i]!='' and productSpecs[i]!=' ' :
                temp.append( productSpecs[i].strip() )
        productSpecs = temp

    productDetails = productSoup.find_all('div', id='productDetails_db_sections')
    if len(productDetails) > 0:
        productDetails = productDetails[0].get_text()
        productDetails = re.split('\n|  ',productDetails) 
        temp = []
        for i in range(len(productDetails)):
            if productDetails[i]!='' and productDetails[i]!=' ' :
                temp.append( productDetails[i].strip() )
        productDetails = temp
    
    context = productNames + '\n' + productDiscountPrice + '. ' + productActualPrice + '.\n' + productRating + '.\n' + productFeatures[0] + '-\n'
    i = 1
    while i < len(productFeatures)-1 :
        context = context + 'The Product has ' + productFeatures[i]+'. '
        i = i+1

    context = context + '\n' + 'Product Specifications - \n'
    i = 0
    while i<len(productSpecs):
        context = context + productSpecs[i]+' is '+productSpecs[i+1]+'. '
        i = i+2
    context = context[:len(context)-2] + '.\n'

    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> | ', productNames, productDiscountPrice, productActualPrice, productFeatures, productSpecs, productDetails, context, sep="_-_-_-_-_")
    details = {
        'product_data' : {
            'productSoup' : productSoup,
            'productNames' : productNames,
            'productDiscountPrice' : productDiscountPrice,
            'productActualPrice' : productActualPrice,
            'productRating' : productRating,
            'productImg' : productImg,
            'productFeatures' : productFeatures,
            'productSpecs' : productSpecs,
            'productDetails' : productDetails,
            'context' : context
        }
    }
    return details

# 7. Run the API with uvicorn in Local system
#    Will run on http://127.0.0.1:8000
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
    
#uvicorn app:app --reload
