#!/bin/sh
#grouphtmlupdate.sh
#   Tested with Python 3.6.1 (Anaconda 4.4.0 stack) on Ubuntu 14.04
#
#///////////////////////////////////////////////////////////////////////////////
## Notes
#   September, 2017
#   Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
#       PHONE: 301 975 8746
#       EMAIL: michael.braine@nist.gov (use this instead of phone)
#
#   Purpose
#       generate webpages for the input group
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
##//////////////////////////////////////////////////////////////////////////////
## Change log from v1.03 to v1.04
#   June 3, 2018
#
#   ver 1.04 - now importing environment graphs in the form of .html
#            - added variable for specifying the past n hours (weeks) that data is interactable
#
#///////////////////////////////////////////////////////////////////////////////
## Inputs
#       $1 - 1st input is group number
#       $2 - 2nd input is group name
#       $3 - 3rd input is web base directory
#       $4 - 4th input is header file
#       $5 - 5th input is footer file
#
#///////////////////////////////////////////////////////////////////////////////

groupnumber=$1
groupname=$2
WEBBASEDIR=$3
pageheader=$4
pagefooter=$5

CWD=$(pwd)
savefilepath=$WEBBASEDIR/data/'Group'$groupnumber/index.html
statspath=$WEBBASEDIR/statistics/'Group'$groupnumber.stats
Tgraphpath=$WEBBASEDIR/data/Group$groupnumber/'Group'$groupnumber''-T.html
RHgraphpath=$WEBBASEDIR/data/Group$groupnumber/'Group'$groupnumber''-RH.html
outagesgraphpath=/Group$groupnumber/'Group'$groupnumber''-outages.png

#///////////////////////////Load variables from text\\\\\\\\\\\\\\\\\\\\\\\\\\\\
nmonths=$(cat $CWD/variables.py | grep nmonths*=)
nmonths=${nmonths#nmonths*=}

IMGWIDTH=$(cat $CWD/variables.py | grep statIMGWIDTH*=)
IMDWIDTH=${statIMGWIDTH#statIMGWIDTH*=}

IMGHEIGHT=$(cat $CWD/variables.py | grep statIMGHEIGHT*=)
IMGHEIGHT=${statIMGHEIGHT#statIMGHEIGHT*=}

graphtime=$(cat $CWD/variables.py | grep graphtime*=)
graphtime=${graphtime#graphtime*=}

inter_time=$(cat $CWD/variables.py | grep inter_time*=)
inter_time=${inter_time#inter_time*=}
inter_time=$((inter_time/24/7))

#///////////////////////////Load statistics from text\\\\\\\\\\\\\\\\\\\\\\\\\\\
nToutages=$(cat $statspath | grep nToutages)
nToutages=${nToutages#nToutages}

nRHoutages=$(cat $statspath | grep nRHoutages)
nRHoutages=${nRHoutages#nRHoutages}

nComboOutages=$(cat $statspath | grep nComboOutages)
nComboOutages=${nComboOutages#nComboOutages}

nUnique=$(cat $statspath | grep nUnique)
nUnique=${nUnique#nUnique}

maxT=$(cat $statspath | grep maxT)
maxT=${maxT#maxT}

maxRH=$(cat $statspath | grep maxRH)
maxRH=${maxRH#maxRH}

#////////////////////////////Generate Group#.html\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
cat > $savefilepath <<- _EOF_
  <html>
    <head>
      <title>NIST LEMAS - $groupnumber</title>
    </head>
    <body>
_EOF_
cat $pageheader >> $savefilepath
cat >> $savefilepath <<- _EOF_
      <center><h2>$groupname</h2></center>
      <br>
      <center>
        <h3>Most Recent Environment</h3>
        <h4>Temperature from the past $graphtime hours</h4>
        <h4>Interactive up to the past $inter_time weeks</h4>
_EOF_
cat $Tgraphpath >> $savefilepath
cat >> $savefilepath <<- _EOF_
        <br><br>
        <h4>Humidity from the past $graphtime hours</h4>
        <h4>Interactive up to the past $inter_time weeks</h4>
_EOF_
cat $RHgraphpath >> $savefilepath
cat >> $savefilepath <<- _EOF_
      </center>
      <br><br>
      <center>
        <h3>Statistics for $groupnumber</h3>
        <h4>Environment Events by Building</h4>
        <h4>Past $nmonths months</h4>
        <img src="$outagesgraphpath" width="$IMGWIDTH" height="$IMGHEIGHT">
      </center>
      <br>
      <center>
        <table>
          <tr>
            <td>Number of temperature events: </td>
            <td>&nbsp;</td>
            <td>$nToutages</td>
          </tr>
          <tr>
            <td>Number of humidity events: </td>
            <td>&nbsp;</td>
            <td>$nRHoutages</td>
          </tr>
          <tr>
            <td>Number of combination (T and RH) events: </td>
            <td>&nbsp;</td>
            <td>$nComboOutages</td>
          </tr>
          <tr>
            <td>Number of unique events: </td>
            <td>&nbsp;</td>
            <td>$nUnique</td>
          </tr>
          <tr>
            <td>Highest temperature: </td>
            <td>&nbsp;</td>
            <td>$maxT</td>
          </tr>
          <tr>
            <td>Highest humidity: </td>
            <td>&nbsp;</td>
            <td>$maxRH</td>
          </tr>
        </table>
      </center>
    </body>
_EOF_
cat $pagefooter >> $savefilepath
cat >> $savefilepath <<- _EOF_
  </html>
_EOF_
