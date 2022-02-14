
import os.path
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
        "People":{"Chairman":None, "ChiefExecutive":None, "Directors":{}},
        "Company Name":None,
        "UK Companies House Registered Number":None,
        "Start date covered by report":None,
        "End date covered by report":None
        
    
    }
    

    # Get Company Name, Director Info etc

    
    important_role_patterns = ["Chairman","ChiefExecutive","Director[0-9]+"]
    important_people = set()

    for tag in ixbrl_file.nonnumeric:

        #Getting important people from document 
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

        elif tag.name == "EntityCurrentLegalOrRegisteredName":
            data["Company Name"] = tag.value

        elif tag.name == "UKCompaniesHouseRegisteredNumber":
            data["UK Companies House Registered Number"] = tag.value

        elif tag.name == "StartDateForPeriodCoveredByReport":
            if re.match(r"^\d{4}-\d{2}-\d{2}$",tag.value):
                year,month,day = [int(x) for x in tag.value.split("-")] #TODO: We can separate y,m,d or leave as yyyy-mm-dd.
                data["Start date covered by report"] = tag.value

        elif tag.name == "EndDateForPeriodCoveredByReport":
            if re.match(r"^\d{4}-\d{2}-\d{2}$",tag.value):
                year,month,day = [int(x) for x in tag.value.split("-")] #TODO: We can separate y,m,d or leave as yyyy-mm-dd.
                data["End date covered by report"] = tag.value

        

        

    #Getting Company Name

    #Getting Company Reference Number


    # Get Balance Sheet Info

    

    #Get etc etc

    #Write to json file
    if True:
        with open(destination_path,"w") as destination_file:
            json.dump(data,destination_file)
        
def checkPaths(input_path,destination_path):
    if os.path.exists(destination_path):
            print(f"Overwriting {destination_path}")
    if not os.path.exists(input_path):
        print(f"File '{input_path}' not found")
        return False
    return True

def checkAndcreateJSON(input_path,destination_path):
    if checkPaths(input_path,destination_path):
        createJSON(input_path,destination_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Expected 2 argument : python <ixbrl-file-path> <destination-json-path>")
    else:
        input_path = sys.argv[1]
        destination_path = sys.argv[2]
        checkAndcreateJSON(input_path,destination_path)


            




