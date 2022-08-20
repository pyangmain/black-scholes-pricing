from bs4 import BeautifulSoup
import requests 

url = "https://www.alphaquery.com/stock/MO/volatility-option-statistics/180-day/historical-volatility"
source = requests.get(url).text
soup = BeautifulSoup(source, "lxml")
histVol = soup.find('div', class_="indicator-figure-inner")
histVol = float(histVol.text)
print(histVol)
# Getting risk free rate (1 month treasury)
url = "https://www.marketwatch.com/investing/bond/tmubmusd01m?countrycode=bx"
source = requests.get(url).text
soup = BeautifulSoup(source, "lxml")
riskFreeRate = soup.find('div', class_='intraday__data')
riskFreeRate = float(riskFreeRate.span.text)/100
print(riskFreeRate)
#print(soup.prettify().encode('utf-8').decode('ascii', 'ignore'))