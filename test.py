import wx

class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

        self.remaining_text = wx.StaticText(self.panel, label="Remaining time: 5 seconds", pos=(10, 10))

        # Start the timer to trigger every second
        self.timer.Start(1000)  # 1000 milliseconds (1 second)
        self.remaining_seconds = 5

    def on_timer(self, event):
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self.remaining_text.SetLabel("Time's up!")
            self.timer.Stop()
            self.Destroy()
        else:
            self.remaining_text.SetLabel(f"Remaining time: {self.remaining_seconds} seconds")

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, title="wxPython Timer Example", size=(300, 200))
    frame.Show()
    app.MainLoop()
