# Copyright (c) 2015, UT-BATTELLE, LLC
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Test management module for LIVV
"""

import os
import sys
import urllib.request
import fnmatch
import subprocess

import util.variables
import util.datastructures

def check_dependencies():
    """ Run all of the checks for dependencies required by LIVV """
    cwd = os.getcwd()
    dep_dir = os.path.join(cwd, 'deps')
    library_list = ["numpy", "netCDF4", "pandas", "matplotlib"]
    error_list = []
    print(os.linesep + "Beginning Dependency Checks........")
    # Make sure we have easy_install, and if not, build it       
    try:
        from setuptools.command import easy_install
    except ImportError:
        if not os.path.exists(dep_dir):
            os.mkdir(dep_dir)
            sys.path.append(dep_dir)
        
        ez_command = install_setup_tools()
        try:
            from setuptools.command import easy_install
        except ImportError:
            print("  !------------------------------------------------------")
            print("  ! ERROR: Could not install the setuptools module!")
            print("  !        Try installing it yourself, and rerunning LIVVkit:")
            print("  !           cd deps/")
            print("  !           " + ez_command)
            print("  !           cd ..")
            print("  !           python3 livv.py...")
            print("  !------------------------------------------------------")
            exit(1)

    # Check if imports work, and if not build a copy 
    print("    Checking for external libraries....")
    libs_installed=[]
    for lib in library_list:
        try:
            __import__(lib)
            print("      Found " + lib + "!")
        except ImportError:
            print("      Could not find " + lib + ".  Building a copy for you...."),
            if not os.path.exists(dep_dir):
                os.mkdir(dep_dir)
                sys.path.append(dep_dir)
            easy_install.main(["--user",lib])
            libs_installed.append(lib)
    # ez_setup instals into $HOME/.local/lib/python2.7/site-packages/ ...
    egg_files = find_eggs(os.path.join(os.environ['HOME'], '.local'))
    # add the found site-packages to the python path
    for ef in egg_files:
        if not (ef in sys.path):
            sys.path.append(ef)
    # check libraries again
    libs_we_did_not_install = []
    for lib in library_list:
        try:
            __import__(lib)
        except ImportError:
            libs_we_did_not_install.append(lib)
    # for some reason sys path did not get updated so... try running livv again.
    if len(libs_we_did_not_install) > 0:
        print("")
        print("")        
        print("------------------------------------------------------------------------------")
        print("  External Python Libraries have been installed!  Libraries installed:")
        for lib in libs_installed:
            print("    " + lib)
        print("  Run LIVV again to continue.  ")
        print("------------------------------------------------------------------------------")
        print("")
        exit(0)
    # Show all of the dependency errors that were found
    if len(error_list) > 0:
        print("Uh oh!")
        print("")
        print("------------------------------------------------------------------------------")
        print("Errors checking dependencies.  Errors found: ")
        for err in error_list: print(err)
        print("------------------------------------------------------------------------------")
        print("")
        exit(len(error_list))
    else:
        print("Okay!" + os.linesep + "Setting up environment....")


def find_eggs(tree):
    """ This will recusively look for python '*.egg' files and folders. """
    matches = []
    for base, dirs, files in os.walk(tree):
        goodfiles = fnmatch.filter(files, '*.egg')
        matches.extend(os.path.join(base, f) for f in goodfiles)
        gooddirs = fnmatch.filter(dirs, '*.egg')
        matches.extend(os.path.join(base, d) for d in gooddirs)
    return matches


def install_setup_tools():
    """ Installs setuptools under the user python libraries """
    cwd = os.getcwd()
    url = "https://bootstrap.pypa.io/ez_setup.py"
    file_path = cwd + os.sep + "deps"
    file_name = "ez_setup.py"
    urllib.request.urlretrieve(url, file_path + os.sep + file_name)
    print("Setting up ez_setup module...")
    ez_command = "python3 " + file_name + " --user 2> ez.err > ez.out"
    ez_commands = ["cd "+file_path, ez_command, 'exit 0']
    subprocess.check_call(str.join(" ; ",ez_commands), executable='/bin/bash', shell=True)
    # ez_setup instals into $HOME/.local/lib/python2.7/site-packages/ ...
    egg_files = find_eggs(os.environ['HOME'] + os.sep + '.local')
    # add the found site-packages to the python path
    for ef in egg_files:
        if not (ef in sys.path):
            sys.path.append(ef)
    return ez_command


