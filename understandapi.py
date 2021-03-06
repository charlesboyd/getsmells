import sys
import platform
import statistics
import os
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

def extractSmells(projectPath, outputPath, runName, log):
    delm = ","
    includeMetricsInCsv = True

    FEW = 4
    ONE_THIRD = 1/3
    HIGH_METHOD_COMPLEXITY = 10

    classStatusUpdateInterval = 200
    methodStatusUpdateInterval = 5000

    outputCsvFileClasses = os.path.join(outputPath, runName + "-smells-classses.csv")
    outputCsvFileMethods = os.path.join(outputPath, runName + "-smells-methods.csv")
    outputTxtDirClasses = os.path.join(outputPath, runName + "-smelly-classes")
    outputTxtDirMethods = os.path.join(outputPath, runName + "-smelly-methods")
    if not os.path.exists(outputTxtDirClasses):
        os.makedirs(outputTxtDirClasses)
    if not os.path.exists(outputTxtDirMethods):
        os.makedirs(outputTxtDirMethods)

    db = understand.open(projectPath)

    totalClassesCount = len(db.ents("Class"))
    totalMethodsCount = len(db.ents("Method"))

    print("\tCalculating complex metrics for "+str(totalClassesCount) + " classes...")

    classLib = list()
    methodLib = list()

    allClassLOC = list()
    allClassWMC = list()
    allMethodLOC = list()

    for aclass in db.ents("Class"):
        if (len(classLib)+1) % classStatusUpdateInterval == 0:
            print("\t\t" + str(round((len(classLib)/totalClassesCount)*100)) + "% complete" ) 

        classLongName = aclass.longname()

        classMetricATFD = getATFD(aclass)
        classMetricWMC = getWMC(aclass)
        classMetricTCC = getTCC(aclass)
        classMetricLOC = getLOC(aclass)
        classMetricCMC = getCMC(aclass, HIGH_METHOD_COMPLEXITY)

        allClassWMC.append(classMetricWMC)
        allClassLOC.append(classMetricLOC)

        classLib.append({"name": classLongName, "ATFD": classMetricATFD, "WMC": classMetricWMC, "TCC": classMetricTCC,
            "LOC": classMetricLOC, "CMC": classMetricCMC})

    print("\tCalculating complex metrics for "+str(totalMethodsCount) + " methods...")

    for amethod in db.ents("Method ~unresolved ~unknown"):
        if (len(methodLib)+1) % methodStatusUpdateInterval == 0:
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

    # Apply Class-Level Smells
    classSmells = {'god': set(), 'lazy': set(), 'complex': set()}

    outputFile = open(outputCsvFileClasses, "w")
    outputData = delm.join(["Class", "God Class", "Lazy Class", "Complex Class"])
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

        if classSmellGod:
            classSmells['god'].add(aclass["name"])
        if classSmellLazy:
            classSmells['lazy'].add(aclass["name"])
        if classSmellComplex:
            classSmells['complex'].add(aclass["name"])

        csvLine = delm.join([aclass["name"], str(classSmellGod), str(classSmellLazy), str(classSmellComplex)])
        if includeMetricsInCsv:
            csvLine += delm + delm.join([str(aclass["ATFD"]), str(aclass["WMC"]), str(aclass["TCC"]), str(aclass["LOC"]), str(aclass["CMC"])])
        outputFile.write(csvLine + "\n")

    outputFile.close()

    # Apply Method-Level Smells
    methodSmells = {'long': set()}

    outputFile = open(outputCsvFileMethods, "w")
    outputData = delm.join(["Method", "Long Method"])
    if includeMetricsInCsv:
            outputData += delm + delm.join(["Metric: LOC"])
    outputFile.write(outputData + "\n")

    for amethod in methodLib:
        # Long Method
        # - LOC (Lines of Code) > mean of system
        methodSmellLong = (amethod["LOC"] > meanMethodLoc)

        if methodSmellLong:
            methodSmells['long'].add(amethod["name"])

        csvLine = delm.join([amethod["name"], str(methodSmellLong)])
        if includeMetricsInCsv:
            csvLine += delm + delm.join([str(amethod["LOC"])])
        outputFile.write(csvLine + "\n")

    outputFile.close()

    print("\tWriting list of smelly classes/methods")

    summaryData = "\tCode smell extraction complete"
    summaryData = "\tNumber of Class-Level Smells:"
    for smellName, classes in classSmells.items():
        outputFileName = os.path.join(outputTxtDirClasses, smellName + ".txt")
        outputFile = open(outputFileName, "w")
        for className in classes:
            outputFile.write(className + "\n")
        outputFile.close()
        summaryData += "\n\t\t" + smellName +"  = " + str(len(classes))
    summaryData += "\n\tNumber of Method-Level Smells:"
    for smellName, methods in methodSmells.items():
        outputFileName = os.path.join(outputTxtDirMethods, smellName + ".txt")
        outputFile = open(outputFileName, "w")
        for methodName in methods:
            outputFile.write(methodName + "\n")
        outputFile.close()
        summaryData += "\n\t\t" + smellName +"  = " + str(len(methods))

    log.write("\n" + summaryData)
    print(summaryData + "\n")


if __name__ == '__main__':
    print("Running code smell extraction on an Understand project standalone using defaults")

    # Default project and output path
    if platform.system() == "Windows":
        logFile = open("C:/Users/cb1782/getsmells-test-output/understandapi-log.txt", "w+")
        extractSmells("C:/Users/cb1782/MyUnderstandProject.udb",
                      "C:/Users/cb1782/getsmells-test-output/",
                      "default",
                      logFile)
        logFile.close()
    else:
        logFile = open("/Users/charles/Documents/DIS/getsmells-test-output/understandapi-log.txt", "w+")
        extractSmells("/Users/charles/Documents/DIS/understandproject.udb",
                    "/Users/charles/Documents/DIS/getsmells-test-output/",
                    "default",
                    logFile)
        logFile.close()

