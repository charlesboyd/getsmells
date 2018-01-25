import understandapi
import understandcli
import sys
import os


def printCliHelp():
    print("Usage:\npython3 getsmells.py [sourcePath] [outputPath (optional)]\n")
    print("sourcePath: The path to the directory with a single project's code")
    print("outputPath: The directory to output the CSV with code smells, the debug output, and the Understand Projects "
          "(defaults to the current directory)")


def cli(args):
    if len(args) < 2:
        printCliHelp()
        return

    sourcePath = args[1]

    if not os.path.isdir(sourcePath):
        print("Error: The specified source path either does not exist or is not a directory")
        return

    runName = os.path.basename(sourcePath)

    outputPath = ""
    if len(args) >= 3:
        outputPath = args[2]

    outputCsvFile = outputPath + "/" + runName + "-smells.csv"
    outputLogFile = outputPath + "/" + runName + "-log.txt"
    print("log file = " + outputLogFile)
    projectDirectoryPath = outputPath + "/UnderstandProjects"
    if not os.path.exists(projectDirectoryPath):
        os.makedirs(projectDirectoryPath)
    projectPath = projectDirectoryPath + "/" + runName + ".udb"

    print("Step 1/2: Creating an Understand Project for '" + runName + "'")
    if understandcli.analyzeCode(sourcePath, projectPath, outputLogFile) == 1:
        return

    print("Step 2/2: Extracting code smells from metrics on '" + runName + "'")
    # if understandapi.extractSmells(projectPath, outputCsvFile, outputLogFile) == 1:
    #    return

    print("Complete! Code smell extraction for '" + runName + "' is complete.")


if __name__ == '__main__':
    # cli(sys.argv)

    # For testing
    cli(["",
         "C:/Users/cb1782/Downloads/apache-tomcat-7.0.82-src/apache-tomcat-7.0.82-src",
         "C:/Users/cb1782/output1"])
