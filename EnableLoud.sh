#!/bin/bash
#EnableLoud.sh
#   Tested with Ubuntu 14.04
#
#///////////////////////////////////////////////////////////////////////////////
## EnableLoud.sh Notes
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
#   ver 1.00 - added ability to enable loud on all devices
#
#///////////////////////////////////////////////////////////////////////////////

loudlist=/home/braine/BraineCode/LEMASmaster/LoudLabs.list

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

  echo 'Enabling messages in '$labbuilding/$lab
  timeout 5 ssh -n -i $rsacreds $hostaddr "cp /home/pi/LEMASdist/LEMASRunLoud.py /home/pi/LEMASdist/LEMASRun.py; sudo reboot 5"
done < $loudlist
unset IFS
