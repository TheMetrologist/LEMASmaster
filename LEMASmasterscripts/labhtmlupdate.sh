#!/bin/bash
#labhtmlupdate.sh
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
#       $2 - 2nd input is building number
#       $3 - 3rd input is lab
#       $4 - 4th input is lab name
#       $5 - 5th input is web base directory
#       $6 - 6th input is header file
#       $7 - 7th input is footer file
#
#///////////////////////////////////////////////////////////////////////////////

#get inputs
group=$1
building=$2
lab=$3
labname=$4
WEBBASEDIR=$5
pageheader=$6
pagefooter=$7
LEMASmasterdir=$8

savefilepath=$WEBBASEDIR/data/Group$group/$building/$lab/index.html
statspath=$WEBBASEDIR''statistics/$building'_'$lab.stats
labsettingspath=$WEBBASEDIR/labsettings/$building'_'$lab.labsettings
Tgraphpath=$WEBBASEDIR/data/Group$group/$building/$lab/$building'_'$lab''-T.html
RHgraphpath=$WEBBASEDIR/data/Group$group/$building/$lab/$building'_'$lab''-RH.html
outagebarpath=$WEBBASEDIR/data/Group$group/$building/$lab/$building'_'$lab''-outages.html
Thistpath=$WEBBASEDIR/data/Group$group/$building/$lab/$building'_'$lab''-Thist.html
RHhistpath=$WEBBASEDIR/data/Group$group/$building/$lab/$building'_'$lab''-RHhist.html

#///////////////////////////Load var/LEMASvar from text\\\\\\\\\\\\\\\\\\\\\\\\\\\\
nmonths=$(cat $LEMASmasterdir/var/LEMASvar.py | grep nmonths*=)
nmonths=${nmonths#nmonths*=}

IMGWIDTH=$(cat $LEMASmasterdir/var/LEMASvar.py | grep statIMGWIDTH*=)
IMDWIDTH=${statIMGWIDTH#statIMGWIDTH*=}

IMGHEIGHT=$(cat $LEMASmasterdir/var/LEMASvar.py | grep statIMGHEIGHT*=)
IMGHEIGHT=${statIMGHEIGHT#statIMGHEIGHT*=}

graphtime=$(cat $LEMASmasterdir/var/LEMASvar.py | grep graphtime*=)
graphtime=${graphtime#graphtime*=}

inter_time=$(cat $LEMASmasterdir/var/LEMASvar.py | grep inter_time*=)
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

avgT=$(cat $statspath | grep avgT)
avgT=${avgT#avgT}

avgRH=$(cat $statspath | grep avgRH)
avgRH=${avgRH#avgRH}

#////////////////////////////Generate lab#.html\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
cat > $savefilepath <<- _EOF_
      <title>NIST LEMAS Lab $building/$lab</title>
_EOF_
cat $pageheader >> $savefilepath
cat >> $savefilepath <<- _EOF_
      <center>
        <h2>$labname</h2>
        <h2>$building/$lab</h2>
      </center>
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
        <h3>Statistics for $building/$lab</h3>
        <h4>Environment Events by Month</h4>
        <h4>Past $nmonths months</h4>
_EOF_
cat $outagebarpath >> $savefilepath
cat >> $savefilepath <<- _EOF_
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
        </table>
        <br><br>
        <h4>Temperature distribution</h4>
        <h4>Past $nmonths months</h4>
_EOF_
cat $Thistpath >> $savefilepath
cat >> $savefilepath <<- _EOF_
        <table>
          <tr>
            <td>Highest temperature: </td>
            <td>&nbsp;</td>
            <td>$maxT</td>
          </tr>
          <tr>
            <td>Average temperature: </td>
            <td>&nbsp;</td>
            <td>$avgT</td>
          </tr>
        </table>
        <br><br>
        <h4>Humidity distribution</h4>
        <h4>Past $nmonths months</h4>
_EOF_
cat $RHhistpath >> $savefilepath
cat >> $savefilepath <<- _EOF_
        <table>
          <tr>
            <td>Highest humidity: </td>
            <td>&nbsp;</td>
            <td>$maxRH</td>
          </tr>
          <tr>
            <td>Average Humidity: </td>
            <td>&nbsp;</td>
            <td>$avgRH</td>
          </tr>
        </table>
      </center>
      <h3>Settings for $building/$lab</h3>
      <p>
_EOF_
cat $labsettingspath >> $savefilepath
cat >> $savefilepath <<- _EOF_
      </p>
_EOF_
cat $pagefooter >> $savefilepath
