"""
LEMASDataAnalysis.py
  Tested with Python 3.6.1 (Anaconda 4.4.0 stack) on Linux Mint 18.2 Sonya Cinnamon, Python 3.4.2, on Raspbian Linux

///////////////////////////////////////////////////////////////////////////////
LEMASDataAnalysis.py Notes
  September, 2017
  Authored by: Michael Braine, Physical Science Technician, NIST, Gaithersburg, MD
      PHONE: 301 975 8746
      EMAIL: michael.braine@nist.gov (use this instead of phone)

Purpose
      Determine number of outages in time period
      Generate graphs from the past graphtime

///////////////////////////////////////////////////////////////////////////////
References

//////////////////////////////////////////////////////////////////////////////
Change log from v1.08 to v1.089
  July 3, 2018

  ver 1.09  -made more PEP8 compliant
            -group graphs were not ranging correctly. fixed

///////////////////////////////////////////////////////////////////////////////
"""

from datetime import datetime, timedelta
import os
import glob
import time
import csv
import sys
import matplotlib
matplotlib.use('Agg')                                                           #switch backends to disable graph showing when saving
import matplotlib.pyplot as plt #pylint: disable=C0413
import numpy as np #pylint: disable=C0413
from bokeh.plotting import figure, output_file, save, ColumnDataSource #pylint: disable=C0413
from bokeh.models import HoverTool #pylint: disable=C0413
# __file__ = '/home/braine/BraineCode/LEMAS/LEMASmaster/LEMASmasterscripts'
install_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(install_location, '..')))
from variables import * #pylint: disable=C0413, W0401, W0614

months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']

linecolor = ["#1f77b4",
             "#ff7f0e",
             "#2ca02c",
             "#d62728",
             "#9467bd",
             "#8c564b",
             "#e377c2",
             "#7f7f7f",
             "#bcbd22",
             "#17becf",
             'aqua',
             'darkblue',
             'grey',
             'olive',
             'orange',
             'purple',
             'black']

icolor = -1
WEBBASEDIR = '/var/www/dmgenv.nist.gov/data/'
statsdir = '/var/www/dmgenv.nist.gov/statistics/'

#file structure '/var/www/dmgenv.nist.gov/EnvData/<group>/<building>/<lab>'
listgroups = next(os.walk(WEBBASEDIR))[1]                                       #list all folders in EnvironmentData
nmainoutages = np.array([[]])
# testtime = datetime(2018, 4, 6, 8, 44, 6, 632526)
# currenttime = matplotlib.dates.date2num(testtime)
# currenttime_past = matplotlib.dates.date2num(testtime - timedelta(hours=graphtime))
# currenttime_past_inter = matplotlib.dates.date2num(testtime - timedelta(hours=inter_time))
currenttime = datetime.now().replace(microsecond=0)

for igroup, _ in enumerate(listgroups):
    listbldgs = next(os.walk(WEBBASEDIR+'/'+listgroups[igroup]))[1]             #list all building folders in current group folder
    ngroupoutages = np.array([[]])
    groupmaxT = 'No data'
    groupminT_graph = 'No data'
    groupmaxT_graph = 'No data'
    groupmaxTtime = 'No data'
    groupmaxTlab = 'No data'
    groupmaxTbldg = 'No data'
    groupmaxRH = 'No data'
    groupminRH_graph = 'No data'
    groupmaxRH_graph = 'No data'
    groupmaxRHtime = 'No data'
    groupmaxRHlab = 'No data'
    groupmaxRHbldg = 'No data'
    ngroupToutages = 'No data'
    ngroupRHoutages = 'No data'
    ngroupcombooutages = 'No data'
    ngroupunique = 'No data'
    #initalize group environment graphs with no data available
    Gtemp = figure(
        plot_width=interIMGWIDTH,
        plot_height=interIMGHEIGHT,
        title=listgroups[igroup]+'\nTemperature\nGenerated '+str(currenttime),
        x_axis_type='datetime',
        tools=bokehtools)
    Gtemp.title.text_font_size = fontsizetitle_inter

    Ghumid = figure(
        plot_width=interIMGWIDTH,
        plot_height=interIMGHEIGHT,
        title=listgroups[igroup]+'\nHumidity\nGenerated '+str(currenttime),
        x_axis_type='datetime',
        tools=bokehtools)
    Ghumid.title.text_font_size = fontsizetitle_inter

    for ibldg, _ in enumerate(listbldgs):
        listlabs = next(os.walk(WEBBASEDIR+'/'+listgroups[igroup]+'/'+listbldgs[ibldg]))[1]
        nbldgoutages = np.array([[]])
        bldgmaxT = 'No data'
        bldgminT_graph = 'No data'
        bldgmaxT_graph = 'No data'
        bldgmaxTtime = 'No data'
        bldgmaxTlab = 'No data'
        bldgmaxRH = 'No data'
        bldgminRH_graph = 'No data'
        bldgmaxRH_graph = 'No data'
        bldgmaxRHtime = 'No data'
        bldgmaxRHlab = 'No data'
        nbldgToutages = 'No data'
        nbldgRHoutages = 'No data'
        nbldgcombooutages = 'No data'
        nbldgunique = 'No data'
        #initialize building environment graphs with no data available
        Btemp = figure(
            plot_width=interIMGWIDTH,
            plot_height=interIMGHEIGHT,
            title='Building '+listbldgs[ibldg]+'\nTemperature\nGenerated '+str(currenttime),
            x_axis_type='datetime',
            tools=bokehtools)
        Btemp.title.text_font_size = fontsizetitle_inter

        Bhumid = figure(
            plot_width=interIMGWIDTH,
            plot_height=interIMGHEIGHT,
            title='Building '+listbldgs[ibldg]+'\nHumidity\nGenerated '+str(currenttime),
            x_axis_type='datetime',
            tools=bokehtools)
        Bhumid.title.text_font_size = fontsizetitle_inter

        for ilab, _ in enumerate(listlabs):
            print('Processing: '+listbldgs[ibldg]+'/'+listlabs[ilab])
            icolor += 1
            if icolor >= len(linecolor):
                icolor = 0
            labmaxT = 'No data'
            labmaxTtime = 'No data'
            labavgT = 'No data'
            labsigmaT = 'No data'
            labmaxRH = 'No data'
            labmaxRHtime = 'No data'
            labavgRH = 'No data'
            labsigmaRH = 'No data'
            nlabToutages = 'No data'
            nlabRHoutages = 'No data'
            nlabcombooutages = 'No data'
            nlabunique = 'No data'
            labID = listbldgs[ibldg]+'_'+listlabs[ilab]                         #path to data is labID (*/219/G032/*-all.env.csv)
            #process recent environment data for graphing
            labaxestime = np.array([])                                          #initialize empty data variables for each lab
            labtemperature = np.array([])
            labhumidity = np.array([])
            currentyear = int(time.strftime("%Y"))
            currentmonth = int(time.strftime("%m"))
            # currentmonth=4
            currenttime = datetime.now()
            # currenttime = testtime
            currenttime_past = currenttime - timedelta(hours=graphtime)
            currenttime_past_inter = currenttime - timedelta(hours=inter_time)
            currenttime = currenttime.strftime("%Y-%m-%d %H:%M:%S")
            currenttime_past = currenttime_past.strftime("%Y-%m-%d %H:%M:%S")
            currenttime_past_inter = currenttime_past_inter.strftime("%Y-%m-%d %H:%M:%S")
            datafilename = labID+'_'+time.strftime("%B%Y")+'-all.env.csv'
            # datafilename = labID+'_April2018-all.env.csv'
            if currentmonth == 1:
                datafilename_past = labID+'_'+'December'+str(currentyear-1)+'-all.env.csv'
            else:
                datafilename_past = labID+'_'+months[currentmonth-2]+str(currentyear)+'-all.env.csv'

            #load environment data from last inter_time hours, open previous month just in case
            if os.path.isfile(WEBBASEDIR+'/'+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+datafilename_past): #if older file exists, get data from both files
                #must get older data first, then append to it the newer data
                with open(WEBBASEDIR+'/'+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+datafilename_past) as openedfile:
                    reader = csv.reader(openedfile, delimiter=',')          #read data from newer file
                    filedata = list(zip(*reader))

                axestime_header = filedata[0]
                labaxestime = np.append(labaxestime, axestime_header[1::])
                temperature_header = filedata[1]
                labtemperature = np.append(labtemperature, temperature_header[1::]).astype(float)
                humidity_header = filedata[2]
                labhumidity = np.append(labhumidity, humidity_header[1::]).astype(float)
                #append newer data to old
                if os.path.isfile(WEBBASEDIR+'/'+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+datafilename):
                    with open(WEBBASEDIR+'/'+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+datafilename) as openedfile:
                        reader = csv.reader(openedfile, delimiter=',')          #read data from newer file
                        filedata = list(zip(*reader))
                    axestime_header = filedata[0]
                    labaxestime = np.append(labaxestime, axestime_header[1::])
                    temperature_header = filedata[1]
                    labtemperature = np.append(labtemperature, temperature_header[1::]).astype(float)
                    humidity_header = filedata[2]
                    labhumidity = np.append(labhumidity, humidity_header[1::]).astype(float)
            elif os.path.isfile(WEBBASEDIR+'/'+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+datafilename):
                with open(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+datafilename) as openedfile:
                    reader = csv.reader(openedfile, delimiter=',')          #read data from newer file
                    filedata = list(zip(*reader))
                axestime_header = filedata[0]
                labaxestime = np.append(labaxestime, axestime_header[1::])
                temperature_header = filedata[1]
                labtemperature = np.append(labtemperature, temperature_header[1::]).astype(float)
                humidity_header = filedata[2]
                labhumidity = np.append(labhumidity, humidity_header[1::]).astype(float)
            #get data within inter_time
            if np.shape(labaxestime) != (0,):
                if labaxestime[-1] >= currenttime_past:                         #only execute if recent temperature is guaranteed to be within designated currentime_past
                    inter_index = np.where(labaxestime > currenttime_past_inter)[0][0]
                    graphtime_index = np.where(labaxestime > currenttime_past)[0][0]
                else:                                                           #otherwise remove data from memory
                    labtemperature = np.array([])
                    labhumidity = np.array([])
                    labaxestime = np.array([])

            #initialize current lab outage variables
            listoutagefiles = glob.glob('*-outages.env.csv')                    #list all outage data in current lab folder
            noutagesfiles = len(listoutagefiles)
            nlaboutages = np.array([[]])
            labaxestime_outage = np.array([])
            labtemperature_outage = np.array([])
            labhumidity_outage = np.array([])
            labwasTout = np.array([])
            labwasRHout = np.array([])
            combineddata = np.array([])
            #initialize variables for current lab environment from nmonths
            labaxestime_stats = np.array([])
            labtemperature_stats = np.array([])
            labhumidity_stats = np.array([])

            #generate list of outage files from nmonths
            nlaboutages = np.append(nlaboutages, ['monthYYYY', 'nTout', 'nRHout', 'ncomboout', 'nunique'])

            for imonth in range(nmonths):
                fileyear = int(currentyear + (currentmonth - imonth - 1)/12)
                filemonth = months[currentmonth - imonth - 1]
                filemonthYYYY = filemonth+str(fileyear)
                nlaboutages = np.vstack([nlaboutages, [filemonthYYYY, 0, 0, 0, 0]]) #append to list of months and outages

                #get outage data from nmonths
                if os.path.isfile(WEBBASEDIR+'/'+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+labID+'_'+filemonthYYYY+'-outages.env.csv'): #check if file exists
                    with open(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+labID+'_'+filemonthYYYY+'-outages.env.csv') as openedfile:
                        reader = csv.reader(openedfile, delimiter=',')          #read data from newer file
                        filedata = list(zip(*reader))
                    if filedata:                                                #if file is populated
                        c, r = np.shape(filedata)
                        if r > 1:
                            #loop data
                            axestime_header = filedata[0]
                            labaxestime_outage = np.append(labaxestime_outage, axestime_header[1::]) #gather lab time data, remove header
                            temperature_header = filedata[1]
                            labtemperature_outage = np.append(labtemperature_outage, temperature_header[1::]).astype(float) #gather lab temperature data, remove header
                            humidity_header = filedata[2]
                            labhumidity_outage = np.append(labhumidity_outage, humidity_header[1::]).astype(float) #gather lab humidity data, remove header
                            wasTout_header = filedata[3]
                            labwasTout = np.append(labwasTout, wasTout_header[1::]) #gather whether lab event was temperature outage, remove header
                            wasRHout_header = filedata[4]
                            labwasRHout = np.append(labwasRHout, wasRHout_header[1::]) #gather whether lab event was humidity outage, remove header
                            combineddata = np.vstack((labaxestime_outage, labtemperature_outage, labhumidity_outage, labwasTout, labwasRHout))
                            combineddata = np.transpose(combineddata)
                            combineddata = combineddata[combineddata[:, 0].argsort()]
                            start = np.where(combineddata == axestime_header[1])[0][0]
                            stop = np.where(combineddata == axestime_header[-1])[0][0]

                            if imonth == 0:                                     #if first month in analysis, determine first outage type and increase count
                                nlaboutages[imonth+1, 4] = nlaboutages[imonth+1, 4].astype(int) + 1 #increase count of unique events
                                if (combineddata[0, 3] == 'TEMPERATURE OUTAGE') and (combineddata[0, 4] != 'HUMIDITY OUTAGE'): #temperature only outage
                                    nlaboutages[imonth+1, 1] = nlaboutages[imonth+1, 1].astype(int) + 1 #increase count for temperature events
                                if (combineddata[0, 4] == 'HUMIDITY OUTAGE') and (combineddata[0, 3] != 'TEMPERATURE OUTAGE'): #humidity ounly outage
                                    nlaboutages[imonth+1, 2] = nlaboutages[imonth+1, 2].astype(int) + 1 #increase count for humidity events
                                if (combineddata[0, 3] == 'TEMPERATURE OUTAGE') and (combineddata[0, 4] == 'HUMIDITY OUTAGE'): #combined outage
                                    nlaboutages[imonth+1, 3] = nlaboutages[imonth+1, 3].astype(int) + 1 #increase count for combined events
                            #determine type of outage
                            for iline in range(start, stop):
                                if (datetime.strptime(combineddata[iline, 0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(combineddata[iline-1, 0], "%Y-%m-%d %H:%M:%S")) > timedelta(hours=normal_period): #if outside normal period, count as unique outage
                                    nlaboutages[imonth+1, 4] = nlaboutages[imonth+1, 4].astype(int) + 1 #increase count of unique events
                                    if (combineddata[iline, 3] == 'TEMPERATURE OUTAGE') and (combineddata[iline, 4] != 'HUMIDITY OUTAGE'): #temperature only outage
                                        nlaboutages[imonth+1, 1] = nlaboutages[imonth+1, 1].astype(int) + 1 #increase count for temperature events
                                    if (combineddata[iline, 4] == 'HUMIDITY OUTAGE') and (combineddata[iline, 3] != 'TEMPERATURE OUTAGE'): #humidity ounly outage
                                        nlaboutages[imonth+1, 2] = nlaboutages[imonth+1, 2].astype(int) + 1 #increase count for humidity events
                                if (combineddata[iline, 3] == 'TEMPERATURE OUTAGE') and (combineddata[iline, 4] == 'HUMIDITY OUTAGE'): #combined outage
                                    if (combineddata[iline-1, 3] != 'TEMPERATURE OUTAGE') or (combineddata[iline-1, 4] != 'HUMIDITY OUTAGE'):
                                        nlaboutages[imonth+1, 3] = nlaboutages[imonth+1, 3].astype(int) + 1 #increase count for combined events

                #get environment data from the nmonths for statistics
                if os.path.isfile(WEBBASEDIR+'/'+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+labID+'_'+filemonthYYYY+'-all.env.csv'):
                    with open(WEBBASEDIR+'/'+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+labID+'_'+filemonthYYYY+'-all.env.csv') as openedfile:
                        reader = csv.reader(openedfile, delimiter=',')          #read data from newer file
                        filedata = list(zip(*reader))
                    axestime_header = filedata[0]
                    labaxestime_stats = np.append(labaxestime_stats, axestime_header[1::]) #gather lab time data, remove header
                    temperature_header = filedata[1]
                    labtemperature_stats = np.append(labtemperature_stats, temperature_header[1::]).astype(float) #gather lab temperature data, remove header
                    humidity_header = filedata[2]
                    labhumidity_stats = np.append(labhumidity_stats, humidity_header[1::]).astype(float) #gather lab humidity data, remove header

            #generate recent environment graphs for current lab
            nlaboutages = np.array(sorted(nlaboutages[1::, :], key=lambda month: datetime.strptime(month[:][0], "%B%Y"))) #sort outages by month
            if labtemperature.any():                                            #if recent data exists for lab
                #determine max temperature, humidity and time for current lab for nmonths
                labmaxT = max(labtemperature_stats)
                labmaxTtime = labaxestime_stats[labtemperature_stats.argmax()]
                labavgT = round(np.average(labtemperature_stats), 2)
                labsigmaT = round(np.std(labtemperature_stats), 3)
                labmaxRH = max(labhumidity_stats)
                labmaxRHtime = labaxestime_stats[labhumidity_stats.argmax()]
                labavgRH = round(np.average(labhumidity_stats), 2)
                labsigmaRH = round(np.std(labhumidity_stats), 3)
                datatosum = nlaboutages[:, 1].astype(int)
                nlabToutages = datatosum.sum()
                datatosum = nlaboutages[:, 2].astype(int)
                nlabRHoutages = datatosum.sum()
                datatosum = nlaboutages[:, 3].astype(int)
                nlabcombooutages = datatosum.sum()
                datatosum = nlaboutages[:, 4].astype(int)
                nlabunique = datatosum.sum()

                #for current building, if no data then first lab in loop is max environment
                if isinstance(bldgmaxT, str):
                    bldgminT_graph = min(labtemperature[graphtime_index::])
                    bldgmaxT_graph = max(labtemperature[graphtime_index::])
                    bldgmaxT = max(labtemperature_stats)
                    bldgmaxTtime = labaxestime_stats[labtemperature_stats.argmax()]
                    bldgmaxTlab = listlabs[ilab]

                    bldgminRH_graph = min(labhumidity[graphtime_index::])
                    bldgmaxRH_graph = max(labhumidity[graphtime_index::])
                    bldgmaxRH = max(labhumidity_stats)
                    bldgmaxRHtime = labaxestime_stats[labhumidity_stats.argmax()]
                    bldgmaxRHlab = listlabs[ilab]
                elif not isinstance(bldgmaxT, str):
                    if max(labtemperature_stats) > bldgmaxT:                    #if new maximum lab temperature is greater than previous lab temperature
                        bldgmaxT = max(labtemperature_stats)
                        bldgmaxTtime = labaxestime_stats[labtemperature_stats.argmax()]
                        bldgmaxTlab = listlabs[ilab]

                    if max(labhumidity_stats) > bldgmaxRH:                      #if new maximum lab humidity is greater than previous lab humidity
                        bldgmaxRH = max(labhumidity_stats)
                        bldgmaxRHtime = labaxestime_stats[labhumidity_stats.argmax()]
                        bldgmaxRHlab = listlabs[ilab]

                    #max environment for building graphs
                    if isinstance(bldgmaxT_graph, str):                         #if max environment for building graphs has NOT been examined
                        if labtemperature:
                            bldgminT_graph = min(labtemperature[graphtime_index::])
                            bldgmaxT_graph = max(labtemperature[graphtime_index::])

                            bldgminRH_graph = min(labhumidity[graphtime_index::])
                            bldgmaxRH_graph = max(labhumidity[graphtime_index::])
                    elif not isinstance(bldgmaxT_graph, str):
                        if labtemperature.any():
                            if min(labtemperature[graphtime_index::]) < bldgminT_graph:
                                bldgminT_graph = min(labtemperature[graphtime_index::])
                            if max(labtemperature[graphtime_index::]) > bldgmaxT_graph:
                                bldgmaxT_graph = max(labtemperature[graphtime_index::])

                            if min(labhumidity[graphtime_index::]) < bldgminRH_graph:
                                bldgminRH_graph = min(labhumidity[graphtime_index::])
                            if max(labhumidity[graphtime_index::]) > bldgmaxRH_graph:
                                bldgmaxRH_graph = max(labhumidity[graphtime_index::])

                #for current group, if no data then first group in loop is max environment
                if isinstance(groupmaxT, str):
                    groupmaxT_graph = bldgmaxT_graph
                    groupminT_graph = bldgminT_graph
                    groupmaxT = bldgmaxT
                    groupmaxTtime = bldgmaxTtime
                    groupmaxTlab = bldgmaxTlab
                    groupmaxTbldg = listbldgs[ibldg]

                    groupminRH_graph = bldgminRH_graph
                    groupmaxRH_graph = bldgmaxRH_graph
                    groupmaxRH = bldgmaxT
                    groupmaxRHtime = bldgmaxRHtime
                    groupmaxRHlab = bldgmaxRHlab
                    groupmaxRHbldg = listbldgs[ibldg]
                elif not isinstance(bldgmaxT, str):
                    if bldgmaxT > groupmaxT:                                    #if new maximum lab temperature is greater than previous group temperature
                        groupmaxT = bldgmaxT
                        groupmaxTtime = bldgmaxTtime
                        groupmaxTlab = bldgmaxTlab
                        groupmaxTbldg = listbldgs[ibldg]

                    if bldgmaxRH > groupmaxRH:                                  #if new maximum lab humidity is greater than previous group humidity
                        groupmaxRH = bldgmaxRH
                        groupmaxRHtime = bldgmaxRHtime
                        groupmaxRHlab = bldgmaxRHlab
                        groupmaxRHbldg = listbldgs[ibldg]

                    #max environment for building graphs
                    if isinstance(groupmaxT_graph, str):
                        groupminT_graph = bldgminT_graph
                        groupmaxT_graph = bldgmaxT_graph
                        groupminRH_graph = bldgminRH_graph
                        groupmaxRH_graph = bldgmaxRH_graph
                    elif not isinstance(groupmaxT_graph, str):
                        if bldgminT_graph < groupminT_graph:
                            groupminT_graph = bldgminT_graph
                        if bldgmaxT_graph > groupmaxT_graph:
                            groupmaxT_graph = bldgmaxT_graph

                        if bldgminRH_graph < groupminRH_graph:
                            groupminRH_graph = bldgminRH_graph
                        if bldgmaxRH_graph > groupmaxRH_graph:
                            groupmaxRH_graph = bldgmaxRH_graph

                timevec_num = np.linspace(1e3*datetime.timestamp(datetime.strptime(labaxestime[0], "%Y-%m-%d %H:%M:%S").replace(second=0, microsecond=0)),
                                          1e3*datetime.timestamp(datetime.strptime(labaxestime[-1], "%Y-%m-%d %H:%M:%S").replace(second=0, microsecond=0)),
                                          len(labtemperature))
                timevec = np.array([])

                for itime in range(inter_index, len(labaxestime)):
                    timevec = np.append(timevec, datetime.strptime(labaxestime[itime], "%Y-%m-%d %H:%M:%S").replace(second=0, microsecond=0))

                Ltemp = figure(
                    plot_width=interIMGWIDTH,
                    plot_height=interIMGHEIGHT,
                    title='Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nTemperature\nGenerated '+str(currenttime),
                    x_axis_type='datetime',
                    tools=bokehtools)
                Ltemp.title.text_font_size = fontsizetitle_inter
                Tsource = ColumnDataSource(data={
                    'lab': [listbldgs[ibldg]+'/'+listlabs[ilab] for j in range(inter_index, len(labtemperature))],
                    'time': timevec,
                    'time_str': labaxestime[inter_index::],
                    'temperature': labtemperature[inter_index::]})
                Ltemp.line('time', 'temperature', source=Tsource, color='red', line_width=graphLinewidth)
                hoverLtemp = Ltemp.select(dict(type=HoverTool))
                hoverLtemp.tooltips = [('lab', '@lab'), ('time', '@time_str'), ('temperature', '@temperature')]
                # hover.mode = 'mouse'
                ticks = np.arange(1e3*datetime.timestamp(timevec[0]), 1e3*datetime.timestamp(timevec[-1]), tickspacing_time*60*60*1e3)
                hoverLtemp.mode = Lhmode
                Ltemp.toolbar.active_drag = None
                Ltemp.xaxis.ticker = ticks
                Ltemp.xaxis.major_label_orientation = 'vertical'
                Ltemp.xaxis.major_label_text_font_size = fontsizeXticks_inter
                Ltemp.x_range.start = datetime.timestamp(timevec[graphtime_index-inter_index])*1e3
                Ltemp.x_range.end = datetime.timestamp(timevec[-1])*1e3
                Ltemp.y_range.start = min(labtemperature[graphtime_index::])-graphTmin
                Ltemp.y_range.end = max(labtemperature[graphtime_index::])+graphTmax
                Ltemp.yaxis.axis_label = 'Temperature (deg. C)'
                Ltemp.yaxis.axis_label_text_font_size = fontsizeYticks_inter
                Ltemp.yaxis.major_label_text_font_size = fontsizeYticks_inter
                Ltemp.yaxis.major_label_orientation = 'horizontal'
                output_file(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-T.html')
                save(Ltemp)

                Lhumid = figure(
                    plot_width=interIMGWIDTH,
                    plot_height=interIMGHEIGHT,
                    title='Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nHumidity\nGenerated '+str(currenttime),
                    x_axis_type='datetime',
                    tools=bokehtools)
                Lhumid.title.text_font_size = fontsizetitle_inter
                RHsource = ColumnDataSource(data={
                    'lab': [listbldgs[ibldg]+'/'+listlabs[ilab] for j in range(inter_index, len(labtemperature))],
                    'time': timevec,
                    'time_str': labaxestime[inter_index::],
                    'humidity': labhumidity[inter_index::]})
                Lhumid.line('time', 'humidity', source=RHsource, color='blue', line_width=graphLinewidth)
                hoverLhumid = Lhumid.select(dict(type=HoverTool))
                hoverLhumid.tooltips = [('lab', '@lab'), ('time', '@time_str'), ('humidity', '@humidity')]
                # hover.mode = 'mouse'
                ticks = np.arange(1e3*datetime.timestamp(timevec[0]), 1e3*datetime.timestamp(timevec[-1]), tickspacing_time*60*60*1e3)
                hoverLhumid.mode = Lhmode
                Lhumid.toolbar.active_drag = None
                Lhumid.xaxis.ticker = ticks
                Lhumid.xaxis.major_label_orientation = 'vertical'
                Lhumid.xaxis.major_label_text_font_size = fontsizeXticks_inter
                Lhumid.x_range.start = datetime.timestamp(timevec[graphtime_index-inter_index])*1e3
                Lhumid.x_range.end = datetime.timestamp(timevec[-1])*1e3
                Lhumid.y_range.start = min(labhumidity[graphtime_index::])-graphRHmin
                Lhumid.y_range.end = max(labhumidity[graphtime_index::])+graphRHmax
                Lhumid.yaxis.axis_label = 'Humidity (%RH)'
                Lhumid.yaxis.axis_label_text_font_size = fontsizeYticks_inter
                Lhumid.yaxis.major_label_text_font_size = fontsizeYticks_inter
                Lhumid.yaxis.major_label_orientation = 'horizontal'
                output_file(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-RH.html')
                save(Lhumid)

                plt.figure("Lab Temperature Histogram", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                plt.hist(labtemperature_stats, bins=nbinsT, alpha=1)
                plt.xlabel('Temperature (deg. C)', fontsize=fontsizeXticks)
                plt.ylabel('Count, ~90 second period', fontsize=fontsizeYticks)
                plt.xticks(np.arange(np.floor(min(labtemperature_stats)), np.ceil(max(labtemperature_stats)), tickspacing_T), fontsize=fontsizeXticks, rotation='vertical')
                plt.yticks(fontsize=fontsizeYticks)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nTemperature distribution from the past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-Thist.png') #save current figure

                plt.figure("Lab Humidity Histogram", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                plt.hist(labhumidity_stats, bins=nbinsRH, alpha=1)
                plt.xlabel('Humdity (%RH)', fontsize=fontsizeXticks)
                plt.ylabel('Count, ~90 second period', fontsize=fontsizeYticks)
                plt.xticks(np.arange(np.floor(min(labhumidity_stats)), np.ceil(max(labhumidity_stats)), tickspacing_RH), fontsize=fontsizeXticks, rotation='vertical')
                plt.yticks(fontsize=fontsizeYticks)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nHumidity distribution from the past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-RHhist.png') #save current figure

                #generate outage bar chart for current lab
                ax4 = plt.figure("Lab Outages", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                ind = np.arange(nmonths)
                bar1 = plt.bar(ind, nlaboutages[:, 1].astype(int), graphBarwidth, color='red', label='Temperature events') #stack temperature events
                bar2 = plt.bar(ind, nlaboutages[:, 2].astype(int), graphBarwidth, color='green', label='Humidity events', bottom=nlaboutages[:, 1].astype(int)) #stack humidity events
                bar3 = plt.bar(ind, nlaboutages[:, 3].astype(int), graphBarwidth, color='blue', label='Temperature and humidity events', bottom=nlaboutages[:, 1].astype(int)+nlaboutages[:, 2].astype(int)) #stack combined events
                plt.grid(axis='y')
                plt.xticks(ind, nlaboutages[:, 0], fontsize=fontsizeXticks, rotation='vertical')
                plt.yticks(range(0, max(nlaboutages[:, 1].astype(int)+nlaboutages[:, 2].astype(int)+nlaboutages[:, 3].astype(int))+1, int(np.ceil((max(nlaboutages[:, 1].astype(int)+nlaboutages[:, 2].astype(int)+nlaboutages[:, 3].astype(int))+1)/8))), fontsize=fontsizeYticks)
                plt.ylim(ymin=0)
                plt.ylabel('Number of Events', fontsize=fontsizeYticks)
                plt.legend(bbox_to_anchor=(0.5, 0.99), loc='upper center', ncol=3)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nEnvironment events by month, past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.pause(0.005)
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-outages.png') #save current figure

                Btemp.line('time', 'temperature', source=Tsource, color=linecolor[icolor], legend=listbldgs[ibldg]+', '+listlabs[ilab], line_width=graphLinewidth)
                Bhumid.line('time', 'humidity', source=RHsource, color=linecolor[icolor], legend=listbldgs[ibldg]+', '+listlabs[ilab], line_width=graphLinewidth)

                Gtemp.line('time', 'temperature', source=Tsource, color=linecolor[icolor], legend=listbldgs[ibldg]+', '+listlabs[ilab], line_width=graphLinewidth)
                Ghumid.line('time', 'humidity', source=RHsource, color=linecolor[icolor], legend=listbldgs[ibldg]+', '+listlabs[ilab], line_width=graphLinewidth)

            elif labtemperature_stats.any():                                    #if no recent data for current lab, fill graphs and stats to inform user of no data
                with open(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-T.html', 'w') as openedfile:
                    openedfile.write('<h3>No data available</h3>')
                with open(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-RH.html', 'w') as openedfile:
                    openedfile.write('<h3>No data available</h3>')

                ax3 = plt.figure("Lab Humidity", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                plt.xlim([0, 10])
                plt.ylim([0, 10])
                plt.text(1, 1, 'No data available', fontsize=64)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nHumidity from the past '+str(graphtime)+' hours\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.pause(0.005)
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-RH.png')

                plt.figure("Lab Temperature Histogram", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                plt.hist(labtemperature_stats, bins=nbinsT, alpha=1)
                plt.xlabel('Temperature (deg. C)', fontsize=fontsizeXticks)
                plt.ylabel('Count, ~90 second period', fontsize=fontsizeYticks)
                plt.xticks(np.arange(np.floor(min(labtemperature_stats)), np.ceil(max(labtemperature_stats)), tickspacing_T), fontsize=fontsizeXticks, rotation='vertical')
                plt.yticks(fontsize=fontsizeYticks)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nTemperature distribution from the past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-Thist.png') #save current figure

                plt.figure("Lab Humidity Histogram", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                plt.hist(labhumidity_stats, bins=nbinsRH, alpha=1)
                plt.xlabel('Humdity (%RH)', fontsize=fontsizeXticks)
                plt.ylabel('Count, ~90 second period', fontsize=fontsizeYticks)
                plt.xticks(np.arange(np.floor(min(labhumidity_stats)), np.ceil(max(labhumidity_stats)), tickspacing_RH), fontsize=fontsizeXticks, rotation='vertical')
                plt.yticks(fontsize=fontsizeYticks)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nHumidity distribution from the past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-RHhist.png') #save current figure

                #generate outage bar chart for current lab
                ax4 = plt.figure("Lab Outages", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                ind = np.arange(nmonths)
                bar1 = plt.bar(ind, nlaboutages[:, 1].astype(int), graphBarwidth, color='red', label='Temperature events') #stack temperature events
                bar2 = plt.bar(ind, nlaboutages[:, 2].astype(int), graphBarwidth, color='green', label='Humidity events', bottom=nlaboutages[:, 1].astype(int)) #stack humidity events
                bar3 = plt.bar(ind, nlaboutages[:, 3].astype(int), graphBarwidth, color='blue', label='Temperature and humidity events', bottom=nlaboutages[:, 1].astype(int)+nlaboutages[:, 2].astype(int)) #stack combined events
                plt.grid(axis='y')
                plt.xticks(ind, nlaboutages[:, 0], fontsize=fontsizeXticks, rotation='vertical')
                plt.yticks(range(0, max(nlaboutages[:, 1].astype(int)+nlaboutages[:, 2].astype(int)+nlaboutages[:, 3].astype(int))+1, int(np.ceil((max(nlaboutages[:, 1].astype(int)+nlaboutages[:, 2].astype(int)+nlaboutages[:, 3].astype(int))+1)/8))), fontsize=fontsizeYticks)
                plt.ylim(ymin=0)
                plt.ylabel('Number of Events', fontsize=fontsizeYticks)
                plt.legend(bbox_to_anchor=(0.5, 0.99), loc='upper center', ncol=3)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nEnvironment events by month, past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.pause(0.005)
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-outages.png') #save current figure

                #determine max temperature and time for current lab
                labmaxT = max(labtemperature_stats)
                labmaxTtime = labaxestime_stats[labtemperature_stats.argmax()]
                labmaxRH = max(labhumidity_stats)
                labmaxRHtime = labaxestime_stats[labhumidity_stats.argmax()]
                labavgT = round(np.average(labtemperature_stats), 2)
                labsigmaT = round(np.std(labtemperature_stats), 3)
                labavgRH = round(np.average(labhumidity_stats), 2)
                labsigmaRH = round(np.std(labhumidity_stats), 3)
                datatosum = nlaboutages[:, 1].astype(int)
                nlabToutages = datatosum.sum()
                datatosum = nlaboutages[:, 2].astype(int)
                nlabRHoutages = datatosum.sum()
                datatosum = nlaboutages[:, 3].astype(int)
                nlabcombooutages = datatosum.sum()
                datatosum = nlaboutages[:, 4].astype(int)
                nlabunique = datatosum.sum()

                #for current building, if no data then first lab in loop is max environment
                if isinstance(bldgmaxT, str):
                    bldgmaxT = max(labtemperature_stats)
                    bldgmaxTtime = labaxestime_stats[labtemperature_stats.argmax()]
                    bldgmaxTlab = listlabs[ilab]

                    bldgmaxRH = max(labhumidity_stats)
                    bldgmaxRHtime = labaxestime_stats[labhumidity_stats.argmax()]
                    bldgmaxRHlab = listlabs[ilab]

                if max(labtemperature_stats) > bldgmaxT:                        #if new maximum lab temperature is greater than previous lab temperature
                    bldgmaxT = max(labtemperature_stats)
                    bldgmaxTtime = labaxestime_stats[labtemperature_stats.argmax()]
                    bldgmaxTlab = listlabs[ilab]

                if max(labhumidity_stats) > bldgmaxRH:                          #if new maximum lab humidity is greater than previous lab humidity
                    bldgmaxRH = max(labhumidity_stats)
                    bldgmaxRHtime = labaxestime_stats[labhumidity_stats.argmax()]
                    bldgmaxRHlab = listlabs[ilab]

                #for current group, if no data then first building in loop is max environment
                if isinstance(groupmaxT, str):
                    groupmaxT = bldgmaxT
                    groupmaxTtime = bldgmaxTtime
                    groupmaxTlab = bldgmaxTlab
                    groupmaxTbldg = listbldgs[ibldg]

                    groupmaxRH = bldgmaxT
                    groupmaxRHtime = bldgmaxRHtime
                    groupmaxRHlab = bldgmaxRHlab
                    groupmaxRHbldg = listbldgs[ibldg]

                if bldgmaxT > groupmaxT:                                        #if new maximum lab temperature is greater than previous group temperature
                    groupmaxT = bldgmaxT
                    groupmaxTtime = bldgmaxTtime
                    groupmaxTlab = bldgmaxTlab
                    groupmaxTbldg = listbldgs[ibldg]

                if bldgmaxRH > groupmaxRH:                                      #if new maximum lab humidity is greater than previous group humidity
                    groupmaxRH = bldgmaxRH
                    groupmaxRHtime = bldgmaxRHtime
                    groupmaxRHlab = bldgmaxRHlab
                    groupmaxRHbldg = listbldgs[ibldg]
            else:
                with open(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-T.html', 'w') as openedfile:
                    openedfile.write('<h3>No data available</h3>')
                with open(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-RH.html', 'w') as openedfile:
                    openedfile.write('<h3>No data available</h3>')

                plt.figure("Lab Temperature Histogram", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                plt.xlim([0, 10])
                plt.ylim([0, 10])
                plt.text(1, 1, 'No data available', fontsize=64)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nTemperature distribution from the past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.pause(0.005)
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-Thist.png') #save current figure

                plt.figure("Lab Humidity Histogram", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                plt.xlim([0, 10])
                plt.ylim([0, 10])
                plt.text(1, 1, 'No data available', fontsize=64)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nHumidity distribution from the past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.pause(0.005)
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-RHhist.png') #save current figure

                #generate outage bar chart for current lab
                ax4 = plt.figure("Lab Outages", figsize=(12.8, 7.2), dpi=dpi_set)
                plt.cla()
                plt.xlim([0, 10])
                plt.ylim([0, 10])
                plt.text(1, 1, 'No data available', fontsize=64)
                plt.title('Laboratory '+listbldgs[ibldg]+'/'+listlabs[ilab]+'\nEnvironment events by month, past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
                plt.tight_layout()
                plt.pause(0.005)
                plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listlabs[ilab]+'/'+listbldgs[ibldg]+'_'+listlabs[ilab]+'-outages.png') #save current figure

            #if data exists, round to 2 places
            if not isinstance(labmaxT, str):
                labmaxT = round(labmaxT, 2)
                labmaxRH = round(labmaxRH, 2)

            #export current lab statistics to file
            with open(statsdir+listbldgs[ibldg]+'_'+listlabs[ilab]+'.stats', 'w') as statsfile:
                statsfile.write('nToutages '+str(nlabToutages)+'\n')
                statsfile.write('nRHoutages '+str(nlabRHoutages)+'\n')
                statsfile.write('nComboOutages '+str(nlabcombooutages)+'\n')
                statsfile.write('nUnique '+str(nlabunique)+'\n')
                statsfile.write('maxT '+str(labmaxT)+' deg. C &nbsp &nbsp at &nbsp '+labmaxTtime+'\n')
                statsfile.write('maxRH '+str(labmaxRH)+' %RH &nbsp &nbsp &nbsp &nbsp at &nbsp '+labmaxRHtime+'\n')
                statsfile.write('avgT'+str(labavgT)+' deg. C, 1 sigma = '+str(labsigmaT)+'\n')
                statsfile.write('avgRH'+str(labavgRH)+' %RH, 1 sigma = '+str(labsigmaRH)+'\n')

            #include current lab outages in current building
            datatosum = nlaboutages[:, 1:5].astype(int)
            noutages = datatosum.sum(axis=0)
            if np.shape(nbldgoutages) == (1, 0):
                nbldgoutages = np.append(nbldgoutages, ['lab', 'nTout', 'nRHout', 'ncomboout', 'nunique'])
                nbldgoutages = np.vstack([nbldgoutages, [listlabs[ilab], noutages[0], noutages[1], noutages[2], noutages[3]]])
            else:
                nbldgoutages = np.vstack([nbldgoutages, [listlabs[ilab], noutages[0], noutages[1], noutages[2], noutages[3]]])

        nbldgoutages = np.array(sorted(nbldgoutages[1::, :], key=lambda nbldgoutages: nbldgoutages[0])) #sort by lab
        #generate outage bar chart for current building, export statistics
        if np.shape(nbldgoutages) != (0,):
            ax7 = plt.figure("Building Outages", figsize=(12.8, 7.2), dpi=dpi_set)
            plt.cla()
            ind = np.arange(len(nbldgoutages))
            bar1 = plt.bar(ind, nbldgoutages[:, 1].astype(int), graphBarwidth, color='red', label='Temperature events') #stack temperature events
            bar2 = plt.bar(ind, nbldgoutages[:, 2].astype(int), graphBarwidth, color='green', label='Humidity events', bottom=nbldgoutages[:, 1].astype(int)) #stack humidity events
            bar3 = plt.bar(ind, nbldgoutages[:, 3].astype(int), graphBarwidth, color='blue', label='Temperature and humidity events', bottom=nbldgoutages[:, 1].astype(int)+nbldgoutages[:, 2].astype(int)) #stack combined events
            plt.grid(axis='y')
            plt.xticks(ind, nbldgoutages[:, 0], fontsize=fontsizeXticks, rotation='vertical')
            plt.yticks(range(0, max(nbldgoutages[:, 1].astype(int)+nbldgoutages[:, 2].astype(int)+nbldgoutages[:, 3].astype(int))+5, int(np.ceil((max(nbldgoutages[:, 1].astype(int)+nbldgoutages[:, 2].astype(int)+nbldgoutages[:, 3].astype(int))+5)/8))), fontsize=fontsizeYticks)
            plt.ylim(ymin=0)
            plt.ylabel('Number of Events', fontsize=fontsizeYticks)
            plt.legend(bbox_to_anchor=(0.5, 0.99), loc='upper center', ncol=3)
            plt.title('Building '+listbldgs[ibldg]+'\nEnvironment events by laboratory, past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
            plt.tight_layout()
            plt.pause(0.005)
            plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listbldgs[ibldg]+'-outages.png')              #save current figure

            #process current building statistics
            datatosum = nbldgoutages[:, 1].astype(int)
            nbldgToutages = datatosum.sum()
            datatosum = nbldgoutages[:, 2].astype(int)
            nbldgRHoutages = datatosum.sum()
            datatosum = nbldgoutages[:, 3].astype(int)
            nbldgcombooutages = datatosum.sum()
            datatosum = nbldgoutages[:, 4].astype(int)
            nbldgunique = datatosum.sum()

        if not isinstance(bldgmaxT_graph, str):
            #save building graphs
            hoverBtemp = Btemp.select(dict(type=HoverTool))
            hoverBtemp.tooltips = [('lab', '@lab'), ('time', '@time_str'), ('temperature', '@temperature')]
            # hover.mode = 'mouse'
            ticks = np.arange(1e3*datetime.timestamp(timevec[0]), 1e3*datetime.timestamp(timevec[-1]), tickspacing_time*60*60*1e3)
            hoverBtemp.mode = hmode
            Btemp.toolbar.active_drag = None
            Btemp.legend.location = 'top_left'
            Btemp.xaxis.ticker = ticks
            Btemp.xaxis.major_label_orientation = 'vertical'
            Btemp.xaxis.major_label_text_font_size = fontsizeXticks_inter
            Btemp.x_range.start = datetime.timestamp(timevec[graphtime_index-inter_index])*1e3
            Btemp.x_range.end = datetime.timestamp(timevec[-1])*1e3
            Btemp.y_range.start = bldgminT_graph-graphTmin
            Btemp.y_range.end = bldgmaxT_graph+graphTmax
            Btemp.yaxis.axis_label = 'Temperature (deg. C)'
            Btemp.yaxis.axis_label_text_font_size = fontsizeYticks_inter
            Btemp.yaxis.major_label_text_font_size = fontsizeYticks_inter
            Btemp.yaxis.major_label_orientation = 'horizontal'
            output_file(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listbldgs[ibldg]+'-T.html')
            save(Btemp)

            hoverBhumid = Bhumid.select(dict(type=HoverTool))
            hoverBhumid.tooltips = [('lab', '@lab'), ('time', '@time_str'), ('humidity', '@humidity')]
            # hover.mode = 'mouse'
            ticks = np.arange(1e3*datetime.timestamp(timevec[0]), 1e3*datetime.timestamp(timevec[-1]), tickspacing_time*60*60*1e3)
            hoverBhumid.mode = hmode
            Bhumid.toolbar.active_drag = None
            Bhumid.legend.location = 'top_left'
            Bhumid.xaxis.ticker = ticks
            Bhumid.xaxis.major_label_orientation = 'vertical'
            Bhumid.xaxis.major_label_text_font_size = fontsizeXticks_inter
            Bhumid.x_range.start = datetime.timestamp(timevec[graphtime_index-inter_index])*1e3
            Bhumid.x_range.end = datetime.timestamp(timevec[-1])*1e3
            Bhumid.y_range.start = bldgminRH_graph-graphRHmin
            Bhumid.y_range.end = bldgmaxRH_graph+graphRHmax
            Bhumid.yaxis.axis_label = 'Humidity (%RH)'
            Bhumid.yaxis.axis_label_text_font_size = fontsizeYticks_inter
            Bhumid.yaxis.major_label_text_font_size = fontsizeYticks_inter
            Bhumid.yaxis.major_label_orientation = 'horizontal'
            output_file(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listbldgs[ibldg]+'-RH.html')
            save(Bhumid)
        else:
            with open(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listbldgs[ibldg]+'-T.html', 'w') as openedfile:
                openedfile.write('<h3>No data available</h3>')
            with open(WEBBASEDIR+listgroups[igroup]+'/'+listbldgs[ibldg]+'/'+listbldgs[ibldg]+'-RH.html', 'w') as openedfile:
                openedfile.write('<h3>No data available</h3>')

        #if data exists, round to 2 places
        if not isinstance(bldgmaxT, str):
            bldgmaxT = round(bldgmaxT, 2)
            bldgmaxRH = round(bldgmaxRH, 2)

        #export current building statistics to file
        with open(statsdir+listbldgs[ibldg]+'.stats', 'w') as statsfile:
            statsfile.write('nToutages '+str(nbldgToutages)+'\n')
            statsfile.write('nRHoutages '+str(nbldgRHoutages)+'\n')
            statsfile.write('nComboOutages '+str(nbldgcombooutages)+'\n')
            statsfile.write('nUnique ' +str(nbldgunique)+'\n')
            statsfile.write('maxT '+str(bldgmaxT)+' deg. C &nbsp in &nbsp '+listbldgs[ibldg]+'/'+bldgmaxTlab+' &nbsp at &nbsp '+bldgmaxTtime+'\n')
            statsfile.write('maxRH '+str(bldgmaxRH)+' %RH &nbsp &nbsp &nbsp in &nbsp '+listbldgs[ibldg]+'/'+bldgmaxRHlab+' &nbsp at &nbsp '+bldgmaxRHtime+'\n')

        #include current building outages in current group
        if len(nbldgoutages) != 0: #pylint: disable=C1801
            datatosum = nbldgoutages[:, 1:5].astype(int)
            noutages = datatosum.sum(axis=0)
            if np.shape(ngroupoutages) == (1, 0):
                ngroupoutages = np.append(ngroupoutages, ['lab', 'nTout', 'nRHout', 'ncomboout', 'nunique'])
                ngroupoutages = np.vstack([ngroupoutages, [listbldgs[ibldg], noutages[0], noutages[1], noutages[2], noutages[3]]])
            else:
                ngroupoutages = np.vstack([ngroupoutages, [listbldgs[ibldg], noutages[0], noutages[1], noutages[2], noutages[3]]])

    ngroupoutages = np.array(sorted(ngroupoutages[1::, :], key=lambda ngroupoutages: ngroupoutages[0])) #sort by building
    #generate outage bar chart for current group
    if len(ngroupoutages) != 0: #pylint: disable=C1801
        ax10 = plt.figure("Group Outages", figsize=(12.8, 7.2), dpi=dpi_set)
        plt.cla()
        ind = np.arange(len(ngroupoutages))
        bar1 = plt.bar(ind, ngroupoutages[:, 1].astype(int), graphBarwidth, color='red', label='Temperature events') #stack temperature events
        bar2 = plt.bar(ind, ngroupoutages[:, 2].astype(int), graphBarwidth, color='green', label='Humidity events', bottom=ngroupoutages[:, 1].astype(int)) #stack humidity events
        bar3 = plt.bar(ind, ngroupoutages[:, 3].astype(int), graphBarwidth, color='blue', label='Temperature and humidity events', bottom=ngroupoutages[:, 1].astype(int)+ngroupoutages[:, 2].astype(int)) #stack combined events
        plt.grid(axis='y')
        plt.xticks(ind, ngroupoutages[:, 0], fontsize=fontsizeXticks, rotation='vertical')
        plt.yticks(range(0, max(ngroupoutages[:, 1].astype(int)+ngroupoutages[:, 2].astype(int)+ngroupoutages[:, 3].astype(int))+10, int(np.ceil((max(ngroupoutages[:, 1].astype(int)+ngroupoutages[:, 2].astype(int)+ngroupoutages[:, 3].astype(int))+10)/8))), fontsize=fontsizeYticks)
        plt.ylim(ymin=0)
        plt.ylabel('Number of Events', fontsize=fontsizeYticks)
        plt.legend(bbox_to_anchor=(0.5, 0.99), loc='upper center', ncol=3)
        plt.title(listgroups[igroup]+'\nEnvironment events by building, past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
        plt.tight_layout()
        plt.pause(0.005)
        plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listgroups[igroup]+'-outages.png')                #save current figure

        #process current building statistics
        datatosum = ngroupoutages[:, 1].astype(int)
        ngroupToutages = datatosum.sum()
        datatosum = ngroupoutages[:, 2].astype(int)
        ngroupRHoutages = datatosum.sum()
        datatosum = ngroupoutages[:, 3].astype(int)
        ngroupcombooutages = datatosum.sum()
        datatosum = ngroupoutages[:, 4].astype(int)
        ngroupunique = datatosum.sum()
    else:
        ax4 = plt.figure("Group Outages", figsize=(12.8, 7.2), dpi=dpi_set)
        plt.cla()
        plt.xlim([0, 10])
        plt.ylim([0, 10])
        plt.text(1, 1, 'No data available', fontsize=64)
        plt.title(listgroups[igroup]+'\nEnvironment events by building, past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
        plt.tight_layout()
        plt.pause(0.005)
        plt.savefig(WEBBASEDIR+listgroups[igroup]+'/'+listgroups[igroup]+'-outages.png')

    if isinstance(groupmaxT, str):
        with open(WEBBASEDIR+listgroups[igroup]+'/'+listgroups[igroup]+'-T.html', 'w') as openedfile:
            openedfile.write('<h3>No data available</h3>')
        with open(WEBBASEDIR+listgroups[igroup]+'/'+listgroups[igroup]+'-RH.html', 'w') as openedfile:
            openedfile.write('<h3>No data available</h3>')

    #save group graphs
    hoverGtemp = Gtemp.select(dict(type=HoverTool))
    hoverGtemp.tooltips = [('lab', '@lab'), ('time', '@time_str'), ('temperature', '@temperature')]
    # hover.mode = 'mouse'
    ticks = np.arange(1e3*datetime.timestamp(timevec[0]), 1e3*datetime.timestamp(timevec[-1]), tickspacing_time*60*60*1e3)
    hoverGtemp.mode = hmode
    Gtemp.toolbar.active_drag = None
    Gtemp.legend.location = 'top_left'
    Gtemp.xaxis.ticker = ticks
    Gtemp.xaxis.major_label_orientation = 'vertical'
    Gtemp.xaxis.major_label_text_font_size = fontsizeXticks_inter
    Gtemp.x_range.start = datetime.timestamp(timevec[graphtime_index-inter_index])*1e3
    Gtemp.x_range.end = datetime.timestamp(timevec[-1])*1e3
    Gtemp.y_range.start = groupminT_graph-graphTmin
    Gtemp.y_range.end = groupmaxT_graph+graphTmax
    Gtemp.yaxis.axis_label = 'Temperature (deg. C)'
    Gtemp.yaxis.axis_label_text_font_size = fontsizeYticks_inter
    Gtemp.yaxis.major_label_text_font_size = fontsizeYticks_inter
    Gtemp.yaxis.major_label_orientation = 'horizontal'
    output_file(WEBBASEDIR+listgroups[igroup]+'/'+listgroups[igroup]+'-T.html')
    save(Gtemp)

    hoverGhumid = Ghumid.select(dict(type=HoverTool))
    hoverGhumid.tooltips = [('lab', '@lab'), ('time', '@time_str'), ('humidity', '@humidity')]
    # hover.mode = 'mouse'
    ticks = np.arange(1e3*datetime.timestamp(timevec[0]), 1e3*datetime.timestamp(timevec[-1]), tickspacing_time*60*60*1e3)
    hoverGhumid.mode = hmode
    Ghumid.toolbar.active_drag = None
    Ghumid.legend.location = 'top_left'
    Ghumid.xaxis.ticker = ticks
    Ghumid.xaxis.major_label_orientation = 'vertical'
    Ghumid.xaxis.major_label_text_font_size = fontsizeXticks_inter
    Ghumid.x_range.start = datetime.timestamp(timevec[graphtime_index-inter_index])*1e3
    Ghumid.x_range.end = datetime.timestamp(timevec[-1])*1e3
    Ghumid.y_range.start = groupminRH_graph-graphRHmin
    Ghumid.y_range.end = groupmaxRH_graph+graphRHmax
    Ghumid.yaxis.axis_label = 'Humidity (%RH)'
    Ghumid.yaxis.axis_label_text_font_size = fontsizeYticks_inter
    Ghumid.yaxis.major_label_text_font_size = fontsizeYticks_inter
    Ghumid.yaxis.major_label_orientation = 'horizontal'
    output_file(WEBBASEDIR+listgroups[igroup]+'/'+listgroups[igroup]+'-RH.html')
    save(Ghumid)

    #if data exists, round to 2 places
    if not isinstance(groupmaxT, str):
        groupmaxT = round(groupmaxT, 2)
        groupmaxRH = round(groupmaxRH, 2)

    #export current building statistics to file
    with open(statsdir+listgroups[igroup]+'.stats', 'w') as statsfile:
        statsfile.write('nToutages '+str(ngroupToutages)+'\n')
        statsfile.write('nRHoutages '+str(ngroupRHoutages)+'\n')
        statsfile.write('nComboOutages '+str(ngroupcombooutages)+'\n')
        statsfile.write('nUnique '+str(ngroupunique)+'\n')
        statsfile.write('maxT '+str(groupmaxT)+' deg. C &nbsp in &nbsp '+groupmaxTbldg+'/'+groupmaxTlab+' &nbsp at &nbsp '+groupmaxTtime+'\n')
        statsfile.write('maxRH '+str(groupmaxRH)+' %RH &nbsp &nbsp &nbsp in &nbsp '+groupmaxRHbldg+'/'+groupmaxRHlab+' &nbsp at &nbsp '+groupmaxRHtime+'\n')

    #include current group outages in main
    if len(ngroupoutages) != 0: #pylint: disable=C1801
        datatosum = ngroupoutages[:, 1:5].astype(int)
        noutages = datatosum.sum(axis=0)
        if np.shape(nmainoutages) == (1, 0):
            nmainoutages = np.append(nmainoutages, ['lab', 'nTout', 'nRHout', 'ncomboout', 'nunique'])
            nmainoutages = np.vstack([nmainoutages, [listgroups[igroup], noutages[0], noutages[1], noutages[2], noutages[3]]])
        else:
            nmainoutages = np.vstack([nmainoutages, [listgroups[igroup], noutages[0], noutages[1], noutages[2], noutages[3]]])

nmainoutages = np.array(sorted(nmainoutages[1::, :], key=lambda nmainoutages: nmainoutages[0])) #sort by building
#process data for main
if len(nmainoutages) != 0: #pylint: disable=C1801
    ax11 = plt.figure("Main Outages", figsize=(12.8, 7.2), dpi=dpi_set)
    plt.cla()
    ind = np.arange(len(nmainoutages))
    bar1 = plt.bar(ind, nmainoutages[:, 1].astype(int), graphBarwidth, color='red', label='Temperature events') #stack temperature events
    bar2 = plt.bar(ind, nmainoutages[:, 2].astype(int), graphBarwidth, color='green', label='Humidity events', bottom=nmainoutages[:, 1].astype(int)) #stack humidity events
    bar3 = plt.bar(ind, nmainoutages[:, 3].astype(int), graphBarwidth, color='blue', label='Temperature and humidity events', bottom=nmainoutages[:, 1].astype(int)+nmainoutages[:, 2].astype(int)) #stack combined events
    plt.grid(axis='y')
    plt.xticks(ind, nmainoutages[:, 0], fontsize=fontsizeXticks, rotation='vertical')
    plt.yticks(range(0, max(nmainoutages[:, 1].astype(int))+max(nmainoutages[:, 2].astype(int))+max(nmainoutages[:, 3].astype(int))+10, int(np.ceil((max(nmainoutages[:, 1].astype(int)+nmainoutages[:, 2].astype(int)+nmainoutages[:, 3].astype(int))+10)/8))), fontsize=fontsizeYticks)
    plt.ylim(ymin=0)
    plt.ylabel('Number of Events', fontsize=fontsizeYticks)
    plt.legend(bbox_to_anchor=(0.5, 0.99), loc='upper center', ncol=3)
    plt.title('Environment events by group, past '+str(nmonths)+' months\nGenerated '+str(currenttime), fontsize=fontsizetitle)
    plt.tight_layout()
    plt.pause(0.005)
    plt.savefig(WEBBASEDIR+'main-outages.png')                                   #save current figure
