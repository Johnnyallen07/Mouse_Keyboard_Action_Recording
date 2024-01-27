import os
import sys
import threading

import keyboard
import wx
import wx.adv
import settings
import control
from pathlib import Path

hotkeys = {
    'enter': 13,
    'esc': 27,
    'delete': 127,
    'shift': 306,
    'alt': 307,
    'ctrl': 308,
    'insert': 322,
    'f1': 340,
    'f2': 341,
    'f3': 342,
    'f4': 343,
    'f5': 344,
    'f6': 345,
    'f7': 346,
    'f8': 347,
    'f9': 348,
    'f10': 349,
    'f11': 350,
    'f12': 351,
}


class MainDialog(wx.Dialog, wx.MiniFrame):
    app_text = ["Load File", "Save File", "Start/Stop Capture", "Play",
                "Preferences", "Help"]
    settings_text = ["&Infinite Playback", "Set &Repeat Count", "Recording &Hotkey",
                     "&Playback Hotkey", "Always on &Top", "&Language", "&About", "Preparation Time", "Exit"]

    def __init__(self, *args, **kwds):
        """Build the interface."""
        if getattr(sys, 'frozen', False):
            self.path = sys._MEIPASS
        else:
            self.path = Path(__file__).parent.absolute()
        on_top = wx.DEFAULT_DIALOG_STYLE
        on_top = on_top if not settings.CONFIG.getboolean('DEFAULT', 'Always On Top') \
            else on_top | wx.STAY_ON_TOP
        kwds["style"] = kwds.get("style", 0) | on_top
        wx.Dialog.__init__(self, *args, **kwds)
        self.panel = wx.Panel(self)
        self.icon = wx.Icon(os.path.join(self.path, "img", "icon.png"))
        self.SetIcon(self.icon)
        self.taskbar = TaskBarIcon(self)
        self.taskbar.SetIcon(self.icon, "johnny")

        # locale = self.__load_locale()
        # self.app_text, self.settings_text = locale[:7], locale[7:]
        self.file_open_button = wx.BitmapButton(self,
                                                wx.ID_ANY,
                                                wx.Bitmap(os.path.join(self.path, "img", "file-upload.png"),
                                                          wx.BITMAP_TYPE_ANY))
        self.file_open_button.SetToolTip(self.app_text[0])
        self.save_button = wx.BitmapButton(self,
                                           wx.ID_ANY,
                                           wx.Bitmap(os.path.join(self.path, "img", "save.png"),
                                                     wx.BITMAP_TYPE_ANY))
        self.save_button.SetToolTip(self.app_text[1])
        self.record_button = wx.BitmapToggleButton(self,
                                                   wx.ID_ANY,
                                                   wx.Bitmap(os.path.join(self.path, "img", "video.png"),
                                                             wx.BITMAP_TYPE_ANY))
        self.record_button.SetToolTip(self.app_text[2])
        self.play_button = wx.BitmapToggleButton(self,
                                                 wx.ID_ANY,
                                                 wx.Bitmap(os.path.join(self.path, "img", "play-circle.png"),
                                                           wx.BITMAP_TYPE_ANY))
        # self.remaining_plays = wx.StaticText(self, label=settings.CONFIG.get("DEFAULT", "Repeat Count"),
        #                                      style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.play_button.SetToolTip(self.app_text[3])
        self.play_button.SetBitmap(wx.Bitmap(os.path.join(self.path, "img", "play-circle.png"),
                                                  wx.BITMAP_TYPE_ANY))

        self.settings_button = wx.BitmapButton(self,
                                               wx.ID_ANY,
                                               wx.Bitmap(os.path.join(self.path, "img", "cog.png"),
                                                         wx.BITMAP_TYPE_ANY))
        self.settings_button.SetToolTip(self.app_text[4])

        self.help_button = wx.BitmapButton(self,
                                           wx.ID_ANY,
                                           wx.Bitmap(os.path.join(self.path, "img", "question-circle.png"),
                                                     wx.BITMAP_TYPE_ANY))
        self.help_button.SetToolTip(self.app_text[5])

        self.__add_bindings()
        self.__set_properties()
        self.__do_layout()

    def get_record_button(self):
        return self.record_button


    def on_settings_click(self, event):
        self.settings_popup()
        event.GetEventObject().PopupMenu(self.settings_popup())
        event.EventObject.Parent.panel.SetFocus()
        event.Skip()

    def settings_popup(self):
        """Build the popup menu."""
        menu = wx.Menu()
        # Replay fast

        #  Infinite Playback
        cp = menu.AppendCheckItem(wx.ID_ANY, self.settings_text[0])
        status = settings.CONFIG.getboolean('DEFAULT', 'Infinite Playback')
        cp.Check(status)
        self.Bind(wx.EVT_MENU,
                  control.SettingsCtrl.infinite_playback,
                  cp)

        # Repeat count
        self.Bind(wx.EVT_MENU, self.sc.repeat_count,
                  menu.Append(wx.ID_ANY, self.settings_text[1]))
        menu.AppendSeparator()

        # Recording hotkey
        self.Bind(wx.EVT_MENU,
                  control.SettingsCtrl.record_action,
                  menu.Append(wx.ID_ANY, self.settings_text[2]))

        # Playback hotkey
        self.Bind(wx.EVT_MENU,
                  control.SettingsCtrl.playback_action,
                  menu.Append(wx.ID_ANY, self.settings_text[3]))
        menu.AppendSeparator()
        #
        #     # Always on top
        #     aot = menu.AppendCheckItem(wx.ID_ANY, self.settings_text[5])
        #     status = settings.CONFIG.getboolean('DEFAULT', 'Always On Top')
        #     aot.Check(status)
        #     self.Bind(wx.EVT_MENU,
        #               self.sc.always_on_top,
        #               aot)
        #
        # Recording Timer
        self.Bind(wx.EVT_MENU,
                  control.RecordCtrl.recording_timer,
                  menu.Append(wx.ID_ANY, self.settings_text[7]))

        #     # Mouse speed
        #     self.Bind(wx.EVT_MENU,
        #               control.RecordCtrl.mouse_speed,
        #               menu.Append(wx.ID_ANY, self.settings_text[9]))
        return menu

    #
    def __add_bindings(self):
        # file_save_ctrl
        self.fsc = control.RecordSaver(self)
        self.Bind(wx.EVT_BUTTON, self.fsc.save_file, self.save_button)

        self.flc = control.RecordLoader(self)
        self.Bind(wx.EVT_BUTTON, self.flc.load_to_cache, self.file_open_button)
        # record_button_ctrl
        self.rbc = control.RecordCtrl(self)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.rbc.action, self.record_button)

        # play_button_ctrl
        self.pbc = control.PlayCtrl()
        self.Bind(wx.EVT_TOGGLEBUTTON, self.pbc.play_event, self.play_button)

        # # Handle the event returned after a playback has completed
        # self.Bind(self.pbc.EVT_THREAD_END, self.on_thread_end)
        #
        # help_button_ctrl
        self.Bind(wx.EVT_BUTTON, control.HelpCtrl.action, self.help_button)

        # settings_button_ctrl
        self.Bind(wx.EVT_BUTTON, self.on_settings_click, self.settings_button)
        self.sc = control.SettingsCtrl()

        self.Bind(wx.EVT_CLOSE, self.on_close_dialog)

        # Handle keyboard shortcuts
        self.panel.Bind(wx.EVT_KEY_UP, self.on_key_press)

        self.panel.SetFocus()

    def __set_properties(self):
        self.file_open_button.SetSize(self.file_open_button.GetBestSize())
        self.save_button.SetSize(self.save_button.GetBestSize())
        self.record_button.SetSize(self.record_button.GetBestSize())
        self.play_button.SetSize(self.play_button.GetBestSize())
        self.settings_button.SetSize(self.settings_button.GetBestSize())
        self.help_button.SetSize(self.help_button.GetBestSize())

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.panel)
        main_sizer.Add(self.file_open_button, 0, 0, 0)
        main_sizer.Add(self.save_button, 0, 0, 0)
        main_sizer.Add(self.record_button, 0, 0, 0)
        main_sizer.Add(self.play_button, 0, 0, 0)
        main_sizer.Add(self.settings_button, 0, 0, 0)
        main_sizer.Add(self.help_button, 0, 0, 0)

        self.SetSizer(main_sizer)
        self.Centre()
        main_sizer.Fit(self)
        self.Layout()

    def on_key_press(self, event):
        """ Create manually the event when the correct key is pressed."""
        keycode = event.GetKeyCode()
        print(keycode)

        if keycode == 'home':
            pass
        #     control.HelpCtrl.action(wx.PyCommandEvent(wx.wxEVT_BUTTON))

        elif keycode == hotkeys.get(settings.CONFIG.get('DEFAULT', 'Recording Hotkey')):
            btn_event = wx.CommandEvent(wx.wxEVT_TOGGLEBUTTON)
            btn_event.EventObject = self.record_button
            if not self.record_button.Value:
                self.record_button.Value = True
                self.rbc.action(btn_event)
            else:
                self.record_button.Value = False
                self.rbc.action(btn_event)

        elif keycode == hotkeys.get(settings.CONFIG.get('DEFAULT', 'Playback Hotkey')):
            if not self.play_button.Value:
                self.play_button.Value = True
                btn_event = wx.CommandEvent(wx.wxEVT_TOGGLEBUTTON)
                btn_event.EventObject = self.play_button
                self.pbc.play_event(btn_event)
            else:
                self.play_button.Value = False

        elif keycode == ord('R') and event.CmdDown():
            menu_event = wx.CommandEvent(wx.wxEVT_MENU)
            self.sc.repeat_count(menu_event)

        elif keycode == ord('O') and event.CmdDown():
            btn_event = wx.CommandEvent(wx.wxEVT_TOGGLEBUTTON)
            btn_event.EventObject = self.file_open_button
            self.flc.load_to_cache(btn_event)

        elif keycode == ord('S') and event.CmdDown():
            btn_event = wx.CommandEvent(wx.wxEVT_TOGGLEBUTTON)
            btn_event.EventObject = self.save_button
            self.fsc.save_file(btn_event)

        elif (keycode == ord('Q') and event.CmdDown()) or hotkeys.get('esc'):
            settings.CONFIG['DEFAULT']['Force Quit'] = True
        event.Skip()

    #
    # def on_thread_end(self, event):
    #     self.play_button.Value = event.toggle_value
    #     self.remaining_plays.Label = str(event.count) if event.count > 0 else \
    #         str(settings.CONFIG.getint('DEFAULT', 'Repeat Count'))
    #     self.remaining_plays.Update()
    #
    def on_exit_app(self, event):
        """Clean exit saving the settings."""
        settings.save_config()
        self.Destroy()
        self.taskbar.Destroy()

    def on_close_dialog(self, event):
        """Confirm exit."""
        dialog = wx.MessageDialog(self,
                                  message="Are you sure you want to quit?",
                                  caption="Confirm Exit",
                                  style=wx.YES_NO,
                                  pos=wx.DefaultPosition)
        response = dialog.ShowModal()

        if (response == wx.ID_YES):
            self.on_exit_app(event)
        else:
            event.StopPropagation()

    # def on_about(self, event):
    #     """About dialog."""
    #     info = wx.adv.AboutDialogInfo()
    #     info.Name = "atbswp"
    #     info.Version = f"{settings.VERSION}"
    #     info.Copyright = (f"©{settings.YEAR} Paul Mairo <github@rmpr.xyz>\n")
    #     info.Description = "Record mouse and keyboard actions and reproduce them identically at will"
    #     info.WebSite = ("https://github.com/atbswp", "Project homepage")
    #     info.Developers = ["Paul Mairo"]
    #     info.License = "GNU General Public License V3"
    #     info.Icon = self.icon
    #     wx.adv.AboutBox(info)


class TaskBarIcon(wx.adv.TaskBarIcon):
    """Taskbar showing the state of the recording."""

    def __init__(self, parent):
        self.parent = parent
        super(TaskBarIcon, self).__init__()
