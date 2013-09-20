#!/bin/bash

#KJE, AJB, NRM 8/2013 evanskj@ornl.gov
#This is the master script to set the parameters and paths to run the LIVV kit on lens
#Efforts funded by DOE BER PISCEES SciDAC project
#Currently it is designed specifically for the GLIDE dycore of the CISM model, because it is designed to read its output


# load these before running
source $MODULESHOME/init/bash #make sure to put "source $MODULESHOME/init/bash" in your .bashrc file
module load ncl/6.0.0
module load nco/4.0.7
module unload python/2.7
module load python/2.7.3
module load python_numpy/1.7.1
module load python_matplotlib/1.2.1
module load netcdf/4.1.3
module load netcdf4-python/1.0

# define user for website
USERNAME=$USER

# user added comment of analysis to be performed
COMMENT="test run of code"

# change to your location of livv kit
export TEST_FILEPATH="/tmp/work/$USER/higher-order"
export SCRIPT_PATH="$TEST_FILEPATH/livv"
#data_dir changes based on what machine livv is run on (choices: titan, hopper, mac)
export DATA_DIR="data_titan"

# specify location where the html files will be sent so they are viewable on the web
# livv will create the www directory in the HTML_PATH if it does not already exist
export HTML_PATH="/ccs/home/$USER/www"
export HTML_LINK="http://users.nccs.gov/~$USER"

# flags to select verification tests
export RUN_DOME30_DIAGNOSTIC=1
export RUN_DOME30_EVOLVING=1
export RUN_CIRCULAR_SHELF=1
export RUN_CONFINED_SHELF=1
export RUN_ISMIP_HOM_A80=0
export RUN_ISMIP_HOM_A20=0
export RUN_ISMIP_HOM_C=0
export RUN_GIS_10KM=0

# flags to select production analysis
export GIS_LARGE_TESTS=0
export RUN_DOME500=0
export RUN_GIS_5KM=0

export RUN_ANT=0

if (($RUN_ANT == 1)); then
		#  directory of run
		export ANT_FILEPATH="$TEST_FILEPATH/ant"
		#  cofigure file
		export ANT_CONFIG="ant_5km.config"
		#  production run screen output for collecting convergence information
		export ANT_OUTPUT="out.gnu"
	fi

# TODO once list of plots created, add feature to have user pick which plots to make, default provided

# From here below, the commands are set automatically and don't require changing by the user

# resulting pathnames from settings given by user
export GIS_OUTPUT_FILEPATH="$PERF_FILEPATH/data"

# date stamp of LIVV run to put with comments
NOW=$(date +"%m-%d-%Y-%r")
echo $NOW $COMMENT

# settings not generally altered, but leaving the option open for future extension
# location where the livv code is located
export PY_PATH="$SCRIPT_PATH/bin"
# location where the ncl directory of the ncl scripts and .nc files are located
export NCL_PATH="$SCRIPT_PATH/plots"

# command to run python script while inputting all of the files listed above
# NOTE: not all settings are required to run the python script, type "python VV_main -h" in the command line for a full list of options
# TODO include options if RUN_ANT is turned on, right now only have settings for GIS
if (($GIS_LARGE_TESTS == 1)); then
		python $PY_PATH/VV_main.py -d "$PY_PATH" -b "$SCRIPT_PATH" -j "$HTML_PATH" -l "$HTML_LINK" -k "$NCL_PATH" -d "$DATA_DIR" -t "$TEST_FILEPATH" -i "$NOW" -m "$COMMENT" -u "$USERNAME" -D "$RUN_DOME30_DIAGNOSTIC" -E "$RUN_DOME30_EVOLVING" -I "$RUN_CIRCULAR_SHELF" -O "$RUN_CONFINED_SHELF" -A "$RUN_ISMIP_HOM_A80" -B "$RUN_ISMIP_HOM_A20" -C "$RUN_ISMIP_HOM_C" -G "$RUN_GIS_10KM" -F "$RUN_DOME500" -H "$RUN_GIS_5KM"
else

		python $PY_PATH/VV_main.py -d "$PY_PATH" -b "$SCRIPT_PATH" -j "$HTML_PATH" -l "$HTML_LINK" -k "$NCL_PATH" -d "$DATA_DIR" -t "$TEST_FILEPATH" -i "$NOW" -m "$COMMENT" -u "$USERNAME" -D "$RUN_DOME30_DIAGNOSTIC" -E "$RUN_DOME30_EVOLVING" -I "$RUN_CIRCULAR_SHELF" -O "$RUN_CONFINED_SHELF" -A "$RUN_ISMIP_HOM_A80" -B "$RUN_ISMIP_HOM_A20" -C "$RUN_ISMIP_HOM_C" -G "$RUN_GIS_10KM" -F "$RUN_DOME500" -H "$RUN_GIS_5KM"
fi

chmod 744 $HTML_PATH/*
