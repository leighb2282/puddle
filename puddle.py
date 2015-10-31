#!/usr/bin/env python
# puddle.py
# Simple Weather App
# Version v00.00.05
# Fri 30 Oct 2015 17:07:17 
# Leigh Burton, lburton@metacache.net


import sys
import urllib2
from xml.dom.minidom import parse
import xml.dom.minidom
import os.path
import wx

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

            wx.Frame.__init__(self, parent, title=title, size=(460,180)) # Init the frame with a size of 390x120 pixels.
            self.Bind(wx.EVT_CLOSE, self.OnClose)
            menuBar = wx.MenuBar()
            self.ficon = wx.Icon("ficon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(self.ficon)
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
            self.zipbox = wx.TextCtrl(panel, style=wx.TE_LEFT, size=(250, 30), pos=(70, 10))
            self.fetch = wx.Button(panel, label="Fetch Weather", pos=(330, 10)) # Add a button
            self.Bind(wx.EVT_BUTTON, self.apilookup, self.fetch) # give is meaning

            self.line1label1 = wx.StaticText(panel, label="", pos=(60, 40)) # City
            self.line2label1 = wx.StaticText(panel, label="", pos=(60, 60)) # Zip
            self.line3label1 = wx.StaticText(panel, label="", pos=(60, 80)) # Latitude
            self.line4label1 = wx.StaticText(panel, label="", pos=(60, 100)) # Longitude
            img = wx.EmptyImage(50,50)
            self.icono = wx.StaticBitmap(panel, wx.ID_ANY, wx.BitmapFromImage(img), pos=(6, 55))
        
            self.apilookup(zippy)
            self.zipbox.SetValue(zippy)
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
                self.zipbox.SetValue(zippy)
                namechk = str(zippy + ".xml")
            else:
                namechk = str(validator + ".xml") 
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
                    apiiconurl = apidet.getElementsByTagName('icon_url')[0]
                    apiupdated = apidet.getElementsByTagName('observation_time')[0]
                    apitime = apidet.getElementsByTagName('local_time_rfc822')[0]

                    temp = apitemp.childNodes[0].data
                    wind = apiwind.childNodes[0].data
                    feels = apifeels.childNodes[0].data
                    giffy = apiiconurl.childNodes[0].data
                    uptime = apiupdated.childNodes[0].data
                    localtime = apitime.childNodes[0].data

                    icongrab = urllib2.urlopen(giffy)
                    iconfetch = icongrab.read()
                    with open("icono.gif", 'wb') as iconfile:
                        iconfile.write(iconfetch)
                        iconfile.close()
                    
                    self.line1label1.SetLabel(str(city) + " (" + str(zipcode) + "), Lat: " + str(lat) + " Long: " + str(lon))
                    self.line2label1.SetLabel("Temp: " + str(temp) + ", Feels like: " + str(feels))
                    self.line3label1.SetLabel("Wind " + str(wind))
                    self.line4label1.SetLabel(str(uptime))
                    img = wx.Image("icono.gif", wx.BITMAP_TYPE_GIF)
                    self.icono.SetBitmap(wx.BitmapFromImage(img))
                    os.remove("icono.gif")
                    os.remove("datafile.xml")
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
    frame = puddle(None, 'Puddle Weather Display')
    app.MainLoop()
    pass

if __name__ == '__main__':
    sys.exit(main())
