
from math import ceil
import os,wx
from templateGUI_panels import TemplateSingleStepPanel
from templateGUI_navigation import TemplateNavigationControls


class TemplateFrame(wx.Frame):
	def __init__(self, parent, id, title, metadata=None):
		wx.Frame.__init__(self, parent, id, title)
		self.CHOICES         = metadata.load_template_choices()
		self.currchoices     = self.CHOICES[0]
		self.metadata        = metadata
		self.nRollovers      = None
		self.panels          = None
		self.rollovers       = None
		self.stepnums        = None
		self.subj            = None
		self.xmlfilenames    = None
		sizer                = self._create_panels()
		self._create_statusbar()
		self.SetSizer(sizer)
		self.Fit()
		self.Centre()
		self.set_subject(0)
		

	def _create_panels(self):
		### create steps panels:
		sizer0             = wx.BoxSizer(wx.HORIZONTAL)
		self.panels        = [TemplateSingleStepPanel(self, size=(200,340))  for i in range(4)]
		[sizer0.Add(panel, 1, flag=wx.EXPAND) for panel in self.panels]
		panel_nav  = TemplateNavigationControls(self, size=(200,50))
		### add to a sizer:
		sizer      = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(sizer0, 5, flag=wx.EXPAND)
		sizer.Add(panel_nav, 1, flag=wx.EXPAND)
		return sizer
		
	def _create_statusbar(self):
		self.statusbar = self.CreateStatusBar(style=wx.BORDER_DOUBLE)
		self.statusbar.SetFieldsCount(3)
		self.statusbar.SetStatusWidths([-5,-1,-3])
		
		
		
	def _get_rollovers(self):
		# get rollover numbers:
		r0   = self.metadata.get_rollovers(self.subj, LR=0, FH=0, only_good=True)
		r1   = self.metadata.get_rollovers(self.subj, LR=1, FH=0, only_good=True)
		r2   = self.metadata.get_rollovers(self.subj, LR=0, FH=1, only_good=True)
		r3   = self.metadata.get_rollovers(self.subj, LR=1, FH=1, only_good=True)
		# get xml file names:
		f0   = self.metadata.get_xmlfilenames_from_rollovers(r0, with_path=False)
		f1   = self.metadata.get_xmlfilenames_from_rollovers(r1, with_path=False)
		f2   = self.metadata.get_xmlfilenames_from_rollovers(r2, with_path=False)
		f3   = self.metadata.get_xmlfilenames_from_rollovers(r3, with_path=False)
		# get sequence numbers:
		n0   = self.metadata.get_stepnums_from_rollovers(r0)
		n1   = self.metadata.get_stepnums_from_rollovers(r1)
		n2   = self.metadata.get_stepnums_from_rollovers(r2)
		n3   = self.metadata.get_stepnums_from_rollovers(r3)
		# assemble all:
		self.rollovers    = [r0, r1, r2, r3]
		self.xmlfilenames = [f0, f1, f2, f3]
		self.stepnums     = [n0, n1, n2, n3]
		self.nRollovers   = [len(r) for r in self.rollovers]
	
	
	def back(self):
		self.statusbar.SetStatusText('(Loading data...)', 2)
		subj  = self.subj
		if subj - 1 < 0:
			subj = self.metadata.nSubj - 1
		else:
			subj -= 1
		self.set_subject(subj)

	
	def forward(self):
		self.statusbar.SetStatusText('(Loading data...)', 2)
		subj  = self.subj
		if subj + 1 == self.metadata.nSubj:
			subj = 0
		else:
			subj += 1
		self.set_subject(subj)
		
	
	def panel_enter(self, event, panel=None):
	        if not panel:
	            panel = event.EventObject
		ind   = self.panels.index(  panel  )
		choice  = self.currchoices[ind]
		fname   = self.xmlfilenames[ind][choice]
		stepnum = self.stepnums[ind][choice]
		msg     = '%s,   Step: %d'%(fname,stepnum)
		self.statusbar.SetStatusText(msg, 0)
	
	def panel_leave(self, event):
		self.statusbar.SetStatusText('', 0)
		
	
	def plot_all(self):
		[panel.cla() for panel in self.panels]
		rollovers = [r[c]  for r,c in zip(self.rollovers,self.currchoices)]
		II        = self.metadata.load_rollovers( rollovers, dbdir='dbr' )
		for panel,I,c,n in zip(self.panels, II, self.currchoices, self.nRollovers):
			panel.plot(I)
			panel.text.SetLabel('%d of %d'%(c+1,n))
			
	
	def quit(self):
		result = wx.MessageBox('Previously specified template trials will be overwritten. OK to proceed?', 'Confirm overwrite', wx.OK | wx.CANCEL)
		if result==wx.OK:
			self.metadata.save_template_choices(self.CHOICES)
		self.Destroy()
		
	def update(self, panel, dirn):
		ind     = self.panels.index(  panel  )
		nTotal  = self.nRollovers[ind]
		choice  = self.currchoices[ind]
		panel.cla()
		if dirn==1:
			if choice+1 == nTotal:
				choice = 0
			else:
				choice += 1
		else:
			if choice-1 < 0:
				choice = nTotal - 1
			else:
				choice -= 1
		self.currchoices[ind] = choice
		### plot:
		rollover  = self.rollovers[ind][choice]
		I         = self.metadata.load_rollover( rollover, dbdir='dbr' )
		panel.plot(I)
		panel.text.SetLabel('%d of %d'%(choice+1,nTotal))
		self.CHOICES[self.subj][ind] = choice

	def set_subject(self, subj):
		self.subj        = subj
		self.currchoices = self.CHOICES[self.subj]
		self._get_rollovers()
		self.plot_all()
		self.set_statusbar_text()
		
	
	def set_statusbar_text(self):
		self.statusbar.SetStatusText('Subj %d of %d'%(self.subj+1,self.metadata.nSubj), 1)
		self.statusbar.SetStatusText(self.metadata.USUBJ[self.subj], 2)




#class MyApp(wx.App):
# 	def OnInit(self):
# 		import pressure_database as DB;  reload(DB)
# 		#dir0     = '/Volumes/DataProc/projectsExternal/uQueensland/test_project/'
# 		dir0     = 'C:\Users\uqopanag\Documents\FOOT PRESSURE EXPERIMENTS_ZEBRIS\plantar_pressure_processing\ppp_camel_project'
# 		metadata = DB.load_metadata(dir0)
#
# 		import numpy as np
#
# 		subj = 0
# 		# n = metadata.get_nrollovers_by_subj(subj, only_good=True)
# 		# labels  = ['Fore Left', 'Fore Right', 'Hind Left', 'Hind Right']
# 		#
# 		# if np.any( np.array(n)<2 ):
# 		# 	ind    = np.argwhere(np.array(n)<2).flatten()
# 		# 	ind    = ind[0]
# 		# 	label  = labels[ind]
# 		# 	result = wx.MessageBox('No good rollovers found for subject "%s", foot: "%s".\nYou must identify at least one good rollover to proceed.'%(metadata.USUBJ[subj], label), 'Error', wx.OK)
#
# 		# subj = 0
# 		# assemble all rollovers for each foot:
#
#
#
# 		# fid  = [0,2]
# 		# rollovers = metadata.get_rollovers(subj, LR=False, FH=True)
# 		# rollovers = metadata.get_rollovers(subj, fid=[0,2], group_by_trial=True)
# 		# rollovers = metadata.get_rollovers(subj)
# 		# print rollovers
#
# 		frame = TemplateFrame(None, -1, 'Choose templates', metadata=metadata)
# 		frame.Show(True)
# 		self.SetTopWindow(frame)
# 		return True
#
#
#
##run app:
#app = MyApp(redirect=False)
#app.MainLoop()

