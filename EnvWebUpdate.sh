#!/bin/bash
#EnvWebUpdate.sh
#   Tested with Python 3.6.2 (Anaconda 4.4.0 stack) on Ubuntu 14.04
#
#///////////////////////////////////////////////////////////////////////////////
## EnvWebUpdate.sh Notes
#   September, 2017
#   Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
#       PHONE: 301 975 8746
#       EMAIL: michael.braine@nist.gov (use this instead of phone)
#
#   Purpose
#       generate all webpages for laboratories monitored by LEMAS
#
#///////////////////////////////////////////////////////////////////////////////
## References
#
##//////////////////////////////////////////////////////////////////////////////
## Change log from v1.06 to v1.07
#   July 3, 2018
#
#   ver 1.07 - cleaned up absolute paths
#
#///////////////////////////////////////////////////////////////////////////////

LEMASmasterdir=/home/$USER/BraineCode/LEMAS/LEMASmaster
WEBBASEDIR="/var/www/dmgenv.nist.gov/"

#specifiy files and directories
TIMETOSLEEP=$(cat $LEMASmasterdir/variables.py | grep TIMETOSLEEP*=)
TIMETOSLEEP=${TIMETOSLEEP#TIMETOSLEEP*=}
groupslist=$LEMASmasterdir/GroupsMonitored.list
buildingslist=$LEMASmasterdir/BuildingsMonitored.list
labslist=$LEMASmasterdir/LabsMonitored.list
HEADERFILE=$WEBBASEDIR/pageheader.html
FOOTERFILE=$WEBBASEDIR/pagefooter.html
starttime=$(date)

#/////////////////////Create dmgenv.nist.gov directories\\\\\\\\\\\\\\\\\\\\\\\\\\\
#base directories
mkdir $WEBBASEDIR 2>/dev/null
mkdir $WEBBASEDIR/data
mkdir $WEBBASEDIR/statistics 2>/dev/null
mkdir $WEBBASEDIR/labsettings 2>/dev/null

#///////////////////////////////Page Header\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
pageheader="<center>
  <img src='/nisttag.jpg' width='305' height='100'>
  <h1>Laboratory Environment Monitoring and Alert System, v1.22</h1>
</center>"

echo $pageheader > $HEADERFILE

#///////////////////////////////Main Start\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#loop for all eternity
while [ true ]
do
  clear
  echo " "
  echo "LEMAS Website builder, v1.22"
  echo "Michael Braine, March 2019 (September 2017)"
  echo "michael.braine@nist.gov"
  echo " "
  echo "Builder started $starttime"
  #///////////////////////////////BASH scripts\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
  #download latest environment and outage data
  #input is 1(path to RSA keygen) 2(client username) 3(client IP address) 4(path to save downloaded data to) 5(laboratory ID)
  echo " "
  echo "$(date): Downloading data from devices ..."

  nloops=1
  IFS=','
  while read group building lab labname rsacreds hostaddr
  do
    #remove leading and trailing spaces
    group=$(echo $group | awk '$1=$1')
    building=$(echo $building | awk '$1=$1')
    lab=$(echo $lab | awk '$1=$1')
    labname=$(echo $labname | awk '$1=$1')
    rsacreds=$(echo $rsacreds | awk '$1=$1')
    hostaddr=$(echo $hostaddr | awk '$1=$1')

    #build directories for website and environment data
    mkdir $WEBBASEDIR/data/$group 2>/dev/null
    mkdir $WEBBASEDIR/data/$group/$building 2>/dev/null
    mkdir $WEBBASEDIR/data/$group/$building/$lab 2>/dev/null

    #download data from device
    sh $LEMASmasterdir/LEMASmasterscripts/LEMASDataDownload.sh $group $building $lab $rsacreds $hostaddr $WEBBASEDIR $LEMASmasterdir
    status=$(bash $LEMASmasterdir/LEMASmasterscripts/LEMASIsRunning.sh $rsacreds $hostaddr $LEMASmasterdir $group $building $lab $WEBBASEDIR) #get status of device
    if [ $nloops -eq '1' ]
    then                                                                        #if first loop
      nloops=$(( $nloops + 1 ))                                                 #increase loop number to prevent from running this section again
      for file in $WEBBASEDIR/status/*                                          #loop through all files in status directory
      do
        > $file                                                                 #reinitialize file contents
      done
    fi
    if [ -f $WEBBASEDIR/status/$building ]
    then                                                                        #if file exists
      echo $group','$building'/'$lab','$status >> $WEBBASEDIR/status/$building  #append lab status to building status file
    else                                                                        #if file does not exist
      touch $WEBBASEDIR'/status/'$building                                      #create new building status file
      echo $building'/'$lab','$status > $WEBBASEDIR/status/$building            #write lab status to building status file
    fi
  done < $labslist #end while loop, loop through monitored lab list
  unset IFS

  chown -R $USER:$USER $WEBBASEDIR
  chmod -R 755 $WEBBASEDIR
  #//////////////////////////////Python scripts\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
  #process environment data that will be pushed to webpages
  echo " "
  echo "$(date): Processing .env.csv data and generating graphs ..."
  /home/$USER/anaconda3/bin/python3 $LEMASmasterdir/LEMASmasterscripts/LEMASDataAnalysis.py #use python to analyze data, generate graphs and statistics for webpages

  #////////////////////////////////Page Footer\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
  #set up footer that will be on every page
  #footer is essentially directory tree links for all labs, buildings, and groups, and a link to return to home page
  #regenerate on every loop because it contains the time of the last time the page was updated
  echo " "
  echo "$(date): Building footer ..."

  pagefooter="<body>
    <h3>Available website navigational directory</h3>
    <p><strong><a href='/index.html'>Home - System Status</a></strong></p>
    <ul style='list-style: none;'>"

  echo $pagefooter > $FOOTERFILE                                                #write current footer to footer file

  IFS=','
  while read group groupname                                                    #loop through GroupsMonitored.list
  do
    #remove leading and trailing spaces
    group=$(echo $group | awk '$1=$1')
    groupname=$(echo $groupname | awk '$1=$1')

    pagefooter="<li>$groupname, $group <a href='/Group$group/index.html'>summary</a></li>
      <ul style='list-style: none;'>"
    echo $pagefooter >> $FOOTERFILE                                             #append current footer to footer file

    while read buildinggroup building buildingname                              #loop through BuildingsMonitored.list
    do
      #remove leading and trailing spaces
      buildinggroup=$(echo $buildinggroup | awk '$1=$1')
      building=$(echo $building | awk '$1=$1')
      buildingname=$(echo $buildingname | awk '$1=$1')

      if [ "$buildinggroup" = "$group" ]                                        #if current building belongs to current group
      then
        pagefooter="<li>$buildingname, Building $building <a href='/Group$group/$building/index.html'>summary</a></li>
          <ul style='list-style: none;'>
            <table>"
        echo $pagefooter >> $FOOTERFILE                                         #append current footer to footer file

        nloops=1 #set number of loops to 1
        while read labgroup labbuilding lab labname rsacreds hostaddr           #loop through LabsMonitored.list
        do
          #remove leading and trailing spaces
          labgroup=$(echo $labgroup | awk '$1=$1')
          labbuilding=$(echo $labbuilding | awk '$1=$1')
          lab=$(echo $lab | awk '$1=$1')
          labname=$(echo $labname | awk '$1=$1')
          rsacreds=$(echo $rsacreds | awk '$1=$1')
          hostaddr=$(echo $hostaddr | awk '$1=$1')

          if [ "$labbuilding" = "$building" ]                                   #if current lab belongs to current building
          then
            if [ $((nloops % 2)) -eq '0' ]
            then                                                                #if even loop number, no background color for lab link text
              pagefooter="<tr><td>&nbsp;<a href='/Group$group/$building/$lab/index.html'>$lab, $labname</a>&nbsp;</td> <td>&nbsp;<a href='/Group$group/$building/$lab/downloads.html'> Downloads</a>&nbsp;</td></tr>"
            else                                                                #if odd loop number, gray background color for lab link text
              pagefooter="<tr style='BACKGROUND-COLOR: LightGray'><td>&nbsp;<a href='/Group$group/$building/$lab/index.html'>$lab, $labname</a>&nbsp;</td> <td>&nbsp;<a href='/Group$group/$building/$lab/downloads.html'> Downloads</a>&nbsp;</td></tr>"
            fi
            nloops=$((nloops + 1))
            echo $pagefooter >> $FOOTERFILE                                     #append current footer to footer file
          fi
        done < $labslist
        pagefooter="</table></ul>"
        echo $pagefooter >> $FOOTERFILE                                         #append current footer to footer file
      fi
    done < $buildingslist
    pagefooter="</ul></ul>"                                                     #append current footer to footer file
  done < $groupslist
  unset IFS

  pagefooter="</ul></ul></ul><br>
  <ul style='list-style: none;'>
    <li>The data displayed does not automatically update in your browser. You must manually refresh the page to see new data.</li>
    <li>This website rebuilds itself every $TIMETOSLEEP seconds.</li>
    <li><strong>Page last updated:</strong> $(date)</li>
    <br>
    <li>This gift of data is brought to you and maintained by Michael Braine (<i><a href='mailto:michael.braine@nist.gov'>michael.braine@nist.gov</a></i>), Dimensional Metrology Group 685.10, PML. October, 2017</li>
    <li>The public distribution of LEMAS source, including sensor manuals and installation instructions, is available on github: <a href='https://github.com/usnistgov/LEMASdistPub'>https://github.com/usnistgov/LEMASdistPub</a>.</li>
    <li>The source for the website construction and many-environment analysis system is available on github: <a href='https://github.com/usnistgov/LEMASmaster'>https://github.com/usnistgov/LEMASmaster</a>.</li>
    <li>If you use <i>dmgenv.nist.gov</i>, and subsequently the LEMAS devices, then you agree to the terms:</li>
    <ol>
      <li>Do not reproduce the LEMAS system or site in any capacity without receiving consent from 685.10. Downloading and publishing data is okay as long as it is annotated as originating from this system. Give credit where appropriate</li>
      <li>You allow other users to use or play with the data</li>
      <li>The data must not be used for calibrations. It is provided purely for monitoring, informational, and decision-making purposes</li>
      <li>E-mail any suggestions, oddities, and abnormal behavior to the site maintainer
      <li>This system is known to the State of Maryland (rather, the office of 220/B114 <i>in</i> the state of MD) to cause personal increased awareness of indoor laboratory environmental conditions. Side effects include, but are not limited to: anxiety, depression, feelings of dread or anger, and increased heart rate. If you experience any of these symptoms lasting more than 1 hour, stop using the system and consult your group leader immediately.</li>
    </li>
    </ol>
  </ul>
</body>"

  echo $pagefooter >> $FOOTERFILE                                               #append current footer to footer file

  #//////////////////////Main page, all laboratory summary\\\\\\\\\\\\\\\\\\\\\\\\
  #update .html for main page
  #script input is 1(header file 2(footer file) 3(save file) 4(outages graph file) 5(building statuses directory)
  sh $LEMASmasterdir/LEMASmasterscripts/mainhtmlupdate.sh $HEADERFILE $FOOTERFILE $WEBBASEDIR/data/index.html /main-outages.png $WEBBASEDIR/status $LEMASmasterdir $WEBBASEDIR

  #///////////////////////////////Group webpages\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
  #update .html for group pages
  echo " "
  echo "$(date): Building webpages, Groups ..."
  IFS=','
  while read group groupname
  do
    #remove leading and trailing zeros
    group=$(echo $group | awk '$1=$1')
    groupname=$(echo $groupname | awk '$1=$1')

    #script input is 1(group number) 2(group name) 3(web base directory) 4(header file) 5(footer file)
    sh $LEMASmasterdir/LEMASmasterscripts/grouphtmlupdate.sh $group $groupname $WEBBASEDIR $HEADERFILE $FOOTERFILE $LEMASmasterdir
  done < $groupslist
  unset IFS

  #/////////////////////////////Building webpages\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
  #update .html for building webpages
  echo "$(date): Building webpages, Building ..."
  IFS=','
  while read group building buildingname
  do
    #remove leading and trailing spaces
    group=$(echo $group | awk '$1=$1')
    building=$(echo $building | awk '$1=$1')
    buildingname=$(echo $buildingname | awk '$1=$1')

    #script input is 1(group number) 2(building number) 3(building name) 4(web base directory) 5(header file) 6(footer file)
    sh $LEMASmasterdir/LEMASmasterscripts/bldghtmlupdate.sh $group $building $buildingname $WEBBASEDIR $HEADERFILE $FOOTERFILE $LEMASmasterdir
  done < $buildingslist
  unset IFS

  #//////////////////////////Laboratory webpages\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
  echo "$(date): Building webpages, Labs ..."
  nloops=1
  IFS=','
  while read group building lab labname rsacreds hostaddr
  do
    #remove leading and trailing spaces
    group=$(echo $group | awk '$1=$1')
    building=$(echo $building | awk '$1=$1')
    lab=$(echo $lab | awk '$1=$1')
    labname=$(echo $labname | awk '$1=$1')
    rsacreds=$(echo $rsacreds | awk '$1=$1')
    hostaddr=$(echo $hostaddr | awk '$1=$1')

    #script input is 1(group number) 2(building number) 3(lab) 4(lab name) 5(web base directory) 6(header file) 7(footer file)
    sh $LEMASmasterdir/LEMASmasterscripts/labhtmlupdate.sh $group $building $lab $labname $WEBBASEDIR $HEADERFILE $FOOTERFILE $LEMASmasterdir
    #script input is 1(group number) 2(building number) 3(lab) 4(web base directory) 5(environment data base directory) 6(header file) 7(footer file)
    sh $LEMASmasterdir/LEMASmasterscripts/downloadhtmlupdate.sh $group $building $lab $WEBBASEDIR $HEADERFILE $FOOTERFILE
  done < $labslist
  unset IFS

  echo " "
  echo "$(date): Website build complete"
  sleep $TIMETOSLEEP #sleep for TIMETOSLEEP seconds
done #end while loop, execute for eternity
