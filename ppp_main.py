
#version 0.0.0003  (2014.09.17)

#v.0.0.0003:   implemented POI functionality
#v.0.0.0002:   fixed a bug in ApplyParameters which ignored negative parameters

import os,wx
import numpy as np
import checkfeetGUI
import checkmeansGUI
import checkpoiGUI
import checkregistrationGUI
import identifyGUI
import poiGUI
import ppp_selector
import pressure_database as DB
import pressure_module as PM
import registrationGUI
from settings import Settings
import templateGUI


class PPMainPanel(wx.Panel):
	def __init__(self,parent,ID=-1,label="",pos=wx.DefaultPosition,size=(100,25)):
		#(0) Initialize panel:
		wx.Panel.__init__(self,parent,ID,pos,size,wx.STATIC_BORDER,label)
		self.SetMinSize(size)
		self.dir0     = None
		self.settings = None
		self._parse_settings()
		self.metadata = None
		self.parent   = parent
		#create controls:
		button0       = wx.Button(self, -1, 'Set project directory',  (50, 100))
		lineA         = wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL)
		button1       = wx.Button(self, -1, 'Resize image grids',  (50, 100))
		button2       = wx.Button(self, -1, 'Identify feet',  (50, 100))
		buttonA       = wx.Button(self, -1, 'Select templates',  (50, 100))
		button3       = wx.Button(self, -1, 'Register (determine parameters)',  (50, 100))
		buttonB       = wx.Button(self, -1, 'Register (apply parameters)',  (50, 100))
		buttonPOI     = wx.Button(self, -1, 'POI analysis',  (50, 100))
		line0         = wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL)
		button4       = wx.Button(self, -1, 'Export means',  (50, 100))
		buttonC       = wx.Button(self, -1, 'Export COP',  (50, 100))
		line1         = wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL)
		button5       = wx.Button(self, -1, 'Check foot labels',  (50, 100))
		button6       = wx.Button(self, -1, 'Check registration',  (50, 100))
		button7       = wx.Button(self, -1, 'Check means',  (50, 100))
		button8       = wx.Button(self, -1, 'Check POIs',  (50, 100))
		line2         = wx.StaticLine(self, -1, style=wx.LI_HORIZONTAL)
		buttonQuit    = wx.Button(self, -1, 'Quit',  (50, 100))
		#layout the controls:
		sizer         = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(button0, 1, flag=wx.EXPAND)
		sizer.Add(lineA, 1, flag=wx.ALL)
		sizer.Add(button1, 1, flag=wx.EXPAND)
		sizer.Add(button2, 1, flag=wx.EXPAND)
		sizer.Add(buttonA, 1, flag=wx.EXPAND)
		sizer.Add(button3, 1, flag=wx.EXPAND)
		sizer.Add(buttonB, 1, flag=wx.EXPAND)
		sizer.Add(buttonPOI, 1, flag=wx.EXPAND)
		sizer.Add(line0, 1, flag=wx.ALL)
		sizer.Add(button4, 1, flag=wx.EXPAND)
		sizer.Add(buttonC, 1, flag=wx.EXPAND)
		sizer.Add(line1, 1, flag=wx.ALL)
		sizer.Add(button5, 1, flag=wx.EXPAND)
		sizer.Add(button6, 1, flag=wx.EXPAND)
		sizer.Add(button7, 1, flag=wx.EXPAND)
		sizer.Add(button8, 1, flag=wx.EXPAND)
		sizer.Add(line2, 1, flag=wx.ALL)
		sizer.Add(buttonQuit, 1, flag=wx.EXPAND)
		self.SetSizer(sizer)
		#bind the controls:
		button0.Bind(wx.EVT_BUTTON, self.onButtonSetProjectDirectory)
		button1.Bind(wx.EVT_BUTTON, self.onButtonResize)
		button2.Bind(wx.EVT_BUTTON, self.onButtonIdentify)
		button5.Bind(wx.EVT_BUTTON, self.onButtonCheckFeet)
		buttonA.Bind(wx.EVT_BUTTON, self.onButtonTemplates)
		button3.Bind(wx.EVT_BUTTON, self.onButtonRegister)
		buttonB.Bind(wx.EVT_BUTTON, self.onButtonApplyParams)
		buttonPOI.Bind(wx.EVT_BUTTON, self.onButtonPOI)
		button4.Bind(wx.EVT_BUTTON, self.onButtonExportMeans)
		buttonC.Bind(wx.EVT_BUTTON, self.onButtonExportCOP)
		button6.Bind(wx.EVT_BUTTON, self.onButtonCheckRegistration)
		button7.Bind(wx.EVT_BUTTON, self.onButtonCheckMeans)
		button8.Bind(wx.EVT_BUTTON, self.onButtonCheckPOIs)
		buttonQuit.Bind(wx.EVT_BUTTON, self.onButtonQuit)
		#set enabled state:
		self.button_setdir            = button0
		self.button_resize            = button1
		self.button_identify          = button2
		self.button_templates         = buttonA
		self.button_register          = button3
		self.button_poi               = buttonPOI
		self.button_export            = button4
		self.button_check_db          = button5
		self.button_check_reg         = button6
		self.buttons                  = [button0, button1, button2, buttonA, button3, buttonB, buttonPOI, button4, buttonC, button5, button6, button7, button8, buttonQuit]
		for button in self.buttons[1:-1]:
			button.Enable(False)
		
			
	def _parse_settings(self):
		self.settings  = Settings(__file__)
		self.dir0      = self.settings.dir_project


	
	def onButtonApplyParams(self, event):
		result        = wx.MessageBox('All rollovers will now be transformed and saved in the "dbrr" director.\nThis process may take several minutes to complete.\n\nOK to proceed?', 'Note:', wx.OK|wx.CANCEL)
		if result==wx.OK:
			self.metadata = DB.load_metadata(self.dir0)
			PARAMS        = self.metadata.load_registration_params()
			dir0          = os.path.join(self.dir0, 'dbr')
			dir1          = os.path.join(self.dir0, 'dbrr')
			if not os.path.exists(dir1):
				os.mkdir(dir1)
			dialog    = wx.ProgressDialog("", "Transforming pressure time series and saving to ./dbrr...", maximum=self.metadata.nRollovers, style = wx.PD_ELAPSED_TIME)
			for i in range(self.metadata.nRollovers):
				dialog.Update(i)
				fname0    = os.path.join(dir0, 'rollover%05d.h5'%i)
				fname1    = os.path.join(dir1, 'rollover%05d.h5'%i)
				I         = PM.load(fname0)
				if np.any(   np.abs(PARAMS[i] - [0,0,0,1]) > 1e-5  ):
					I     = PM.transformXYRS(I, PARAMS[i])
				PM.save(fname1, I)
			dialog.Destroy()


	
	
	def onButtonCheckFeet(self, event):
		metadata      = DB.load_metadata(self.dir0)
		self.metadata = metadata
		dialog        = ppp_selector.PPDatabaseQueryDialog(metadata, by_foot=True, only_good=True)
		dialog.ShowModal()
		rollovers = None
		if not dialog.canceled:
			rollovers = dialog.get_rollovers()
		dialog.Destroy()
		if rollovers!=None:
			frame = checkfeetGUI.CheckFeetFrame(None, -1, 'PPP Check Foot Labels', metadata=metadata, rollovers=rollovers)
			frame.Show(True)

	def onButtonCheckMeans(self, event):
 		dir0          = os.path.join(self.dir0, 'dbmeans')
		if not os.path.exists(dir0):
			wx.MessageBox('Means not yet computed.\nUse "Export means" from the main menu.', 'Error:', wx.OK)
		else:
			self.metadata = DB.load_metadata(self.dir0)
			frame = checkmeansGUI.CheckMeansFrame(None, -1, 'PPP Check Means', metadata=self.metadata)
			frame.Show(True)

	def onButtonCheckRegistration(self, event):
 		dir0          = os.path.join(self.dir0, 'dbrr')
		if not os.path.exists(dir0):
			wx.MessageBox('Registration must be conducted and parameters applied before checking registration.', 'Error:', wx.OK)
		else:
			self.metadata = DB.load_metadata(self.dir0)
			dialog        = ppp_selector.PPDatabaseQueryDialog(self.metadata, by_foot=True)
			dialog.ShowModal()
			subj          = None
			if not dialog.canceled:
				canceled  = dialog.canceled
				if not canceled:
					subj,byfoot,LR,FH,alltrials,trials = dialog.get_choices()
			dialog.Destroy()
			if subj!=None:
				subjname  = self.metadata.USUBJ[subj]
				footlabel = self.metadata.get_foot_label(LR, FH)
				frame     = checkregistrationGUI.CheckRegistrationFrame(None, -1, 'PPP Check Registration (%s: %s)'%(subjname,footlabel), metadata=self.metadata, subj=subj, LR=LR, FH=FH)
	 			frame.Show(True)


	def onButtonCheckPOIs(self, event):
		dir0          = os.path.join(self.dir0, 'dbrr')
		if not os.path.exists(dir0):
			wx.MessageBox('Registration must be conducted and parameters applied before checking POIs.', 'Error:', wx.OK)
		if not os.path.exists(   os.path.join(self.dir0, '_poi.npy')   ):
			wx.MessageBox('POIs must be defined before checking.\nUse the "POI analysis" button to define POIs', 'Error:', wx.OK)
		else:
			self.metadata = DB.load_metadata(self.dir0)
			POI           = self.metadata.load_pois()
			allnone       = True
			for poi in POI:
				for p in poi:
					if p!=None:
						allnone = False
						break
			if allnone:
				wx.MessageBox('Warning:  No POIs defined.\nUse the "POI analysis" button to define POIs', 'Error:', wx.OK)
			else:
				dialog        = ppp_selector.PPDatabaseQueryDialog(self.metadata, by_foot=True)
				dialog.ShowModal()
				subj          = None
				if not dialog.canceled:
					canceled  = dialog.canceled
					if not canceled:
						subj,byfoot,LR,FH,alltrials,trials = dialog.get_choices()
				dialog.Destroy()
				if subj!=None:
					subjname  = self.metadata.USUBJ[subj]
					footlabel = self.metadata.get_foot_label(LR, FH)
					frame     = checkpoiGUI.CheckPOIFrame(None, -1, 'PPP Check POIs (%s: %s)'%(subjname,footlabel), metadata=self.metadata, subj=subj, LR=LR, FH=FH)
				 	frame.Show(True)


	def onButtonExportCOP(self, event):
 		dir0          = os.path.join(self.dir0, 'dbrr')
		if not os.path.exists(dir0):
			wx.MessageBox('Registration must be conducted and parameters applied before exporting COP trajectories.', 'Error:', wx.OK)
		else:
			dialog    = wx.ProgressDialog("", "Extracting COP trajectories and saving to ./dbcop...", maximum=4*self.metadata.nSubj, style=wx.PD_ELAPSED_TIME)
			self.metadata = DB.load_metadata(self.dir0)
			dir1          = os.path.join(self.dir0, 'dbcop')
			if not os.path.exists(dir1):
				os.mkdir(dir1)
			ii = 0
			for subj in range(self.metadata.nSubj):
				i     = 0
				for FH in [False,True]:
					for LR in [False,True]:
						rollovers = self.metadata.get_rollovers(subj, LR=LR, FH=FH, only_good=True)
						II        = self.metadata.load_rollovers(rollovers, dbdir='dbrr', max=False)
						R         = np.array([PM.extract_cop(I, interp=True, n=101)   for I in II])
						fname1    = os.path.join(dir1, 'subj%03d_cop%d.npy'%(subj,i))
						np.save(fname1, R)
						dialog.Update(ii)
						i += 1
						ii += 1
			dialog.Destroy()



	def onButtonExportMeans(self, event):
 		dir0          = os.path.join(self.dir0, 'dbrr')
		if not os.path.exists(dir0):
			wx.MessageBox('Registration must be conducted and parameters applied before exporting COP trajectories.', 'Error:', wx.OK)
		else:
			result        = wx.MessageBox('Computing means may take several minutes.\nPress OK to continue.', 'Note:', wx.OK|wx.CANCEL)
			if result == wx.OK:
				dir1          = os.path.join(self.dir0, 'dbmeans')
				if not os.path.exists(dir1):
					os.mkdir(dir1)
				dialog    = wx.ProgressDialog("", "Computing means and saving to ./dbmeans...", maximum=4*self.metadata.nSubj, style=wx.PD_ELAPSED_TIME)
				self.metadata = DB.load_metadata(self.dir0)
				ii = 0
				for subj in range(self.metadata.nSubj):
					i     = 0
					for FH in [False,True]:
						for LR in [False,True]:
							rollovers = self.metadata.get_rollovers(subj, LR=LR, FH=FH, only_good=True)
							II        = self.metadata.load_rollovers(rollovers, dbdir='dbrr', max=True)
							II        = np.dstack(II)
							I         = II.mean(axis=2)
							fname1    = os.path.join(dir1, 'subj%03d_mean%d.h5'%(subj,i))
							PM.save(fname1, I)
							dialog.Update(ii)
							i += 1
							ii += 1
				dialog.Destroy()
				
			
 		


	def onButtonIdentify(self, event):
		if not os.path.exists(  os.path.join(self.dir0, 'dbr') ):
			result = wx.MessageBox('Images must be resized before idenitfying feet.\nSelect "Resize image grids" from the main menu.', 'Error.', wx.OK)
			return
		self.metadata = DB.load_metadata(self.dir0)
		dialog        = ppp_selector.PPDatabaseQueryDialog(self.metadata, by_trial=True)
		dialog.ShowModal()
		rollovers = None
		if not dialog.canceled:
			rollovers = dialog.get_rollovers(group_by_trial=True)
		dialog.Destroy()
		if rollovers!=None:
			frame = identifyGUI.IdentifyFrame(None, -1, 'PPP Foot Identificaiton', metadata=self.metadata, rollovers=rollovers)
			frame.Show(True)

	
	def onButtonPOI(self, event):
		if not os.path.exists(  os.path.join(self.dir0, 'dbmeans')  ):
			wx.MessageBox('Mean images must be exported before conducting POI analysis.', 'Error:', wx.OK)
		else:
			self.metadata = DB.load_metadata(self.dir0)
			if not os.path.exists( os.path.join(self.dir0, '_poi.npy')  ):
				self.metadata.save_pois()
			frame = poiGUI.POIFrame(None, -1, 'PPP POI Selector', metadata=self.metadata)
			frame.Show(True)


	def onButtonQuit(self, event):
		self.parent.Destroy()
		

	def onButtonRegister(self, event):
		self.metadata = DB.load_metadata(self.dir0)
		if not os.path.exists( os.path.join(self.dir0, '_registration_params.npy')  ):
			self.metadata.save_registration_parameters()
		dialog        = ppp_selector.PPDatabaseQueryDialog(self.metadata, by_foot=True)
		dialog.ShowModal()
		subj          = None
		if not dialog.canceled:
			canceled  = dialog.canceled
			if not canceled:
				subj,byfoot,LR,FH,alltrials,trials = dialog.get_choices()
		dialog.Destroy()
		if subj!=None:
			subjname  = self.metadata.USUBJ[subj]
			footlabel = self.metadata.get_foot_label(LR, FH)
			frame    = registrationGUI.RegistrationFrame(None, -1, 'PPP Registration (%s: %s)'%(subjname,footlabel), metadata=self.metadata, subj=subj, LR=LR, FH=FH)
			frame.Show(True)


	def onButtonResize(self, event):
		result = wx.MessageBox('Resizing image grids can take several minutes to complete. Click OK to proceed.', 'Image resizing', wx.CANCEL | wx.OK)
		if result==wx.OK:
			metadata  = DB.load_metadata(self.dir0)
			dialog    = wx.ProgressDialog("", "Reading image sizes...", maximum=metadata.nRollovers, style = wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME)
			dirDB     = os.path.join(self.dir0, 'db')
			dirDBr    = os.path.join(self.dir0, 'dbr')
			if not os.path.exists(dirDBr):
				os.mkdir(dirDBr)
			fnames    = [os.path.join(dirDB, 'rollover%05d.h5'%i)   for i in range(metadata.nRollovers)]
			gs        = PM.find_max_grid(fnames)
			pad       = 5
			gs        = [gs[0]+2*pad, gs[1]+2*pad]
			keepGoing = dialog.Update(0, 'Resizing images...')[0]
			count     = 0
			for i,fname in enumerate(fnames):
				I     = PM.load(fname)
				I     = PM.resize(I,gs)
				keepGoing = dialog.Update(i)[0]
				fname1 = os.path.join( dirDBr, os.path.split(fname)[1]  )
				PM.save(fname1, I)
			dialog.Destroy()
			
			
	
	def onButtonSetProjectDirectory(self, event):
		dir0   = None
		dialog = wx.DirDialog(self.parent, 'Select a directory...', self.dir0, style=wx.DD_DEFAULT_STYLE)
		if dialog.ShowModal() == wx.ID_OK:
			dir0 = dialog.GetPath()
		dialog.Destroy()
		### load metadata:
		if dir0!=None:
			self.dir0 = dir0
			self.settings.set_dir_project(dir0)
			self.parent.statusbar.SetStatusText(dir0, 1)
			for button in self.buttons[1:-1]:
				button.Enable(True)
			db        = DB.PressureDatabaseInitializer(dir0)
			db.check_initiated()
			db.check_for_other_files()
			if db.isinitiated:
				self.metadata = DB.load_metadata(dir0)
				self.metadata.dir0 = dir0
				self.metadata.save()
			else:
				db.assemble_xml_filenames()
				db.check_xml_filenames()
				metadataXML = db.parse_xml_filenames()
				result = wx.MessageBox('This project has not yet been initialized.\nInitialize now?\n\nNote: All XML files will be imported. This could take several minutes to complete.', 'Database initialization', wx.CANCEL | wx.OK)
				if result==wx.OK:
					importer  = DB.XMLImporter(metadataXML, False)
					dialog    = wx.ProgressDialog("", "Importing XML files...", maximum=importer.nFiles, style = wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME)
					keepGoing = True
					count     = 0
					while keepGoing and (count < importer.nFiles):
						keepGoing = dialog.Update(count)[0]
						importer.filenum = count
						importer.import_next()
						count += 1
					dialog.Destroy()
					### save metadata:
					metadataH5 = importer.finish()
					metadataH5.save()
					metadataH5.savexls()
					metadataH5.savexls_subjmetadata()
					metadataH5.save_template_choices()


	

	
	def onButtonTemplates(self, event):
		metadata      = DB.load_metadata(self.dir0)
		labels        = ['Fore Left', 'Fore Right', 'Hind Left', 'Hind Right']
		### check that good feet are available for all subjects:
		for subj in range(metadata.nSubj):
			n = metadata.get_nrollovers_by_subj(subj, only_good=True)
			if np.any( np.array(n)<1 ):
				ind    = np.argwhere(np.array(n)<1).flatten()
				ind    = ind[0]
				label  = labels[ind]
				result = wx.MessageBox('No good rollovers found for subject "%s", foot: "%s".\nYou must identify at least one good rollover to proceed.'%(metadata.USUBJ[subj], label), 'Error', wx.OK)
				return None
		self.metadata = metadata
		frame = templateGUI.TemplateFrame(None, -1, 'PPP Template Selection', metadata=metadata)
		frame.Show(True)
		





class PPStartFrame(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title, size=(500,500))
		self.panel = PPMainPanel(self)
		self._create_statusbar()
		self.Centre()
	
	def _create_statusbar(self):
		self.statusbar = self.CreateStatusBar(style=wx.BORDER_DOUBLE)
		self.statusbar.SetFieldsCount(2)
		self.statusbar.SetStatusWidths([-1,-4])
		self.statusbar.SetStatusText('Project directory:',0)
		self.statusbar.SetStatusText('(None)',1)
	




class MyApp(wx.App):
	def OnInit(self):
		frame = PPStartFrame(None, -1, 'Plantar Pressure Processor: MAIN MENU')
		frame.Show(True)
		self.SetTopWindow(frame)
		return True



#run app:
app = MyApp(redirect=False)
app.MainLoop()

	