from bs4 import BeautifulSoup
import requests 
import numpy as np
from scipy.stats import norm 
from datetime import date

TDAMERITRADE_API_KEY = "WXXVUGKDSSDG10JE9WEKDBJTC6ILWGWF"
# Returns a short term risk free rate using the 1 month us treasury yield. 
# Data scraped off MarketWatch
def getRiskFreeRate():
    url = "https://www.marketwatch.com/investing/bond/tmubmusd01m?countrycode=bx"
    source = requests.get(url).text
    soup = BeautifulSoup(source, "lxml")
    riskFreeRate = soup.find('div', class_='intraday__data')
    return float(riskFreeRate.span.text)/100

# Returns the Historical Volatility (Close to Close) in the last 60 days of a stock given the ticker
# Data scraped off alphaquery
def getHistVol(ticker):
    url = "https://www.alphaquery.com/stock/" + ticker + "/volatility-option-statistics/60-day/historical-volatility"
    source = requests.get(url).text
    soup = BeautifulSoup(source, "lxml")
    histVol = soup.find('div', class_="indicator-figure-inner")
    return float(histVol.text)

def getPrice(ticker):
    url = "https://api.tdameritrade.com/v1/marketdata/" + ticker + "/quotes"
    params = {}
    params.update({'apikey': TDAMERITRADE_API_KEY}) 
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
# Returns the bid, ask, and last prices of an options contract given that contract's infromation
def getBidAskLast(url, parameters, daysToExpiration, contractType):
    data = requests.get(url, params= parameters).json()
    bid = data[contractType+"ExpDateMap"][parameters['fromDate']+":"+str(daysToExpiration)][str(float(parameters["strike"]))][0]["bid"]
    ask = data[contractType+"ExpDateMap"][parameters['fromDate']+":"+str(daysToExpiration)][str(float(parameters["strike"]))][0]["ask"]
    last = data[contractType+"ExpDateMap"][parameters['fromDate']+":"+str(daysToExpiration)][str(float(parameters["strike"]))][0]["last"]
    return "          Bid: " + str(bid) + "     Ask: " + str(ask) + "     Last: " + str(last)
tickerSuccess = False
strikeSuccess = False
typeSuccess = False
expirationDateSuccess = False
while not tickerSuccess:
    try:
        ticker = input("Enter the Ticker: ")
        getPrice(ticker)
        tickerSuccess = True
    except:
        print("Please enter a valid Ticker")
link = "https://api.tdameritrade.com/v1/marketdata/chains"
params = {}
params.update({'apikey': TDAMERITRADE_API_KEY})
params.update({'symbol': ticker})
while not strikeSuccess:  
        strike = input("Enter the Strike: ")
        params.update({'strike': strike})
        data = requests.get(link, params=params).json()
        if(data['status'] == "SUCCESS"):
            strikeSuccess = True
            break
        print("Please enter a valid Strike")
while not typeSuccess:
    contractType = input("Enter the type(call/put): ")
    if(contractType == "call" or contractType == "put"):
        typeSuccess = True
        break
    print("Please enter a valid contract type")
expirationDate = input("Enter the expiration date(YYYY-MM-DD): ")
while not expirationDateSuccess:
    params.update({'fromDate': expirationDate})
    params.update({'toDate': expirationDate})
    data = requests.get(link, params=params).json()
    if(data['status'] == "SUCCESS"):
        expirationDateSuccess = True
        break
    print("Please enter a valid expiration date")

expirationDate = date(int(expirationDate[0:4]), int(expirationDate[5:7]), int(expirationDate[-2:]))
currDate = date.today()
daysToExpiration = (expirationDate - currDate).days
while(True):
    print("Theoretical Value: " + str(round(blackScholes(ticker, float(strike), daysToExpiration, type=contractType), 2)) + getBidAskLast(link, params, daysToExpiration, contractType))
