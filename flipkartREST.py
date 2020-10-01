from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup




# helper function
def flipkart():
    response = requests.get('https://www.flipkart.com/search?q=nokia+smartphones&sid=tyy%2C4io&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_0_10_na_na_pr&otracker1=AS_QueryStore_OrganicAutoSuggest_0_10_na_na_pr&as-pos=0&as-type=RECENT&suggestionId=nokia+smartphones&requestId=675612e2-512b-4d0e-8b75-6bdf91921d7c&as-backfill=on')

    soup = BeautifulSoup(response.text, 'lxml')
    mname, mrating, mprice, mdesc = list(), list(), list(), list()
    mobile_name = soup.find_all(class_='_3wU53n')
    rating = soup.find_all(class_='hGSR34')
    price = soup.find_all(class_='_1vC4OE _2rQ-NK')
    description = soup.find_all(class_='vFw0gD')

    product = list()

    for a, b, c, d in zip(mobile_name, rating, price, description):
        product.append({"name": a.get_text(), "rating": b.get_text(), "price": c.get_text(), "description": d.get_text()})

    return product





app = Flask(__name__)   # flask app initialised
CORS(app)               # just to remove CORS error

@app.errorhandler(404)  #error handling for 404
def not_found(e): 
  return jsonify({"status": 0, "error": str(e)})
  
@app.route("/scrapeflipkart")
def scrapeit():
    # only accespts GET requests
    if request.method == "GET": return jsonify({"status": 1, "mobile_phones": flipkart()})
    else: return jsonify({"status": 0, "error": "method not callable"})
        


if __name__ =="__main__": app.run(debug = True)  # just remove dubug = True when using it in production