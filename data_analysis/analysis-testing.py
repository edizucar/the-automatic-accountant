import sys
import json
import os

sys.path.append('.')
sys.path.append('../data_analysis')
from data_mining.TestingMiner.ixbrl_testing import checkAndcreateJSON


#Input should be the name of a file rather than a path, assuming that all the
#data files are extracted from the same folder, can be changed later to match
#the actual name
def readFromDataFolder(file_name):
    path = os.path.realpath(__file__)
    dir = os.path.dirname(path)
    dir1 = dir.replace('data_analysis', 'data_mining/TestingMiner')
    os.chdir(dir1)
    checkAndcreateJSON(file_name, 'data.json')
    f = open('data.json')
    data = json.load(f)
    f.close()
    os.remove('data.json')
    os.chdir(dir)
    return data

def main():
    data = readFromDataFolder('CE Statutory-Accounts-FY14-15.html')
    

if __name__ == "__main__":
    main()