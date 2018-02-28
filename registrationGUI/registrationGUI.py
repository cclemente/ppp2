
from math import ceil
import os,wx
from registrationGUI_panels import RegistrationPanel
from registrationGUI_navigation import RegistrationNavigationControls
import pressure_module as PM



class RegistrationFrame(wx.Frame):
	def __init__(self, parent, id, title, metadata=None, subj=0, LR=0, FH=0):
		wx.Frame.__init__(self, parent, id, title)
		self.PARAMS       = metadata.load_registration_params()
		self.metadata     = metadata
		self.subj         = subj
		self.LR           = LR
		self.FH           = FH
		self.currrollover = 0
		self.panel        = None
		self.rollovers    = None
		self.nRollovers   = None
		self.stepnums     = None
		self.template     = None
		self.template_msg_shown = False
		self.xmlfilenames = None
		self.I0           = None
		self.I            = None
		self._get_rollovers()
		self._load_template()
		sizer             = self._create_panels()
		self._create_statusbar()
		self.SetSizer(sizer)
		self.Fit()
		self.Centre()
		self.plot()
		

	def _create_panels(self):
		### create panels:
		self.panel         = RegistrationPanel(self, size=(1000,600))
		# self.panel.Bind(wx.EVT_KEY_DOWN, self.callback_key)
		# return None


		self.button_revert = wx.Button(self, -1, 'Revert to original image',  (800, 50))
		self.slider        = wx.Slider(self, -1, 5, 0, 100, pos=(10, 10), size=(500, 50), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )


		# self.slider.SetTickFreq(20, 1)
		panel_nav          = RegistrationNavigationControls(self, size=(800,50))
		### add to a sizer:
		sizerh             = wx.BoxSizer(wx.HORIZONTAL)
		sizerh.Add(self.slider, 1)
		sizerh.Add(self.button_revert, 1)
		sizer              = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.panel, 10, flag=wx.EXPAND)
		sizer.Add(sizerh, 1, flag=wx.CENTER)
		sizer.Add(panel_nav, 1, flag=wx.EXPAND)
		self.button_revert.Bind(wx.EVT_BUTTON, self.callback_revert)
		self.slider.Bind(wx.EVT_SLIDER, self.callback_slider)
		return sizer
		



	def _create_statusbar(self):
		self.statusbar = self.CreateStatusBar(style=wx.BORDER_DOUBLE)
		self.statusbar.SetFieldsCount(3)
		self.statusbar.SetStatusWidths([-5,-1,-3])
		
	
	def _get_rollovers(self):
		self.rollovers    = self.metadata.get_rollovers(self.subj, LR=self.LR, FH=self.FH, only_good=True)
		self.nRollovers   = self.rollovers.size
		self.xmlfilenames = self.metadata.get_xmlfilenames_from_rollovers(self.rollovers, with_path=False)
		self.stepnums     = self.metadata.get_stepnums_from_rollovers(self.rollovers)
		
	def _load_template(self):
		self.template  = self.metadata.get_template(self.subj, LR=self.LR, FH=self.FH)
		self.I0 = self.metadata.load_rollover(self.template, dbdir='dbr')
	
		
	def back(self):
		self.statusbar.SetStatusText('(Loading data...)', 2)
		self.save_current_params()
		i = self.currrollover
		if i - 1 < 0:
			i = self.nRollovers - 1
		else:
			i -= 1
		self.currrollover = i
		self.plot()

	
	
	def callback_revert(self, event):
		i     = self.rollovers[self.currrollover]
		self.PARAMS[i]  = [0,0,0,1]
		self.plot()
	
	def callback_slider(self, event):
		self.plot_template()
	
	
	def forward(self):
		self.statusbar.SetStatusText('(Loading data...)', 2)
		self.save_current_params()
		i = self.currrollover
		if i + 1 == self.nRollovers:
			i = 0
		else:
			i += 1
		self.currrollover = i
		self.plot()
		
	def load_source(self):
		i   = self.rollovers[self.currrollover]
		I   = self.metadata.load_rollover(i, dbdir='dbr', max=True)
		self.panel.set_Iq(I, self.PARAMS[i])
		return I
	
	
	def plot(self):
		self.panel.cla()
		self.load_source()
		self.panel.plot()
		self.plot_template()
		self.set_statusbar_text()
		i   = self.rollovers[self.currrollover]
		if (i == self.template) and (not self.template_msg_shown):
			wx.MessageBox('The current rollover is the template.\nDO NOT TRANSFORM THIS IMAGE!\n\nThis message will not be shown again during this registration session.', 'Warning:', wx.OK)
			self.template_msg_shown = True
		self.panel.SetFocus()

		
	def plot_template(self):
		th   = self.slider.GetValue()
		self.panel.plot_template(self.I0, th)
	
	
	def quit(self):
		#save transformation parameters:
		result = wx.MessageBox('Pressing OK will overwrite registration parameters from previous session.\n\nOK to continue?', 'Warning:', wx.OK|wx.CANCEL)
		if result == wx.OK:
			self.metadata.save_registration_parameters(self.PARAMS)
		self.Destroy()
		

	def save_current_params(self):
		i     = self.rollovers[self.currrollover]
		self.PARAMS[i] = self.panel.q

	
	def set_statusbar_text(self):
		ind     = self.currrollover
		fname   = self.xmlfilenames[ind]
		stepnum = self.stepnums[ind]
		msg     = '%s,   Step: %d'%(fname,stepnum)
		self.statusbar.SetStatusText(msg, 0)
		self.statusbar.SetStatusText('%d of %d'%(ind+1,self.nRollovers), 1)
		self.statusbar.SetStatusText('', 2)




#class MyApp(wx.App):
#        def OnInit(self):
# 		import pressure_database as DB;  reload(DB)
# 		dir0     = 'c:\Temp\plantar_pressure_processing\test2'
# 		metadata = DB.load_metadata(dir0)
# 		# PARAMS    = metadata.load_registration_params()
# 		# PARAMS[0] = [5,0,0,1]
# 		# print PARAMS
# 		# metadata.save_registration_parameters()
# 		frame = RegistrationFrame(None, -1, 'Registration', metadata=metadata, subj=0, LR=0, FH=0)
# 		frame.Show(True)
# 		self.SetTopWindow(frame)
# 		return True
# #run app:
#app = MyApp(redirect=False)
#app.MainLoop()

