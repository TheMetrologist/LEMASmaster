#!/bin/sh
#!/bin/sh
#sshprocess.sh
#   Tested on Ubuntu 14.04 (client) with Raspbian (host)
#
#///////////////////////////////////////////////////////////////////////////////
## sshprocess.sh Notes
#   November, 2017
#   Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
#       PHONE: 301 975 8746
#       EMAIL: michael.braine@nist.gov (use this instead of phone)
#
#   Purpose
#       script to test if LEMASRun.py python script is currently an active process
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
##//////////////////////////////////////////////////////////////////////////////
## Change log from v1.00 to v1.00
#   November 2, 2017
#
#   ver 1.00 - initial release
#
#///////////////////////////////////////////////////////////////////////////////
## Inputs
#       $1 - path to RSA keygen file
#       $2 - remote username
#       $3 - remote IP address
#       $4 - labID
#
#///////////////////////////////////////////////////////////////////////////////

if [ $(pgrep -af python | grep -c LEMASRun.py) -eq "0" ]
then
  echo "<FONT style='BACKGROUND-COLOR: yellow'>&nbsp;NOT RUNNING&nbsp;</FONT>"
else
  echo "<FONT style='BACKGROUND-COLOR: green'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>"
fi
