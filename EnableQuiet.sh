#!/bin/bash
#EnableQuiet.sh
#   Tested with Ubuntu 14.04
#
#///////////////////////////////////////////////////////////////////////////////
## EnableQuiet.sh Notes
#   November, 2017
#   Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
#       PHONE: 301 975 8746
#       EMAIL: michael.braine@nist.gov (use this instead of phone)
#
#   Purpose
#       Enable quiet monitoring of a lab, i.e. no messages sent
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
##//////////////////////////////////////////////////////////////////////////////
## Change log from v1.00 to v1.01
#   November 26, 2017
#
#   ver 1.01 - added ability to enable quiet on all devices
#
#///////////////////////////////////////////////////////////////////////////////

quietlist=/home/braine/BraineCode/LEMASmaster/QuietLabsTemp.list

IFS=','
while read labgroup labbuilding lab labname rsacreds hostaddr                 #loop through list
do
  #remove leading and trailing spaces
  labgroup=$(echo $labgroup | awk '$1=$1')
  labbuilding=$(echo $labbuilding | awk '$1=$1')
  lab=$(echo $lab | awk '$1=$1')
  labname=$(echo $labname | awk '$1=$1')
  rsacreds=$(echo $rsacreds | awk '$1=$1')
  hostaddr=$(echo $hostaddr | awk '$1=$1')

  echo 'Quieting '$labbuilding/$lab
  timeout 5 ssh -n -i $rsacreds $hostaddr "cp /home/pi/LEMASdist/LEMASRunQuiet.py /home/pi/LEMASdist/LEMASRun.py; sudo reboot"
done < $quietlist
unset IFS
