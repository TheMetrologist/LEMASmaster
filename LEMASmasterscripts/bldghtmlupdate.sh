#!/bin/sh
#bldghtmlupdate.sh
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
#       generate webpages for the input building
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
#       $3 - 3rd input is building name
#       $4 - 4th input is web base directory
#       $5 - 5th input is header file
#       $6 - 6th input is footer file
#
#///////////////////////////////////////////////////////////////////////////////

group=$1
building=$2
buildingname=$3
WEBBASEDIR=$4
pageheader=$5
pagefooter=$6
LEMASmasterdir=$7

savefilepath=$WEBBASEDIR/data/Group$group/$building/index.html
statspath=$WEBBASEDIR/statistics/$building.stats
Tgraphpath=$WEBBASEDIR/data/Group$group/$building/$building-T.html
RHgraphpath=$WEBBASEDIR/data/Group$group/$building/$building-RH.html
outagebarpath=$WEBBASEDIR/data/Group$group/$building/$building-outages.html

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

#////////////////////////////Generate <Building#>.html\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
cat > $savefilepath <<- _EOF_
      <title>NIST LEMAS Building $building</title>
_EOF_
cat $pageheader >> $savefilepath
cat >> $savefilepath <<- _EOF_
      <center><h2>$buildingname, Building $building</h2></center>
      <br>
      <center>
        <h3>Most Recent Environment</h3>
        <h6>Graphs may take a few seconds to load if there are many labs in this building</h6>
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
      <br>
      <center>
        <h3>Statistics for $building</h3>
        <h4>Environment Events by Laboratory</h4>
        <h4>Past $nmonths months</h4>
_EOF_
cat $outagebarpath >> $savefilepath
cat >> $savefilepath <<- _EOF_
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
