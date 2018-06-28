#!bin/sh
#mainhtmlupdate.sh
#   Tested with Python 3.6.1 (Anaconda 4.4.0 stack) on Ubuntu 14.04
#
#///////////////////////////////////////////////////////////////////////////////
## mainhtmlupdate.sh Notes
#   September, 2017
#   Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
#       PHONE: 301 975 8746
#       EMAIL: michael.braine@nist.gov (use this instead of phone)
#
#   Purpose
#       generate webpage for the main page
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
##//////////////////////////////////////////////////////////////////////////////
## Change log from v1.01 to v1.02
#   November 4, 2017
#
#   ver 1.02 - rewritten to generate pages  in a loop
#            - made reference from LEMASmaster directory instead of absolute
#
#///////////////////////////////////////////////////////////////////////////////
## Inputs
#       $1 - 1st input is header file
#       $2 - 2nd input is footer file
#       $3 - 3rd input is path to save .html
#       #4 - 4th input is outages graph file
#       #5 - 5th input is path to building statuses
#
#///////////////////////////////////////////////////////////////////////////////

#get inputs
pageheader=$1
pagefooter=$2
savefilepath=$3
outagesgraphpath=$4
statuspath=$5

CWD=$(pwd)

#//////////////////////Load variables from variables.py\\\\\\\\\\\\\\\\\\\\\\\\
nmonths=$(cat $CWD/variables.py | grep nmonths*=)
nmonths=${nmonths#nmonths*=}

IMGWIDTH=$(cat $CWD/variables.py | grep IMGWIDTH*=)
IMDWIDTH=${IMGWIDTH#IMGWIDTH*=}

IMGHEIGHT=$(cat $CWD/variables.py | grep IMGHEIGHT*=)
IMGHEIGHT=${IMGHEIGHT#IMGHEIGHT*=}

graphtime=$(cat $CWD/variables.py | grep graphtime*=)
graphtime=${graphtime#graphtime*=}

#////////////////////////////Generate main.html\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
cat > $savefilepath <<- _EOF_
  <!doctype html>
  <html>
    <head>
      <title>NIST LEMAS Home - System Status</title>
    </head>
    <body>
_EOF_
cat $pageheader >> $savefilepath
cat >> $savefilepath <<- _EOF_
      <center>
        <h2>Home - System Status</h2>
        <table>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: green">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT> = script is running, everything is fine and dandy</td>
          </tr>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: yellow">&nbsp;NOT RUNNING&nbsp;</FONT> = connection to device, but script is not running</td>
          </tr>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: red">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OFFLINE&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT> = no connection to device, but script may be running</td>
          </tr>
        </table>
        <br>
        <table>
          <tr>
            <td>&nbsp;</td>
            <td><center><strong>Laboratory&nbsp;&nbsp;</strong></center></td>
            <td><center><strong>Status</strong></center></td>
          </tr>
_EOF_
IFS=','
for file in $statuspath/*
do
  building=$(echo $file | rev | cut -d '/' -f1 | rev)
  echo "<tr><td><strong>$building Labs</strong></td><td></td><td></td></tr><tr>" >> $savefilepath
  while read labID status
  do
    labID=$(echo $labID | awk '$1=$1')
    status=$(echo $status | awk '$1=$1')
    echo "<td>&nbsp;</td>" >> $savefilepath
    echo "<td>$labID</td>" >> $savefilepath
    echo "<td>$status</td></tr>" >> $savefilepath
  done < $file
done
unset IFS

cat >> $savefilepath <<- _EOF_
        </table>
      </center>
    </body>
    <br>
    <body>
      <center>
        <h3>Environment Events by Group</h3>
        <h4>Past $nmonths months</h4>
        <img src="$outagesgraphpath" width="$IMGWIDTH" height="$IMGHEIGHT">
      </center>
      <h3>Universal settings</h3>
      <strong>Current NoContact list</strong>
      <p>The NoContact list temporarily suppresses messages to users on the list, e.g. for users during travel when an outage message may incur roaming charges.</p>
      <p>email <i><a href="mailto:michael.braine@nist.gov">michael.braine@nist.gov</a></i> to be added to or removed from the list.</p>
      <ul style='list-style: none;'>
_EOF_
cat /var/www/dmgenv.nist.gov/NoContact.list | while read -r line; do
  echo '<li>'$line'</li>' >> $savefilepath
done

cat >> $savefilepath <<- _EOF_
      </ul>
      <br>
      <strong>Current QuietLab list</strong>
      <p>Enabling QuietLab suppresses <i>all</i> messages from a lab, e.g. a lab where environment monitoring is desired, but outage messages are not wanted.</p>
      <p>email <i><a href="mailto:michael.braine@nist.gov">michael.braine@nist.gov</a></i> to enable or disable QuietLab.</p>
      <ul style='list-style: none;'>
_EOF_

IFS=','
while read labgroup labbuilding lab labname rsacreds hostaddr                   #loop through QuietLab.list
do
  #remove leading and trailing spaces
  labgroup=$(echo $labgroup | awk '$1=$1')
  labbuilding=$(echo $labbuilding | awk '$1=$1')
  lab=$(echo $lab | awk '$1=$1')
  labname=$(echo $labname | awk '$1=$1')
  rsacreds=$(echo $rsacreds | awk '$1=$1')
  hostaddr=$(echo $hostaddr | awk '$1=$1')

  echo '<li>'$labbuilding/$lab, $labname'</li>' >> $savefilepath
done < /var/www/dmgenv.nist.gov/QuietLabs.list
unset IFS

cat >> $savefilepath <<- _EOF_
      </ul>
      <br>
    </body>
_EOF_
cat $pagefooter >> $savefilepath
cat >> $savefilepath <<- _EOF_
  </html>
_EOF_
