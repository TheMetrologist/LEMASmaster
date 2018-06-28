#!/bin/bash
#sshgrepscript.sh
#   Tested with Python 3.6.1 (Anaconda 4.4.0 stack) on Ubuntu 14.04
#
#///////////////////////////////////////////////////////////////////////////////
## sshgrepscript.sh Notes
#   October, 2017
#   Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
#       PHONE: 301 975 8746
#       EMAIL: michael.braine@nist.gov (use this instead of phone)
#
#   Purpose
#       script to run inline with SSH, extracts specific LabSettings.py data without SCP entire file
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
##//////////////////////////////////////////////////////////////////////////////
## Change log from v1.00 to v1.00
#   November 1, 2017
#
#   ver 1.00 - initial release version
#
#///////////////////////////////////////////////////////////////////////////////
## Inputs
#       $1 - 1st input is laboratory ID
#       $2 - 2nd input is date to set on RPi3
#       $3 - 3rd input is time to set on RPi3
#
#///////////////////////////////////////////////////////////////////////////////
labID=$1

echo "<strong>Alert message recipients</strong><br>"

nusers=$(cat /home/pi/LEMASdist/Contacts.py | grep -c "labusers\['$labID'\]")
if [[ $nusers > 1 ]]
then
  cat /home/pi/LEMASdist/Contacts.py | grep "labusers\['$labID'\]" | tr -d "[]'" | sed -n -e 's/^.*= //g' -e 's/,/<br>/p'
else
  cat /home/pi/LEMASdist/Contacts.py | grep "labusers\['$labID'\]" | tr -d "[]'" | cut -d "=" -f 2
fi
echo "<br><br><strong>Current 'NoContact' list</strong><br>"
echo "<p>email <i><a href='mailto:michael.braine@nist.gov'>michael.braine@nist.gov</a></i> to be added to or removed from the list.</p>"
cat /home/pi/LEMASdist/NoContact.list
echo "<br><br><strong>Temperature range setting</strong><br>[min, max]<br>"
cat /home/pi/LEMASdist/Tcontrols.py | grep "Tcontrols\['$labID'\]" | sed -n -e 's/^.*= //p'
echo "&#176;C<br><br><strong>Humidity range setting</strong><br>[min, max]<br>"
cat /home/pi/LEMASdist/RHcontrols.py | grep "RHcontrols\['$labID'\]" | sed -n -e 's/^.*= //p'
echo "&#37;RH"
echo "<br><br><strong>Username, hostname and IP address</strong><br>"
echo "<pre>"
echo $USER@$(cat /etc/hostname): $(hostname --all-ip-addresses)
echo "</pre>"
echo "<br><strong>Device storage and miscellaneous statistics</strong><br>"
echo "<pre>"
uptime -p
df -h
echo "</pre>"
