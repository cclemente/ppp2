
from math import ceil
import os,wx
import identifyGUI_panels as IP
import identifyGUI_navigation as IN



class IdentifyFrame(wx.Frame):
	def __init__(self, parent, id, title, metadata=None, rollovers=None):
		wx.Frame.__init__(self, parent, id, title)
		self.currtrial       = 0
		self.metadata        = metadata
		self.rollover_groups = rollovers
		self.nTrials         = len(self.rollover_groups)
		self.panels_steps    = None
		sizer                = self._create_panels()
		self._create_statusbar()
		self.SetSizer(sizer)
		self.Fit()
		self.Centre()
		self.plot_trial()

	def _create_panels(self):
		### create steps panels:
		sizer_steps0       = wx.BoxSizer(wx.HORIZONTAL)
		sizer_steps1       = wx.BoxSizer(wx.HORIZONTAL)
		self.panels_steps0 = [IP.IdentifySingleStepPanel(self, size=(200,340))  for i in range(5)]
		self.panels_steps1 = [IP.IdentifySingleStepPanel(self, size=(200,340))  for i in range(5)]
		self.panels_steps  = self.panels_steps0 + self.panels_steps1
		[sizer_steps0.Add(panel, 1, flag=wx.EXPAND) for panel in self.panels_steps0]
		[sizer_steps1.Add(panel, 1, flag=wx.EXPAND) for panel in self.panels_steps1]
		### create navigation panel:
		panel_nav  = IN.IdentifyNavigationControls(self, size=(200,50))
		if self.nTrials==1:
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
		self.save_metadata()
		if (self.currtrial - 1) < 0:
			self.currtrial = self.nTrials - 1
		else:
			 self.currtrial -= 1
		self.plot_trial()
		self.set_statusbar_text()
	
	def forward(self):
		self.statusbar.SetStatusText('(Loading data...)', 2)
		self.save_metadata()
		if (self.currtrial + 1) >= self.nTrials:
			self.currtrial = 0
		else:
			 self.currtrial += 1
		self.plot_trial()
		self.set_statusbar_text()
	
	def get_rollover_metadata(self, rollovers):
		good  = self.metadata.GOOD[rollovers]
		lr    = self.metadata.LR[rollovers]
		fh    = self.metadata.FH[rollovers]
		return good,lr,fh
	
	def get_xmlfilename(self, rollover_group):
		fname = self.metadata.get_xmlfilenames_from_rollovers(rollover_group)
		path,fname = os.path.split(fname[0])
		return path,fname
		
	def load_images(self):
		rollovers  = self.rollover_groups[self.currtrial]
		II         = self.metadata.load_rollovers( rollovers, dbdir='dbr' )
		return II
	
	def plot_trial(self):
		[panel.cla() for panel in self.panels_steps]
		[panel.enable(False)  for panel in self.panels_steps]
		II          = self.load_images()
		cmax        = max([I.max()  for I in II])
		GOOD,LR,FH  = self.get_rollover_metadata(  self.rollover_groups[self.currtrial]  )
		for panel,I,good,lr,fh in zip(self.panels_steps,II,GOOD,LR,FH):
			panel.plot(I, cmax=cmax)
			panel.enable(True)
			panel.set_metadata_controls(good, lr, fh)
	
	def set_statusbar_text(self):
		path,fname     = self.get_xmlfilename(self.rollover_groups[self.currtrial])
		self.statusbar.SetStatusText('%s'%path, 0)
		self.statusbar.SetStatusText('%d of %d'%(self.currtrial+1,self.nTrials), 1)
		self.statusbar.SetStatusText('%s'%fname, 2)
		
	def save_metadata(self):
		rollovers  = self.rollover_groups[self.currtrial]
		for panel,i in zip(self.panels_steps, rollovers):
			good,lr,fh = panel.get_metadata()
			self.metadata.GOOD[i] = good
			self.metadata.LR[i]   = lr
			self.metadata.FH[i]   = fh
		
	def quit(self):
		result = wx.MessageBox('Metadata files will be overwritten. OK to proceed?', 'Confirm overwrite', wx.OK | wx.CANCEL)
		if result==wx.OK:
		        self.save_metadata()
			self.metadata.save()
			self.metadata.savexls()
		self.Destroy()




# class MyApp(wx.App):
# 	def OnInit(self):
# 		import pressure_database as DB;  reload(DB)
# 		dir0     = '/Volumes/DataProc/projectsExternal/uQueensland/test_project/'
# 		metadata = DB.load_metadata(dir0)
# 		subj = 1
# 		fid  = [0,2]
# 		# rollovers = metadata.get_rollovers(subj, LR=False, FH=True)
# 		# rollovers = metadata.get_rollovers(subj, fid=[0,2], group_by_trial=True)
# 		rollovers = metadata.get_rollovers(subj, group_by_trial=True)
# 		# print rollovers
#
# 		frame = IdentifyFrame(None, -1, 'Step Selection and Foot Identificaiton', metadata=metadata, rollovers=rollovers)
# 		frame.Show(True)
# 		self.SetTopWindow(frame)
# 		return True
#
#
#
# #run app:
# app = MyApp(redirect=False)
# app.MainLoop()

