
import os.path
from unicodedata import name
from ixbrlparse import IXBRL
import re
import sys
import json


def matchAny(patterns, string):
    return len(filter(lambda pattern: re.match(pattern,string),patterns)) != 0

def searchAny(patterns, string):
    return len(filter(lambda pattern: re.search(pattern,string),patterns)) != 0

def sanitiseName(name):
    return re.sub(r"[^a-zA-Z\- ]","",name)


def createJSON(input_path,destination_path):
    with open(input_path, encoding="utf8") as file:
        ixbrl_file = IXBRL(file)

    data = {
        "test_key":"test_value",
        "People":{"Chairman":None, "ChiefExecutive":None, "Directors":{}}
    
    }
    

    # Get Company Name, Director Info etc

    #Getting important people from document 
    important_role_patterns = ["Chairman","ChiefExecutive","Director[0-9]+"]
    important_people = set()
    for tag in ixbrl_file.nonnumeric:
        if tag.name == "NameEntityOfficer":
            val = tag.context.segments[0]["value"]
            san_name = sanitiseName(tag.value) #tag.value is the string of the chairman's name
            #Exhaust the different relevant roles
            if re.search("Chairman",val):
                data["People"]["Chairman"] = san_name
            elif re.search("ChiefExecutive",val):
                data["People"]["ChiefExecutive"] = san_name
            elif re.search("Director[0-9]+",val):
                director_number = int(re.findall('\d+', val)[-1]) # Each director is assigned a number from 1-40, so I extract this number
                data["People"]["Directors"][director_number] = san_name

    # Get Balance Sheet Info

    #Get etc etc

    #Write to json file
    with open(destination_path,"w") as destination_file:
        json.dump(data,destination_file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Expected 2 argument : python <ixbrl-file-path> <destination-json-path>")
    else:
        input_path = sys.argv[1]
        destination_path = sys.argv[2]
        if os.path.exists(destination_path):
            print(f"Overwriting {destination_path}")
        if not os.path.exists(input_path):
            print(f"File '{input_path}' not found")
        else:
            createJSON(input_path,destination_path)

            


if False:
#root = ""
#f = root + "/Bilitech Ltd.xhtml"
#f = root + "CE Statutory-Accounts-FY14-15.html"

#x.contexts

    for c in x.numeric:
        print(c.name)
        if c.context.instant != None:
            print("instant: ", c.context.instant)
        if c.context.startdate != None:
            print("startdate: ", c.context.startdate)
        if c.context.enddate != None:
            print("enddate: ", c.context.enddate)
        print(c.value)
        print()




    #getting director names




