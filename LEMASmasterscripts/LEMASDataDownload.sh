#!/bin/sh
#LEMASDataDownload.sh
#   Tested with Linux Mint 18.2 Sonya
#
#///////////////////////////////////////////////////////////////////////////////
## LEMASDataDownload.sh Notes
#   August, 2017
#   Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
#       PHONE: 301 975 8746
#       EMAIL: michael.braine@nist.gov (use this instead of phone)
#
#   Purpose
#       Shell script to secure copy data files from client computer on a schedule defined by sleeptimer
#       Requires the setup of rsacredss for ssh to scp without being prompted for a password
#
#///////////////////////////////////////////////////////////////////////////////
#   Inputs
#       $1 - 1st input is group number
#       $2 - 2nd input is building number
#       $3 - 3rd input is lab
#       $4 - 4th input is RSA credentials file
#       $5 - 5th input is host@IPaddress
#       $6 - 6th input is web base directory
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
#   Setup of rsacreds
#       On host computer, use terminal command: ssh-keygen
#       Follow prompts to generate key. Copy from host to client using terminal command: ssh-copy-id -i <key file> <client>@<hostname>
#
##///////////////////////////////////////////////////////////////////////////////
## Change log from v1.03 to v1.04
#   November 23, 2017
#
#   ver 1.04 - moved location of environment data storage to under directory containing web pages
#
#///////////////////////////////////////////////////////////////////////////////

#get inputs
group=$1
building=$2
lab=$3
rsacreds=$4
hostaddr=$5
WEBBASEDIR=$6
LEMASmasterdir=$7

labsettingspath=$WEBBASEDIR/labsettings/$building'_'$lab.labsettings

# labIDf=$(echo $labID | sed -n -e 's/\//_/p')                                    #replaced / with _ to prevent confusing filenames with directory path

#generate most recent data filename and copy from client computer
currentdate="$(date '+%B%Y')"                                                   #get current date in <month><YYYY> format
allfilename=$currentdate'-all.env.csv'                                          #append tocurrent date the filename and extension
outagesfilename=$currentdate'-outages.env.csv'                                  #append tocurrent date the filename and extension
echo "Grabbing data from: $building/$lab"
timeout 5 scp -i $rsacreds $hostaddr:/home/pi/Desktop/EnvironmentData/$allfilename $WEBBASEDIR''data/$group/$building/$lab/$building'_'$lab'_'$allfilename #secure copy latest data from device
timeout 5 scp -i $rsacreds $hostaddr:/home/pi/Desktop/EnvironmentData/$outagesfilename $WEBBASEDIR''data/$group/$building/$lab/$building'_'$lab'_'$outagesfilename #secure copy latest data from device
timeout 5 ssh -i $rsacreds $hostaddr sh -s < $LEMASmasterdir/LEMASmasterscripts/sshgrepscript.sh $building'/'$lab > $labsettingspath 2>/dev/null #echo only the lab settings, prevents downloading of contact information
#scp -i $rsacreds /var/www/dmgenv.nist.gov/NoContact.list $username@$ipaddr:/home/pi/LEMASdist/NoContact.list #secure copy to the device NoContact settings
