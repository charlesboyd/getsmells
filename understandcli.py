import subprocess
import platform

# Relevant Understand CLI Documentation:
# https://scitools.com/support/commandline/


if platform.system() == "Windows":
    undPath = "und"
else:
    undPath = "/Applications/Understand.app/Contents/MacOS/und"

def makecmd(args):
    if platform.system() == "Windows":
        return args
    else:
        return " ".join(args)

def analyzeCode(sourcePath, projectPath, log):
    understandVersion = str(subprocess.getoutput(makecmd([undPath, 'version'])))
    if "Build" not in understandVersion:
        print("Error: Could not run the Understand command line (could not run '" + undPath + "'); check the PATH")
        log.write("Error: '$ und version' returned '" + understandVersion + "'")
        return 1

    log.write("Understand version = " + understandVersion + "\n")
    log.write("Create project output = " +
              str(subprocess.getoutput(makecmd([undPath, 'create', '-languages', 'Java', projectPath]))) + "\n")
    undOutput = str(subprocess.getoutput(makecmd([undPath, 'add', sourcePath, projectPath])))
    print("\t" + undOutput)
    log.write("Add files output = " + undOutput + "\n")
    log.write("Update settings output = " +
              str(subprocess.getoutput(makecmd([undPath, 'settings', '-metrics', 'all', projectPath]))) + "\n")

    print("\tStarting metric analysis...")
    log.write("Starting metric analysis...\n" +
              str(subprocess.getoutput(makecmd([undPath, 'analyze', projectPath]))) + "\n")

    print("\tMetric analysis complete")

    return 0


if __name__ == '__main__':
    print("Running code analysis and project output on a directory standalone using defaults")

    # Default project and output path
    if platform.system() == "Windows":
        logFile = open("C:/Users/cb1782/understandcli-log.txt", "w+")
        analyzeCode("C:/Users/cb1782/Downloads/apache-tomcat-7.0.82-src/apache-tomcat-7.0.82-src",
                    "C:/Users/cb1782/understandcli-project.udb",
                    logFile)
        logFile.close()
    else:
        logFile = open("/Users/charles/Documents/DIS/understandcli-log.txt", "w+")
        analyzeCode("/Users/charles/Documents/DIS/code/apache-tomcat-8.0.49-src",
                    "/Users/charles/Documents/DIS/understandproject.udb",
                    logFile)
        logFile.close()
