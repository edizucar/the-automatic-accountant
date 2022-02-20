import sys
import json
import os
import matplotlib.pyplot as plt

sys.path.append('.')
sys.path.append('../data_analysis')
<<<<<<< HEAD
from data_mining.data_mine import checkAndcreateJSON,checkAndGetJSON
=======
from data_mining.data_mine import checkAndGetJSON
>>>>>>> 938cd0caddceb6d6876474abfa8d44c8c966e6ff

#Find out percentage change of a specific index, eg. gross profit,
#from data1 to data2
def change(data1, data2, index):
    index1 = data1[index]
    index2 = data2[index]
    if(index1 == 0):
        return 0
    return (index2 - index1) / (index1)

#Just some examples of indices where we can look at the change over time
def checkIfSuspicious(comparison, indices):
    drastic_changes = {}
    none_values = {}
    for index in indices:
        diff = comparison[index]["Relative Change"]
        if diff is None:
            none_values[index] = diff
        elif abs(diff) > 0.2:
            drastic_changes[index] = diff
    return {"Drastic Changes": drastic_changes, "None values": none_values}

#Plot graphs of specific indices over time
def plotOverTime(data, index, name):
    plt.plot(data["name"], index)
    plt.savefig('graphs/' + name + '.png')

def returnCompare(data1, data2, index):
    company1 = data1[index]
    company2 = data2[index]
    if company1 is None or company2 is None:
        absolute_change = None
    else:
        absolute_change = company2 - company1
    if absolute_change is None: 
        relative_change = None
    else:
        relative_change = change(data1, data2, index)
    return {"Company1": company1, "Company2": company2, "Absolute Change": absolute_change, \
        "Relative Change": relative_change}

def company_details(data):
    d = {}
    for x in ["Company Name", "UK Companies House Registered Number", "Start date covered by report", "End date covered by report"]:
        d[x] = data[x]
    return d



#Compare two sets of data, returns a dictionary which has all the data, absolute changes, relative changes, as well as points that are worth reporting 
#(including over 20% change in certain indices, certain indices being negative when they shouldn't be)
def compare(data1, data2):
    #Temporary replace None values by 0 function, should update analysis function in the future to handle None values instead of this
    profit_and_loss1 = data1["Profit & Loss Account"]
    profit_and_loss2 = data2["Profit & Loss Account"]
    turnover = returnCompare(profit_and_loss1, profit_and_loss2, "Turnover")
    gross_profit = returnCompare(profit_and_loss1, profit_and_loss2, "Gross profit/loss")
    net_profit = returnCompare(profit_and_loss1, profit_and_loss2, "Net profit/loss")
    balance1 = data1["Balance Sheet"]
    balance2 = data2["Balance Sheet"]
    fixed_assets1 = balance1["Fixed assets"]
    fixed_assets2 = balance2["Fixed assets"]
    tangible_fixed_assets = returnCompare(fixed_assets1, fixed_assets2, "Tangible fixed assets")
    investment_fixed_assets = returnCompare(fixed_assets1, fixed_assets2, "Investments fixed assets")
    fixed_asset_balance = returnCompare(fixed_assets1, fixed_assets2, "Fixed assets balance")
    current_assets1 = balance1["Current assets"]
    current_assets2 = balance2["Current assets"]
    debtors = returnCompare(current_assets1, current_assets2, "Debtors (due within one year)")
    cash_balance = returnCompare(current_assets1, current_assets2, "Cash balance")
    current_assets_balance = returnCompare(current_assets1, current_assets2, "Current assets balance")

    current_liabilities1 = balance1["Current liabilities"]
    current_liabilities2 = balance2["Current liabilities"]
    creditors = returnCompare(current_liabilities1, current_liabilities2, "Creditors (due within one year)")

    current_liabilities_balance = returnCompare(current_liabilities1, current_liabilities2, \
        "Current liabilities balance")
    net_al_balance = returnCompare(balance1, balance2, \
        "Net assets/liabilities balance")
    ratio1 = data1["Ratio Analysis Table"]
    ratio2 = data2["Ratio Analysis Table"]
    gross_profit_margin = returnCompare(ratio1, ratio2, "Gross profit margin")
    liquidity_ratio = returnCompare(ratio1, ratio2, "Liquidity ratio")
    debtor_days = returnCompare(ratio1, ratio2, "Debtor days")
    comparison = {"Turnover": turnover, "Gross profit/loss": gross_profit, \
        "Net profit/loss": net_profit, "Tangible fixed assets": tangible_fixed_assets, "Investments fixed assets": investment_fixed_assets, "Fixed assets balance": \
            fixed_asset_balance, "Debtors (due within one year)": debtors, "Cash balance": cash_balance, "Current assets balance": current_assets_balance, \
                "Creditors (due within one year)": creditors, "Current liabilities balance": current_liabilities_balance, "Net assets/liabilities balance": \
                    net_al_balance, "Gross profit margin": gross_profit_margin, "Liquidity ratio": liquidity_ratio, "Debtor days": debtor_days}

    #Checking for indicies that report a 20%+ change 
    suspicious_changes = checkIfSuspicious(comparison, comparison.keys())
    comparison["Suspicious Changes"] = suspicious_changes

    #Checking for indicies that shouldn't be negative, but are
    negative_indices = {}
    for positive_index in ["Turnover", "Tangible fixed assets", "Investments fixed assets", "Fixed assets balance", "Debtors (due within one year)", "Cash balance", "Current assets balance",\
        "Creditors (due within one year)", "Current liabilities balance", "Net assets/liabilities balance"]:
        companies = {}
        if comparison[positive_index]["Company1"] is not None and comparison[positive_index]["Company1"] < 0:
            companies["Company1"] = True
        if comparison[positive_index]["Company2"] is not None and comparison[positive_index]["Company2"]< 0:
            companies["Company2"] = True
        if(len(companies) > 0):
            negative_indices[positive_index] = companies
    comparison["Indices that are negative but should not be"] = negative_indices
    comparison["Company1"] = company_details(data1)
    comparison["Company2"] = company_details(data2)

    return comparison

def main():
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    dir1 = dir.replace('data_analysis', 'data_mining\input-files')
    os.chdir(dir1)
    data1 = checkAndGetJSON('CE Statutory Accounts FY14-15.html')
    data2 = checkAndGetJSON('CUTS Statutory Accounts FY14-15.html')
    comparison = compare(data1,data2)
    os.chdir(dir)
    with open('comparison.json', 'w') as fp:
        json.dump(comparison, fp)
    print(comparison)
    
    
if __name__ == "__main__":
    main()