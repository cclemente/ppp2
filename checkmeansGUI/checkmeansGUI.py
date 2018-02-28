

import os,wx
from checkmeansGUI_panels import CheckMeansPanel
from checkmeansGUI_navigation import CheckMeansNavigationControls


class CheckMeansFrame(wx.Frame):
	def __init__(self, parent, id, title, metadata=None):
		wx.Frame.__init__(self, parent, id, title)
		self.subj             = 0
		self.metadata         = metadata
		self.panel            = None
		sizer                 = self._create_panels()
		self._create_statusbar()
		self.SetSizer(sizer)
		self.Fit()
		self.Centre()
		self.plot()

	def _create_panels(self):
		self.panel = CheckMeansPanel(self, size=(400,500))
		panel_nav  = CheckMeansNavigationControls(self, size=(200,50))
		if self.metadata.nSubj<2:
			panel_nav.button_back.Enable(False)
			panel_nav.button_forward.Enable(False)
		button      = wx.Button(self, -1, 'Save as PNG', (50, 130))
		# self.slider = wx.Slider(self, -1, 500, 200, 1000, pos=(10, 10), size=(500, 100), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
		### add to a sizer:
		# sizerH     = wx.BoxSizer(wx.HORIZONTAL)
		# sizerH.Add(self.slider, 1)
		# sizerH.Add(button, 1)
		sizer      = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.panel, 10, flag=wx.EXPAND)
		sizer.Add(button, 1, flag=wx.CENTER)
		# sizer.Add(sizerH, 1, flag=wx.CENTER)
		sizer.Add(panel_nav, 1, flag=wx.EXPAND)
		button.Bind(wx.EVT_BUTTON, self.save_png)
		# self.slider.Bind(wx.EVT_SLIDER, self.callback_slider)
		return sizer
		
	def _create_statusbar(self):
		self.statusbar = self.CreateStatusBar(style=wx.BORDER_DOUBLE)
		self.statusbar.SetFieldsCount(2)
		self.statusbar.SetStatusWidths([-2,-6])
		self.set_statusbar_text()
		
		
	def back(self):
		self.statusbar.SetStatusText('(Loading data...)', 1)
		if self.subj - 1 < 0:
			self.subj = self.metadata.nSubj - 1
		else:
			self.subj -= 1
		self.plot()
		self.set_statusbar_text()

	
	# def callback_slider(self, event):
	# 	pass
	
	def forward(self):
		self.statusbar.SetStatusText('(Loading data...)', 1)
		if self.subj + 1 == self.metadata.nSubj:
			self.subj = 0
		else:
			self.subj += 1
		self.plot()
		self.set_statusbar_text()
		
	
	def plot(self):
		self.panel.cla()
		I   = self.metadata.load_means(self.subj, stacked=True)
		self.panel.plot(I)
		
	
	def quit(self):
		self.Destroy()
		
	def save_png(self, event):
		fname  = '%s_means.png' %self.metadata.USUBJ[self.subj]
		dialog = wx.FileDialog(self, 'Save as...', os.path.curdir, defaultFile=fname, style=wx.FD_SAVE|wx.FD_CHANGE_DIR)
		if dialog.ShowModal() == wx.ID_OK:
			fname1 = dialog.GetPath()
			os.chdir( os.path.split(fname1)[0] )
			self.panel.figure.savefig(fname1)
	
	def set_statusbar_text(self):
		self.statusbar.SetStatusText('Subj %d of %d'%(self.subj+1,self.metadata.nSubj), 0)
		self.statusbar.SetStatusText(self.metadata.USUBJ[self.subj], 1)




# class MyApp(wx.App):
# 	def OnInit(self):
# 		import pressure_database as DB;  reload(DB)
# 		dir0     = '/Volumes/DataProc/projectsExternal/uQueensland/test_project/'
# 		metadata = DB.load_metadata(dir0)
# 		frame = CheckMeansFrame(None, -1, 'Check means', metadata=metadata)
# 		frame.Show(True)
# 		self.SetTopWindow(frame)
# 		return True
# #run app:
# app = MyApp(redirect=False)
# app.MainLoop()

