import csv
import codecs
import akshare as ak #抓取股市数据
import datetime
import re #正则表达

def main():
    stockData = getDataFromCSV('stock.csv')

    #关联个股交易记录
    stockTradingRecords = transactionsForIndividualStock(stockData)


    holdingStockValue = 0.0 #当前持仓总市值
    holdingStockCost = 0.0
    totalYield = 0.0
    for stockCode, value in stockTradingRecords.items():
        print(value[0]['name'])
        #cumulativeProfit为历史累计收益(包括中途卖出所得/所失，和分红所得)，stockValueOnHand仅为当前持仓市值
        totalCost = 0.0 
        yieldAsForNow = 0.0
        totalUnits = 0.0
        print(">>>>>>>>>>>>>>>>>>>")
        print("交易记录")
        for record in stockTradingRecords[stockCode]:
            outputStockInfo(record)
            #买入/卖出股票, 非分红与基金
            if record['transaction'] != 'dividend' and record['shares'] != '': 
                if record['transaction'] == 'buy':
                    totalUnits += float(record['shares'])
                    totalCost += float(record['Total amount'])
                else:
                    averageUnitCost = (-1*totalCost) / totalUnits
                    #减少的成本=(卖出前持仓均价)*(卖出份额)
                    totalCost += (float(record['shares']) * averageUnitCost)
                    #卖出获利:(卖出单价 - 之前买入平均价) *份额
                    yieldAsForNow += (float(record['unit price']) - averageUnitCost)*float(record['shares'])
                    totalUnits -= float(record['shares']) 
            #分红
            else: 
                yieldAsForNow += float(record['Total amount'])
                totalCost += float(record['Total amount'])

        totalYield += yieldAsForNow

        #设置大于一是过滤掉计算过程当中产生的误差，这个值很小
        if totalUnits >= 1: 
            print("成本价: "+str(getRoundTwoDecimal(-totalCost/totalUnits)))
            print("持有数量: "+str(totalUnits))  
            print("持仓成本: "+str(-totalCost)) 

        
        print("历史收益: "+str(getRoundTwoDecimal(yieldAsForNow)))
        
      
        #如持有当前股票，获取并打印股票当前最新信息
        if totalUnits != 0 and isValidStockCode(stockCode): 
            #如果是周末，则获取礼拜五作为有效时间
            lastValidDate = datetime.datetime.now().strftime('%Y%m%d') if isWeekday() else getLastValidDate()
          
            current_stock_hist = getStockInfo(stockCode, lastValidDate, lastValidDate)

            #按今日收盘价计算持仓市值
            marketValue = current_stock_hist.loc[0,'收盘':'收盘'].values[0] * totalUnits
            print("持仓市值: "+str(getRoundTwoDecimal(marketValue)))
            print("持仓盈亏: "+str(getRoundTwoDecimal(totalCost - (-1*marketValue))))
            print("盈亏比例: "+str(getRoundTwoDecimal((totalCost - (-1*marketValue))*100/-totalCost))+"%")
            print("-------")
            print(current_stock_hist.loc[0,'日期':'最低'].to_string())
            holdingStockValue += marketValue
            holdingStockCost += totalCost
        print("<<<<<<<<<<<<<<<<<<<")
          
        print()

    print("------------------------")
    print("历史总收益: "+str(totalYield))
    print("持仓总市值: "+str(holdingStockValue))
    print("持仓总成本: "+str(holdingStockCost))
    print("持仓盈亏:   "+str(holdingStockCost + holdingStockValue))
    print("持仓盈亏比: "+str(getRoundTwoDecimal(((holdingStockCost + holdingStockValue)/-holdingStockCost)*100))+"%")


def getRoundTwoDecimal(number):
    return round(number, 2)

def transactionsForIndividualStock(stockData):
    stockTradingRecords = dict() #结构为类似java map
    for row in stockData:
         #以个股代码为key, 储存个股交易记录
        if row['code'] in stockTradingRecords:
            stockTradingRecords[row['code']].append(row)
        else:
            stockTradingRecords[row['code']] = [row]

    return stockTradingRecords


def outputStockInfo(record):
    if record['transaction'] == 'buy':
        print("> 买入: ", end=" ")
    elif record['transaction'] == 'sold':
        print("> 卖出: ", end=" ")
    else:
        print("> 分红: ", end=" ")

    print("份额: "+record['shares']       + " | "  , end=" ")
    print("总价: "+record['Total amount'] + " | "  , end=" ")
    print("成交单价: "+record['unit price']+ " | "  , end=" ")
    print("日期: "+record['date']+ " | "          )


def getDataFromCSV(csvFileName):
    #retrieve data from current .csv file
    stockData = list()
    with codecs.open(csvFileName, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stockData.append(row)
    return stockData


def isValidStockCode(stockCode):
    #validating stock code, excluded fund's code
    return len(re.findall(r'^(60[0-3]|00[0-4]|300)[0-9][0-9][0-9]$',stockCode)) != 0


#crawling for latest stock info
def getStockInfo(stockCode, start_date, end_date ):
    return ak.stock_zh_a_hist(symbol=stockCode, period="daily", start_date=start_date, end_date=start_date, adjust="")
        

def isWeekday():
    day = datetime.datetime.today().weekday()
    return True if day < 5 else False


def getLastValidDate():
    today = datetime.date.today()
    if isWeekday():
        return today
    else:
        return today - datetime.timedelta(days = (1 if today == 5 else 2))





main()