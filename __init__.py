import wx

class MyApp(wx.App):
    def OnInit(self):
        # Create and show the main frame or other components here
        return True

if __name__ == '__main__':
    app = MyApp(False)  # Create an instance of the application
    dlg = wx.MessageDialog(None, "Record Successfully!", "Congrats", wx.OK | wx.ICON_WARNING)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()