
import wx
import pressure_database as DB;  reload(DB)



class PPDatabaseQueryDialog(wx.Dialog):
	def __init__(self, metadata, by_trial=False, by_foot=False, only_good=False):
		wx.Dialog.__init__(self, None, -1, 'Database query', size=(500,300))
		
		self.canceled   = False
		self.fnames,fid = metadata.get_xmlfilenames_from_subj(0, with_path=False)
		self.fids       = fid
		self.nFiles     = len(self.fnames)
		self.metadata   = metadata
		self.only_good  = only_good
		
		
		text0           = wx.StaticText(self, label='Subject', pos=(10, 10))
		text1           = wx.StaticText(self, label='Select by...', pos=(180, 10))

		choices_subj   = ['(%d)  %s'%(i,s) for i,s in enumerate(metadata.USUBJ)]
		choices_by     = ['Foot', 'Trial']
		choices_foot   = ['Fore Left', 'Fore Right', 'Hind Left', 'Hind Right']
		choices_trials = ['All trials (total: %d)'%self.nFiles, 'Single trial(s)']
		list_trials    = self.fnames
		self.choice_subj   = wx.Choice(self, choices=choices_subj, pos=(10,30))
		self.choice_by     = wx.Choice(self, choices=choices_by, pos=(180,30))
		self.choice_foot   = wx.Choice(self, choices=choices_foot, pos=(80,100))
		self.choice_trials = wx.Choice(self, choices=choices_trials, pos=(50,100))
		self.list_trials   = wx.ListBox(self, choices=list_trials, pos=(50,130), style=wx.LB_MULTIPLE|wx.LB_ALWAYS_SB)
		
		
		self.choice_trials.Show(False)
		self.list_trials.Show(False)
		
		
		
		button0      = wx.Button(self, -1, 'Cancel', pos=(300,230))
		button1      = wx.Button(self, -1, 'OK', pos=(400,230))
		button0.Bind(wx.EVT_BUTTON, self.onButtonCancel)
		button1.Bind(wx.EVT_BUTTON, self.onButtonOK)
		self.choice_subj.Bind(wx.EVT_CHOICE, self.onChoiceSubj)
		self.choice_by.Bind(wx.EVT_CHOICE, self.onChoiceBy)
		self.choice_trials.Bind(wx.EVT_CHOICE, self.onChoiceTrial)
		

		
		self.choice_subj.Select(0)
		self.choice_foot.Select(0)
		self.choice_by.Select(0)
		self.choice_trials.Select(0)
		self.list_trials.Select(0)
		
		if by_trial:
			self.choice_by.SetSelection(1)
			self.choice_by.Enable(False)
			self.choice_foot.Show(False)
			self.choice_trials.Show(True)
			
			
		elif by_foot:
			self.choice_by.SetSelection(0)
			self.choice_by.Enable(False)
			
			
		
		
		### layout:
		sizer0        = wx.BoxSizer(wx.VERTICAL)
		sizer0.Add(text0, 1, flag=wx.EXPAND)
		sizer0.Add(self.choice_subj, 10, flag=wx.EXPAND)		
		
		sizer1        = wx.BoxSizer(wx.VERTICAL)
		sizer1.Add(text1, 1, flag=wx.EXPAND)
		sizer1.Add(self.choice_by, 1, flag=wx.EXPAND)
		sizer1.Add(self.choice_foot, 2, flag=wx.EXPAND)
		sizer1.Add(self.choice_trials, 2, flag=wx.EXPAND)
		sizer1.Add(self.list_trials, 10, flag=wx.EXPAND)
		
		sizerButtons  = wx.BoxSizer(wx.HORIZONTAL)
		sizerButtons.Add(button0, 1, flag=wx.CENTER)	
		sizerButtons.Add(button1, 1, flag=wx.CENTER)	
		
		
		sizerH        = wx.BoxSizer(wx.HORIZONTAL)
		sizerH.Add(sizer0, 1, flag=wx.ALL)
                sizerH.Add(sizer1, 1, flag=wx.ALL)		
          	
          	
          	sizer         = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(sizerH, 10, flag=wx.ALL)
		sizer.Add(sizerButtons, 1, flag=wx.ALL|wx.CENTER)
		self.SetSizer(sizer)
		self.Fit()
		self.Centre()
		
		
		
	def get_choices(self):
		footLR    = [0, 1, 0, 1]
		footFH    = [0, 0, 1, 1]
		subj      = self.choice_subj.GetSelection()
		byfoot    = not bool( self.choice_by.GetSelection() )
		foot      = self.choice_foot.GetSelection()
		LR        = bool(footLR[foot])
		FH        = bool(footFH[foot])
		alltrials = not self.choice_trials.GetSelection()
		trials    = list(self.list_trials.GetSelections())
		return subj,byfoot,LR,FH,alltrials,trials
	
	def get_rollovers(self, group_by_trial=True):
		subj,byfoot,LR,FH,alltrials,trials = self.get_choices()
		if byfoot:
			rollovers = self.metadata.get_rollovers(subj, LR=LR, FH=FH, only_good=self.only_good)
		elif alltrials:
			rollovers = self.metadata.get_rollovers(subj, group_by_trial=group_by_trial, only_good=self.only_good)
		else:
			rollovers = self.metadata.get_rollovers(subj, fid=self.fids[trials].tolist(), group_by_trial=group_by_trial, only_good=self.only_good)
		return rollovers
	
	def onButtonCancel(self, event):
		self.canceled = True
		self.Close()
	def onButtonOK(self, event):
		self.Close()
	def onChoiceBy(self, event):
		if self.choice_by.GetSelection()==0:
			self.choice_foot.Show(True)
			self.choice_trials.Show(False)
			self.list_trials.Show(False)
		else:
			self.choice_foot.Show(False)
			self.choice_trials.Show(True)
			if self.choice_trials.GetSelection()==0:
                                self.list_trials.Show(False)
                        else:
                                self.list_trials.Show(True)
		self.Fit()
	def onChoiceSubj(self, event):
		subj            = self.choice_subj.GetSelection()
		selection       = self.choice_trials.GetSelection()
		self.fnames,fid = self.metadata.get_xmlfilenames_from_subj(subj, with_path=False)
		self.fids       = fid
		self.nFiles     = len(self.fnames)
		choices_trials  = ['All trials (total: %d)'%self.nFiles, 'Single trial(s)']
		self.choice_trials.SetItems(choices_trials)
		self.choice_trials.SetSelection(selection)
		self.list_trials.SetItems(self.fnames)
		self.list_trials.Select(0)
		self.Fit()
	
	def onChoiceTrial(self, event):
		if self.choice_trials.GetSelection()==0:
			self.list_trials.Show(False)
		else:
			self.list_trials.Show(True)
		self.Fit()


##run app:
##dir0     = '/Volumes/DataProc/projectsExternal/uQueensland/test_project/'
#dir0     = 'C:\Users\uqopanag\Documents\FOOT PRESSURE EXPERIMENTS_ZEBRIS\plantar_pressure_processing\ppp_camel_project'
#metadata = DB.load_metadata(dir0)
#
#
#app = wx.PySimpleApp(redirect=False)
#app.MainLoop()
#dialog = PPDatabaseQueryDialog(metadata, by_foot=False, by_trial=True)
#dialog.ShowModal()
#if not dialog.canceled:
#	# subj,byfoot,LR,FH,alltrials,trials = dialog.get_choices()
# 	# print subj,byfoot,LR,FH,alltrials
# 	# print trials
# 	# print
#    rollovers = dialog.get_rollovers(group_by_trial=True)
#    print rollovers
#
#dialog.Destroy()



	