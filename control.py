import os
import shutil
import sys
import tempfile
import threading
from datetime import date

import mouse
import keyboard
import pyautogui
import time
import gui
import wx
import wx.adv
from custom_widgets import SliderDialog
import settings
from mouse import *
from keyboard._keyboard_event import KeyboardEvent
from pathlib import Path

TMP_PATH = os.path.join(tempfile.gettempdir(),
                        "johnny" + ".txt")
SPECIAL_KEY = ['alt', 'altleft', 'altright', 'backspace', 'capslock', 'winleft',
               'winright', 'ctrlleft', 'ctrlright', 'delete', 'down', 'end', 'enter',
               'esc', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11',
               'f12', 'home', 'left']


class Timer(wx.Frame):
    def __init__(self, *args, **kw):
        super(Timer, self).__init__(*args, **kw)
        self.parent = args[0]
        self.panel = wx.Panel(self)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        total_time = settings.CONFIG.getint(
            'DEFAULT', 'Recording Timer')
        self.remaining_text = wx.StaticText(self.panel, label=f"Remaining time: {total_time} seconds", pos=(10, 10))

        # Start the timer to trigger every second
        self.timer.Start(1000)  # 1000 milliseconds (1 second)
        self.remaining_seconds = total_time

    def on_timer(self, event):
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self.remaining_text.SetLabel("Time's up!")
            self.timer.Stop()
            self.Destroy()
            self.additional_actions()

        else:
            self.remaining_text.SetLabel(f"Remaining time: {self.remaining_seconds} seconds")

    def additional_actions(self):
        RecordCtrl(self.parent).record()


class RecordCtrl:

    def __init__(self, parent):
        self.parent = parent

    def action(self, event):
        self.timer = settings.CONFIG.getint(
                'DEFAULT', 'Recording Timer')
        if self.timer > 0:
            side_frame = Timer(self.parent,title="Timer")
            side_frame.Show()
        else:
            self.record()

    def record(self):
        if getattr(sys, 'frozen', False):
            self.path = sys._MEIPASS
        else:
            self.path = Path(__file__).parent.absolute()
        self.parent.get_record_button().SetBitmap(wx.Bitmap(os.path.join(self.path, "img", "pause.png"),
                                                          wx.BITMAP_TYPE_ANY))
        self.parent.Refresh()
        self.parent.Update()
        events = []
        hotkey = settings.CONFIG.get('DEFAULT','Recording Hotkey')

        position = pyautogui.position()
        mouse.hook(events.append)
        keyboard.hook(events.append)
        keyboard.wait(hotkey)
        mouse.unhook(events.append)
        keyboard.unhook(events.append)
        print("HELLO")
        events = events[:-1]
        RecordSaver.save_to_cache(position, events)
        self.parent.get_record_button().SetBitmap(wx.Bitmap(os.path.join(self.path, "img", "video.png"),
                                                          wx.BITMAP_TYPE_ANY))
        self.parent.Refresh()
        self.parent.Update()


    def recording_timer(event):
        """Set the recording timer."""
        # Workaround for user upgrading from a previous version
        try:
            current_value = settings.CONFIG.getint(
                'DEFAULT', 'Recording Timer')
        except:
            current_value = 0

        dialog = wx.NumberEntryDialog(None, message="Choose an amount of time (seconds)",
                                      prompt="", caption="Recording Timer", value=current_value, min=0, max=999)
        dialog.ShowModal()
        new_value = dialog.Value
        dialog.Destroy()
        settings.CONFIG['DEFAULT']['Recording Timer'] = str(new_value)


class PlayCtrl:

    def play_event(self, event):
        self.position, self.events = RecordLoader.load_file()
        play_list = self.sequential()
        infinite = settings.CONFIG.getboolean('DEFAULT', 'Infinite Playback')
        count = settings.CONFIG.getint('DEFAULT', 'Repeat Count')

        while count > 0 or infinite:
            pyautogui.position(self.position[0], self.position[1])
            if settings.CONFIG.getboolean('DEFAULT', 'Force Quit') or (
                    keyboard.is_pressed('Q') and keyboard.is_pressed('ctrl')):
                settings.CONFIG['DEFAULT']['Force Quit'] = 'False'
                return
            for sequence in play_list:

                if sequence[0].__class__.__name__ == 'KeyboardEvent':
                    keyboard.play(sequence)
                else:
                    mouse.play(sequence)
            count -= 1
            time.sleep(float(1))

    def sequential(self):
        event_type = 'KeyboardEvent'
        play_list = []
        idx = 0
        is_keyboard = False
        if self.events[0].__class__.__name__ == event_type:
            is_keyboard = True
        while idx < len(self.events):
            idx, temp_list = self.sublist(is_keyboard, idx)
            play_list.append(temp_list)
            is_keyboard = not is_keyboard

        return play_list

    def sublist(self, is_keyboard_event, start):
        # return sublist of the events
        if not is_keyboard_event:
            for i in range(start, len(self.events)):
                if self.events[i].__class__.__name__ == 'KeyboardEvent':
                    return i, self.events[start:i]
        else:
            for i in range(start, len(self.events)):
                if self.events[i].__class__.__name__ != 'KeyboardEvent':
                    return i, self.events[start:i]
        return len(self.events), self.events[start:len(self.events)]


class RecordSaver:
    def __init__(self, parent):
        self.parent = parent

    def save_file(self, event):
        event.EventObject.Parent.panel.SetFocus()
        with wx.FileDialog(self.parent, "Save recording file", wildcard="*",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            try:
                shutil.copy(TMP_PATH, pathname)
            except IOError:
                wx.LogError(f"Cannot save current data in file {pathname}.")

    @staticmethod
    def save_to_cache(position, events):
        f = open(TMP_PATH, "w")
        f.write(f"{position[0]} {position[1]}\n")
        for i in range(len(events)):
            event = events[i]
            event_name = event.__class__.__name__
            if event_name == 'KeyboardEvent':
                f.write(f"{event_name} {event.event_type} {event.name} {event.time}\n")
            elif event_name == 'ButtonEvent':
                f.write(f"{event_name} {event.event_type} {event.button} {event.time}\n")
            elif event_name == 'WheelEvent':
                f.write(f"{event_name} {event.delta} {event.time}\n")
            else:
                f.write(f"{event_name} {event.x} {event.y} {event.time}\n")
        f.close()


class RecordLoader:
    def __init__(self, parent):
        self.parent = parent

    @staticmethod
    def load_file():
        event_list = []
        f = open(TMP_PATH, "r")
        event_position = f.readline()

        for line in f:
            info = line.split(" ")
            event_name = info[0]
            event_time = float(info[-1])
            if event_name == 'MoveEvent':
                event_list.append(MoveEvent(info[1], info[2], event_time))
            elif event_name == 'ButtonEvent':
                event_list.append(ButtonEvent(info[1], info[2], event_time))
            elif event_name == 'KeyboardEvent':
                event_list.append(
                    KeyboardEvent(info[1], info[2], time=event_time))
            else:
                event_list.append(WheelEvent(float(info[1]), event_time))
        f.close()
        return event_position, event_list

    def load_to_cache(self, event):

        title = "Choose a recording file(.txt):"
        dlg = wx.FileDialog(self.parent,
                            message=title,
                            style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            shutil.copy(dlg.GetPath(), TMP_PATH)
        event.EventObject.Parent.panel.SetFocus()
        dlg.Destroy()


class RecordHotkeyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(RecordHotkeyFrame, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        # self.message_label = wx.StaticText(self.panel, label="Enter your message:")
        self.message_textctrl = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.submit_button = wx.Button(self.panel, label="Submit")
        # self.result_label = wx.StaticText(self.panel, label="Result:")

        self.Bind(wx.EVT_BUTTON, self.on_submit, self.submit_button)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_submit, self.message_textctrl)

        self.layout = wx.BoxSizer(wx.HORIZONTAL)

        self.layout.Add(self.message_textctrl, proportion=1, flag=wx.EXPAND)
        self.layout.Add(self.submit_button, 0, wx.ALL)

        self.panel.SetSizer(self.layout)

    def on_submit(self, event):
        self.entered_message = self.message_textctrl.GetValue()
        print(self.entered_message)
        self.message_textctrl.SetValue("")
        self.additional_actions()

    def additional_actions(self):
        SettingsCtrl().recording_hotkey(self, str(self.entered_message))


class PlaybackHotkeyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(PlaybackHotkeyFrame, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        # self.message_label = wx.StaticText(self.panel, label="Enter your message:")
        self.message_textctrl = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.submit_button = wx.Button(self.panel, label="Submit")
        # self.result_label = wx.StaticText(self.panel, label="Result:")

        self.Bind(wx.EVT_BUTTON, self.on_submit, self.submit_button)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_submit, self.message_textctrl)

        self.layout = wx.BoxSizer(wx.HORIZONTAL)

        self.layout.Add(self.message_textctrl, proportion=1, flag=wx.EXPAND)
        self.layout.Add(self.submit_button, 0, wx.ALL)

        self.panel.SetSizer(self.layout)

    def on_submit(self, event):
        self.entered_message = self.message_textctrl.GetValue()
        print(self.entered_message)
        self.message_textctrl.SetValue("")
        self.additional_actions()

    def additional_actions(self):
        SettingsCtrl().playback_hotkey(self, str(self.entered_message))


class SettingsCtrl:

    @staticmethod
    def infinite_playback(event):
        """infinite playback"""
        current_value = settings.CONFIG.getboolean(
            'DEFAULT', 'Infinite Playback'
        )
        settings.CONFIG['DEFAULT']['Infinite Playback'] = str(
            not current_value
        )

    def repeat_count(self, event):
        current_value = settings.CONFIG.getint('DEFAULT', 'Repeat Count')
        dialog = wx.NumberEntryDialog(None, message="Choose repeat times",
                                      prompt="", caption="Repeat Count", value=current_value, min=1, max=1000)
        dialog.ShowModal()
        new_value = str(dialog.Value)
        dialog.Destroy()
        settings.CONFIG['DEFAULT']['Repeat Count'] = new_value
        # self.main_dialog.remaining_plays.Label = new_value

    @staticmethod
    def record_action(event):
        frame = RecordHotkeyFrame(None,
                                  title='Please enter a valid hotkey '
                                        '(recommend f1-f12 and esc)',
                                  size=(1000, 120))
        frame.Show()

    def recording_hotkey(self, frame, hotkey):
        """Set the recording hotkey."""
        if hotkey == str(settings.CONFIG.get('DEFAULT', 'Playback Hotkey')):
            dlg = wx.MessageDialog(
                None, "Recording hotkey should be different from Playback one", "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        elif hotkey not in SPECIAL_KEY:
            dlg = wx.MessageDialog(
                None, "Recording hotkey should not be a common letter", "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            frame.Destroy()
        settings.CONFIG['DEFAULT']['Recording Hotkey'] = hotkey

    @staticmethod
    def playback_action(event):
        frame = PlaybackHotkeyFrame(None,
                                    title='Please enter a valid hotkey '
                                          '(recommend f1-f12 and esc)',
                                    size=(1000, 120))
        frame.Show()

    def playback_hotkey(self, frame, hotkey):
        """Set the playback hotkey."""
        if hotkey == str(settings.CONFIG.get('DEFAULT', 'Recording Hotkey')):
            dlg = wx.MessageDialog(
                None, "Playback hotkey should be different from Recording one", "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        elif hotkey not in SPECIAL_KEY:
            dlg = wx.MessageDialog(
                None, "Playback hotkey should not be a common letter", "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            frame.Destroy()
        settings.CONFIG['DEFAULT']['Playback Hotkey'] = hotkey

    def always_on_top(self, event):
        """Toggle the always on top setting."""
        current_value = settings.CONFIG['DEFAULT']['Always On Top']
        style = self.main_dialog.GetWindowStyle()
        self.main_dialog.SetWindowStyle(style ^ wx.STAY_ON_TOP)
        settings.CONFIG['DEFAULT']['Always On Top'] = str(not current_value)


class HelpCtrl:
    """Control class for the About menu."""

    @staticmethod
    def action(event):
        """Open the browser on the quick demo of atbswp"""
        url = "https://youtu.be/L0jjSgX5FYk"
        wx.LaunchDefaultBrowser(url, flags=0)
