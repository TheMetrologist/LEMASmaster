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
#       $4 - 4th input is outages graph file
#       $5 - 5th input is path to building statuses
#       $6 - directory to master scripts
#       $7 - base directory for website
#
#///////////////////////////////////////////////////////////////////////////////

#get inputs
pageheader=$1
pagefooter=$2
savefilepath=$3
outagesgraphpath=$4
statuspath=$5
LEMASmasterdir=$6
WEBBASEDIR=$7

#//////////////////////Load var/LEMASvar from var/LEMASvar.py\\\\\\\\\\\\\\\\\\\\\\\\
nmonths=$(cat $LEMASmasterdir/var/LEMASvar.py | grep nmonths*=)
nmonths=${nmonths#nmonths*=}

IMGWIDTH=$(cat $LEMASmasterdir/var/LEMASvar.py | grep IMGWIDTH*=)
IMDWIDTH=${IMGWIDTH#IMGWIDTH*=}

IMGHEIGHT=$(cat $LEMASmasterdir/var/LEMASvar.py | grep IMGHEIGHT*=)
IMGHEIGHT=${IMGHEIGHT#IMGHEIGHT*=}

graphtime=$(cat $LEMASmasterdir/var/LEMASvar.py | grep graphtime*=)
graphtime=${graphtime#graphtime*=}

#////////////////////////////Generate main.html\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
cat > $savefilepath <<- _EOF_
      <title>NIST LEMAS Home</title>
_EOF_
cat $pageheader >> $savefilepath
cat >> $savefilepath <<- _EOF_
      <center>
        <h2>Home - System Status</h2>
        <br>
        <h4>Connectivity Legend</h4>
        <table>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: #008000">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT> = script is running, connection successful</td>
          </tr>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: #FFFF00">&nbsp;NOT RUNNING&nbsp;</FONT> = connection to device, but script is not running</td>
          </tr>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: #FF0000">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OFFLINE&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT> = no connection to device, but script may be running</td>
          </tr>
        </table>
        <br>
        <h4>Environment Status Legend</h4>
        <table>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: #008000">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;OK&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT> = rest easy, environment is within specified ranges</td>
          </tr>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: #FF0000">&nbsp;&nbsp;TEMPERATURE&nbsp;&nbsp;</FONT> = sorry, temperature event</td>
          </tr>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: #0000FF">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<font color="#FFFFFF">HUMIDITY</font>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</font> = ruh roh, shaggy. humidity event</td>
          </tr>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: #808080">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;MULTIPLE&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</FONT> = temperature <i>and</i> humidity event</td>
          </tr>
          <tr>
            <td><FONT style="BACKGROUND-COLOR: #000000">&nbsp;&nbsp;&nbsp;<font color="#FFFFFF">CONN./SCRIPT</font>&nbsp;&nbsp;</FONT> = connectivity or script issue, see connectivity status</td>
          </tr>
        </table>
        <br>
        <table>
          <tr>
            <td>&nbsp;</td>
            <td><center><strong>Laboratory&nbsp;&nbsp;</strong></center></td>
            <td><center><strong>Connectivity</strong></center></td>
            <td><center><strong>Environment Status</strong></center></td>
          </tr>
_EOF_
IFS=','

for file in $statuspath/*
do
  building=$(echo $file | rev | cut -d '/' -f1 | rev)
  i=0
  while read group labID status
  do
    if [ $i -eq 0 ]
    then
      echo "<tr><td><strong>$building Labs</strong></td><td></td><td></td></tr><tr>" >> $savefilepath
    fi
    i=$((i+1))
    building=$(echo $labID | cut -d '/' -f1)
    lab=$(echo $labID | cut -d '/' -f2)
    echo "<td>&nbsp;</td>" >> $savefilepath
    echo "<td><a href='/Group$group/$building/$lab/index.html'>$building/$lab</a></td>" >> $savefilepath
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
      <h3>Universal settings</h3>
      <strong>Current NoContact list</strong>
      <p>The NoContact list temporarily suppresses messages to users on the list, e.g. for users on travel when an outage message may incur roaming charges.</p>
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
_EOF_
cat $pagefooter >> $savefilepath
