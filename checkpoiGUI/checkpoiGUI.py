
from math import ceil
import os,wx
import numpy as np
from checkpoiGUI_panels import CheckPOISingleStepPanel
from checkpoiGUI_navigation import CheckPOINavigationControls


class CheckPOIFrame(wx.Frame):
	def __init__(self, parent, id, title, metadata=None, subj=0, LR=0, FH=0):
		wx.Frame.__init__(self, parent, id, title)
		self.metadata         = metadata
		self.POI              = None
		self.subj             = subj
		self.LR               = LR
		self.FH               = FH
		self.currgroup        = 0
		self.currrollovers    = None
		self.currrolloverinds = None
		self.rollovers        = None
		self.nRollovers       = None
		self.panels           = None
		self._init_rollovers()
		self.nGroups          = int( ceil(self.nRollovers / 10.0)  )
		self.stepnums         = self.metadata.get_stepnums_from_rollovers(self.rollovers)
		self.xmlfilenames     = self.metadata.get_xmlfilenames_from_rollovers(self.rollovers, with_path=False)
		sizer                 = self._create_panels()

		self._get_pois()
		self._create_statusbar()
		self.SetSizer(sizer)
		self.Fit()
		self.Centre()
		self.set_current_rollovers()
		self.plot_group()

	def _get_pois(self):
		POI    = self.metadata.load_pois()[self.subj]
		if (not self.LR) and (not self.FH):
			POI = POI[0]
		elif self.LR and (not self.FH):
			POI = POI[1]
		elif (not self.LR) and self.FH:
			POI = POI[2]
		else:
			POI = POI[3]
		if POI != None:
			POI  = np.asarray(POI)
		self.POI  = POI
	
	def _init_rollovers(self):
		self.rollovers        = self.metadata.get_rollovers(self.subj, LR=self.LR, FH=self.FH, only_good=True)
		self.nRollovers       = self.rollovers.size
		template              = self.metadata.get_template(self.subj, LR=self.LR, FH=self.FH)
		self.I0               = self.metadata.load_rollover(template, dbdir='dbrr')

	def _create_panels(self):
		### create steps panels:
		sizer_steps0       = wx.BoxSizer(wx.HORIZONTAL)
		sizer_steps1       = wx.BoxSizer(wx.HORIZONTAL)
		self.panels_steps0 = [CheckPOISingleStepPanel(self, size=(200,340))  for i in range(5)]
		self.panels_steps1 = [CheckPOISingleStepPanel(self, size=(200,340))  for i in range(5)]
		self.panels        = self.panels_steps0 + self.panels_steps1
		[sizer_steps0.Add(panel, 1, flag=wx.EXPAND) for panel in self.panels_steps0]
		[sizer_steps1.Add(panel, 1, flag=wx.EXPAND) for panel in self.panels_steps1]

		### create navigation panel:
		panel_nav  = CheckPOINavigationControls(self, size=(200,50))
		if self.nGroups<2:
			panel_nav.button_back.Enable(False)
			panel_nav.button_forward.Enable(False)

		### add to a sizer:
		sizer      = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(sizer_steps0, 5, flag=wx.EXPAND)
		sizer.Add(sizer_steps1, 5, flag=wx.EXPAND)
		sizer.Add(panel_nav, 1, flag=wx.EXPAND)
		return sizer
		
	def _create_statusbar(self):
		self.statusbar = self.CreateStatusBar(style=wx.BORDER_DOUBLE)
		self.statusbar.SetFieldsCount(3)
		self.statusbar.SetStatusWidths([-5,-1,-3])
		self.set_statusbar_text()
		
		
	def back(self):
		self.statusbar.SetStatusText('(Loading data...)', 2)
		if self.currgroup - 1 < 0:
			self.currgroup = self.nGroups - 1
		else:
			self.currgroup -= 1
		self.set_current_rollovers()
		self.plot_group()
		self.set_statusbar_text()

	
	def forward(self):
		self.statusbar.SetStatusText('(Loading data...)', 2)
		if self.currgroup + 1 == self.nGroups:
			self.currgroup = 0
		else:
			self.currgroup += 1
		self.set_current_rollovers()
		self.plot_group()
		self.set_statusbar_text()
		
	
	def panel_enter(self, event, panel=None):
	        if not panel:
	            panel = event.EventObject
		ind   = self.panels.index(  panel  )
		if ind < len(self.currrollovers):
			i       = self.currrolloverinds[ind]
			fname   = self.xmlfilenames[i]
			stepnum = self.stepnums[i]
			msg     = '%s,   Step: %d'%(fname,stepnum)
			self.statusbar.SetStatusText(msg, 0)
	
	def panel_leave(self, event):
		self.statusbar.SetStatusText('', 0)
		
	
	def plot_group(self):
		[panel.cla() for panel in self.panels]
		rollovers = self.currrollovers
		II        = self.metadata.load_rollovers( rollovers, dbdir='dbrr' )
		cmax      = max([I.max()  for I in II])
		for panel,I in zip(self.panels, II):
			panel.plot(self.I0, I, cmax=cmax, pois=self.POI)
	
	def quit(self):
		self.Destroy()
		
	def set_current_rollovers(self):
		i0                    = self.currgroup * 10
		self.currrollovers    = self.rollovers[i0:i0+10]
		self.currrolloverinds = range(i0,i0+10)
	
	def set_statusbar_text(self):
		self.statusbar.SetStatusText('Page %d of %d'%(self.currgroup+1,self.nGroups), 1)
		self.statusbar.SetStatusText('', 2)




# class MyApp(wx.App):
#        def OnInit(self):
# 		import pressure_database as DB;  reload(DB)
# 		#dir0     = '/Volumes/DataProc/projectsExternal/uQueensland/test_project/'
# 		# dir0     = 'C:\Users\uqopanag\Documents\FOOT PRESSURE EXPERIMENTS_ZEBRIS\plantar_pressure_processing\ppp_camel_project'
# 		dir0  = '/Users/todd/Desktop/test2'
# 		metadata = DB.load_metadata(dir0)
# 		subj = 1
# 		LR   = 1
# 		FH   = 1
# 		frame = CheckPOIFrame(None, -1, 'Check POIs (%s: %s)', metadata=metadata, subj=subj, LR=LR, FH=FH)
# 		frame.Show(True)
# 		self.SetTopWindow(frame)
# 		return True
# #run app:
# app = MyApp(redirect=False)
# app.MainLoop()

