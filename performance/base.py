'''
Performance Testing Base Module.  Defines the AbstractTest that will be inherited by all performance test classes.

Created on Apr 21, 2015

@author: arbennett
'''
import re
import os
import operator
import matplotlib.pyplot as pyplot
import glob
import jinja2
from abc import ABCMeta, abstractmethod

import util.variables

# A mapping of the options to the test cases that can be run
cases = {'none' : [],
         'dome' : ['dome'],
         'gis' : ['gis'],
         'all' : ['dome', 'gis']}

''' Return a list of options '''
def choices():
    return list( cases.keys() )

''' Return the tests associated with an option '''
def choose(key):
    return cases[key] if cases.has_key(key) else None

'''
AbstractTest provides base functionality for a Performance test

Each test within LIVV needs to be able to run specific test code, and
generate its output.  Tests inherit a common method of generating 
scaling plots
'''
class AbstractTest(object):
    __metaclass__ = ABCMeta

    ''' Constructor '''
    def __init__(self):
        self.name = "n/a"    # A name for the test
        self.testsRun = []    # A list of the test cases run
        self.plotDetails = dict()    # Summary of plots generated
        self.fileTestDetails = dict()    # Mapping of tests to files
        self.modelDir, self.benchDir = "", "" # Paths to the model and benchmark data
        self.modelConfigs, self.benchConfigs = dict(), dict()    # Summaries of the config files parsed
        self.modelTimingData, self.benchTimingData = dict(), dict()    # Summaries of the timing data parsed

        # A list of some key indicators 
        self.summary = dict()

    ''' Definition for the general test run '''
    @abstractmethod
    def run(self, test):
        pass

    '''
    Generates scaling plots for each variable and dycore combination of a given
    type.

    @param type : the overarching test category to generate scaling plots for (ie dome/gis)
    '''
    def runScaling(self, type, resolutions):
        self.imagesGenerated = []
        print(os.linesep + "  Generating scaling plots for " + type + "....")
        tests = filter(re.compile(type + "*").search, self.modelTimingData.keys())

        self.weakScaling(type, resolutions)
        self.strongScaling(type, resolutions)

        # Record the plots
        self.plotDetails['Scaling'] = self.imagesGenerated

    '''
    Run weak scaling analysis
    '''
    def weakScaling(self, type, resolutions):
        return

    '''
    Run strong scaling analysis
    '''
    def strongScaling(self, type, resolutions):
        # Generate all of the plots
        for res in sorted(resolutions):
            # Fix string for Greenland runs
            test = type + res
            # Add the data if it's available
            if self.modelTimingData[test] != [] and self.modelTimingData[test] != [[],[]]:
                modelData = self.modelTimingData[test]
                fig, ax = pyplot.subplots(1)
                pyplot.title("Strong scaling for " + type  + res)
                pyplot.xlabel("Number of processors")
                pyplot.ylabel("Time (s)")
                pyplot.xticks()
                pyplot.yticks()
                ax.plot(modelData[0], modelData[1], 'bo-', label='Model')

                # Add benchmark data if it's there
                if self.benchTimingData[test] != [] and self.benchTimingData[test] != [[],[]]:
                    benchData = self.benchTimingData[test]
                    ax.plot(benchData[0], benchData[1], 'r^--', label='Benchmark')
                    pyplot.legend()

                print("Saving plot to " + util.variables.imgDir + os.sep + self.name + os.sep + type + "_" + res + "_scaling" + ".png")
                pyplot.savefig(util.variables.imgDir + os.sep + self.name.capitalize() + os.sep + type + "_" + res +  "_scaling" + ".png")
                self.imagesGenerated.append( [type + "_" + res + "_scaling" + ".png", "Strong scaling for " + type + res])


    '''
    Create a {{test}}.html page in the output directory.
    This page will contain a detailed list of the results from LIVV.  Details
    from the run are pulled from two locations.  Global definitions that are 
    displayed on every page, or used for navigation purposes are imported
    from the main livv.py module.  All test specific information is supplied
    via class variables.
    
    @note Paths that are contained in templateVars should not be using os.sep
          since they are for html.
    '''
    def generate(self):
        # Set up jinja related variables
        templateLoader = jinja2.FileSystemLoader(searchpath=util.variables.templateDir)
        templateEnv = jinja2.Environment(loader=templateLoader, extensions=["jinja2.ext.do",])
        templateFile = "/performance_test.html"
        template = templateEnv.get_template(templateFile)

        # Set up relative paths
        indexDir = ".."
        cssDir = indexDir + "/css"
        imgDir = indexDir + "/imgs"

        # Grab all of our images
        testImgDir = util.variables.imgDir + os.sep + self.name
        testImages = [os.path.basename(img) for img in glob.glob(testImgDir + os.sep + "*.png")]
        testImages.append([os.path.basename(img) for img in glob.glob(testImgDir + os.sep +"*.jpg")])
        testImages.append([os.path.basename(img) for img in glob.glob(testImgDir + os.sep +"*.svg")])

        # Set up the template variables  
        templateVars = {"timestamp" : util.variables.timestamp,
                        "user" : util.variables.user,
                        "comment" : util.variables.comment,
                        "testName" : self.name,
                        "indexDir" : indexDir,
                        "cssDir" : cssDir,
                        "imgDir" : imgDir,
                        "testDescription" : self.description,
                        "testsRun" : self.testsRun,
                        "testHeader" : util.variables.parserVars,
                        "testDetails" : self.fileTestDetails,
                        "plotDetails" : self.plotDetails,
                        "modelConfigs" : self.modelConfigs,
                        "benchConfigs" : self.benchConfigs,
                        "modelTimingData" : self.modelTimingData,
                        "benchTimingData" : self.benchTimingData,
                        "testImages" : testImages}
        outputText = template.render( templateVars )
        page = open(util.variables.indexDir + os.sep + "performance" + os.sep + self.name.lower() + '.html', "w")
        page.write(outputText)
        page.close()
