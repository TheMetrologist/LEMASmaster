#!/bin/sh
#downloadhtmlupdate.sh
#   Tested with Python 3.6.1 (Anaconda 4.4.0 stack) on Ubuntu 14.04
#
#///////////////////////////////////////////////////////////////////////////////
## downloadhtmlupdate.sh Notes
#   September, 2017
#   Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
#       PHONE: 301 975 8746
#       EMAIL: michael.braine@nist.gov (use this instead of phone)
#
#   Purpose
#       generate webpages for a downloads page for the input building and lab data path
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
##//////////////////////////////////////////////////////////////////////////////
## Change log from v1.01 to v1.02
#   November 23, 2017
#
#   ver 1.02 - moved location of environment data to under directory containing web pages
#
#///////////////////////////////////////////////////////////////////////////////
## Inputs
#       $1 - 1st input is group name
#       $2 - 2nd input is building number
#       $3 - 3rd input is lab
#       $4 - 4th input is web base directory
#       $5 - 5th input is header file
#       $6 - 6th input is footer file
#
#///////////////////////////////////////////////////////////////////////////////

group=$1
building=$2
lab=$3
WEBBASEDIR=$4
pageheader=$5
pagefooter=$6

filesize=
filedate=
savefilepath=$WEBBASEDIR/data/$group/$building/$lab/downloads.html
envdatadir=/data/$group/$building/$lab/

cat > $savefilepath <<- _EOF_
  <html>
    <head>
      <title>NIST LEMAS - $building/$lab Downloads</title>
    </head>
    <body>
_EOF_
cat $pageheader >> $savefilepath
cat >> $savefilepath <<- _EOF_
  <center>
    <h2>Downloads for $building/$lab</h2>
    <br>
    <h3>Complete environment data files</h3>
    <h5>( [building]_[lab]_[month][year]-all.env.csv )</h5>
    <table><tr>
      <td><center>Filename</center></td><td>&nbsp;</td><td><center>File size</center></td>
_EOF_

#loop to insert download links for *-all.env.csv
ls -1 $WEBBASEDIR/data/$group/$building/$lab/ | grep '**-all.env.csv' | while read -r line; do
  filesize=$(($(stat --printf="%s" $WEBBASEDIR/data/$group/$building/$lab/$line)/1024))
  cat >> $savefilepath <<- _EOF_
    <tr><td><a href="/$group/$building/$lab/$line">$line</a></td><td>&nbsp;</td><td>$filesize kb</td></tr>
_EOF_
done

cat >> $savefilepath <<- _EOF_
  </tr></table>
  <br><br>
  <h3>Environment outage files</h3>
  <h5>( [building]_[lab]_[month][year]-outages.env.csv )</h5>
  <table><tr>
    <td><center>Filename</center></td><td>&nbsp;</td><td><center>File size</center></td>
_EOF_

#loop to insert download links for *-outages.env.csv
ls -1 $WEBBASEDIR/data/$group/$building/$lab/ | grep '**-outages.env.csv' | while read -r line; do
  filesize=$(stat --printf="%s" $WEBBASEDIR/data/$group/$building/$lab/$line)
  cat >> $savefilepath <<- _EOF_
    <tr><td><a href="/$group/$building/$lab/$line">$line</a></td><td>&nbsp;</td><td>$filesize b</td></tr>
_EOF_
done

#append and close table
cat >> $savefilepath <<- _EOF_
  </tr></table></center>
_EOF_

cat $pagefooter >> $savefilepath
cat >> $savefilepath <<- _EOF_
  </html>
_EOF_
