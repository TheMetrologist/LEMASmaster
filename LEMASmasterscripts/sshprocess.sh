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
## Change log from v1.00 to v1.01
#   November 20, 2020
#
#   ver 1.01 - added wildcard so LEMASRun process to detect any running LEMASRun process (LEMASRun.py, LEMASRunLoud.py, LEMASRunQuiet.py)
#
#///////////////////////////////////////////////////////////////////////////////
## Inputs
#       $1 - path to RSA keygen file
#       $2 - remote username
#       $3 - remote IP address
#       $4 - labID
#
#///////////////////////////////////////////////////////////////////////////////

if [ $(pgrep -af python | grep -c LEMASRun*) -eq "0" ]
then
  echo "<FONT style='BACKGROUND-COLOR: #FFFF00'>&nbsp;NOT RUNNING&nbsp;</FONT>"
else
  echo "<FONT style='BACKGROUND-COLOR: #008000'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>"
fi
