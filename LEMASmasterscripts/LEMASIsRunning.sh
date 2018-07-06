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
#       -$2 - username - username of remote machine
#       -$3 - ipaddr - hostname or IP address of remote machine
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
#   Setup of keygen
#       On host computer, use terminal command: ssh-keygen
#       Follow prompts to generate key. Copy from host to client using terminal command: ssh-copy-id -i <key file> <client>@<hostname>
#
##///////////////////////////////////////////////////////////////////////////////
## Change log from v1.04 to v1.05
#   November 15, 2017
#
#   ver 1.05 - added timeout to ssh
#
#///////////////////////////////////////////////////////////////////////////////

#get inputs
keygen=$1
hostaddr=$2
LEMASmasterdir=$3

timeout 5 ssh -i $keygen $hostaddr sh < $LEMASmasterdir/LEMASmasterscripts/sshprocess.sh > /tmp/LEMASstatus 2>/dev/null   #ssh to device and run script, do not print error messages
if [ $? -eq 0 ]                                                                 #if connected, return status of LEMASRun.py process
then
  echo $(cat /tmp/LEMASstatus)
else                                                                            #otherwise, if could not connect, return OFFLINE status
  echo "<FONT style=\"BACKGROUND-COLOR: red\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OFFLINE&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT>"
fi
