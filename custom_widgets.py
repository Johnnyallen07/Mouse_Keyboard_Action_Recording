import wx


class SliderDialog(wx.Dialog):

    def __init__(self, *args, **kwargs):

        self._current_value = kwargs.pop("default_value", 1)
        self.min_value = kwargs.pop("min_value", 1)
        self.max_value = kwargs.pop("max_value", 1000)
        super(SliderDialog, self).__init__(*args, **kwargs)
        self._value = 1
        self.init_ui()
        self.slider.Bind(wx.EVT_KEY_UP, self.on_esc_press)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def init_ui(self):

        pnl = wx.Panel(self)
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.slider = wx.Slider(parent=pnl, id=wx.ID_ANY, value=self._current_value,
                                minValue=self.min_value, maxValue=self.max_value,
                                name="Choose a number", size=self.GetSize(),
                                style=wx.SL_VALUE_LABEL | wx.SL_AUTOTICKS)
        sizer.Add(self.slider)
        pnl.SetSizer(sizer)
        sizer.Fit(self)

    def on_esc_press(self, event):

        if event.KeyCode == wx.WXK_ESCAPE:
            self.Close()
        event.Skip()

    def on_close(self, event):

        self._value = self.slider.Value
        self.Destroy()

    @property
    def value(self):

        return self._value

    @value.setter
    def value(self, value):
        self._value = value
