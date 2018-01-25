import subprocess

# Relevant Understand CLI Documentation:
# https://scitools.com/support/commandline/


def analyzeCode(sourcePath, projectPath, log):
    understandVersion = str(subprocess.getoutput(['und', 'version']))
    if "Build" not in understandVersion:
        print("Error: Could not run the Understand command line (could not run 'und'); check the PATH")
        log.write("Error: '$ und version' returned '" + understandVersion + "'")
        return 1

    log.write("Understand version = " + understandVersion + "\n")
    log.write("Create project output = " +
              str(subprocess.getoutput(['und', 'create', '-languages', 'Java', projectPath])) + "\n")
    undOutput = str(subprocess.getoutput(['und', 'add', sourcePath, projectPath]))
    print("\t" + undOutput)
    log.write("Add files output = " + undOutput + "\n")
    log.write("Update settings output = " +
              str(subprocess.getoutput(['und', 'settings', '-metrics', 'all', projectPath])) + "\n")

    print("\tStarting metric analysis...")
    log.write("Starting metric analysis...\n" +
              str(subprocess.getoutput(['und', 'analyze', projectPath])) + "\n")

    print("\tMetric analysis complete")

    return 0


if __name__ == '__main__':
    print("Running code analysis and project output on a directory standalone using defaults")

    logFile = open("C:/Users/cb1782/understandcli-log.txt", "w+")

    # Default project and output path
    analyzeCode("C:/Users/cb1782/Downloads/apache-tomcat-7.0.82-src/apache-tomcat-7.0.82-src",
                "C:/Users/cb1782/understandcli-project.udb",
                logFile)
