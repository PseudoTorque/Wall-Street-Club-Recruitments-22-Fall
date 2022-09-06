import pandas as p
from scipy.optimize import minimize
from scipy.optimize import Bounds


#This function returns the Yearly Return Rate from the stock data of a security. 
def getYearlyReturn(file):
    result = {}

    #The file is read and formatted in such a way that only the Date, Closing and Opening prices are considered in the pandas dataframe.
    file = p.read_csv("Q5\Src\%s.csv" % file)
    file["Date"] = p.to_datetime(file["Date"])
    file = p.DataFrame().assign(Date=file["Date"], Open=file["Open"], Close=file["Close"])

    #The data is grouped by year
    yeargroup = dict(tuple(file.groupby(file.Date.dt.year)))
    for i in yeargroup.keys():

        #the yearly return is calculated by subtracting the opening price of the year from the closing price and dividing it by the opening price.
        #The last year's data is multiplied by 3 to extrapolate the entire year since we only 4 months of data (1 quarter) and the remaining quarters are obscure.
        yearly_return = round((float(yeargroup[i].take([-1])["Close"])-float(yeargroup[i].take([0])["Open"]))/float(yeargroup[i].take([0])["Open"]), 4)
        if(i==2021):
            yearly_return *= 3
        result[i] = yearly_return
    return result

#This function calculates the Risk-Free Rate of return weighed against a government bond in particular the 10Y G-Sec Yield Rate of India.
def calculateRiskFreeReturn(gbond):
    #The file is opened and the data is formatted according to the year with the yield rate in the months of that year
    yieldrate = p.read_csv("Q5\Src\%s.csv" % gbond)
    yieldrate = p.DataFrame().assign(Date = yieldrate["Date"], Yield = yieldrate["Price"])
    yieldrate["Date"] = yieldrate["Date"].transform(lambda x: "20"+x.split(" ")[1])
    result = {}

    #the yield rate of the year is calculated by calculating the mean of the mean monthly yield rates in that year which is then stored against the year in the dictionary
    meanyield = tuple(yieldrate.groupby(["Date"])["Yield"].mean())
    r = 0
    for i in yieldrate.groupby(["Date"]):
        result[int(i[0])] = meanyield[r]/100
        r += 1
    return result

#Returns the simple population mean and standard deviation (volatility, in this case.)
def getVolatility(returns):
    mean = sum(returns)/len(returns)
    variance = sum([(i-mean)**2 for i in returns])/len(returns)
    return mean, variance**(1/2)

#This function calculates the Sharpe Ratio of the securities with the weights according to the formula Rx - Rb/sigma Rx
def getSharpeRatio(assets, weights):
    #invokes the function to return and store the Risk free rate of return from data
    Rb = calculateRiskFreeReturn("gbond")
    

    #formats the return of every asset yearwise into the yearly return of every assetwise which can simply be weighted-summed to obtain the total portfolio return of that year.
    portfolioreturn = {}  
    for i in assets:
        portfolioreturn[i] = getYearlyReturn(i)
    Rx = {}
    for i in Rb.keys():
        temp = {}
        for j in assets:
            temp[j] = portfolioreturn[j][i]
        Rx[i] = temp
    
    
    #summed according to the weights of the assets
    for i in Rx.keys():
        temp = 0
        for j in Rx[i].keys():
            temp += Rx[i][j]*(weights[j]+0.3)
        Rx[i] = temp

    #Return on assets - Risk free rate of Return / volatility gives the Sharpe Ratio.
    Rx, sigmaRx = getVolatility(Rx.values())
    Rb = sum(Rb.values())/len(Rb)
    return (Rx-Rb)/sigmaRx

#The function that the optimizer from SciPy uses to optimize. It basically only takes the weights that the assets would have and returns the value of 1/(Sharpe Ratio) so that 
#if this value is minized. The Sharpe Ratio is automatically maximized.
def toMinimize(weights):
    weights = {assets[i]: weights[i] for i in range(len(weights))}
    return 1/getSharpeRatio(assets, weights)

if __name__ == "__main__":
    #This defined the assets, the boundary conditions i.e. x,y,z are weights and x,y,z = [0, 0.1] and the constraint being sum(x, y, z) = 0.1.
    assets = ["HDFC", "ITC", "RELIANCE"]
    bounds=Bounds([0,0,0],[0.1, 0.1, 0.1])
    constraint = ({'type': 'eq', 'fun': lambda x:  0.1 - sum(x)})

    #this performs the necessary convergence and calculates the minimum value of the minizable function and as a result the maximum sharpe ratio that we can obtain.
    print(minimize(toMinimize,x0=[0,0,0],bounds=bounds, constraints = constraint, tol=1e-2, options={'maxiter': 1e3}))

    #result clearly shows that the ideal split would be 0.4, 0.3, 0.3 for HDFC, ITC and Reliance, respectively.
    print(getSharpeRatio(assets, {"HDFC":0.1,"ITC":0,"RELIANCE":0}))