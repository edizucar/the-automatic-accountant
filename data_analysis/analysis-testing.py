import sys
import json
import os
import matplotlib.pyplot as plt

sys.path.append('.')
sys.path.append('../data_analysis')
from data_mining.ixbrl_testing import checkAndcreateJSON,checkAndGetJSON


#Input should be the name of a file rather than a path, assuming that all the
#data files are extracted from the same folder, can be changed later to match
#the actual name
def readFromDataFolder(file_name):
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    dir1 = dir.replace('data_analysis', 'data_mining')
    os.chdir(dir1)
    data = checkAndGetJSON(file_name)
    os.chdir(dir)
    return data

#Find out percentage change of a specific index, eg. gross profit,
#from data1 to data2
def change(data1, data2, index):
    index1 = data1[index]
    index2 = data2[index]
    return (index2 - index1) / (index1)

#Just some examples of indices where we can look at the change over time
def checkIfScam(data1, data2):
    indices = []
    for index in indices:
        if abs(change(data1,data2, index)) > 0.2:
            return True
    return False    

#Plot graphs of specific indices over time
def plotOverTime(data, index):
    lst = []
    date = []
    for d in data:
        lst.append(d[index])
        date.append(d["Date"])
    plt.plot(lst, date)
    plt.savefig('data.png')
    

def main():
    data = readFromDataFolder('data-files\\CE Statutory-Accounts-FY14-15.html')
    
if __name__ == "__main__":
    main()