#!/bin/bash

#KJE 1/2013 evanskj@ornl.gov
#This is the master script to set the parameters and paths to run the LIVV kit on mac os computer
#Efforts funded by DOE BER PISCEES SciDAC project
#Currently it is designed specifically for the GLIDE dycore of the CISM model, because it is
#designed to read its output

# load these before running
#source $MODULESHOME/init/bash
#module load ncl/6.0.0
#module load nco/4.0.7
#module load python/2.7
#module load netcdf/4.1.3

#define user for website
USERNAME=$USER

#user added comment of analysis to be performed
COMMENT="test run of code"

# change to your location of livv kit
export TEST_FILEPATH="/Users/$USER/mac_run"
export SCRIPT_PATH="$TEST_FILEPATH/livv"

#specify location where the html files will be sent so they are viewable on the web
export HTML_PATH="/Users/$USER/mac_run/www"
export HTML_LINK="file://$HTML_PATH"

# flags to run the test suite versus production analysis
#TODO pass these to analysis code and only present the ones asked for
export RUN_TESTS=1
export RUN_GIS=0
export RUN_ANT=0

#specify location of the production GIS run if RUN_GIS is turned
if (($RUN_GIS == 1)); then
		#  directory of run
		export GIS_FILEPATH="$TEST_FILEPATH/gis_5km_long"
		#  cofigure file
		export GIS_CONFIG="gis_5km.config"
		#  production run screen output for collecting convergence information
		export GIS_OUTPUT="out.gnu"
		#  xml file
		export GIS_XML="trilinosOptions.xml"
	fi

if (($RUN_ANT == 1)); then
		#  directory of run
		export ANT_FILEPATH="$TEST_FILEPATH/ant"
		#  cofigure file
		export ANT_CONFIG="ant_5km.config"
		#  production run screen output for collecting convergence information
		export ANT_OUTPUT="out.gnu"
	fi

#TODO once list of plots created, add feature to have user pick which plots to make, default provided

#From here below, the commands are set automatically and don't require changing by the user

#resulting pathnames from settings given by user
export GIS_CONFIG_FILE="$GIS_FILEPATH/$GIS_CONFIG"
export GIS_OUTPUT_FILEPATH="$GIS_FILEPATH/data"
export GIS_OUTPUT_FILE="$GIS_OUTPUT_FILEPATH/$GIS_OUTPUT"

#sets the filepath to the benchmark netcdf file 
export GIS_BENCH_NETCDF_FILEPATH="$GIS_FILEPATH/data"
export GIS_BENCH_NETCDF_FILENAME="gis_5km.ice2sea.init.nc"
export GIS_BENCH_NETCDF_FILE="$GIS_BENCH_NETCDF_FILEPATH/$GIS_BENCH_NETCDF_FILENAME"

#sets the filepath to the production output file to be analyzed
export GIS_VAR_NETCDF_FILENAME="gis_5km.ice2sea.51-100.nc"
export GIS_VAR_NETCDF_FILE="$GIS_BENCH_NETCDF_FILEPATH/$GIS_VAR_NETCDF_FILENAME"

# date stamp of LIVV run to put with comments
NOW=$(date +"%m-%d-%Y-%r")
echo $NOW $COMMENT

# settings not generally altered, but leaving the option open for future extension
#location where the livv code is located
export PY_PATH="$SCRIPT_PATH/bin"
#location where the ncl directory of the ncl scripts and .nc files are located
export NCL_PATH="$SCRIPT_PATH/plots"
export DATA_PATH="$SCRIPT_PATH/data"

#command to run python script while inputting all of the files listed above
#NOTE: not all settings are required to run the python script, type "python VV_main -h" in the command line for a full list of options
#TODO include options if RUN_ANT is turned on, right now only have settings for GIS
if (($RUN_GIS == 1)); then
		python $PY_PATH/VV_main.py -d "$PY_PATH" -j "$HTML_PATH" -l "$HTML_LINK" -k "$NCL_PATH" -c "$GIS_CONFIG_FILE" -o "$GIS_OUTPUT_FILE" -s "$GIS_BENCH_NETCDF_FILE" -n "$GIS_VAR_NETCDF_FILE" -t "$TEST_FILEPATH" -i "$NOW" -m "$COMMENT" -u "$USERNAME" -g "$GIS_FILEPATH"  #-a "$DATA_PATH"
else

		python $PY_PATH/VV_main.py -d "$PY_PATH" -j "$HTML_PATH" -l "$HTML_LINK" -k "$NCL_PATH" -t "$TEST_FILEPATH" -i "$NOW" -m "$COMMENT" -u "$USERNAME"
fi

chmod 744 $HTML_PATH/*
