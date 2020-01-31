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

LEMASmasterdir="/home/$USER/BraineCode/LEMAS/LEMASmaster2"
# LEMASmasterdir="/media/$USER/A/BraineCode/LEMAS/LEMASmaster2/"
WEBBASEDIR="/var/www/dev_dmgenv.nist.gov/"

#specifiy files and directories
TIMETOSLEEP=$(cat $LEMASmasterdir/var/LEMASvar.py | grep TIMETOSLEEP*=)
TIMETOSLEEP=${TIMETOSLEEP#TIMETOSLEEP*=}
groupslist=$LEMASmasterdir/GroupsMonitored.list
buildingslist=$LEMASmasterdir/BuildingsMonitored.list
labslist=$LEMASmasterdir/LabsMonitored.list
HEADERFILE=$WEBBASEDIR/pageheader.html
FOOTERFILE=$WEBBASEDIR/pagefooter.html
HEADERTEMPLATE=$LEMASmasterdir/templates/navbar.html
FOOTERTEMPLATE=$LEMASmasterdir/templates/pagefooter.html
ABOUTTEMPLATE=$LEMASmasterdir/templates/about.html
CALCTEMPLATE=$LEMASmasterdir/templates/Calculators.html
starttime=$(date)

#/////////////////////Create dmgenv.nist.gov directories\\\\\\\\\\\\\\\\\\\\\\\\\\\
#base directories
mkdir $WEBBASEDIR 2>/dev/null
mkdir $WEBBASEDIR/data
mkdir $WEBBASEDIR/statistics 2>/dev/null
mkdir $WEBBASEDIR/labsettings 2>/dev/null

#///////////////////////////////Page Header\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
cat $HEADERTEMPLATE > $HEADERFILE
cat $FOOTERTEMPLATE > $FOOTERFILE

#////////////////////////////////Page Navigation Bar Construction\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#set up navigation bar that will be on every page

IFS=','
echo "<nav>
  <ul id='menu'>
    <li><a class='home' href='/'>System home</a></li>
    <li><a class='prett'>Group summaries</a>
          <ul class='menus'>" >> $HEADERFILE

# group summaries menu
while read group groupname                                                    #loop through GroupsMonitored.list
do
  #remove leading and trailing spaces
  group=$(echo $group | awk '$1=$1')
  groupname=$(echo $groupname | awk '$1=$1')

  navbar="<li><a href='/Group$group/index.html'>$groupname, $group_</a></li>"
  echo $navbar >> $HEADERFILE                                                 #append current navbar to header file
done < $groupslist
echo "      </ul>
    </li>
    <li><a class='prett'>Building summaries</a>
      <ul class='menus'>" >> $HEADERFILE

# building summaries menu
while read group groupname                                                    #loop through GroupsMonitored.list
do
  #remove leading and trailing spaces
  group=$(echo $group | awk '$1=$1')
  groupname=$(echo $groupname | awk '$1=$1')
  navbar="<li class='has-submenu'><a class='prett'>$groupname, $group_</a>
    <ul class='submenu'>"
  echo $navbar >> $HEADERFILE
  while read buildinggroup building buildingname                              #loop through BuildingsMonitored.list
  do
    #remove leading and trailing spaces
    buildinggroup=$(echo $buildinggroup | awk '$1=$1')
    building=$(echo $building | awk '$1=$1')
    buildingname=$(echo $buildingname | awk '$1=$1')

    if [ "$buildinggroup" = "$group" ]                                        #if current building belongs to current group
    then
      navbar="<li><a href='/Group$group/$building/index.html'>$buildingname, Building $building</a></li>"
      echo $navbar >> $HEADERFILE                                             #append current navbar string to header file
    fi
  done < $buildingslist
  echo "</ul>
        </li>" >> $HEADERFILE
done < $groupslist

echo "  </ul>
        </li>
      <li><a class='prett'>Lab environments</a>
        <ul class='menus'>" >> $HEADERFILE

# lab environments menu
while read group groupname                                                    #loop through GroupsMonitored.list
do
  #remove leading and trailing spaces
  group=$(echo $group | awk '$1=$1')
  groupname=$(echo $groupname | awk '$1=$1')
  navbar="<li class='has-submenu'><a class='prett'>$groupname, $group_</a>
            <ul class='submenu'>"
  echo $navbar >> $HEADERFILE
  while read buildinggroup building buildingname                              #loop through BuildingsMonitored.list
  do
    #remove leading and trailing spaces
    buildinggroup=$(echo $buildinggroup | awk '$1=$1')
    building=$(echo $building | awk '$1=$1')
    buildingname=$(echo $buildingname | awk '$1=$1')

    if [ "$buildinggroup" = "$group" ]                                       #if current building belongs to current group
    then
      echo "<li style='color: white; text-align: center;'><b>$buildingname, Building $building</b></li>" >> $HEADERFILE
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
          if [ "$labgroup" = "$group" ]
          then
            navbar="<li><a href='/Group$group/$building/$lab/index.html'>$lab, $labname </a></li>"
            echo $navbar >> $HEADERFILE                                       #append navbar to header file
          fi
        fi
      done < $labslist
    fi
  done < $buildingslist
  echo "</ul>
    </li>" >> $HEADERFILE
done < $groupslist

echo "      </ul>
      </li>
      <li><a class='prett'>Downloads</a>
      <ul class='menus'>" >> $HEADERFILE

# downloads menu
while read group groupname                                                    #loop through GroupsMonitored.list
do
  #remove leading and trailing spaces
  group=$(echo $group | awk '$1=$1')
  groupname=$(echo $groupname | awk '$1=$1')
  navbar="<li class='has-submenu'><a class='prett'>$groupname, $group_</a>
            <ul class='submenu'>"
  echo $navbar >> $HEADERFILE
  while read buildinggroup building buildingname                              #loop through BuildingsMonitored.list
  do
    #remove leading and trailing spaces
    buildinggroup=$(echo $buildinggroup | awk '$1=$1')
    building=$(echo $building | awk '$1=$1')
    buildingname=$(echo $buildingname | awk '$1=$1')

    if [ "$buildinggroup" = "$group" ]                                       #if current building belongs to current group
    then
      echo "<li style='color: white; text-align: center;'><b>$buildingname, Building $building</b></li>" >> $HEADERFILE
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
          if [ "$labgroup" = "$group" ]
          then
            navbar="<li><a href='/Group$group/$building/$lab/downloads.html'>$lab, $labname </a></li>"
            echo $navbar >> $HEADERFILE                                       #append navbar to header file
          fi
        fi
      done < $labslist
    fi
  done < $buildingslist
  echo "</ul>
    </li>" >> $HEADERFILE
done < $groupslist
unset IFS

echo "  </ul>
  </li>
  <li><a href='http://dmgenv.nist.gov/ArchivedData/'>Archived data</a></li>
  <li><a href='http://129.6.97.77:8888/notebooks/LEMASCalculators/LEMASCalculators.ipynb'>Calculators</a></li>
  <li style='float: right;'><a href=/about.html>About the system</a></li>
  <li style='float: right;'><a class='prett'>Other</a>
    <ul class='menus'>
      <li><a href='http://dmgenv.nist.gov/JupyterNotebooks/ImageAnalysisVisionInterferometers.pdf'>Fringefinder paper</a></li>
      <li><a href='129.6.97.77:8888/notebooks/fringefinder.ipynb'>Fringefinder paper supplement</a></li>
      <li><a href='http://dmgenv.nist.gov/JupyterNotebooks/results.html'>Fringefinder supplement results</a></li>
    </ul>
  </li>
  </ul>
  </nav>

  <body>
  <div class='header'>
  <center>
    <img src='/nisttag.jpg' width='305' height='100'>
    <h2>Laboratory Environment Monitoring and Alert System</h2>
    <h3>(LEMAS)</h3>
    </center>
    </div>" >> $HEADERFILE

cat $HEADERFILE > $WEBBASEDIR/data/about.html
cat $ABOUTTEMPLATE >> $WEBBASEDIR/data/about.html

cat $HEADERFILE > $WEBBASEDIR/data/calculators.html
cat $CALCTEMPLATE >> $WEBBASEDIR/data/calculators.html
cat $FOOTERTEMPLATE >> $WEBBASEDIR/data/calculators.html
chmod -R 755 $WEBBASEDIR/data/*

#///////////////////////////////Main Start\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#loop for all eternity
while [ true ]
do
  clear
  echo " "
  echo "LEMAS Website builder, v1.24"
  echo "Michael Braine, January 2020 (September 2017)"
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
    mkdir $WEBBASEDIR/data/Group$group 2>/dev/null
    mkdir $WEBBASEDIR/data/Group$group/$building 2>/dev/null
    mkdir $WEBBASEDIR/data/Group$group/$building/$lab 2>/dev/null

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
