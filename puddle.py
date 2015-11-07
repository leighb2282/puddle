#!/usr/bin/env python
# puddle.py
# Simple Weather App
# Version v00.00.10
# Sat 07 Nov 2015 11:43:21 
# Leigh Burton, lburton@metacache.net


import sys
import urllib2
from xml.dom.minidom import parse
import xml.dom.minidom
import os.path
import wx



##############################
# Default Locations Settings #
# Ideally Imported from File #
##############################

# Location 1
zippy1def = "94101"
zippy1 = zippy1def
namechk1 = zippy1 + ".xml"
# Location 2
zippy2def = "10001"
zippy2 = zippy2def
namechk2 = zippy2 + ".xml"
# Location 3
zippy3def = "GB/London"
zippy3 = zippy3def
namechk3 = zippy3 + ".xml"

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
settings_button = "res/settings_button.png"
refresh_button = "res/refresh_button.png"
appicon = "res/ficon.ico"

def main():
    """ Main entry point for the script."""
    global apifetch
    global namechk
    
    class PreferenceFrame(wx.Frame):
        ''' PreferenceFrame launched from puddle '''
        def __init__(self, parent, id):
            wx.Frame.__init__(self, parent, -1,
                              title="Puddle Preferences",
                              size=(300,150),
                              style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)

            panel = wx.Panel(self, -1)
            closeButton = wx.Button(panel, label="Close Me")

            self.Bind(wx.EVT_BUTTON, self.__onClose, id=closeButton.GetId())
            self.Bind(wx.EVT_CLOSE, self.__onClose) # (Allows frame's title-bar close to work)

            self.CenterOnParent()
            self.GetParent().Enable(False)
            self.Show(True)

            self.__eventLoop = wx.EventLoop()
            self.__eventLoop.Run()
        def __onClose(self, event):
            self.GetParent().Enable(True)
            self.__eventLoop.Exit()
            self.Destroy()

    # Start of GUI happiness
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
            self.Bind(wx.EVT_MENU, self.OnEditPref, self.e_pref)
            menuBar.Append(e_menu, "&Edit")
  
            # Define the Help Menu
            h_menu = wx.Menu()    
            self.m_about = h_menu.Append(wx.ID_ABOUT, "About", "About Puddle.")
            self.m_faq = h_menu.Append(wx.ID_ABOUT, "FAQ & Tips", "FAQ & Tips.")
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

            #self.refresh1.Bind(wx.EVT_ENTER_WINDOW, self.rOnMouseOver) #Hover On Refresh
            #self.refresh1.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            #self.settings1.Bind(wx.EVT_ENTER_WINDOW, self.sOnMouseOver) #Hover On Settings
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

            #self.refresh2.Bind(wx.EVT_ENTER_WINDOW, self.rOnMouseOver) #Hover On Refresh
            #self.refresh2.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            #self.settings2.Bind(wx.EVT_ENTER_WINDOW, self.sOnMouseOver) #Hover On Settings
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

            #self.refresh3.Bind(wx.EVT_ENTER_WINDOW, self.rOnMouseOver) #Hover On Refresh
            #self.refresh3.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave) #Hover Off Refresh
            #self.settings3.Bind(wx.EVT_ENTER_WINDOW, self.sOnMouseOver) #Hover On Settings
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

            if str(zippy1) == "":
                namechk1 = str(zippy1def + ".xml")
            else:
                namechk1 = str(zippy1 + ".xml") 

            try:
                apifetch = "http://api.wunderground.com/api/6d38851d6740fcff/conditions/lang:EN/q/" + str(namechk1)
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
                print "Unexpected error."

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
                apifetch = "http://api.wunderground.com/api/6d38851d6740fcff/conditions/lang:EN/q/" + str(namechk2)
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
                print "Unexpected error."

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
                apifetch = "http://api.wunderground.com/api/6d38851d6740fcff/conditions/lang:EN/q/" + str(namechk3)
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
                print "Unexpected error."

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
