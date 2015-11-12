#!/usr/bin/env python
# puddle.py
# Simple Weather App
# Version v00.00.16
# Thu 12 Nov 2015 01:15:05 
# Leigh Burton, lburton@metacache.net


import sys
import urllib2
from xml.dom.minidom import parse
import xml.dom.minidom
import os.path
import wx


from ConfigParser import SafeConfigParser

settings_button = "res/settings_button.png"
refresh_button = "res/refresh_button.png"
appicon = "res/ficon.ico"
conffile = "res/config.ini"
wunderlogo = "res/wlogo.png"
puddlelogo = "res/plogo.png"
vinfo = "v00.00.15"
zippy1 = ""
zippy2 = ""
zippy3 = ""
zippy1def = ""
zippy2def = ""
zippy3def = ""
apikey = ""
emailer = ""
zipcode = ""
city = ""
lat = ""
lon = ""
temp = ""
wind = ""
feels = ""
giffy = ""
uptime = ""
localtime = ""

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
                              size=(300,270),
                              style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
            self.picon = wx.Icon(appicon, wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.picon)
            panel = wx.Panel(self, -1)

            self.apilabel = wx.StaticText(panel, label="API Key: ", pos=(15, 15)) # API Label
            self.apibox = wx.TextCtrl(panel, style=wx.TE_LEFT, size=(200, 30), pos=(80, 10)) # API Textbox

            self.eline1 = wx.StaticLine(panel, pos=(0,50), size=(300, 4), style=wx.LI_HORIZONTAL)

            self.defloclabel = wx.StaticText(panel, label="Default Locations", pos=(10, 60)) # Def Loc label + [R]
            self.defloclabel2 = wx.StaticText(panel, label="[R]", pos=(233, 60)) # Def Loc label + [R]

            self.loc1label = wx.StaticText(panel, label="Location 1: ", pos=(10, 85)) # Location 1 Label
            self.loc1box = wx.TextCtrl(panel, style=wx.TE_LEFT, size=(150, 30), pos=(80, 80)) # Location 1 Textbox
            self.l1act_check = wx.CheckBox(panel, label="", pos=(230,84))

            self.loc2label = wx.StaticText(panel, label="Location 2: ", pos=(10, 115)) # Location 2 Label
            self.loc2box = wx.TextCtrl(panel, style=wx.TE_LEFT, size=(150, 30), pos=(80, 110)) # Location 2 Textbox
            self.l2act_check = wx.CheckBox(panel, label="", pos=(230,114))

            self.loc3label = wx.StaticText(panel, label="Location 3: ", pos=(10, 145)) # Location 3 Label
            self.loc3box = wx.TextCtrl(panel, style=wx.TE_LEFT, size=(150, 30), pos=(80, 140)) # Location 3 Textbox
            self.l3act_check = wx.CheckBox(panel, label="", pos=(230,144))

            self.eline2 = wx.StaticLine(panel, pos=(0,179), size=(300, 4), style=wx.LI_HORIZONTAL)

            self.emaillabel = wx.StaticText(panel, label="Email: ", pos=(10, 195)) # Email Label
            self.emailbox = wx.TextCtrl(panel, style=wx.TE_LEFT, size=(200, 30), pos=(80, 190)) # Email Textbox

            self.eline3 = wx.StaticLine(panel, pos=(0,227), size=(300, 4), style=wx.LI_HORIZONTAL)

            self.applyButton = wx.Button(panel, label="Apply", pos=(10, 235))
            self.cancelButton = wx.Button(panel, label="Cancel", pos=(100, 235))

            self.Bind(wx.EVT_BUTTON, self.onApply, self.applyButton)
            self.Bind(wx.EVT_BUTTON, self.onClose, self.cancelButton)
            self.Bind(wx.EVT_CLOSE, self.onClose) # (Allows frame's title-bar close to work)

            # Disabled controls because no functionality
            self.l1act_check.Enable(False)
            self.l2act_check.Enable(False)
            self.l3act_check.Enable(False)
            self.emailbox.Enable(False)

            self.apibox.SetValue(apikey)
            self.loc1box.SetValue(str(zippy1def))
            self.loc2box.SetValue(str(zippy2def))
            self.loc3box.SetValue(str(zippy3def))
            self.emailbox.SetValue(emailer)

            self.CenterOnParent()
            self.GetParent().Enable(False)
            self.Show(True)

            self.__eventLoop = wx.EventLoop()
            self.__eventLoop.Run()

        def onClose(self, event):
            self.GetParent().Enable(True)
            self.__eventLoop.Exit()
            self.Destroy()

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
                print "No previosu config file, creating new one."

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
            btnSizer        = wx.BoxSizer(wx.HORIZONTAL)

            iconSizer.Add(self.pudd, 0, wx.ALL, 5)
            appverSizer.Add(self.titlelabel, 0, wx.ALL, 5)
            blurb1Sizer.Add(self.blurb1label, 0, wx.ALL, 0)
            blurb2Sizer.Add(self.blurb2label, 0, wx.ALL, 0)
            copySizer.Add(self.copyrlabel, 0, wx.ALL, 5)
            wunderSizer.Add(self.wunder, 0, wx.ALL, 5)
            btnSizer.Add(self.closeButton, 0, wx.ALL, 5)

            topSizer.Add(iconSizer, 0, wx.CENTER)
            topSizer.Add(appverSizer, 0, wx.CENTER, 5)
            topSizer.Add(blurb1Sizer, 0, wx.CENTER, 5)
            topSizer.Add(blurb2Sizer, 0, wx.CENTER, 5)
            topSizer.Add(copySizer, 0, wx.CENTER, 5)
            topSizer.Add(wunderSizer, 0, wx.LEFT, 5)
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
            self.m_about = h_menu.Append(wx.ID_ABOUT, "About", "About Puddle.")
            self.m_faq = h_menu.Append(wx.ID_ABOUT, "FAQ / Tips", "FAQ and Tips on Usage.")
            self.Bind(wx.EVT_MENU, self.OnAbout, self.m_about)
            menuBar.Append(h_menu, "&Help")

            self.SetMenuBar(menuBar)
            panel = wx.Panel(self)

            # Define the Status Bar
            self.statusbar = self.CreateStatusBar()

            img = wx.EmptyImage(50,50)
            self.eline0 = wx.StaticLine(panel, pos=(0,0), size=(460, 4), style=wx.LI_HORIZONTAL)

            # LOCATION 1
            self.icon1 = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(img), pos=(15, 10))
            self.line1label1 = wx.StaticText(panel, label="", pos=(80, 10)) # City + Zip
            self.line2label1 = wx.StaticText(panel, label="", pos=(80, 30)) # Lat/Lon
            self.line3label1 = wx.StaticText(panel, label="", pos=(80, 50)) # Temp / Humidity

            self.refresh1 = wx.BitmapButton(panel, -1, refresher, pos=(6, 65)) # Refresh Button
            self.settings1 = wx.BitmapButton(panel, -1, settings, pos=(41, 65)) #Settings Button

            self.line4label1 = wx.StaticText(panel, label="", pos=(80, 70)) # Wind
            self.line5label1 = wx.StaticText(panel, label="", pos=(80, 90)) # Updated

            self.eline1 = wx.StaticLine(panel, pos=(0,110), size=(460, 4), style=wx.LI_HORIZONTAL)

            #self.refresh1.Bind(wx.EVT_ENTER_WINDOW, self.rOnMouseOver1) #Hover On Refresh
            #self.refresh1.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            #self.settings1.Bind(wx.EVT_ENTER_WINDOW, self.sOnMouseOver1) #Hover On Settings
            #self.settings1.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Settings
            self.Bind(wx.EVT_BUTTON, self.apilookup1, self.refresh1) # Refresh Location
            self.Bind(wx.EVT_BUTTON, self.locset1, self.settings1) # Location Settings

            # LOCATION 2
            self.icon2 = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(img), pos=(15, 120))
            self.line1label2 = wx.StaticText(panel, label="", pos=(80, 120)) # City + Zip
            self.line2label2 = wx.StaticText(panel, label="", pos=(80, 140)) # Lat/Lon
            self.line3label2 = wx.StaticText(panel, label="", pos=(80, 160)) # Temp / Humidity

            self.refresh2 = wx.BitmapButton(panel, -1, refresher, pos=(6, 175))
            self.settings2 = wx.BitmapButton(panel, -1, settings, pos=(41, 175))

            self.line4label2 = wx.StaticText(panel, label="", pos=(80, 180)) # Wind
            self.line5label2 = wx.StaticText(panel, label="", pos=(80, 200)) # Updated

            self.eline2 = wx.StaticLine(panel, pos=(0,220), size=(460, 4), style=wx.LI_HORIZONTAL)

            #self.refresh2.Bind(wx.EVT_ENTER_WINDOW, self.rOnMouseOver2) #Hover On Refresh
            #self.refresh2.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            #self.settings2.Bind(wx.EVT_ENTER_WINDOW, self.sOnMouseOver2) #Hover On Settings
            #self.settings2.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Settings
            self.Bind(wx.EVT_BUTTON, self.apilookup2, self.refresh2) # give is meaning
            self.Bind(wx.EVT_BUTTON, self.locset2, self.settings2) # give is meaning

            # LOCATION 3
            self.icon3 = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(img), pos=(15, 230))
            self.line1label3 = wx.StaticText(panel, label="", pos=(80, 230)) # City + Zip
            self.line2label3 = wx.StaticText(panel, label="", pos=(80, 250)) # Lat/Lon
            self.line3label3 = wx.StaticText(panel, label="", pos=(80, 270)) # Temp / Humidity

            self.refresh3 = wx.BitmapButton(panel, -1, refresher, pos=(6, 285))
            self.settings3 = wx.BitmapButton(panel, -1, settings, pos=(41, 285))

            self.line4label3 = wx.StaticText(panel, label="", pos=(80, 290)) # Wind
            self.line5label3 = wx.StaticText(panel, label="", pos=(80, 310)) # Updated

            self.eline3 = wx.StaticLine(panel, pos=(0,330), size=(460, 4), style=wx.LI_HORIZONTAL)

            #self.refresh3.Bind(wx.EVT_ENTER_WINDOW, self.rOnMouseOver3) #Hover On Refresh
            #self.refresh3.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            #self.settings3.Bind(wx.EVT_ENTER_WINDOW, self.sOnMouseOver3) #Hover On Settings
            #self.settings3.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Settings
            self.Bind(wx.EVT_BUTTON, self.apilookup3, self.refresh3) # give is meaning
            self.Bind(wx.EVT_BUTTON, self.locset3, self.settings3) # give is meaning
        
            self.apilookup1(zippy1)
            self.apilookup2(zippy2)
            self.apilookup3(zippy3)


            panel.Layout()
            self.Show(True) # show shit!
        
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
            global namechk1
            global zipcode
            global city
            global lat
            global lon
            global wind
            global feels
            global giffy
            global uptime
            global localtime
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
            global namechk2
            global zipcode
            global city
            global lat
            global lon
            global wind
            global feels
            global giffy
            global uptime
            global localtime
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
            global namechk3
            global zipcode
            global city
            global lat
            global lon
            global wind
            global feels
            global giffy
            global uptime
            global localtime
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
            global zipcode
            global city
            global lat
            global lon
            global wind
            global feels
            global giffy
            global uptime
            global localtime
            global apikey

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
            global zipcode
            global city
            global lat
            global lon
            global wind
            global feels
            global giffy
            global uptime
            global localtime

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
            global zipcode
            global city
            global lat
            global lon
            global wind
            global feels
            global giffy
            global uptime
            global localtime

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
