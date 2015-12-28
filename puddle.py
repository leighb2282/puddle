#!/usr/bin/env python
# puddle.py
# Simple Weather App
# Version v00.00.26
# Sun 22 Nov 2015 17:08:29 
# Leigh Burton, lburton@metacache.net


import sys
import urllib2
from xml.dom.minidom import parse
import xml.dom.minidom
import os.path
import wx
import webbrowser


from ConfigParser import SafeConfigParser

day_button = "res/day_button.png"
week_button = "res/week_button.png"
settings_button = "res/settings_button.png"
refresh_button = "res/refresh_button.png"
appicon = "res/ficon.ico"
conffile = "res/config.ini"
wunderlogo = "res/wlogo.png"
puddlelogo = "res/plogo.png"
vinfo = "v00.00.26"
usezip = ""
usecity = ""
zippy1 = ""
zippy2 = ""
zippy3 = ""
zippy1def = ""
zippy2def = ""
zippy3def = ""
apikey = ""
emailer = ""
city1 = ""
city2 = ""
city3 = ""
apistring = "http://api"
apistring_hourly = "http://api"
apistring_10day = "http://api"

##############################
# Default Locations Settings #
##############################
try:
    config = SafeConfigParser()
    config.read(conffile)

    apikey = config.get('main', 'apikey')
    zippy1def = config.get('main', 'location_1')
    zippy2def = config.get('main', 'location_2')
    zippy3def = config.get('main', 'location_3')
    emailer = config.get('main', 'email')

    # Location 1
    zippy1 = zippy1def
    namechk1 = zippy1 + ".xml"
    # Location 2
    zippy2 = zippy2def
    namechk2 = zippy2 + ".xml"
    # Location 3
    zippy3 = zippy3def
    namechk3 = zippy3 + ".xml"

    apistring = "http://api.wunderground.com/api/" + apikey + "/conditions/lang:EN/q/"
    apistring_hourly = "http://api.wunderground.com/api/" + apikey + "/hourly/lang:EN/q/"
    apistring_10day = "http://api.wunderground.com/api/" + apikey + "/forecast10day/lang:EN/q/"

except:
    print "Issue with Config file, no defaults loaded."    

def main():
    """ Main entry point for the script."""
    global apifetch
    global namechk


    #####################
    # Preferences Frame #
    #####################
    class PreferenceFrame(wx.Frame):

        ''' PreferenceFrame launched from puddle '''
        def __init__(self, parent, id):
            wx.Frame.__init__(self, parent, -1,
                              title="Puddle Preferences",
                              style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
            self.picon = wx.Icon(appicon, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.picon)
            panel = wx.Panel(self,wx.ID_ANY)

            self.apilabel = wx.StaticText(panel, label="API Key: ") # API Label
            self.apibox = wx.TextCtrl(panel, style=wx.TE_LEFT,) # API Textbox

            self.loc1label = wx.StaticText(panel, label="Location 1: ") # Location 1 Label
            self.loc1box = wx.TextCtrl(panel, style=wx.TE_LEFT) # Location 1 Textbox
            self.l1usecur_check = wx.CheckBox(panel, label="Use Current                ")

            self.loc2label = wx.StaticText(panel, label="Location 2: ") # Location 2 Label
            self.loc2box = wx.TextCtrl(panel, style=wx.TE_LEFT) # Location 2 Textbox
            self.l2usecur_check = wx.CheckBox(panel, label="Use Current                ")

            self.loc3label = wx.StaticText(panel, label="Location 3: ") # Location 3 Label
            self.loc3box = wx.TextCtrl(panel, style=wx.TE_LEFT,) # Location 3 Textbox
            self.l3usecur_check = wx.CheckBox(panel, label="Use Current                ")

            self.emaillabel = wx.StaticText(panel, label="Email: ") # Email Label
            self.emailbox = wx.TextCtrl(panel, style=wx.TE_LEFT) # Email Textbox
            self.emailcheck = wx.CheckBox(panel, label="Activate")

            self.applyButton = wx.Button(panel, label="Apply")
            self.cancelButton = wx.Button(panel, label="Cancel")

            self.Bind(wx.EVT_BUTTON, self.onApply, self.applyButton)
            self.Bind(wx.EVT_BUTTON, self.onClose, self.cancelButton)
            self.Bind(wx.EVT_CLOSE, self.onClose)

            self.Bind(wx.EVT_CHECKBOX, self.onCheck1, self.l1usecur_check)
            self.Bind(wx.EVT_CHECKBOX, self.onCheck2, self.l2usecur_check)
            self.Bind(wx.EVT_CHECKBOX, self.onCheck3, self.l3usecur_check)

            #Sizers!
            topSizer        = wx.BoxSizer(wx.VERTICAL)
            apiSizer      = wx.BoxSizer(wx.HORIZONTAL)
            loc1Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc2Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            loc3Sizer   = wx.BoxSizer(wx.HORIZONTAL)
            emailSizer   = wx.BoxSizer(wx.HORIZONTAL)
            btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

            apiSizer.Add(self.apilabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            apiSizer.Add(self.apibox, 1, wx.ALL|wx.EXPAND, 2)

            loc1Sizer.Add(self.loc1label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            loc1Sizer.Add(self.loc1box, 1, wx.ALL|wx.EXPAND, 2)
            loc1Sizer.Add(self.l1usecur_check, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

            loc2Sizer.Add(self.loc2label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            loc2Sizer.Add(self.loc2box, 1, wx.ALL|wx.EXPAND, 2)
            loc2Sizer.Add(self.l2usecur_check, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

            loc3Sizer.Add(self.loc3label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            loc3Sizer.Add(self.loc3box, 1, wx.ALL|wx.EXPAND, 2)
            loc3Sizer.Add(self.l3usecur_check, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

            emailSizer.Add(self.emaillabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
            emailSizer.Add(self.emailbox, 1, wx.ALL|wx.EXPAND, 2)
            emailSizer.Add(self.emailcheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

            btnSizer.Add(self.applyButton, 0, wx.ALL, 2)
            btnSizer.Add(self.cancelButton, 0, wx.ALL, 2)

            topSizer.Add(apiSizer, 0, wx.ALL|wx.EXPAND, 4)
            topSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(loc1Sizer, 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(loc2Sizer, 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(loc3Sizer, 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(emailSizer, 0, wx.ALL|wx.EXPAND, 4)
            topSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(btnSizer, 0, wx.ALL|wx.CENTER, 5)

            panel.SetSizer(topSizer)
            topSizer.Fit(self)

            self.apibox.SetValue(apikey)
            self.loc1box.SetValue(str(zippy1def))
            self.loc2box.SetValue(str(zippy2def))
            self.loc3box.SetValue(str(zippy3def))
            self.emailbox.SetValue(emailer)

            # Disabled controls because no functionality... yet!
            if zippy1def == zippy1:
                self.l1usecur_check.Enable(False)
            if zippy2def == zippy2:
                self.l2usecur_check.Enable(False)
            if zippy3def == zippy3:
                self.l3usecur_check.Enable(False)
            self.emailbox.Enable(False)
            self.emailcheck.Enable(False)

            self.CenterOnParent()
            self.GetParent().Enable(False)
            self.Show(True)

            self.__eventLoop = wx.EventLoop()
            self.__eventLoop.Run()

        def onClose(self, event):
            self.GetParent().Enable(True)
            self.__eventLoop.Exit()
            self.Destroy()

        def onCheck1(self, event):
            self.loc1box.SetValue(str(zippy1def))
            l1_status = self.l1usecur_check.GetValue()
            if l1_status == True:
                self.loc1box.SetValue(str(zippy1))
            elif l1_status == False:
                self.loc1box.SetValue(str(zippy1def))

        def onCheck2(self, event):
            self.loc2box.SetValue(str(zippy2def))
            l2_status = self.l2usecur_check.GetValue()
            if l2_status == True:
                self.loc2box.SetValue(str(zippy2))
            elif l2_status == False:
                self.loc2box.SetValue(str(zippy2def))

        def onCheck3(self, event):
            self.loc3box.SetValue(str(zippy3def))
            l3_status = self.l3usecur_check.GetValue()
            if l3_status == True:
                self.loc3box.SetValue(str(zippy3))
            elif l3_status == False:
                self.loc3box.SetValue(str(zippy3def))

        def onApply(self, event):
            global apikey
            global zippy1def
            global zippy2def
            global zippy3def
            global emailer
            global apistring
            global conffile

            apikey = self.apibox.GetValue()
            zippy1def = self.loc1box.GetValue()
            zippy2def = self.loc2box.GetValue()
            zippy3def = self.loc3box.GetValue()
            emailer = self.emailbox.GetValue()
            apistring = "http://api.wunderground.com/api/" + apikey + "/conditions/lang:EN/q/"
            
            try:
                os.remove(conffile)
            except:
                print "No previous config file, creating new one."

            config = SafeConfigParser()
            config.read(conffile)
            config.add_section('main')
            config.set('main', 'apikey', apikey)
            config.set('main', 'location_1', zippy1def)
            config.set('main', 'location_2', zippy2def)
            config.set('main', 'location_3', zippy3def)
            config.set('main', 'email', emailer)
            
            with open(conffile, 'w') as f:
                config.write(f)
            self.GetParent().Enable(True)
            self.__eventLoop.Exit()
            self.Destroy()

    #####################
    # About Frame #
    #####################
    class AboutFrame(wx.Frame):
        ''' AboutFrame launched from puddle '''
        def __init__(self, parent, id):
            wx.Frame.__init__(self, parent, -1,
                              title="About Puddle",
                              style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
            self.picon = wx.Icon(appicon, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.picon)
            panel = wx.Panel(self, -1)
            plogo = wx.EmptyImage(64,64)
            plogo = wx.Image(puddlelogo, wx.BITMAP_TYPE_PNG)
            self.pudd = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(plogo))

            self.titlelabel = wx.StaticText(panel, label="Puddle " + vinfo)
            titleFont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
            self.titlelabel.SetFont(titleFont)

            self.blurb1label = wx.StaticText(panel, label=" Puddle is a simple weather broadcast application. ")
            self.blurb2label = wx.StaticText(panel, label="Uses Weather Underground API data.") # blurb1 Label
            blurbFont = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
            self.blurb1label.SetFont(blurbFont)
            self.blurb2label.SetFont(blurbFont)

            self.copyrlabel = wx.StaticText(panel, label="Copyright 2015 Leigh Burton") # copyright Label
            copyFont = wx.Font(8, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
            self.copyrlabel.SetFont(copyFont)

            #Weather Underground Logo
            wlogo = wx.EmptyImage(200,47)
            wlogo = wx.Image(wunderlogo, wx.BITMAP_TYPE_PNG)
            self.wunder = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(wlogo))
            self.wunderclabel = wx.StaticText(panel, label="Weather Underground is a registered trademark of The Weather Channel,\nLLC. both in the United States and internationally.\nThe Weather Underground Logo is a trademark of Weather Underground, LLC.")
            self.wunderclabel.SetFont(copyFont)
            self.closeButton = wx.Button(panel, label="Close", pos=(210, 235))

            self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
            self.Bind(wx.EVT_CLOSE, self.onClose) # (Allows frame's title-bar close to work)

            topSizer        = wx.BoxSizer(wx.VERTICAL)
            iconSizer      = wx.BoxSizer(wx.HORIZONTAL)
            appverSizer   = wx.BoxSizer(wx.HORIZONTAL)
            blurb1Sizer   = wx.BoxSizer(wx.VERTICAL)
            blurb2Sizer   = wx.BoxSizer(wx.VERTICAL)
            copySizer   = wx.BoxSizer(wx.HORIZONTAL)
            wunderSizer   = wx.BoxSizer(wx.HORIZONTAL)
            wundercSizer   = wx.BoxSizer(wx.HORIZONTAL)
            btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

            iconSizer.Add(self.pudd, 0, wx.ALL, 5)
            appverSizer.Add(self.titlelabel, 0, wx.ALL, 5)
            blurb1Sizer.Add(self.blurb1label, 0, wx.ALL, 0)
            blurb2Sizer.Add(self.blurb2label, 0, wx.ALL, 0)
            copySizer.Add(self.copyrlabel, 0, wx.ALL, 5)
            wunderSizer.Add(self.wunder, 0, wx.ALL, 5)
            wundercSizer.Add(self.wunderclabel, 0, wx.ALL, 5)
            btnSizer.Add(self.closeButton, 0, wx.ALL, 5)

            topSizer.Add(iconSizer, 0, wx.CENTER)
            topSizer.Add(appverSizer, 0, wx.CENTER, 5)
            topSizer.Add(blurb1Sizer, 0, wx.CENTER, 5)
            topSizer.Add(blurb2Sizer, 0, wx.CENTER, 5)
            topSizer.Add(copySizer, 0, wx.CENTER, 5)
            topSizer.Add(wunderSizer, 0, wx.LEFT, 5)
            topSizer.Add(wundercSizer, 0, wx.LEFT, 5)
            topSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT, 5)

            panel.SetSizer(topSizer)
            topSizer.Fit(self)

            self.CenterOnParent()
            self.GetParent().Enable(False)
            self.Show(True)

            self.__eventLoop = wx.EventLoop()
            self.__eventLoop.Run()

        def onClose(self, event):
            self.GetParent().Enable(True)
            self.__eventLoop.Exit()
            self.Destroy()

    #####################
    # Hourly Frame #
    #####################
    class HourlyFrame(wx.Frame):
        ''' AboutFrame launched from puddle '''
        def __init__(self, parent, id):
            global usezip
            global usecity
            wx.Frame.__init__(self, parent, -1,
                              title="Puddle: 10 hour forecast for " + usezip,
                              style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
            self.picon = wx.Icon(appicon, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.picon)
            panel = wx.Panel(self, -1)

            topSizer        = wx.BoxSizer(wx.VERTICAL)
            colSizer        = wx.BoxSizer(wx.HORIZONTAL)
            hourSizer        = wx.BoxSizer(wx.VERTICAL)
            condSizer        = wx.BoxSizer(wx.VERTICAL)
            tempSizer        = wx.BoxSizer(wx.VERTICAL)
            windSizer        = wx.BoxSizer(wx.VERTICAL)
            humSizer        = wx.BoxSizer(wx.VERTICAL)

            coltoppersFont = wx.Font(8, wx.DECORATIVE, wx.NORMAL, wx.BOLD)

            self.hourlabel = wx.StaticText(panel, label="Time (Local)")
            self.hourlabel.SetFont(coltoppersFont)

            self.templabel = wx.StaticText(panel, label="Temperatures")
            self.templabel.SetFont(coltoppersFont)

            self.condlabel = wx.StaticText(panel, label="Conditions")
            self.condlabel.SetFont(coltoppersFont)

            self.windlabel = wx.StaticText(panel, label="Wind")
            self.windlabel.SetFont(coltoppersFont)

            self.humlabel = wx.StaticText(panel, label="Humidity")
            self.humlabel.SetFont(coltoppersFont)

            hourSizer.Add(self.hourlabel, 0, wx.LEFT, 5)
            condSizer.Add(self.condlabel, 0, wx.LEFT, 5)
            tempSizer.Add(self.templabel, 0, wx.LEFT, 5)
            windSizer.Add(self.windlabel, 0, wx.LEFT, 5)
            humSizer.Add(self.humlabel, 0, wx.LEFT, 5)

            hourSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
            condSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
            tempSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
            windSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
            humSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)

            try:
                DOMTree = xml.dom.minidom.parse("datafile_hourly.xml")
                api_hourlydata = DOMTree.documentElement
                
                apideets = api_hourlydata.getElementsByTagName("forecast")
                i = 0
                for apidet in apideets:
                        if i == 10:
                            break
                        apihour = apidet.getElementsByTagName('civil')[0]
                        apimon = apidet.getElementsByTagName('mon_abbrev')[0]
                        apiday = apidet.getElementsByTagName('mday')[0]
                        apitempf = apidet.getElementsByTagName('english')[0]
                        apitempc = apidet.getElementsByTagName('metric')[0]
                        apiwspdm = apidet.getElementsByTagName('english')[2]
                        apicond = apidet.getElementsByTagName('condition')[0]
                        apihum = apidet.getElementsByTagName('humidity')[0]
                        apiwdir = apidet.getElementsByTagName('dir')[0]

                        hour = apihour.childNodes[0].data + " " + apimon.childNodes[0].data + " " + apiday.childNodes[0].data
                        cond = apicond.childNodes[0].data
                        temp = apitempf.childNodes[0].data + " F (" + apitempc.childNodes[0].data + " C)"
                        wind = apiwdir.childNodes[0].data + " at " + apiwspdm.childNodes[0].data + "MPH"
                        hum = apihum.childNodes[0].data + "%"
                        self.lblhour= wx.StaticText(panel, label=hour)
                        self.lblcond= wx.StaticText(panel, label=cond)
                        self.lbltemp= wx.StaticText(panel, label=temp)
                        self.lblwind= wx.StaticText(panel, label=wind)
                        self.lblhum= wx.StaticText(panel, label=hum)

                        hourSizer.Add(self.lblhour, 0, wx.LEFT, 5)
                        hourSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
                        condSizer.Add(self.lblcond, 0, wx.LEFT, 5)
                        condSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
                        tempSizer.Add(self.lbltemp, 0, wx.LEFT, 5)
                        tempSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
                        windSizer.Add(self.lblwind, 0, wx.LEFT, 5)
                        windSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
                        humSizer.Add(self.lblhum, 0, wx.LEFT, 5)
                        humSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
                        i = i + 1
            except:
                print "HOURLY HOSED!"
            os.remove("datafile_hourly.xml")

            self.titlelabel = wx.StaticText(panel, label=usecity + " (" + usezip + ") 10 hour forecast")
            titleFont = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
            self.titlelabel.SetFont(titleFont)

            self.closeButton = wx.Button(panel, label="Close")

            self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
            self.Bind(wx.EVT_CLOSE, self.onClose) # (Allows frame's title-bar close to work)

            topSizer.Add(self.titlelabel, 0, wx.LEFT, 7)
            colSizer.Add(hourSizer, 1, wx.LEFT, 5)
            colSizer.Add(condSizer, 1, wx.LEFT, 5)
            colSizer.Add(tempSizer, 1, wx.LEFT, 5)
            colSizer.Add(windSizer, 1, wx.LEFT, 5)
            colSizer.Add(humSizer, 1, wx.LEFT, 5)
            topSizer.Add(colSizer, 1, wx.LEFT|wx.EXPAND, 5)
            topSizer.Add(self.closeButton, 0, wx.RIGHT, 5)
            panel.SetSizer(topSizer)
            topSizer.Fit(self)

            self.CenterOnParent()
            self.GetParent().Enable(False)
            self.Show(True)

            self.__eventLoop = wx.EventLoop()
            self.__eventLoop.Run()

        def onClose(self, event):
            self.GetParent().Enable(True)
            self.__eventLoop.Exit()
            self.Destroy()

    # Start of GUI happiness

    #####################
    # Main App Frame    #
    #####################
    class puddle(wx.Frame):
        def __init__(self, parent, title):
            global apifetch
            global namechk
            refresher = wx.Image(refresh_button, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            settings = wx.Image(settings_button, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            dayer = wx.Image(day_button, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            weeker = wx.Image(week_button, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

            wx.Frame.__init__(self, parent, title=title, size=(460,380), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER) # Init the frame with a size of 460x300 pixels.
            self.Bind(wx.EVT_CLOSE, self.OnClose)
            menuBar = wx.MenuBar()
            self.ficon = wx.Icon(appicon, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.ficon)

            # Define the File Menu.
            f_menu = wx.Menu()    
            self.m_exit = f_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")         
            self.Bind(wx.EVT_MENU, self.OnClose, self.m_exit)
            menuBar.Append(f_menu, "&File")

            # Define the Edit Menu
            e_menu = wx.Menu()    
            self.e_pref = e_menu.Append(wx.ID_PROPERTIES, "&Preferences", "Set Puddle Preferences.")
            self.e_default = e_menu.Append(wx.ID_REFRESH, "&Default Locations", "Return to Default View.")
            self.Bind(wx.EVT_MENU, self.OnEditPref, self.e_pref)
            self.Bind(wx.EVT_MENU, self.OnEditDef, self.e_default)
            menuBar.Append(e_menu, "&Edit")
  
            # Define the Help Menu
            h_menu = wx.Menu()    
            self.e_about = h_menu.Append(wx.ID_ABOUT, "About", "About Puddle.")
            self.e_faq = h_menu.Append(wx.ID_ANY, "FAQ / Tips", "FAQ and Tips on Usage.")

            

            self.Bind(wx.EVT_MENU, self.onFAQ, self.e_faq)
            self.Bind(wx.EVT_MENU, self.OnAbout, self.e_about)
            menuBar.Append(h_menu, "&Help")

            self.SetMenuBar(menuBar)
            panel = wx.Panel(self)

            # Define the Status Bar
            self.statusbar = self.CreateStatusBar()

            img = wx.EmptyImage(50,50)

            # LOCATION 1
            self.icon1 = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(img))
            self.line1label1 = wx.StaticText(panel, label="") # City + Zip
            self.line2label1 = wx.StaticText(panel, label="") # Lat/Lon
            self.line3label1 = wx.StaticText(panel, label="") # Temp / Humidity

            self.refresh1 = wx.BitmapButton(panel, 1110, refresher) # Refresh Button
            self.settings1 = wx.BitmapButton(panel, 1120, settings) #Settings Button
            self.day1 = wx.BitmapButton(panel, 1130, dayer) # Hourly Forecast Button
            self.week1 = wx.BitmapButton(panel, 1140, weeker) # Future Forecast Button

            self.line4label1 = wx.StaticText(panel, label="") # Wind
            self.line5label1 = wx.StaticText(panel, label="") # Updated

            self.Bind(wx.EVT_BUTTON, self.apilookup1, self.refresh1) # Refresh Location
            self.Bind(wx.EVT_BUTTON, self.locset1, self.settings1) # Location Settings
            self.Bind(wx.EVT_BUTTON, self.cast_hourly, self.day1) # Refresh Location
            self.Bind(wx.EVT_BUTTON, self.cast_10day, self.week1) # Location Settings

            # LOCATION 2
            self.icon2 = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(img))
            self.line1label2 = wx.StaticText(panel, label="") # City + Zip
            self.line2label2 = wx.StaticText(panel, label="") # Lat/Lon
            self.line3label2 = wx.StaticText(panel, label="") # Temp / Humidity

            self.refresh2 = wx.BitmapButton(panel, 2110, refresher)
            self.settings2 = wx.BitmapButton(panel, 2120, settings)
            self.day2 = wx.BitmapButton(panel, 2130, dayer) # Hourly Forecast Button
            self.week2 = wx.BitmapButton(panel, 2140, weeker) # Future Forecast Button

            self.line4label2 = wx.StaticText(panel, label="") # Wind
            self.line5label2 = wx.StaticText(panel, label="") # Updated

            self.Bind(wx.EVT_BUTTON, self.apilookup2, self.refresh2) # give is meaning
            self.Bind(wx.EVT_BUTTON, self.locset2, self.settings2) # give is meaning
            self.Bind(wx.EVT_BUTTON, self.cast_hourly, self.day2) # Refresh Location
            self.Bind(wx.EVT_BUTTON, self.cast_10day, self.week2) # Location Settings

            # LOCATION 3
            self.icon3 = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(img))
            self.line1label3 = wx.StaticText(panel, label="") # City + Zip
            self.line2label3 = wx.StaticText(panel, label="") # Lat/Lon
            self.line3label3 = wx.StaticText(panel, label="") # Temp / Humidity

            self.refresh3 = wx.BitmapButton(panel, 3110, refresher)
            self.settings3 = wx.BitmapButton(panel, 3120, settings)
            self.day3 = wx.BitmapButton(panel, 3130, dayer) # Hourly Forecast Button
            self.week3 = wx.BitmapButton(panel, 3140, weeker) # Future Forecast Button

            self.line4label3 = wx.StaticText(panel, label="") # Wind
            self.line5label3 = wx.StaticText(panel, label="") # Updated

            self.Bind(wx.EVT_BUTTON, self.apilookup3, self.refresh3) # give is meaning
            self.Bind(wx.EVT_BUTTON, self.locset3, self.settings3) # give is meaning
            self.Bind(wx.EVT_BUTTON, self.cast_hourly, self.day3) # Refresh Location
            self.Bind(wx.EVT_BUTTON, self.cast_10day, self.week3) # Location Settings

            #Sizers!
            topSizer = wx.BoxSizer(wx.VERTICAL)

            midSizer1 = wx.BoxSizer(wx.HORIZONTAL)
            leftSizer1 = wx.BoxSizer(wx.VERTICAL)
            centerSizer1 = wx.BoxSizer(wx.VERTICAL)
            rightSizer1 = wx.BoxSizer(wx.VERTICAL)
            iconSizer1 = wx.BoxSizer(wx.HORIZONTAL)
            btn1Sizer1 = wx.BoxSizer(wx.HORIZONTAL)
            btn2Sizer1 = wx.BoxSizer(wx.VERTICAL)

            midSizer2 = wx.BoxSizer(wx.HORIZONTAL)
            leftSizer2 = wx.BoxSizer(wx.VERTICAL)
            centerSizer2 = wx.BoxSizer(wx.VERTICAL)
            rightSizer2 = wx.BoxSizer(wx.VERTICAL)
            iconSizer2 = wx.BoxSizer(wx.HORIZONTAL)
            btn1Sizer2 = wx.BoxSizer(wx.HORIZONTAL)
            btn2Sizer2 = wx.BoxSizer(wx.VERTICAL)

            midSizer3 = wx.BoxSizer(wx.HORIZONTAL)
            leftSizer3 = wx.BoxSizer(wx.VERTICAL)
            centerSizer3 = wx.BoxSizer(wx.VERTICAL)
            rightSizer3 = wx.BoxSizer(wx.VERTICAL)
            iconSizer3 = wx.BoxSizer(wx.HORIZONTAL)
            btn1Sizer3 = wx.BoxSizer(wx.HORIZONTAL)
            btn2Sizer3 = wx.BoxSizer(wx.VERTICAL)

            # LOCATION1
            iconSizer1.Add(self.icon1, 0, wx.ALL, 2)
            btn1Sizer1.Add(self.day1, 0, wx.ALL, 2)
            btn1Sizer1.Add(self.week1, 0, wx.ALL, 2)
            leftSizer1.Add(iconSizer1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
            leftSizer1.Add(btn1Sizer1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
            
            centerSizer1.Add(self.line1label1, 0, wx.ALL, 2)
            centerSizer1.Add(self.line2label1, 0, wx.ALL, 2)
            centerSizer1.Add(self.line3label1, 0, wx.ALL, 2)
            centerSizer1.Add(self.line4label1, 0, wx.ALL, 2)
            centerSizer1.Add(self.line5label1, 0, wx.ALL, 2)

            btn2Sizer1.Add(self.refresh1, 0, wx.ALL, 2)
            btn2Sizer1.Add(self.settings1, 0, wx.ALL, 2)
            rightSizer1.Add(btn2Sizer1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)

            midSizer1.Add(leftSizer1, 0, wx.ALL, 2)
            midSizer1.Add(centerSizer1, 1, wx.ALL|wx.EXPAND, 2)
            midSizer1.Add(rightSizer1, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

            # LOCATION2
            iconSizer2.Add(self.icon2, 0, wx.ALL, 2)
            btn1Sizer2.Add(self.day2, 0, wx.ALL, 2)
            btn1Sizer2.Add(self.week2, 0, wx.ALL, 2)
            leftSizer2.Add(iconSizer2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
            leftSizer2.Add(btn1Sizer2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
            
            centerSizer2.Add(self.line1label2, 0, wx.ALL, 2)
            centerSizer2.Add(self.line2label2, 0, wx.ALL, 2)
            centerSizer2.Add(self.line3label2, 0, wx.ALL, 2)
            centerSizer2.Add(self.line4label2, 0, wx.ALL, 2)
            centerSizer2.Add(self.line5label2, 0, wx.ALL, 2)

            btn2Sizer2.Add(self.refresh2, 0, wx.ALL, 2)
            btn2Sizer2.Add(self.settings2, 0, wx.ALL, 2)
            rightSizer2.Add(btn2Sizer2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)

            midSizer2.Add(leftSizer2, 0, wx.ALL, 2)
            midSizer2.Add(centerSizer2, 1, wx.ALL|wx.EXPAND, 2)
            midSizer2.Add(rightSizer2, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

            # LOCATION3
            iconSizer3.Add(self.icon3, 0, wx.ALL, 2)
            btn1Sizer3.Add(self.day3, 0, wx.ALL, 2)
            btn1Sizer3.Add(self.week3, 0, wx.ALL, 2)
            leftSizer3.Add(iconSizer3, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
            leftSizer3.Add(btn1Sizer3, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
            
            centerSizer3.Add(self.line1label3, 0, wx.ALL, 2)
            centerSizer3.Add(self.line2label3, 0, wx.ALL, 2)
            centerSizer3.Add(self.line3label3, 0, wx.ALL, 2)
            centerSizer3.Add(self.line4label3, 0, wx.ALL, 2)
            centerSizer3.Add(self.line5label3, 0, wx.ALL, 2)

            btn2Sizer3.Add(self.refresh3, 0, wx.ALL, 2)
            btn2Sizer3.Add(self.settings3, 0, wx.ALL, 2)
            rightSizer3.Add(btn2Sizer3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)

            midSizer3.Add(leftSizer3, 0, wx.ALL, 2)
            midSizer3.Add(centerSizer3, 1, wx.ALL|wx.EXPAND, 2)
            midSizer3.Add(rightSizer3, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

            topSizer.Add(wx.StaticLine(panel, size=(460, 1)), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(midSizer1, 0, wx.ALIGN_LEFT|wx.EXPAND, 5)
            topSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(midSizer2, 0, wx.ALIGN_LEFT|wx.EXPAND, 5)
            topSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)
            topSizer.Add(midSizer3, 0, wx.ALIGN_LEFT|wx.EXPAND, 5)
            topSizer.Add(wx.StaticLine(panel), 0, wx.ALL|wx.EXPAND, 0)

            self.apilookup1(zippy1)
            self.apilookup2(zippy2)
            self.apilookup3(zippy3)

            panel.SetSizer(topSizer)
            topSizer.Fit(self)

            panel.Layout()
            self.Show(True) # show shit!
        
        # hourly function referer
        def cast_hourly(self,event):
            global usezip
            global usecity
            zip_id = event.GetId()
            if zip_id == 1130:
                usecity = city1
                usezip = zippy1
            elif zip_id == 2130:
                usecity = city2
                usezip = zippy2
            elif zip_id == 3130:
                usecity = city3
                usezip = zippy3
            hourlyfetch = str(apistring_hourly) + str(usezip + ".xml")
            hourlygrab = urllib2.urlopen(hourlyfetch)
            hourlyxml = hourlygrab.read()
            with open("datafile_hourly.xml", 'wb') as hourlyfile:
                hourlyfile.write(hourlyxml)
                hourlyfile.close()
            dialog = HourlyFrame(self, -1)
            

        # Temporary 10 Day function
        def cast_10day(self,event):
            zip_id = event.GetId()
            if zip_id == 1140:
                usecity = city1
                usezip = zippy1
            elif zip_id == 2140:
                usecity = city2
                usezip = zippy2
            elif zip_id == 3140:
                usecity = city3
                usezip = zippy3            
            dlg = wx.MessageDialog(self, 
                "10 Day Forecast for " + usecity + " (" + usezip + ") unavailable.\nFeature coming soon!",
                "10 Day Forecast not available", wx.OK|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()

        def onFAQ(self, event):
            faq_href = "http://www.metacache.net/pudle_faq.html"
            webbrowser.open(faq_href)

        # On-Hover functions for the refresh and settings buttons
        def rOnMouseOver(self,event):
            self.statusbar.SetStatusText('Refresh the weather data for this location')
        def sOnMouseOver(self,event):
            self.statusbar.SetStatusText('Configure settings for this location')
        def OnMouseLeave(self,event):
            self.statusbar.SetStatusText('')

        # Edit>Preferences
        def OnEditPref(self,event):
            dialog = PreferenceFrame(self, -1)

        # Help>About
        def OnAbout(self,event):
            dialog = AboutFrame(self, -1)

        # Edit>Default
        def OnEditDef(self,event):
            global zippy1
            global zippy2
            global zippy3
            global zippy1def
            global zippy2def
            global zippy3def

            # Location 1
            zippy1 = zippy1def
            # Location 2
            zippy2 = zippy2def
            # Location 3
            zippy3 = zippy3def

            self.apilookup1(zippy1)
            self.apilookup2(zippy2)
            self.apilookup3(zippy3)
            

        #Location 1 Settings Button
        def locset1(self,event):
            global zippy1
            dlg1 = wx.TextEntryDialog(self, 
                "ZIP (ex:94101) or Country/Loc (ex: GB/Chelsea)",
                "Please enter a Location using the following formats", zippy1)
            result1 = dlg1.ShowModal()
            if result1 == wx.ID_OK:
                zippy1 = dlg1.GetValue()
                
            else:
                pass
            self.apilookup1(zippy1)

        #Location 2 Settings Button
        def locset2(self,event):
            global zippy2
            dlg2 = wx.TextEntryDialog(self, 
                "ZIP (ex:94101) or Country/Loc (ex: GB/Chelsea)",
                "Please enter a Location using the following formats", zippy2)
            result2 = dlg2.ShowModal()
            if result2 == wx.ID_OK:
                zippy2 = dlg2.GetValue()
                
            else:
                pass
            self.apilookup2(zippy2)

        #Location 3 Settings Button
        def locset3(self,event):
            global zippy3
            dlg3 = wx.TextEntryDialog(self, 
                "ZIP (ex:94101) or Country/Loc (ex: GB/Chelsea)",
                "Please enter a Location using the following formats", zippy3)
            result3 = dlg3.ShowModal()
            if result3 == wx.ID_OK:
                zippy3 = dlg3.GetValue()
                
            else:
                pass
            self.apilookup3(zippy3)
            
            
        # Location 1 Lookup Function
        def apilookup1(self,event):
            global zippy1
            global namechk1
            global city1

            if str(zippy1) == "":
                namechk1 = str(zippy1def + ".xml")
            else:
                namechk1 = str(zippy1 + ".xml") 

            try:
                apifetch = str(apistring) + str(namechk1)
                apigrab = urllib2.urlopen(apifetch)
                apixml = apigrab.read()
                with open("datafile1.xml", 'wb') as newfile:
                    newfile.write(apixml)
                    newfile.close()
                DOMTree = xml.dom.minidom.parse("datafile1.xml")
                apidata = DOMTree.documentElement

                # Start of pull for name + location.
                apilocs = apidata.getElementsByTagName("display_location")
                for apiloc in apilocs:
                    apizip1 = apiloc.getElementsByTagName('zip')[0]
                    apicity1 = apiloc.getElementsByTagName('full')[0]
                    apilat1 = apiloc.getElementsByTagName('latitude')[0]
                    apilong1 = apiloc.getElementsByTagName('longitude')[0]
                    
                    zipcode1 = apizip1.childNodes[0].data
                    city1 = apicity1.childNodes[0].data
                    lat1 = apilat1.childNodes[0].data
                    lon1 = apilong1.childNodes[0].data
                    break
                
                # Start of actual Weather Details.
                apideets = apidata.getElementsByTagName("current_observation")
                for apidet in apideets:
                    apitemp1 = apidet.getElementsByTagName('temperature_string')[0]
                    apiwind1 = apidet.getElementsByTagName('wind_string')[0]
                    apifeels1 = apidet.getElementsByTagName('feelslike_string')[0]
                    apiiconurl1 = apidet.getElementsByTagName('icon_url')[0]
                    apiupdated1 = apidet.getElementsByTagName('observation_time')[0]
                    apitime1 = apidet.getElementsByTagName('local_time_rfc822')[0]

                    temp1 = apitemp1.childNodes[0].data
                    wind1 = apiwind1.childNodes[0].data
                    feels1 = apifeels1.childNodes[0].data
                    giffy1 = apiiconurl1.childNodes[0].data
                    uptime1 = apiupdated1.childNodes[0].data
                    localtime1 = apitime1.childNodes[0].data

                    icongrab = urllib2.urlopen(giffy1)
                    iconfetch = icongrab.read()
                    with open("icon1.gif", 'wb') as iconfile:
                        iconfile.write(iconfetch)
                        iconfile.close()
                    
                    self.line1label1.SetLabel(str(city1) + " (" + str(zipcode1) + ")")
                    self.line2label1.SetLabel("Lat: " + str(lat1) + " Long: " + str(lon1))
                    self.line3label1.SetLabel("Temp: " + str(temp1) + ", Feels like: " + str(feels1))
                    self.line4label1.SetLabel("Wind " + str(wind1))
                    self.line5label1.SetLabel(str(uptime1))
                    img = wx.Image("icon1.gif", wx.BITMAP_TYPE_GIF)
                    self.icon1.SetBitmap(wx.BitmapFromImage(img))
                    os.remove("icon1.gif")
                    os.remove("datafile1.xml")
                    break
            except:
                print "No Location Data, config file missing?"

        # Location 2 Lookup Function
        def apilookup2(self,event):
            global zippy2
            global namechk2
            global city2

            if str(zippy2) == "":
                namechk2 = str(zippy2def + ".xml")
            else:
                namechk2 = str(zippy2 + ".xml") 

            try:
                apifetch = str(apistring) + str(namechk2)
                apigrab = urllib2.urlopen(apifetch)
                apixml = apigrab.read()
                with open("datafile2.xml", 'wb') as newfile:
                    newfile.write(apixml)
                    newfile.close()
                DOMTree = xml.dom.minidom.parse("datafile2.xml")
                apidata = DOMTree.documentElement

                # Start of pull for name + location.
                apilocs = apidata.getElementsByTagName("display_location")
                for apiloc in apilocs:
                    apizip2 = apiloc.getElementsByTagName('zip')[0]
                    apicity2 = apiloc.getElementsByTagName('full')[0]
                    apilat2 = apiloc.getElementsByTagName('latitude')[0]
                    apilong2 = apiloc.getElementsByTagName('longitude')[0]
                    
                    zipcode2 = apizip2.childNodes[0].data
                    city2 = apicity2.childNodes[0].data
                    lat2 = apilat2.childNodes[0].data
                    lon2 = apilong2.childNodes[0].data
                    break
                
                # Start of actual Weather Details.
                apideets = apidata.getElementsByTagName("current_observation")
                for apidet in apideets:
                    apitemp2 = apidet.getElementsByTagName('temperature_string')[0]
                    apiwind2 = apidet.getElementsByTagName('wind_string')[0]
                    apifeels2 = apidet.getElementsByTagName('feelslike_string')[0]
                    apiiconurl2 = apidet.getElementsByTagName('icon_url')[0]
                    apiupdated2 = apidet.getElementsByTagName('observation_time')[0]
                    apitime2 = apidet.getElementsByTagName('local_time_rfc822')[0]

                    temp2 = apitemp2.childNodes[0].data
                    wind2 = apiwind2.childNodes[0].data
                    feels2 = apifeels2.childNodes[0].data
                    giffy2 = apiiconurl2.childNodes[0].data
                    uptime2 = apiupdated2.childNodes[0].data
                    localtime2 = apitime2.childNodes[0].data

                    icongrab = urllib2.urlopen(giffy2)
                    iconfetch = icongrab.read()
                    with open("icon2.gif", 'wb') as iconfile:
                        iconfile.write(iconfetch)
                        iconfile.close()
                    
                    self.line1label2.SetLabel(str(city2) + " (" + str(zipcode2) + ")")
                    self.line2label2.SetLabel("Lat: " + str(lat2) + " Long: " + str(lon2))
                    self.line3label2.SetLabel("Temp: " + str(temp2) + ", Feels like: " + str(feels2))
                    self.line4label2.SetLabel("Wind " + str(wind2))
                    self.line5label2.SetLabel(str(uptime2))
                    img = wx.Image("icon2.gif", wx.BITMAP_TYPE_GIF)
                    self.icon2.SetBitmap(wx.BitmapFromImage(img))
                    os.remove("icon2.gif")
                    os.remove("datafile2.xml")
                    break
            except:
                print "No Location Data, config file missing?"

        # Location 3 Lookup Function
        def apilookup3(self,event):
            global zippy3
            global namechk3
            global city3

            if str(zippy3) == "":
                namechk3 = str(zippy3def + ".xml")
            else:
                namechk3 = str(zippy3 + ".xml") 

            try:
                apifetch = str(apistring) + str(namechk3)
                apigrab = urllib2.urlopen(apifetch)
                apixml = apigrab.read()
                with open("datafile3.xml", 'wb') as newfile:
                    newfile.write(apixml)
                    newfile.close()
                DOMTree = xml.dom.minidom.parse("datafile3.xml")
                apidata = DOMTree.documentElement

                # Start of pull for name + location.
                apilocs = apidata.getElementsByTagName("display_location")
                for apiloc in apilocs:
                    apizip3 = apiloc.getElementsByTagName('zip')[0]
                    apicity3 = apiloc.getElementsByTagName('full')[0]
                    apilat3 = apiloc.getElementsByTagName('latitude')[0]
                    apilong3 = apiloc.getElementsByTagName('longitude')[0]
                    
                    zipcode3 = apizip3.childNodes[0].data
                    city3 = apicity3.childNodes[0].data
                    lat3 = apilat3.childNodes[0].data
                    lon3 = apilong3.childNodes[0].data
                    break
                
                # Start of actual Weather Details.
                apideets = apidata.getElementsByTagName("current_observation")
                for apidet in apideets:
                    apitemp3 = apidet.getElementsByTagName('temperature_string')[0]
                    apiwind3 = apidet.getElementsByTagName('wind_string')[0]
                    apifeels3 = apidet.getElementsByTagName('feelslike_string')[0]
                    apiiconurl3 = apidet.getElementsByTagName('icon_url')[0]
                    apiupdated3 = apidet.getElementsByTagName('observation_time')[0]
                    apitime3 = apidet.getElementsByTagName('local_time_rfc822')[0]

                    temp3 = apitemp3.childNodes[0].data
                    wind3 = apiwind3.childNodes[0].data
                    feels3 = apifeels3.childNodes[0].data
                    giffy3 = apiiconurl3.childNodes[0].data
                    uptime3 = apiupdated3.childNodes[0].data
                    localtime3 = apitime3.childNodes[0].data

                    icongrab = urllib2.urlopen(giffy3)
                    iconfetch = icongrab.read()
                    with open("icon3.gif", 'wb') as iconfile:
                        iconfile.write(iconfetch)
                        iconfile.close()
                    
                    self.line1label3.SetLabel(str(city3) + " (" + str(zipcode3) + ")")
                    self.line2label3.SetLabel("Lat: " + str(lat3) + " Long: " + str(lon3))
                    self.line3label3.SetLabel("Temp: " + str(temp3) + ", Feels like: " + str(feels3))
                    self.line4label3.SetLabel("Wind " + str(wind3))
                    self.line5label3.SetLabel(str(uptime3))
                    img = wx.Image("icon3.gif", wx.BITMAP_TYPE_GIF)
                    self.icon3.SetBitmap(wx.BitmapFromImage(img))
                    os.remove("icon3.gif")
                    os.remove("datafile3.xml")
                    break
            except:
                print "No Location Data, config file missing?"

        def OnClose(self,event):
            dlg = wx.MessageDialog(self, 
                "Do you really want to close this application?",
                "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.Destroy() # GUI dedded :(
                #print "\033[91mApp killed by File|Exit or App's 'x' button"
                sys.exit() # App dedded :(

    app = wx.App(False)
    frame = puddle(None, 'Puddle - Weather Forecast')
    app.MainLoop()
    pass

if __name__ == '__main__':
    sys.exit(main())
