import csv
import codecs
import akshare as ak #抓取股市数据
from datetime import datetime
from datetime import timedelta
import re #正则表达

stockData = list()

#retrieve data from current .csv file
with codecs.open('stock.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        stockData.append(row)


#关联个股交易记录
stockCodeToName = dict()
stockTradingRecords = dict() # map.put(code, List[transaction])
for row in stockData:
    #list all info
    if row['code'] in stockTradingRecords:
        stockTradingRecords[row['code']].append(row)
    else:
        stockCodeToName[row['code']] = row['name']
        stockTradingRecords[row['code']] = [row]


totalStockValue = 0
for stockCode, value in stockTradingRecords.items():
    print(stockCodeToName[stockCode])
    totalValue = 0.0
    totalUnits = 0
    print(">>>>>>>>>>>>>>>>>>>")
    print("交易记录")
    for record in stockTradingRecords[stockCode]:
        if float(record['Total amount']) < 0:
            print("> 买入: ", end=" ")
        else:
            if len(record['shares']) == 0:
                print("> 分红: ", end=" ")
            else:
                print("> 卖出: ", end=" ")

        print("份额: "+record['shares']       + " | "  , end=" ")
        print("总价: "+record['Total amount'] + " | "  , end=" ")
        print("每股单价: "+record['unit price']+ " | "  , end=" ")
        print("日期: "+record['date']+ " | "          )
        totalValue += float(record['Total amount'])
        #sum up total shares
        if len(record['shares']) != 0:
            if float(record['Total amount']) < 0: #买入份额
                totalUnits += int(record['shares'])
            else:
                totalUnits -= int(record['shares']) #卖出份额
    
    print("持仓收益: "+str(totalValue)) if totalUnits == 0 else print("持仓成本: "+str(totalValue))
    print("持有份额: "+str(totalUnits))
    
  
    #crawling for latest stock info
    if totalUnits != 0 and len(re.findall(r'^(60[0-3]|00[0-4]|300)[0-9][0-9][0-9]$',stockCode)) != 0: #validating stock code, excluded fund's code
        valid_stock_code = r'(600|601)[0-9][0-9][0-9]'
        todayDate = datetime.now().strftime('%Y%m%d')
        current_stock_hist = ak.stock_zh_a_hist(symbol=stockCode, period="daily", start_date=todayDate, end_date=todayDate, adjust="")
        #打印部分数据
        print(current_stock_hist.loc[0,'日期':'最低'].to_string())
        #按最近收盘价计算持仓市值
        marketValue = current_stock_hist.loc[0,'收盘':'收盘'].values[0] * totalUnits
        print("持仓市值: "+str(marketValue))
        print("当前盈亏: "+str(totalValue + marketValue))
    print("<<<<<<<<<<<<<<<<<<<")
      
    print()
    totalStockValue += totalValue

print("------------------------")
print("持仓总成本 ", end=" ")
print(totalStockValue)


