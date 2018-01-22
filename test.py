import understand
# https://scitools.com/sup/api-2/
# https://scitools.com/documents/manuals/python/understand.html
# help (understand)

print("hello!")

db = understand.open("C:\\Users\\cb1782\\MyUnderstandProject.udb")

for aclass in db.ents("Class"):
    # print directory name
    #print(aclass.longname())
    #print(aclass.metrics())
    classATFD = 0
    #if aclass.longname() == "org.apache.catalina.core.StandardContext":
    for amethod in aclass.ents("Define", "Method"):
        #print("|||> " + amethod.kindname())
        #print("---METHOD--> " + amethod.longname())
        #print(amethod.metrics())
        # https://scitools.com/documents/manuals/html/understand_api/wwhelp/wwhimpl/js/html/wwhelp.htm
        # https://scitools.com/documents/manuals/html/understand_api/wwhelp/wwhimpl/js/html/wwhelp.htm
        for aent in amethod.ents("Call, Use, Set", "Method ~unresolved ~unknown, Variable ~unresolved ~unknown"):
            if aclass.longname() not in aent.longname():
                classATFD += 1
                #print("      |+++" + aent.kindname() + "+++>" + aent.longname())
    print("ATFD for " + aclass.longname() + ": " + str(classATFD))

print(db.metrics())

# God Class
# - ATFD (Access to Foreign Data) > Few
# - WMC (Weighted Method Count) >= Very High --- 'SumCyclomaticModified'
# - TCC (Tight Class Cohesion) < 1/3
#
