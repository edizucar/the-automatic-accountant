from ixbrlparse import IXBRL

root = ""
#f = root + "/Bilitech Ltd.xhtml"
f = root + "/CE Statutory-Accounts-FY14-15.html"

with open(f, encoding="utf8") as a:
    x = IXBRL(a)

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
    
print("----------------")
print()

#for c in x.nonnumeric:
#    print(c.name)
#    print(c.value)
#    print()


#print("----------------")
#print()
