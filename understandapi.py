import sys
import platform
import statistics
import numpy as np

if platform.system() == "Windows":
    sys.path.append('C:/Program Files/SciTools/bin/pc-win64/Python')
else:
    sys.path.append('/Applications/Understand.app/Contents/MacOS/Python')

# Relevant Understand API Documentation:
# https://scitools.com/sup/api-2/
# https://scitools.com/documents/manuals/python/understand.html
# help(understand)
import understand


# -------------------------
#       METRICS
# -------------------------

# ATFD (Access to Foreign Data)
# Class-Level Metric
def getATFD(classObj):
    classATFD = 0
    for amethod in classObj.ents("Define", "Method"):
        # https://scitools.com/documents/manuals/html/understand_api/kindApp121.html
        # https://scitools.com/documents/manuals/html/understand_api/kindApp158.html
        # NOTE: Includes all foreign methods called, even if not a getter or setter
        for aent in amethod.ents("Call, Use, Set", "Method ~unresolved ~unknown, Variable ~unresolved ~unknown"):
            if classObj.longname() not in aent.longname():
                classATFD += 1
    return classATFD


# WMC (Weighted Method Count)
# Class-Level Metric
# = SumCyclomaticModified
def getWMC(classObj):
    return classObj.metric(["SumCyclomaticModified"])['SumCyclomaticModified'] or 0


# TCC (Tight Class Cohesion) 
# Class-Level Metric
def getTCC(classObj):
    methods = classObj.ents("Define", "Method")
    numberOfPairs = 0
    numberOfShares = 0
    for x in range(0, len(methods)):
        for y in range(x + 1, len(methods)):
            numberOfPairs += 1
            atrrsAccessedInMethodX = methods[x].ents("Use, Set", "Variable ~unresolved ~unknown")
            atrrsAccessedInMethodY = methods[y].ents("Use, Set", "Variable ~unresolved ~unknown")
            atrrsAccessedInMethodXNames = set()
            atrrsAccessedInMethodYNames = set()
            for attr in atrrsAccessedInMethodX:
                atrrsAccessedInMethodXNames.add(attr.longname())
            for attr in atrrsAccessedInMethodY:
                atrrsAccessedInMethodYNames.add(attr.longname())
            commonAttrs = atrrsAccessedInMethodXNames.intersection(atrrsAccessedInMethodYNames)
            for atrrName in commonAttrs:
                if classObj.longname() in atrrName:
                    numberOfShares += 1
                    break
    if numberOfPairs == 0:
        # NOTE: Default is currently 0.0
        return 0.0
    else:
        return (numberOfShares / numberOfPairs) * 1.0

# LAA (Locality of Attribute Accesses)
def getLAA(classObj):
    # TODO(INCOMPLETE): Calculate LAA
    return 1

# FDP (Foreign Data Providers)
def getFDP(classObj):
    # TODO(INCOMPLETE): Calculate FDP
    return 1

# LOC (Lines of Code)
# Class- or metric-level metric
def getLOC(classOrMethodObj):
    return classOrMethodObj.metric(["CountLineCode"])['CountLineCode'] or 0

# CMC (Complex Method Count)
# Returns number of methods in class with complexity greater than the threshold
# Original, custom metric (used to determine Complex Class smell)
# Class-level metric
def getCMC(classObj, complexityThreshold):
    count = 0
    for amethod in classObj.ents("Define", "Method"):
        if getCyclomatic(amethod) > complexityThreshold:
            count += 1
    return count

# Cyclomatic Complexity
# Class- or metric-level metric
def getCyclomatic(methodObj):
    return methodObj.metric(["Cyclomatic"])['Cyclomatic'] or 0


# -------------------------
#       SMELLS
# -------------------------

def extractSmells(projectPath, csvOutputPath, log):
    delm = ","
    includeMetricsInCsv = True

    FEW = 4
    ONE_THIRD = 1/3
    HIGH_METHOD_COMPLEXITY = 10

    db = understand.open(projectPath)

    totalClassesCount = len(db.ents("Class"))
    totalMethodsCount = len(db.ents("Method"))

    print("\tCalculating complex metrics for "+str(totalClassesCount) + " classes...")

    classLib = list()
    methodLib = list()

    allClassLOC = list()
    allClassWMC = list()
    allMethodLOC = list()

    godClasses = set()
    lazyClasses = set()
    complexClasses = set()
    featureEnvyClasses = set()
    longMethods = set()

    for aclass in db.ents("Class"):
        if (len(classLib)+1) % 200 == 0:
            print("\t\t" + str(round((len(classLib)/totalClassesCount)*100)) + "% complete" ) 

        classLongName = aclass.longname()

        classMetricATFD = getATFD(aclass)
        classMetricWMC = getWMC(aclass)
        classMetricTCC = 0# getTCC(aclass)
        classMetricLAA = getLAA(aclass)
        classMetricFDP = getFDP(aclass)
        classMetricLOC = getLOC(aclass)
        classMetricCMC = getCMC(aclass, HIGH_METHOD_COMPLEXITY)

        allClassWMC.append(classMetricWMC)
        allClassLOC.append(classMetricLOC)

        classLib.append({"name": classLongName, "ATFD": classMetricATFD, "WMC": classMetricWMC, "TCC": classMetricTCC,
            "LAA": classMetricLAA, "FDP": classMetricFDP, "LOC": classMetricLOC, "CMC": classMetricCMC})

    print("\tCalculating complex metrics for "+str(totalMethodsCount) + " methods...")

    for amethod in db.ents("Method ~unresolved ~unknown"):
        if (len(methodLib)+1) % 5000 == 0:
            print("\t\t" + str(round((len(methodLib)/totalMethodsCount)*100)) + "%% complete" ) 

        methodLongName = amethod.name()

        methodMetricLOC = getLOC(amethod)

        allMethodLOC.append(methodMetricLOC)

        methodLib.append({"name": methodLongName, "LOC": methodMetricLOC})

    print("\tCalculating system-wide averages and metrics")

    meanClassWMC = statistics.mean(allClassWMC)
    devClassWMC = statistics.pstdev(allClassWMC)
    veryHighClassWMC = meanClassWMC + (1.5 * devClassWMC) # 1.5 std. dev. above the mean (upper ~15%)
    # TODO(performance improvement): Improve such that 1st quartile LOC can be cacluated without storing all
    # observations (see http://www.cs.wustl.edu/~jain/papers/ftp/psqr.pdf) for "Lazy Class"
    firstQuartileClassLOC = np.percentile(allClassLOC, 25) # Get the 1st quartitle
    meanMethodLoc = statistics.mean(allMethodLOC)

    log.write("Class WMC: mean = " + str(meanClassWMC) + ", pstdev = " + str(devClassWMC) + ", VERY_HIGH = " + str(veryHighClassWMC) + "\n")
    log.write("Class LOC: 1st Quartile = " + str(firstQuartileClassLOC) + "\n")
    log.write("Method LOC: mean = " + str(meanMethodLoc) + "\n")

    print("\tApplying code smell thresholds")

    # Class-Level Smells

    outputFile = open(csvOutputPath, "w")
    outputData = delm.join(["Class", "God Class", "Lazy Class", "Complex Class", "Feature Envy"])
    if includeMetricsInCsv:
            outputData += delm + delm.join(["Metric: ATFD", "Metric: WMC", "Metric: TCC", "Metric: LOC", "Metric: CMC"])
    outputFile.write(outputData + "\n")

    for aclass in classLib:
        # God Class
        # - ATFD (Access to Foreign Data) > Few
        # - WMC (Weighted Method Count) >= Very High
        # - TCC (Tight Class Cohesion) < 1/3
        classSmellGod = (aclass["ATFD"] > FEW) and (aclass["WMC"] >= veryHighClassWMC) and (aclass["TCC"] < ONE_THIRD)

        # Lazy Class
        # - LOC (Lines of Code) < 1st quartile of system
        classSmellLazy = (aclass["LOC"] < firstQuartileClassLOC)

        # Complex Class
        # - CMC (Complex Method Count; number of methods with complexity > HIGH_METHOD_COMPLEXITY) >= 1
        classSmellComplex = (aclass["CMC"] >= 1)

        # Feature Envy
        # - ATFD (Access to Foreign Data) > Few
        # - LAA (Locality of Attribute Accesses) < 1/3
        # - FDP (Foreign Data Providers) <= FEW
        classSmellFeatureEnvy = (aclass["ATFD"] > FEW) and (aclass["LAA"] < ONE_THIRD) and (aclass["FDP"] <= FEW )

        if classSmellGod:
            godClasses.add(aclass["name"])
        if classSmellLazy:
            lazyClasses.add(aclass["name"])
        if classSmellComplex:
            complexClasses.add(aclass["name"])
        if classSmellFeatureEnvy:
            featureEnvyClasses.add(aclass["name"])

        csvLine = delm.join([aclass["name"], str(classSmellGod), str(classSmellLazy), str(classSmellComplex), str(classSmellFeatureEnvy)])
        if includeMetricsInCsv:
            csvLine += delm + delm.join([str(aclass["ATFD"]), str(aclass["WMC"]), str(aclass["TCC"]), str(aclass["LOC"]), str(aclass["CMC"])])
        outputFile.write(csvLine + "\n")

    outputFile.close()

    # Method-Level Smells

    outputFile = open(csvOutputPath+"method.csv", "w")
    outputData = delm.join(["Method", "Long Method"])
    if includeMetricsInCsv:
            outputData += delm + delm.join(["Metric: LOC"])
    outputFile.write(outputData + "\n")

    for amethod in methodLib:
        # Long Method
        # - LOC (Lines of Code) > mean of system
        methodSmellLong = (amethod["LOC"] > meanMethodLoc)

        if methodSmellLong:
            longMethods.add(amethod["name"])

        csvLine = delm.join([amethod["name"], str(methodSmellLong)])
        if includeMetricsInCsv:
            csvLine += delm + delm.join([str(amethod["LOC"])])
        outputFile.write(csvLine + "\n")

    outputFile.close()

    #log.write("\n\nGod Classes (count = " + str(len(godClasses)) + "): " + str(godClasses) + "\n\n")
    #log.write("\n\nLazy Classes (count = " + str(len(lazyClasses)) + "): " + str(lazyClasses) + "\n\n")
    #log.write("\n\nFeature Envy (count = " + str(len(featureEnvyClasses)) + "): " + str(featureEnvyClasses) + "\n\n")

    summaryData = "\tCode smell extraction complete"

    summaryData = "\tClass-Level Smells:"
    summaryData += "\n\t\tGod Class = " + str(len(godClasses))
    summaryData += "\n\t\tLazy Class = " + str(len(lazyClasses))
    summaryData += "\n\t\tComplex Class = " + str(len(complexClasses))
    summaryData += "\n\t\tFeature Envy = " + str(len(featureEnvyClasses))

    summaryData += "\n\tMethod-Level Smells:"
    summaryData += "\n\t\tLong Method = " + str(len(longMethods))


    log.write("\n" + summaryData)
    print(summaryData + "\n")


if __name__ == '__main__':
    print("Running code smell extraction on an Understand project standalone using defaults")

    # Default project and output path
    if platform.system() == "Windows":
        logFile = open("C:/Users/cb1782/understandapi-log.txt", "w+")
        extractSmells("C:/Users/cb1782/MyUnderstandProject.udb",
                      "C:/Users/cb1782/understandapi-csv.csv",
                      logFile)
    else:
        logFile = open("/Users/charles/Documents/DIS/understandapi-log.txt", "w+")
        extractSmells("/Users/charles/Documents/DIS/understandproject.udb",
                    "/Users/charles/Documents/DIS/understandapi-csv.csv",
                    logFile)

