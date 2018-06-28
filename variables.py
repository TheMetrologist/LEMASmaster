#///////////////////////////////bash Variables\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#amount of time to wait before rebuilding website, seconds
TIMETOSLEEP=300
#width of graphs, pixels
statIMGWIDTH=960
#height of graphs, pixels
statIMGHEIGHT=540


#/////////////////////////////python Variables\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#amount of time before considering a unique outage has occurred, hours
normal_period=12
#fontsize of x-tick labels, matplotlib
fontsizeXticks=12
#fontsize of y-tick labels, matplotlib
fontsizeYticks=12
#fontsize of title, matplotlib
fontsizetitle=16
#fontsize of x-tick labels, bokeh
fontsizeXticks_inter='12pt'
#fontsize of y-tick labels, bokeh
fontsizeYticks_inter='12pt'
#fontsize of title, bokeh
fontsizetitle_inter='16pt'
#distance between ticks, hours
tickspacing_time=2
#how far below minimimum/maximum temperature to graph, deg. C
graphTmin=0.5
graphTmax=0.5
#how far below minimimum/maximum humidity to graph, %RH
graphRHmin=5
graphRHmax=5
#linewidth of temperature/humidity graphs
graphLinewidth=2.0
#width of bar graphs
graphBarwidth=0.5
#dpi of graphs, keep at 100 ti maintain 1 inch:100 pixels
dpi_set=100
#number of bins for temperature/humidity histograms
nbinsT=40
nbinsRH=100
#horizontal tick spacing for temperature histogram, deg. C
tickspacing_T=0.2
#horizontal tick spacing for humidity histogram, %RH
tickspacing_RH=1.0
#mode selection for Bokeh hover tool of graphs with multiple sets: vline, hline or mouse
hmode='mouse'
#mode selection for Bokeh hover tool of lab graphs: vline, hline or mouse
Lhmode='vline'
#width of graphs, pixels
interIMGWIDTH=1200
#height of graphs, pixels
interIMGHEIGHT=720
#tools to use in bokeh interactive graphs
bokehtools=['pan, wheel_zoom, hover, save, reset']

#///////////////////////python and bash Variables\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#number of months into past to get data for statistics
nmonths=6
#amount of time into the past to display initial environment data, hours
graphtime=72
#amount of time into the past to graph additional environment data, hours
#caution: do not go back more than 3 weeks. 1) risk of slow graphs 2) python analysis will probably break
inter_time=336
