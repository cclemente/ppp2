

import glob,natsort,os,wx
import numpy as np




class CheckPOINavigationControls(wx.Panel):
	def __init__(self, parent, ID=-1, label="", pos=wx.DefaultPosition, size=(100,25)):
		wx.Panel.__init__(self, parent, ID, pos, size, wx.STATIC_BORDER, label)
		self.SetMinSize(size)
		self.parent     = parent
		sizer           = self._create_buttons()
		self.SetSizer(sizer)
		self.Fit()
		self.Centre()

	def _create_buttons(self):
		button0     = wx.Button(self, -1, '<', (50, 130))
		button1     = wx.Button(self, -1, 'Quit', (50, 130))
		button2     = wx.Button(self, -1, '>', (50, 130))
		sizer       = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(button0, 4, flag=wx.EXPAND)
		sizer.Add(button1, 1, flag=wx.EXPAND)
		sizer.Add(button2, 4, flag=wx.EXPAND)
		self.parent.Bind(wx.EVT_BUTTON, self.callback_back, button0)
		self.parent.Bind(wx.EVT_BUTTON, self.callback_quit, button1)
		self.parent.Bind(wx.EVT_BUTTON, self.callback_forward, button2)
		self.button_back    = button0
		self.button_forward = button2
		return sizer

	def callback_forward(self, event):
		self.parent.forward()
	def callback_back(self, event):
		self.parent.back()
	def callback_quit(self, event):
		self.parent.quit()






	