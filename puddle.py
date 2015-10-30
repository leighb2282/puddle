#!/usr/bin/env python
# puddle.py
# Simple Weather App
# Version v00.00.02
# Thu 29 Oct 2015 22:48:32 
# Leigh Burton, lburton@metacache.net


import sys
import urllib2
from xml.dom.minidom import parse
import xml.dom.minidom
import os.path
import wx      # wxPython

zippy = "94101"
namechk = zippy + ".xml"

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

def main():
    """ Main entry point for the script."""
    global apifetch
    global namechk
    

    # Start of GUI happiness
    class puddle(wx.Frame):
        def __init__(self, parent, title):
            global apifetch
            global namechk

            wx.Frame.__init__(self, parent, title=title, size=(390,320)) # Init the frame with a size of 390x120 pixels.
            self.Bind(wx.EVT_CLOSE, self.OnClose)
            menuBar = wx.MenuBar()
        
            # Define the File Menu.
            f_menu = wx.Menu()    
            self.m_exit = f_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")         
            self.Bind(wx.EVT_MENU, self.OnClose, self.m_exit)
            menuBar.Append(f_menu, "&File")
            self.SetMenuBar(menuBar)
            panel = wx.Panel(self)

            # Define the Status Bar
            self.statusbar = self.CreateStatusBar()
            self.ziplabel = wx.StaticText(panel, label="Location: ", pos=(10, 15)) # Zip/Country:city label
            self.zipbox = wx.TextCtrl(panel, style=wx.TE_LEFT, size=(300, 30), pos=(80, 10)) # Username Textbox
            self.fetch = wx.Button(panel, label="Get Weather Information", pos=(10, 50)) # Add a button
            self.Bind(wx.EVT_BUTTON, self.apilookup, self.fetch) # give is meaning
        
            
            panel.Layout()
            self.Show(True) # show shit!

        def apilookup(self,event):
            global zippy
            global namechk
            global zipcode
            global city
            global lat
            global lon
            global wind
            global feels
            global giffy
            global uptime
            global localtime
            
            validator = str(self.zipbox.GetValue())
            if str(validator) == "" or str(validator) == "":
                print "Using Default Value of " + namechk.split(".")[0]
            else:
                namechk = str(validator) + ".xml"
                print "Using User Defined value of " + str(validator)
            try:
                apifetch = "http://api.wunderground.com/api/6d38851d6740fcff/conditions/lang:EN/q/" + str(namechk)
                apigrab = urllib2.urlopen(apifetch)
                apixml = apigrab.read()
                with open("datafile.xml", 'wb') as newfile:
                    newfile.write(apixml)
                    newfile.close()
                DOMTree = xml.dom.minidom.parse("datafile.xml")
                apidata = DOMTree.documentElement

                # Start of pull for name + location.
                apilocs = apidata.getElementsByTagName("display_location")
                for apiloc in apilocs:
                    apizip = apiloc.getElementsByTagName('zip')[0]
                    apicity = apiloc.getElementsByTagName('full')[0]
                    apilat = apiloc.getElementsByTagName('latitude')[0]
                    apilong = apiloc.getElementsByTagName('longitude')[0]
                    
                    zipcode = apizip.childNodes[0].data
                    city = apicity.childNodes[0].data
                    lat = apilat.childNodes[0].data
                    lon = apilong.childNodes[0].data
                    break
                
                # Start of actual Weather Details.
                apideets = apidata.getElementsByTagName("current_observation")
                for apidet in apideets:
                    apitemp = apidet.getElementsByTagName('temperature_string')[0]
                    apiwind = apidet.getElementsByTagName('wind_string')[0]
                    apifeels = apidet.getElementsByTagName('feelslike_string')[0]
                    apiconurl = apidet.getElementsByTagName('icon_url')[0]
                    apiupdated = apidet.getElementsByTagName('observation_time')[0]
                    apitime = apidet.getElementsByTagName('local_time_rfc822')[0]

                    temp = apitemp.childNodes[0].data
                    wind = apiwind.childNodes[0].data
                    feels = apifeels.childNodes[0].data
                    giffy = apiconurl.childNodes[0].data
                    uptime = apiupdated.childNodes[0].data
                    localtime = apitime.childNodes[0].data
                    print str(city) + "(" + str(zipcode) + "), Lat: " + str(lat) + " Long: " + str(lon)
                    print "Temp: " + str(temp) + ", Feels like: " + str(feels)
                    print "Wind " + str(wind)
                    print str(uptime)
                    print ""
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
                print "\033[91mApp killed by File|Exit or App's 'x' button"
                sys.exit() # App dedded :(
            else:
                print "\033[93mUser chose not to close the encoder."
        

    app = wx.App(False)
    frame = puddle(None, 'Puddle Weather Display')
    app.MainLoop()
    pass

if __name__ == '__main__':
    sys.exit(main())
