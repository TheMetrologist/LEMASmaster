#!/bin/sh
#LEMASIsRunning.sh
#   Tested with Linux Mint 18.2 Sonya
#
#///////////////////////////////////////////////////////////////////////////////
## LEMASIsRunning.sh Notes
#   August, 2017
#   Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
#       PHONE: 301 975 8746
#       EMAIL: michael.braine@nist.gov (use this instead of phone)
#
#   Purpose
#       Shell script to log into remote machine and check if process is running
#
#   Inputs
#       -$1 - keygen - path to RSA keygen
#       -$2 - hostaddr - user@host
#       -$3 - LEMASmasterdir - path of master scripts
#       -$4 - group - group number
#       -$5 - building - building number
#       -$6 - lab - lab number
#       -$7 - WEBBASEDIR - path to website base
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
#   Setup of keygen
#       On host computer, use terminal command: ssh-keygen
#       Follow prompts to generate key. Copy from host to client using terminal command: ssh-copy-id -i <key file> <client>@<hostname>
#
##///////////////////////////////////////////////////////////////////////////////
## Change log from v1.05 to v1.06
#   March 11, 2019
#
#   ver 1.06 - added output of string for environment status
#
#///////////////////////////////////////////////////////////////////////////////

#get inputs
keygen=$1
hostaddr=$2
LEMASmasterdir=$3
group=$4
building=$5
lab=$6
WEBBASEDIR=$7

timeout 5 ssh -i $keygen $hostaddr sh < $LEMASmasterdir/LEMASmasterscripts/sshprocess.sh > /tmp/LEMASstatus 2>/dev/null   #ssh to device and run script, do not print error messages
if [ $? -eq 0 ]                                                                 #if connected, return status of LEMASRun.py process
then
  month=$(date -d "$D" +'%B')
  year=$(date -d "$D" +'%Y')
  # get data from *.labsettings file and strip down string
  Trangeline=$(grep -nr 'Temperature range' $WEBBASEDIR'labsettings/'$building'_'$lab'.labsettings' | cut -d : -f 1)
  Trangeline=$((Trangeline + 1))
  RHrangeline=$(grep -nr 'Humidity range' $WEBBASEDIR'labsettings/'$building'_'$lab'.labsettings' | cut -d : -f 1)
  RHrangeline=$((RHrangeline + 1))
  Trange=$(sed -n $Trangeline','$Trangeline'p' $WEBBASEDIR'labsettings/'$building'_'$lab'.labsettings')
  RHrange=$(sed -n $RHrangeline','$RHrangeline'p' $WEBBASEDIR'labsettings/'$building'_'$lab'.labsettings')
  lastline=$(sed -e '$!d' $WEBBASEDIR'data/'$group'/'$building'/'$lab'/'$building'_'$lab'_'$month$year'-all.env.csv')
  Tlast=$(echo $lastline | cut -d ',' -f2)
  RHlast=$(echo $lastline | cut -d ',' -f3)
  Tmin=$(echo $Trange | cut -d ',' -f1 | sed 's/\[//g')
  Tmax=$(echo $Trange | cut -d ',' -f2 | sed 's/\]//g')
  RHmin=$(echo $RHrange | cut -d ',' -f1 | sed 's/\[//g')
  RHmax=$(echo $RHrange | cut -d ',' -f2 | sed 's/\]//g')
  if (( $(echo "$Tlast>$Tmax" | bc -l) )) || (( $(echo "$Tlast<$Tmin" | bc -l) ))
  then
    if (( $(echo "$RHlast>$RHmax" | bc -l) )) || (( $(echo "$RHlast<$RHmin" | bc -l) ))
    #both out
    then
      string='</td><td><FONT style=\"BACKGROUND-COLOR: #858585\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>'
    elif (( $(echo "$RHlast<$RHmax" | bc -l) )) && (( $(echo "$RHlast>$RHmin" | bc -l) ))
    #only T out
    then
      string='</td><td><FONT style=\"BACKGROUND-COLOR: #FF0000\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>'
    fi
  elif (( $(echo "$RHlast>$RHmax" | bc -l) )) || (( $(echo "$RHlast<$RHmin" | bc -l) ))
  #only RH out
  then
    if (( $(echo "$Tlast<$Tmax" | bc -l) )) && (( $(echo "$Tlast>$Tmin" | bc -l) ))
    then
      string='</td><td><FONT style=\"BACKGROUND-COLOR: #0000FF\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>'
    fi
  #both in
  else
    string='</td><td><FONT style=\"BACKGROUND-COLOR: #008000\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>'
  fi

  # echo $(cat /tmp/LEMASstatus)$string
  echo $(cat /tmp/LEMASstatus)
else                                                                            #otherwise, if could not connect, return OFFLINE status
  echo "<FONT style=\"BACKGROUND-COLOR: #FF0000\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OFFLINE&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT><td><FONT style=\"BACKGROUND-COLOR: #FFFF00\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>"
fi
