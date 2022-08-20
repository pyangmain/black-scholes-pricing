from bs4 import BeautifulSoup
import requests
import numpy as np
from scipy.stats import norm 

key = ""
# Returns a short term risk free rate using the 1 month us treasury yield. 
# Data scraped off MarketWatch
def getRiskFreeRate():
    url = "https://www.marketwatch.com/investing/bond/tmubmusd01m?countrycode=bx"
    source = requests.get(url).text
    soup = BeautifulSoup(source, "lxml")
    riskFreeRate = soup.find('div', class_='intraday__data')
    return float(riskFreeRate.span.text)/100

# Returns the Historical Volatility (Close to Close) in the last 180 days of a stock given the ticker
# Data scraped off alphaquery
def getHistVol(ticker):
    url = "https://www.alphaquery.com/stock/" + ticker + "/volatility-option-statistics/180-day/historical-volatility"
    source = requests.get(url).text
    soup = BeautifulSoup(source, "lxml")
    histVol = soup.find('div', class_="indicator-figure-inner")
    return float(histVol.text)

def getPrice(ticker):
    url = "https://api.tdameritrade.com/v1/marketdata/" + ticker + "/quotes"
    params = {}
    params.update({'apikey': key}) 
    data = requests.get(url, params=params).json()
    return data[ticker]["lastPrice"]
# Calculates the theoretical value of an option using the black-scholes model, with volatility being the historical close to close 180 day volatility and 
# The risk free rate being the current 1 month us treasury yield
def blackScholes(ticker, strikePrice, timeToExpiration, type = "call"):
    price = getPrice(ticker)
    riskfree = getRiskFreeRate()
    volatility = getHistVol(ticker)
    timeToExpiration = timeToExpiration/365
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

print(blackScholes("MO", 45.5, 5, type="call"))

