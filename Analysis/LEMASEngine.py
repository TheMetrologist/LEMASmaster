import os
import sys
import csv
import glob
import time
import threading
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
# __file__ = "D:/BraineCode/LEMAS/LEMASmaster2/Analysis/LEMASObjects.py"
install_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(install_location+"/../")))
import var.LEMASvar as LEMASvar

WebBaseDir = "/var/www/dev_dmgenv.nist.gov/data/"
StatsDir = "/var/www/dev_dmgenv.nist.gov/statistics/"
# WebBaseDir = "/media/strang/A/dmgenv.nist.gov/data/"
# StatsDir = "/media/strang/A/dmgenv.nist.gov/statistics/"
# WebBaseDir = "D:/dmgenv.nist.gov/data/"
# StatsDir = "D:/dmgenv.nist.gov/statistics/"

# file structure "/var/www/dmgenv.nist.gov/EnvData/<group>/<building>/<lab>"
listgroups = next(os.walk(WebBaseDir))[1]                                       # list all folders in EnvironmentData
if "ArchivedData" in listgroups:
    del listgroups[listgroups.index("ArchivedData")]                                # remove ArchivedData directory from list
if "JupyterNotebooks" in listgroups:
    del listgroups[listgroups.index("JupyterNotebooks")]                            # remove ArchivedData directory from list

months = [
    'January',
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
    'December',
]

class Lab():
    def __init__(self, Group, Building, Room, Name):
        super().__init__()

        # variables
        self.Group = Group.replace(" ", "")
        self.Building = str(Building)
        self.Room = str(Room)
        self.LabID = self.Building + "_" + self.Room
        self.Path = WebBaseDir + self.Group + "/" + self.Building + "/" + self.Room + "/"
        self.StatisticsPath = StatsDir
        self.Name = Name
        self.MaxT = 0
        self.AvgT = 0
        self.SigmaT = 0
        self.TimeMaxT = ""
        self.MaxRH = 0
        self.AvgRH = 0
        self.SigmaRH = 0
        self.TimeMaxRH = ""
        self.ThreadEvent = threading.Event()
        self.UpdateThread = threading.Thread(target=self.UpdateAll)
        self.LabEnv = pd.DataFrame(np.array([[]]), columns=[])
        self.LabEnv_nmonths = pd.DataFrame(np.array([[]]), columns=[])
        self.nOutages = pd.DataFrame(np.array([[]]), columns=[])
        self.TFigure = ""
        self.RHFigure = ""
        self.THistogram = ""
        self.RHHistogram = ""
        self.OutageBars = ""
        self.GetRecentData()
        self.AnalyzeStatistics()

    def GetOutageDataFromPeriod(self, start, end):
        start = datetime.strptime(start, "%B %d, %Y")
        end = datetime.strptime(end, "%B %d, %Y")
        nOutages = ""

        # generate month and year component of filename for date range
        yoffset = 0
        moffset = 0
        MonthYYYY = []
        while start.year+yoffset <= end.year:
            if start.year+yoffset == end.year:
                while start.month-1+moffset < end.month:
                    MonthYYYY.append(months[start.month-1+moffset] + " " + str(start.year+yoffset))
                    moffset += 1
            else:
                while start.month-1+moffset < 12:
                    MonthYYYY.append(months[start.month-1+moffset] + " " + str(start.year+yoffset))
                    moffset += 1
            yoffset += 1
            moffset = -start.month+1

        first = True
        for ifile, filepart in enumerate(MonthYYYY):
            filemonth = filepart.split(" ")[0]
            fileyear = filepart.split(" ")[1]
            if os.path.isfile(self.Path + self.LabID + "_" + filemonth+fileyear + "-outages.env.csv"):
                with open(self.Path + self.LabID + "_" + filemonth+fileyear + "-outages.env.csv", "r") as openedfile:
                    filedata = list(zip(*csv.reader(openedfile)))

                PandaDate = pd.period_range(filepart, freq="M", periods=1)
                if "pandas" not in str(type(nOutages)):
                    nOutages = pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=PandaDate)
                else:
                    nOutages = nOutages.append(pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=PandaDate))

                if filedata:                                                    # if file is populated
                    _, nrows = np.shape(filedata)
                    if nrows > 1:
                        axestime_header = filedata[0]
                        LabAxesTime_outage = axestime_header[1::]               # gather lab time data, remove header
                        wasTout_header = filedata[3]
                        WasTout = wasTout_header[1::]                           # gather whether lab event was temperature outage, remove header
                        wasRHout_header = filedata[4]
                        WasRHout = wasRHout_header[1::]                         # gather whether lab event was humidity outage, remove header
                        CombinedData = np.vstack((LabAxesTime_outage, WasTout, WasRHout))
                        CombinedData = np.transpose(CombinedData)
                        CombinedData = CombinedData[CombinedData[:, 0].argsort()]

                        if first:                                          # if first file in analysis, determine first outage type and increase count
                            first = False
                            nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nUnique"] += 1 # increase count of unique events
                            if (CombinedData[0, 1] == 'TEMPERATURE OUTAGE') and (CombinedData[0, 2] != 'HUMIDITY OUTAGE'): # temperature only outage
                                nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nToutages"] += 1
                            if (CombinedData[0, 2] == 'HUMIDITY OUTAGE') and (CombinedData[0, 1] != 'TEMPERATURE OUTAGE'): # humidity ounly outage
                                nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nRHoutages"] += 1
                            if (CombinedData[0, 1] == 'TEMPERATURE OUTAGE') and (CombinedData[0, 2] == 'HUMIDITY OUTAGE'): # combined outage
                                nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nCombined"] += 1

                        #determine type of outage
                        for iline, _ in enumerate(LabAxesTime_outage):
                            if abs(datetime.strptime(CombinedData[iline, 0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(CombinedData[iline-1, 0], "%Y-%m-%d %H:%M:%S")) > timedelta(hours=LEMASvar.normal_period): # if outside normal period, count as unique outage
                                nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nUnique"] += 1 # increase count of unique events
                                if (CombinedData[iline, 1] == 'TEMPERATURE OUTAGE') and (CombinedData[iline, 2] != 'HUMIDITY OUTAGE'): # temperature only outage
                                    nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nToutages"] += 1 # increase count for temperature events
                                if (CombinedData[iline, 2] == 'HUMIDITY OUTAGE') and (CombinedData[iline, 1] != 'TEMPERATURE OUTAGE'): # humidity ounly outage
                                    nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nRHoutages"] += 1 # increase count for humidity events
                            if (CombinedData[iline, 1] == 'TEMPERATURE OUTAGE') and (CombinedData[iline, 2] == 'HUMIDITY OUTAGE'): # combined outage
                                if (CombinedData[iline-1, 1] != 'TEMPERATURE OUTAGE') or (CombinedData[iline-1, 2] != 'HUMIDITY OUTAGE'):
                                    nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nUnique"] += 1 # increase count of unique events # increase count for combined events

            else:
                print("Data does not exist for lab "+self.LabID+" in "+filepart)
        self.nOutages = nOutages

    def GetRecentData(self):
        currenttime = datetime.now().replace(microsecond=0)
        currenttime_past = currenttime - timedelta(hours=LEMASvar.graphtime)
        currenttime_past = currenttime_past.strftime("%Y-%m-%d %H:%M:%S")
        currenttime_past_inter = currenttime - timedelta(hours=LEMASvar.inter_time)
        currenttime_past_inter = currenttime_past_inter.strftime("%Y-%m-%d %H:%M:%S")

        LabTemperature = np.array([])
        LabHumidity = np.array([])
        LabAxesTime = np.array([])

        currentyear = int(time.strftime("%Y"))
        currentmonth = int(time.strftime("%m"))
        if currentmonth == 1:
            datafilename_past = self.LabID+'_'+'December'+str(currentyear-1)+'-all.env.csv'
        else:
            datafilename_past = self.LabID+'_'+months[currentmonth-2]+str(currentyear)+'-all.env.csv'
        datafilename = self.LabID + '_'+time.strftime("%B%Y") + '-all.env.csv'

        # load environment data from last inter_time hours, open previous month just in case at beginning of new month
        if os.path.isfile(self.Path + datafilename_past):                       # if older file exists, get data from both files
            with open(self.Path + datafilename_past) as openedfile:
                filedata = list(zip(*csv.reader(openedfile)))
            axestime_header = filedata[0]
            LabAxesTime = np.append(LabAxesTime, axestime_header[1::])
            temperature_header = filedata[1]
            LabTemperature = np.append(LabTemperature, temperature_header[1::]).astype(float)
            humidity_header = filedata[2]
            LabHumidity = np.append(LabHumidity, humidity_header[1::]).astype(float)
            if os.path.isfile(self.Path + datafilename):
                with open(self.Path + datafilename) as openedfile:
                    filedata = list(zip(*csv.reader(openedfile)))
                axestime_header = filedata[0]
                LabAxesTime = np.append(LabAxesTime, axestime_header[1::])
                temperature_header = filedata[1]
                LabTemperature = np.append(LabTemperature, temperature_header[1::]).astype(float)
                humidity_header = filedata[2]
                LabHumidity = np.append(LabHumidity, humidity_header[1::]).astype(float)
        if os.path.isfile(self.Path + datafilename):
            with open(self.Path + datafilename) as openedfile:
                filedata = list(zip(*csv.reader(openedfile)))
            axestime_header = filedata[0]
            LabAxesTime = np.append(LabAxesTime, axestime_header[1::])
            temperature_header = filedata[1]
            LabTemperature = np.append(LabTemperature, temperature_header[1::]).astype(float)
            humidity_header = filedata[2]
            LabHumidity = np.append(LabHumidity, humidity_header[1::]).astype(float)

        if len(LabAxesTime) != 0:
            if (LabAxesTime > currenttime_past_inter).any():
                start = np.where(LabAxesTime > currenttime_past_inter)[0][0]
                LabID = np.zeros((len(LabTemperature[start::]),)).astype(str)
                LabID[:] = self.Building + "/" + self.Room
                self.LabEnv = pd.DataFrame(np.array([LabAxesTime[start::], LabTemperature[start::], LabHumidity[start::], LabID]).transpose(), columns=["Time", "Temperature", "Humidity", "Lab"])
                self.LabEnv.sort_values(by="Time", inplace=True)
            else:
                self.LabEnv = "No data"
        else:
            self.LabEnv = "No data"

    def AnalyzeStatistics(self):
        # initialize current lab outage data for pandas dataframe
        listoutagefiles = glob.glob(self.Path + '*-outages.env.csv')            # list all outage data in current lab folder
        noutagesfiles = len(listoutagefiles)
        WasTout = np.array([])
        WasRHout = np.array([])
        CombinedData = np.array([])
        LabAxesTime_outage = np.array([])
        LabTemperature_outage = np.array([])
        LabHumidity_outage = np.array([])
        LabAxesTime_stats = np.array([])
        LabTemperature_stats = np.array([])
        LabHumidity_stats = np.array([])

        currentyear = int(time.strftime("%Y"))
        currentmonth = int(time.strftime("%m"))

        #generate list of outage files from nmonths
        for imonth in range(LEMASvar.nmonths):
            fileyear = int(currentyear + (currentmonth - imonth - 1)/12)
            filemonth = months[currentmonth - imonth - 1]
            filemonthYYYY = filemonth+str(fileyear)
            PandaDate = pd.period_range(filemonth+" "+str(fileyear), freq="M", periods=1)
            if imonth == 0:
                nOutages = pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=PandaDate)
            else:
                nOutages = nOutages.append(pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=PandaDate))

            # get outage data from nmonths
            if os.path.isfile(self.Path + self.LabID + '_' + filemonthYYYY + '-outages.env.csv'): # check if file exists
                with open(self.Path + self.LabID + '_' + filemonthYYYY + '-outages.env.csv') as openedfile:
                    filedata = list(zip(*csv.reader(openedfile)))
                if filedata:                                                    # if file is populated
                    _, nrows = np.shape(filedata)
                    if nrows > 1:
                        axestime_header = filedata[0]
                        LabAxesTime_outage = np.append(LabAxesTime_outage, axestime_header[1::]) # gather lab time data, remove header
                        temperature_header = filedata[1]
                        LabTemperature_outage = np.append(LabTemperature_outage, temperature_header[1::]).astype(float) # gather lab temperature data, remove header
                        humidity_header = filedata[2]
                        LabHumidity_outage = np.append(LabHumidity_outage, humidity_header[1::]).astype(float) # gather lab humidity data, remove header
                        wasTout_header = filedata[3]
                        WasTout = np.append(WasTout, wasTout_header[1::])       # gather whether lab event was temperature outage, remove header
                        wasRHout_header = filedata[4]
                        WasRHout = np.append(WasRHout, wasRHout_header[1::])    # gather whether lab event was humidity outage, remove header
                        CombinedData = np.vstack((LabAxesTime_outage, LabTemperature_outage, LabHumidity_outage, WasTout, WasRHout))
                        CombinedData = np.transpose(CombinedData)
                        CombinedData = CombinedData[CombinedData[:, 0].argsort()]
                        start = np.where(CombinedData == axestime_header[1])[0][0]
                        stop = np.where(CombinedData == axestime_header[-1])[0][0]

                        if imonth == 0:                                         # if first month in analysis, determine first outage type and increase count
                            nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nUnique"] += 1 # increase count of unique events
                            if (CombinedData[0, 3] == 'TEMPERATURE OUTAGE') and (CombinedData[0, 4] != 'HUMIDITY OUTAGE'): # temperature only outage
                                nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nToutages"] += 1
                            if (CombinedData[0, 4] == 'HUMIDITY OUTAGE') and (CombinedData[0, 3] != 'TEMPERATURE OUTAGE'): # humidity ounly outage
                                nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nRHoutages"] += 1
                            if (CombinedData[0, 3] == 'TEMPERATURE OUTAGE') and (CombinedData[0, 4] == 'HUMIDITY OUTAGE'): # combined outage
                                nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nCombined"] += 1

                        #determine type of outage
                        for iline in range(start, stop):
                            if abs(datetime.strptime(CombinedData[iline, 0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(CombinedData[iline-1, 0], "%Y-%m-%d %H:%M:%S")) > timedelta(hours=LEMASvar.normal_period): # if outside normal period, count as unique outage
                                nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nUnique"] += 1 # increase count of unique events
                                if (CombinedData[iline, 3] == 'TEMPERATURE OUTAGE') and (CombinedData[iline, 4] != 'HUMIDITY OUTAGE'): # temperature only outage
                                    nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nToutages"] += 1 # increase count for temperature events
                                if (CombinedData[iline, 4] == 'HUMIDITY OUTAGE') and (CombinedData[iline, 3] != 'TEMPERATURE OUTAGE'): # humidity ounly outage
                                    nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nRHoutages"] += 1 # increase count for humidity events
                            if (CombinedData[iline, 3] == 'TEMPERATURE OUTAGE') and (CombinedData[iline, 4] == 'HUMIDITY OUTAGE'): # combined outage
                                if (CombinedData[iline-1, 3] != 'TEMPERATURE OUTAGE') or (CombinedData[iline-1, 4] != 'HUMIDITY OUTAGE'):
                                    nOutages.loc[str(fileyear) + "-" + str(months.index(filemonth)+1)]["nUnique"] += 1 # increase count of unique events # increase count for combined events

            # get environment data from the nmonths for statistics
            if os.path.isfile(self.Path + self.LabID + '_' + filemonthYYYY + '-all.env.csv'):
                with open(self.Path + self.LabID + '_' + filemonthYYYY + '-all.env.csv') as openedfile:
                    filedata = list(zip(*csv.reader(openedfile)))
                axestime_header = filedata[0]
                LabAxesTime_stats = np.append(LabAxesTime_stats, axestime_header[1::]) # gather lab time data, remove header
                temperature_header = filedata[1]
                LabTemperature_stats = np.append(LabTemperature_stats, temperature_header[1::]).astype(float) # gather lab temperature data, remove header
                humidity_header = filedata[2]
                LabHumidity_stats = np.append(LabHumidity_stats, humidity_header[1::]).astype(float) # gather lab humidity data, remove header

        if LabTemperature_stats.any():                                          # if recent data exists for lab
            # determine max temperature, humidity and time for current lab for nmonths
            self.MaxT = np.round(max(LabTemperature_stats), 2)
            self.TimeMaxT = LabAxesTime_stats[LabTemperature_stats.argmax()]
            self.AvgT = round(np.average(LabTemperature_stats), 2)
            self.SigmaT = round(np.std(LabTemperature_stats), 3)

            self.MaxRH = np.round(max(LabHumidity_stats), 2)
            self.TimeMaxRH = LabAxesTime_stats[LabHumidity_stats.argmax()]
            self.AvgRH = round(np.average(LabHumidity_stats), 2)
            self.SigmaRH = round(np.std(LabHumidity_stats), 3)

            with open(self.StatisticsPath + self.LabID + ".stats", "w") as openedfile:
                openedfile.write("nToutages " + str(nOutages["nToutages"].sum()) + "\n")
                openedfile.write("nRHoutages " + str(nOutages["nRHoutages"].sum()) + "\n")
                openedfile.write("nComboOutages " + str(nOutages["nCombined"].sum()) + "\n")
                openedfile.write("nUnique " + str(nOutages["nUnique"].sum()) + "\n")
                openedfile.write("max T" + str(self.MaxT) + " deg. C &nbsp &nbsp at &nbsp " + self.TimeMaxT + "\n")
                openedfile.write("maxRH " + str(self.MaxRH) + " %RH &nbsp &nbsp &nbsp &nbsp at &nbsp " + self.TimeMaxRH + "\n")
                openedfile.write("avgT " + str(self.AvgT) + " deg. C, 1 sigma = " + str(self.SigmaT) + "\n")
                openedfile.write("avgRH "+str(self.AvgRH)+" %RH, 1 sigma = "+str(self.SigmaRH)+"\n")
        else:
            with open(self.StatisticsPath + self.LabID + ".stats", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")
        nOutages = nOutages.sort_index()
        self.nOutages = nOutages
        LabID = np.zeros((len(LabTemperature_stats),)).astype(str)
        LabID[:] = self.Building + "/" + self.Room
        self.LabEnv_nmonths = pd.DataFrame(np.array([LabAxesTime_stats, LabTemperature_stats, LabHumidity_stats, LabID]).transpose(), columns=["Time", "Temperature", "Humidity", "Lab"])

    def GenerateEnvCharts(self):
        if "pandas" in str(type(self.LabEnv)):
            self.TFigure = px.line(self.LabEnv, x="Time", y="Temperature", color="Lab")
            self.RHFigure = px.line(self.LabEnv, x="Time", y="Humidity", color="Lab")

            self.TFigure.update_layout(
                height=LEMASvar.interIMGHEIGHT,
                width=LEMASvar.interIMGWIDTH,
                template=LEMASvar.template,
                yaxis_title="Temperature (deg. C)",
                title="Laboratory "+self.Building+"/"+self.Room+" temperatures. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
            )
            self.RHFigure.update_layout(
                height=LEMASvar.interIMGHEIGHT,
                width=LEMASvar.interIMGWIDTH,
                template=LEMASvar.template,
                yaxis_title="Humidity (%RH)",
                title="Laboratory "+self.Building+"/"+self.Room+" for humidities. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
            )
            self.TFigure.layout.hovermode = LEMASvar.hovermode_lab
            self.RHFigure.layout.hovermode = LEMASvar.hovermode_lab

            currenttime = datetime.now().replace(microsecond=0)
            currenttime_past = currenttime - timedelta(hours=LEMASvar.graphtime)
            currenttime_past = currenttime_past.strftime("%Y-%m-%d %H:%M:%S")
            if self.LabEnv["Time"].to_numpy()[-1] >= currenttime_past:              # only execute if recent temperature is guaranteed to be within designated currentime_past
                self.TFigure.layout.xaxis.range = [currenttime_past, currenttime]
                self.RHFigure.layout.xaxis.range = [currenttime_past, currenttime]
                start = np.where(self.LabEnv["Time"] >= currenttime_past)[0][0]
                Tmin = float(self.LabEnv["Temperature"][start::].min())
                Tmax = float(self.LabEnv["Temperature"][start::].max())
                self.TFigure.layout.yaxis.range = [Tmin-LEMASvar.graphTmin, Tmax+LEMASvar.graphTmax]
                RHmin = float(self.LabEnv["Humidity"][start::].min())
                RHmax = float(self.LabEnv["Humidity"][start::].max())
                self.RHFigure.layout.yaxis.range = [RHmin-LEMASvar.graphRHmin, RHmax+LEMASvar.graphRHmax]

            plotly.offline.plot(self.TFigure, filename=self.Path + self.Building + "_" + self.Room + "-T.html", auto_open=False)
            plotly.offline.plot(self.RHFigure, filename=self.Path + self.Building + "_" + self.Room + "-RH.html", auto_open=False)
        else:
            with open(self.Path + self.Building + "_" + self.Room + "-T.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")
            with open(self.Path + self.Building + "_" + self.Room + "-RH.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")

    def GenerateHistograms(self):
        if "pandas" in str(type(self.LabEnv_nmonths)):
            self.THistogram = px.histogram(self.LabEnv_nmonths, x="Temperature", color="Lab", nbins=LEMASvar.nbinsT)
            self.RHHistogram = px.histogram(self.LabEnv_nmonths, x="Humidity", color="Lab", nbins=LEMASvar.nbinsRH)

            self.THistogram.update_layout(
                height=LEMASvar.interIMGHEIGHT,
                width=LEMASvar.interIMGWIDTH,
                template=LEMASvar.template,
                xaxis_title="Temperature (deg. C)",
                title="Laboratory "+self.Building+"/"+self.Room+" distribution of temperatures for past "+str(LEMASvar.nmonths)+" months. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
            )
            self.RHHistogram.update_layout(
                height=LEMASvar.interIMGHEIGHT,
                width=LEMASvar.interIMGWIDTH,
                template=LEMASvar.template,
                xaxis_title="Humidity (%RH)",
                title="Laboratory "+self.Building+"/"+self.Room+" distribution of humidities for past "+str(LEMASvar.nmonths)+" months. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
            )

            plotly.offline.plot(self.THistogram, filename=self.Path + self.Building + "_" + self.Room + "-Thist.html", auto_open=False)
            plotly.offline.plot(self.RHHistogram, filename=self.Path + self.Building + "_" + self.Room + "-RHhist.html", auto_open=False)
        else:
            with open(self.Path + self.Building + "_" + self.Room + "-Thist.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")
            with open(self.Path + self.Building + "_" + self.Room + "-RHhist.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")

    def GenerateOutageBars(self):
        if "pandas" in str(type(self.LabEnv_nmonths)):
            MonthYear = []
            for _, val in enumerate(self.nOutages.index):
                MonthYear.append(datetime.strftime(datetime.strptime(str(val), "%Y-%m"), "%B %Y"))

            self.OutageBars = go.Figure(data=[
                go.Bar(name="Humidity events", x=MonthYear, y=self.nOutages["nRHoutages"]),
                go.Bar(name="Temperature events", x=MonthYear, y=self.nOutages["nToutages"]),
                go.Bar(name="Combined (temperature and humidity) events", x=MonthYear, y=self.nOutages["nCombined"]),
            ])
            self.OutageBars.update_layout(
                height=LEMASvar.interIMGHEIGHT,
                width=LEMASvar.interIMGWIDTH,
                template=LEMASvar.template,
                title="Laboratory "+self.Building+"/"+self.Room+" events by month for past "+str(LEMASvar.nmonths)+" months. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
                barmode="stack",
            )

    def SaveOutageBars(self):
        if "pandas" in str(type(self.LabEnv_nmonths)):
            plotly.offline.plot(self.OutageBars, filename=self.Path + self.Building + "_" + self.Room + "-outages.html", auto_open=False)
        else:
            with open(self.Path + self.Building + "_" + self.Room + "-outages.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")

    def UpdateAll(self):
        paused = False
        while not paused:
            if self.ThreadEvent.isSet():
                paused = True
            else:
                self.GetRecentData()
                self.AnalyzeStatistics()
                self.GenerateEnvCharts()
                self.GenerateHistograms()
                self.GenerateOutageBars()
                self.SaveOutageBars()
                time.sleep(LEMASvar.TIMETOSLEEP)

    def StopThread(self):
        self.ThreadEvent.set()

    def StartThread(self):
        self.ThreadEvent.clear()
        self.UpdateThread = threading.Thread(target=self.UpdateAll)
        self.UpdateThread.start()

class Building():
    def __init__(self, Group, Building, ListLabsMonitored):
        super().__init__()

        # variables
        self.Building = Building
        self.Group = Group
        self.Path = WebBaseDir + self.Group + "/" + self.Building + "/"
        self.StatisticsPath = StatsDir
        self.MaxT = 0
        self.TimeMaxT = ""
        self.MaxTLab = ""
        self.MaxRH = 0
        self.TimeMaxRH = ""
        self.MaxRHLab = ""
        self.ThreadEvent = threading.Event()
        self.UpdateThread = threading.Thread(target=self.UpdateAll)
        self.nOutages = pd.DataFrame(np.array([[]]), columns=[])
        self.TFigure = ""
        self.RHFigure = ""
        self.OutageBars = ""

        # associate labs with this building
        self.Labs = {}
        _, nlabs = np.shape(ListLabsMonitored)
        for i in range(0, nlabs):
            lab = ListLabsMonitored[0, i]
            if lab.lstrip().rstrip() not in self.Labs.keys():
                matching = np.where(lab == ListLabsMonitored[0])[0]
                # LabsMonitored = ListLabsMonitored[0, matching]
                LabNamesMonitored = ListLabsMonitored[1, matching]
                self.Labs[lab.lstrip().rstrip()] = Lab(self.Group, self.Building, lab.lstrip().rstrip(), LabNamesMonitored)
        self.AnalyzeStatistics()

    def AnalyzeStatistics(self):
        for ilab, lab in enumerate(self.Labs.keys()):
            if self.Labs[lab].MaxT > self.MaxT:
                self.MaxT = self.Labs[lab].MaxT
                self.TimeMaxT = self.Labs[lab].TimeMaxT
                self.MaxTLab = lab

            if self.Labs[lab].MaxRH > self.MaxRH:
                self.MaxRH = self.Labs[lab].MaxRH
                self.TimeMaxRH = self.Labs[lab].TimeMaxRH
                self.MaxRHLab = lab

            if ilab == 0:
                nOutages = pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=[lab])
            else:
                nOutages = nOutages.append(pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=[lab]))

            nOutages.loc[lab]["nToutages"] = self.Labs[lab].nOutages["nToutages"].sum()
            nOutages.loc[lab]["nRHoutages"] = self.Labs[lab].nOutages["nRHoutages"].sum()
            nOutages.loc[lab]["nCombined"] = self.Labs[lab].nOutages["nCombined"].sum()
            nOutages.loc[lab]["nUnique"] = self.Labs[lab].nOutages["nUnique"].sum()

        if len(nOutages.index) > 0:                                             # if recent data exists for building
            with open(self.StatisticsPath + self.Building + ".stats", "w") as openedfile:
                openedfile.write('nToutages '+str(nOutages["nToutages"].sum())+'\n')
                openedfile.write('nRHoutages '+str(nOutages["nRHoutages"].sum())+'\n')
                openedfile.write('nComboOutages '+str(nOutages["nCombined"].sum())+'\n')
                openedfile.write('nUnique ' +str(nOutages["nUnique"].sum())+'\n')
                openedfile.write('maxT '+str(self.MaxT)+' deg. C &nbsp in &nbsp '+self.Building+'/'+self.MaxTLab+' &nbsp at &nbsp '+self.TimeMaxT+'\n')
                openedfile.write('maxRH '+str(self.MaxRH)+' %RH &nbsp &nbsp &nbsp in &nbsp '+self.Building+'/'+self.MaxRHLab+' &nbsp at &nbsp '+self.TimeMaxRH+'\n')
        else:
            with open(self.Path + self.Building + "-T.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")
            with open(self.Path + self.Building + "-RH.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")

        self.nOutages = nOutages

    def GetOutageDataFromPeriod(self, start, end):
        for ilab, lab in enumerate(self.Labs.keys()):
            self.Labs[lab].GetOutageDataFromPeriod(start, end)
            if ilab == 0:
                nOutages = pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=[lab])
            else:
                nOutages = nOutages.append(pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=[lab]))

            nOutages.loc[lab]["nToutages"] = self.Labs[lab].nOutages["nToutages"].sum()
            nOutages.loc[lab]["nRHoutages"] = self.Labs[lab].nOutages["nRHoutages"].sum()
            nOutages.loc[lab]["nCombined"] = self.Labs[lab].nOutages["nCombined"].sum()
            nOutages.loc[lab]["nUnique"] = self.Labs[lab].nOutages["nUnique"].sum()

        self.nOutages = nOutages

    def GenerateEnvCharts(self):
        self.TFigure = go.Figure()
        self.RHFigure = go.Figure()
        currenttime = datetime.now().replace(microsecond=0)
        currenttime_past = currenttime - timedelta(hours=LEMASvar.graphtime)
        currenttime_past = currenttime_past.strftime("%Y-%m-%d %H:%M:%S")
        for ilab, lab in enumerate(self.Labs.keys()):
            if "pandas" in str(type(self.Labs[lab].LabEnv)):
                self.TFigure.add_trace(
                    go.Scatter(x=self.Labs[lab].LabEnv["Time"], y=self.Labs[lab].LabEnv["Temperature"], name=self.Labs[lab].LabEnv["Lab"][0], mode="lines")
                )
                self.RHFigure.add_trace(
                    go.Scatter(x=self.Labs[lab].LabEnv["Time"], y=self.Labs[lab].LabEnv["Humidity"], name=self.Labs[lab].LabEnv["Lab"][0], mode="lines")
                )
                start = np.where(self.Labs[lab].LabEnv["Time"] >= currenttime_past)[0][0]
                if ilab == 0 or "Tmin" not in locals():
                    Tmin = float(self.Labs[lab].LabEnv["Temperature"][start::].min())
                    Tmax = float(self.Labs[lab].LabEnv["Temperature"][start::].max())
                    RHmin = float(self.Labs[lab].LabEnv["Humidity"][start::].min())
                    RHmax = float(self.Labs[lab].LabEnv["Humidity"][start::].max())
                if float(self.Labs[lab].LabEnv["Temperature"][start::].min()) < Tmin:
                    Tmin = float(self.Labs[lab].LabEnv["Temperature"][start::].min())
                if float(self.Labs[lab].LabEnv["Temperature"][start::].max()) > Tmax:
                    Tmax = float(self.Labs[lab].LabEnv["Temperature"][start::].max())
                if float(self.Labs[lab].LabEnv["Humidity"][start::].min()) < RHmin:
                    RHmin = float(self.Labs[lab].LabEnv["Humidity"][start::].min())
                if float(self.Labs[lab].LabEnv["Humidity"][start::].max()) > RHmax:
                    RHmax = float(self.Labs[lab].LabEnv["Humidity"][start::].max())

        if "Tmin" in locals():
            self.TFigure.layout.hovermode = LEMASvar.hovermode_building
            self.RHFigure.layout.hovermode = LEMASvar.hovermode_building
            self.TFigure.layout.xaxis.range = [currenttime_past, currenttime]
            self.RHFigure.layout.xaxis.range = [currenttime_past, currenttime]
            self.TFigure.layout.yaxis.range = [Tmin-LEMASvar.graphTmin, Tmax+LEMASvar.graphTmax]
            self.RHFigure.layout.yaxis.range = [RHmin-LEMASvar.graphRHmin, RHmax+LEMASvar.graphRHmax]

            self.TFigure.update_layout(
                height=LEMASvar.interIMGHEIGHT,
                width=LEMASvar.interIMGWIDTH,
                template=LEMASvar.template,
                yaxis_title="Temperature (deg. C)",
                title="Building " + self.Building + " temperatures. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
            )
            self.RHFigure.update_layout(
                height=LEMASvar.interIMGHEIGHT,
                width=LEMASvar.interIMGWIDTH,
                template=LEMASvar.template,
                yaxis_title="Humidity (%RH)",
                title="Building " + self.Building + " humidities. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
            )

            plotly.offline.plot(self.TFigure, filename=self.Path + self.Building + "-T.html", auto_open=False)
            plotly.offline.plot(self.RHFigure, filename=self.Path + self.Building + "-RH.html", auto_open=False)
        else:
            with open(self.Path + self.Building + "-T.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")
            with open(self.Path + self.Building + "-RH.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")

    def GenerateOutageBars(self):
        Labs = []
        for _, val in enumerate(self.nOutages.index):
            Labs.append("Room"+str(val))

        self.OutageBars = go.Figure(data=[
            go.Bar(name="Humidity events", x=Labs, y=self.nOutages["nRHoutages"]),
            go.Bar(name="Temperature events", x=Labs, y=self.nOutages["nToutages"]),
            go.Bar(name="Combined (temperature and humidity) events", x=Labs, y=self.nOutages["nCombined"]),
        ])

        self.OutageBars.update_layout(
            height=LEMASvar.interIMGHEIGHT,
            width=LEMASvar.interIMGWIDTH,
            template=LEMASvar.template,
            title="Building "+self.Building+" events by lab for past "+str(LEMASvar.nmonths)+" months. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
            barmode="stack",
        )

    def SaveOutageBars(self):
        plotly.offline.plot(self.OutageBars, filename=self.Path + self.Building + "-outages.html", auto_open=False)

    def UpdateAll(self):
        paused = False
        while not paused:
            if self.ThreadEvent.isSet():
                paused = True
            else:
                self.AnalyzeStatistics()
                self.GenerateEnvCharts()
                self.GenerateOutageBars()
                self.SaveOutageBars()
                time.sleep(LEMASvar.TIMETOSLEEP)

    def StopThread(self):
        self.ThreadEvent.set()

    def StartThread(self):
        self.ThreadEvent.clear()
        self.UpdateThread = threading.Thread(target=self.UpdateAll)
        self.UpdateThread.start()

class Group():
    def __init__(self, Group, ListLabsMonitored):
        super().__init__()

        # variables
        self.Group = Group.replace(" ", "")
        self.GroupNumber = Group.split(" ")[-1]
        self.Path = WebBaseDir + self.Group + "/"
        self.StatisticsPath = StatsDir
        self.MaxT = 0
        self.TimeMaxT = ""
        self.MaxTLab = ""
        self.MaxRH = 0
        self.TimeMaxRH = ""
        self.MaxRHLab = ""
        self.ThreadEvent = threading.Event()
        self.UpdateThread = threading.Thread(target=self.UpdateAll)
        self.nOutages = pd.DataFrame(np.array([[]]), columns=[])
        self.TFigure = ""
        self.RHFigure = ""
        self.OutageBars = ""

        # associate buildings with this group
        self.Buildings = {}
        _, nlabs = np.shape(ListLabsMonitored)
        for i in range(0, nlabs):
            building = ListLabsMonitored[0, i]
            if building.lstrip().rstrip() not in self.Buildings.keys():
                matching = np.where(building == ListLabsMonitored[0])[0]
                LabsMonitored = ListLabsMonitored[1, matching]
                LabNamesMonitored = ListLabsMonitored[2, matching]
                AllData = np.vstack([LabsMonitored, LabNamesMonitored])
                self.Buildings[building.lstrip().rstrip()] = Building(self.Group, building.lstrip().rstrip(), AllData)

    def AnalyzeStatistics(self):
        for ibuilding, building in enumerate(self.Buildings.keys()):
            if self.Buildings[building].MaxT > self.MaxT:
                self.MaxT = self.Buildings[building].MaxT
                self.TimeMaxT = self.Buildings[building].TimeMaxT
                self.MaxTLab = building + "/" + self.Buildings[building].MaxTLab

            if self.Buildings[building].MaxRH > self.MaxRH:
                self.MaxRH = self.Buildings[building].MaxRH
                self.TimeMaxRH = self.Buildings[building].TimeMaxRH
                self.MaxRHLab = building + "/" + self.Buildings[building].MaxRHLab

            if ibuilding == 0:
                nOutages = pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=[building])
            else:
                nOutages = nOutages.append(pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=[building]))
            nOutages.loc[building]["nToutages"] = self.Buildings[building].nOutages["nToutages"].sum()
            nOutages.loc[building]["nRHoutages"] = self.Buildings[building].nOutages["nRHoutages"].sum()
            nOutages.loc[building]["nCombined"] = self.Buildings[building].nOutages["nCombined"].sum()
            nOutages.loc[building]["nUnique"] = self.Buildings[building].nOutages["nUnique"].sum()

        if len(nOutages.index) > 0:                                             # if recent data exists for building
            with open(self.StatisticsPath + self.Group + ".stats", "w") as openedfile:
                openedfile.write('nToutages '+str(nOutages["nToutages"].sum())+'\n')
                openedfile.write('nRHoutages '+str(nOutages["nRHoutages"].sum())+'\n')
                openedfile.write('nComboOutages '+str(nOutages["nCombined"].sum())+'\n')
                openedfile.write('nUnique ' +str(nOutages["nUnique"].sum())+'\n')
                openedfile.write('maxT '+str(self.MaxT)+' deg. C &nbsp in &nbsp '+self.MaxTLab+' &nbsp at &nbsp '+self.TimeMaxT+'\n')
                openedfile.write('maxRH '+str(self.MaxRH)+' %RH &nbsp &nbsp &nbsp in &nbsp '+self.MaxRHLab+' &nbsp at &nbsp '+self.TimeMaxRH+'\n')
        else:
            with open(self.Path + self.Group + "-T.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")
            with open(self.Path + self.Group + "-RH.html", "w") as openedfile:
                openedfile.write("<h3>No data available</h3>")

        self.nOutages = nOutages

    def GetOutageDataFromPeriod(self, start, stop):
        for ibuilding, building in enumerate(self.Buildings.keys()):
            self.Buildings[building].GetOutageDataFromPeriod(start, stop)

            if ibuilding == 0:
                nOutages = pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=[building])
            else:
                nOutages = nOutages.append(pd.DataFrame(np.array([[0, 0, 0, 0]]), columns=["nToutages", "nRHoutages", "nCombined", "nUnique"], index=[building]))
            nOutages.loc[building]["nToutages"] = self.Buildings[building].nOutages["nToutages"].sum()
            nOutages.loc[building]["nRHoutages"] = self.Buildings[building].nOutages["nRHoutages"].sum()
            nOutages.loc[building]["nCombined"] = self.Buildings[building].nOutages["nCombined"].sum()
            nOutages.loc[building]["nUnique"] = self.Buildings[building].nOutages["nUnique"].sum()

        self.nOutages = nOutages

    def GenerateEnvCharts(self):
        self.TFigure = go.Figure()
        self.RHFigure = go.Figure()
        currenttime = datetime.now().replace(microsecond=0)
        currenttime_past = currenttime - timedelta(hours=LEMASvar.graphtime)
        currenttime_past = currenttime_past.strftime("%Y-%m-%d %H:%M:%S")
        for ibuilding, building in enumerate(self.Buildings.keys()):
            for ilab, lab in enumerate(self.Buildings[building].Labs.keys()):
                if "pandas" in str(type(self.Buildings[building].Labs[lab].LabEnv)):
                    self.TFigure.add_trace(
                        go.Scatter(x=self.Buildings[building].Labs[lab].LabEnv["Time"], y=self.Buildings[building].Labs[lab].LabEnv["Temperature"], name=self.Buildings[building].Labs[lab].LabEnv["Lab"][0], mode="lines")
                    )
                    self.RHFigure.add_trace(
                        go.Scatter(x=self.Buildings[building].Labs[lab].LabEnv["Time"], y=self.Buildings[building].Labs[lab].LabEnv["Humidity"], name=self.Buildings[building].Labs[lab].LabEnv["Lab"][0], mode="lines")
                    )
                    start = np.where(self.Buildings[building].Labs[lab].LabEnv["Time"] >= currenttime_past)[0][0]
                    if (ilab == 0 and ibuilding == 0) or "Tmin" not in locals():
                        Tmin = float(self.Buildings[building].Labs[lab].LabEnv["Temperature"][start::].min())
                        Tmax = float(self.Buildings[building].Labs[lab].LabEnv["Temperature"][start::].max())
                        RHmin = float(self.Buildings[building].Labs[lab].LabEnv["Humidity"][start::].min())
                        RHmax = float(self.Buildings[building].Labs[lab].LabEnv["Humidity"][start::].max())
                    if float(self.Buildings[building].Labs[lab].LabEnv["Temperature"][start::].min()) < Tmin:
                        Tmin = float(self.Buildings[building].Labs[lab].LabEnv["Temperature"][start::].min())
                    if float(self.Buildings[building].Labs[lab].LabEnv["Temperature"][start::].max()) > Tmax:
                        Tmax = float(self.Buildings[building].Labs[lab].LabEnv["Temperature"][start::].max())
                    if float(self.Buildings[building].Labs[lab].LabEnv["Humidity"][start::].min()) < RHmin:
                        RHmin = float(self.Buildings[building].Labs[lab].LabEnv["Humidity"][start::].min())
                    if float(self.Buildings[building].Labs[lab].LabEnv["Humidity"][start::].max()) > RHmax:
                        RHmax = float(self.Buildings[building].Labs[lab].LabEnv["Humidity"][start::].max())

        self.TFigure.layout.hovermode = LEMASvar.hovermode_group
        self.RHFigure.layout.hovermode = LEMASvar.hovermode_group
        self.TFigure.layout.xaxis.range = [currenttime_past, currenttime]
        self.RHFigure.layout.xaxis.range = [currenttime_past, currenttime]
        self.TFigure.layout.yaxis.range = [Tmin-LEMASvar.graphTmin, Tmax+LEMASvar.graphTmax]
        self.RHFigure.layout.yaxis.range = [RHmin-LEMASvar.graphRHmin, RHmax+LEMASvar.graphRHmax]

        self.TFigure.update_layout(
            height=LEMASvar.interIMGHEIGHT,
            width=LEMASvar.interIMGWIDTH,
            template=LEMASvar.template,
            yaxis_title="Temperature (deg. C)",
            title="Group " + self.GroupNumber + " temperatures. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
        )
        self.RHFigure.update_layout(
            height=LEMASvar.interIMGHEIGHT,
            width=LEMASvar.interIMGWIDTH,
            template=LEMASvar.template,
            yaxis_title="Humidity (%RH)",
            title="Group " + self.GroupNumber + " humidities. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
        )

        plotly.offline.plot(self.TFigure, filename=self.Path + self.Group + "-T.html", auto_open=False)
        plotly.offline.plot(self.RHFigure, filename=self.Path + self.Group + "-RH.html", auto_open=False)

    def GenerateOutageBars(self):
        Building = []
        for _, val in enumerate(self.nOutages.index):
            Building.append("Building "+str(val))

        self.OutageBars = go.Figure(data=[
            go.Bar(name="Humidity events", x=Building, y=self.nOutages["nRHoutages"]),
            go.Bar(name="Temperature events", x=Building, y=self.nOutages["nToutages"]),
            go.Bar(name="Combined (temperature and humidity) events", x=Building, y=self.nOutages["nCombined"]),
        ])

        self.OutageBars.update_layout(
            height=LEMASvar.interIMGHEIGHT,
            width=LEMASvar.interIMGWIDTH,
            template=LEMASvar.template,
            title="Group "+self.GroupNumber+" events by building for past "+str(LEMASvar.nmonths)+" months. Generated on " + datetime.strftime(datetime.now(), "%d %B, %Y at %H:%M"),
            barmode="stack",
        )

    def SaveOutageBars(self):
        plotly.offline.plot(self.OutageBars, filename=self.Path + self.Group + "-outages.html", auto_open=False)

    def UpdateAll(self):
        paused = False
        while not paused:
            if self.ThreadEvent.isSet():
                paused = True
            else:
                self.AnalyzeStatistics()
                self.GenerateEnvCharts()
                self.GenerateOutageBars()
                self.SaveOutageBars()
                time.sleep(LEMASvar.TIMETOSLEEP)

    def StopAllThreads(self):
        for _, building in enumerate(self.Buildings.keys()):
            for _, lab in enumerate(self.Buildings[building].Labs.keys()):
                self.Buildings[building].Labs[lab].StopThread()
            self.Buildings[building].StopThread()
        self.ThreadEvent.set()

    def StartAllThreads(self):
        for _, building in enumerate(self.Buildings.keys()):
            for _, lab in enumerate(self.Buildings[building].Labs.keys()):
                self.Buildings[building].Labs[lab].StartThread()
            self.Buildings[building].StartThread()
        self.ThreadEvent.clear()
        self.UpdateThread = threading.Thread(target=self.UpdateAll)
        self.UpdateThread.start()

def CreateGroup(GroupAndNumber, LabsMonitoredFilename):
    GroupAndNumber = GroupAndNumber.rstrip(" ").lstrip(" ")
    if "Group " not in GroupAndNumber:
        GroupAndNumber = "Group "+GroupAndNumber
    GroupNumber = GroupAndNumber.split(" ")[-1]
    with open(LabsMonitoredFilename, "r") as openedfile:
        data = list(zip(*csv.reader(openedfile)))
    AllGroups = np.array(data[0])
    AllBuildings = np.array(data[1])
    AllLabs = np.array(data[2])
    AllLabNames = np.array(data[3])

    matching = np.where(GroupNumber == AllGroups)[0]
    BuildingsMonitored = AllBuildings[matching]
    LabsMonitored = AllLabs[matching]
    LabNamesMonitored = AllLabNames[matching]
    AllData = np.vstack([BuildingsMonitored, LabsMonitored, LabNamesMonitored])

    return Group(GroupAndNumber, AllData)
