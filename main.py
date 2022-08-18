import requests
import numpy as np
from scipy.stats import norm 

key = ""
def blackScholes(ticker, riskfree, strikePrice, volatility, timeToExpiration, type = "call"):
    url = "https://api.tdameritrade.com/v1/marketdata/" + ticker + "/quotes"
    params = {}
    params.update({'apikey': key}) 
    data = requests.get(url, params=params).json()
    price = data[ticker]["lastPrice"]
    d1 = (np.log(price/strikePrice) + (riskfree + volatility**2/2)*timeToExpiration)/(volatility*np.sqrt(timeToExpiration))
    d2 = d1 - volatility*np.sqrt(timeToExpiration)
    try:
        if type == "call":
            price = price*norm.cdf(d1, 0, 1) - strikePrice*np.exp(-riskfree*timeToExpiration)*norm.cdf(d2, 0, 1)
        elif type == "put":
            price = strikePrice*np.exp(-riskfree*timeToExpiration)*norm.cdf(-d2, 0, 1) - price*norm.cdf(-d1, 0, 1)
        return price
    except:
        print("Please enter a valid option type: either 'call' or 'put'")

print(round(blackScholes("MO", .0222, 45.5, .3301, 1/365, type="call"), 2))

