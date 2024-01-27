import gui

import wx


class MainApp(wx.App):
    """Main class of the program."""

    def OnInit(self):
        """Initialize the main Window."""
        self.main = gui.MainDialog(None, wx.ID_ANY, "johnny")
        self.SetTopWindow(self.main)
        self.main.Show()
        return True


if __name__ == "__main__":
    app = MainApp(0)
    app.MainLoop()
