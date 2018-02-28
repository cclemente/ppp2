
import datetime,glob,natsort,os,xlwt
import numpy as np
import zebrisXML;  reload(zebrisXML)
import pressure_module;  reload(pressure_module)



class MetadataH5(object):
	def __init__(self, SUBJ, DATE, TRIAL, FID, ROLLOVER, MOVEMENT, STEP, SEQUENCE, GOOD, LR, FH, metadataXML=None):
		self.SUBJ        = np.asarray(SUBJ, dtype=np.uint8)
		self.DATE        = np.asarray(DATE, dtype=np.uint8)
		self.TRIAL       = np.asarray(TRIAL, dtype=np.uint16)
		self.FID         = np.asarray(FID, dtype=np.uint16)
		# ### rollover parameters:
		self.ROLLOVER    = np.asarray(ROLLOVER, dtype=np.uint16)
		self.MOVEMENT    = np.asarray(MOVEMENT, dtype=np.uint8)
		self.STEP        = np.asarray(STEP, dtype=np.uint8)
		self.SEQUENCE    = np.asarray(SEQUENCE, dtype=np.uint8)
		### identification parameters:
		self.GOOD        = np.asarray(GOOD, dtype=bool)
		self.LR          = np.asarray(LR, dtype=bool)
		self.FH          = np.asarray(FH, dtype=bool)
		### metadataXML:
		self.nRollovers  = self.ROLLOVER.size
		if isinstance(metadataXML, MetadataXML):
			self._from_metadata(metadataXML)
		else:
			self._from_XX(metadataXML)
		
	def _from_metadata(self, metadataXML):
		self.dir0        = metadataXML.dir0
		self.nDates      = metadataXML.nDates
		self.nSubj       = metadataXML.nSubj
		self.nFilesXML   = metadataXML.nFilesXML
		self.UDATE       = metadataXML.UDATE
		self.UFNAMESXML  = metadataXML.FNAMESXML
		self.USUBJ       = metadataXML.USUBJ
		
	def _from_XX(self, XX):
		self.dir0        = str(XX['dir0'])
		self.nDates      = int(XX['nDates'])
		self.nSubj       = int(XX['nSubj'])
		self.nFilesXML   = int(XX['nFilesXML'])
		self.UDATE       = XX['UDATE']
		self.UFNAMESXML  = XX['UFNAMESXML']
		self.USUBJ       = XX['USUBJ']
	

	def extract_poi_data(self, subj, POI):
		LRFH  = [(0,0),(1,0), (0,1),(1,1)]
		Z     = []
		for i,(lrfh,poi) in enumerate(zip(LRFH,POI)):
			if poi==None:
				Z.append(None)
			else:
				LR,FH     = lrfh
				rollovers = self.get_rollovers(subj, LR=LR, FH=FH, group_by_trial=False, only_good=True)
				II        = np.array(self.load_rollovers(rollovers, dbdir='dbrr', max=True))
				z         = np.array([II[:,y,x] for x,y in poi]).T
				Z.append(z)
		return Z
		
	
	def get_foot_label(self, LR=False, FH=False):
		labels   = ['Fore Left', 'Fore Right', 'Hind Left', 'Hind Right']
		if (not LR) and (not FH):
			s    = labels[0]
		elif LR and (not FH):
			s    = labels[1]
		elif (not LR) and FH:
			s    = labels[2]
		else:
			s    = labels[3]
		return s
			
		
	
	def get_nrollovers_by_subj(self, subj, only_good=True):
		i           = self.SUBJ==subj
		if only_good:
			i       = i & self.GOOD
		i0          = i & (self.LR==0) & (self.FH==0)
		i1          = i & (self.LR==1) & (self.FH==0)
		i2          = i & (self.LR==0) & (self.FH==1)
		i3          = i & (self.LR==1) & (self.FH==1)
		n0,n1,n2,n3 = i0.sum(), i1.sum(), i2.sum(), i3.sum()
		return n0,n1,n2,n3
	
	def get_rollovers(self, subj, fid=None, LR=None, FH=None, group_by_trial=False, only_good=False):
		i           = self.SUBJ==subj
		if fid!=None:
			if isinstance(fid, (list,tuple)):
				i0 = np.array([False]*self.nRollovers)
				for f in fid:
					i0 = np.logical_or(i0, self.FID==f)
				i   = i & i0
			else:
				i   = i & (self.FID==fid)
		if LR!=None:
			i       = i & (self.LR==LR)
		if FH!=None:
			i       = i & (self.FH==FH)
		if only_good:
			i       = i & (self.GOOD)
		rollovers   = self.ROLLOVER[i]
		if group_by_trial:
			#trials    = self.TRIAL[i]
			#utrials   = np.unique(trials)
			#rollovers = [rollovers[trials==u]   for u in utrials]
			fids      = self.FID[i] 
			ufid      = np.unique(fids)
			rollovers = [rollovers[fids==u]   for u in ufid]
		return rollovers

	def get_stepnums_from_rollovers(self, rollovers):
		return self.SEQUENCE[rollovers]
	
	
	def get_template(self, subj, LR=False, FH=False):
		rollovers = self.get_rollovers(subj, LR=LR, FH=FH, only_good=True)
		choices   = self.load_template_choices()[subj]
		if (not LR) & (not FH):
			choice = choices[0]
		elif LR & (not FH):
			choice = choices[1]
		elif (not LR) & FH:
			choice = choices[2]
		else:
			choice = choices[3]
		return rollovers[choice]

	
	def get_xmlfilenames_from_rollovers(self, rollovers, with_path=True):
		i            = np.array([False]*self.nRollovers)
		i[rollovers] = True
		fids         = self.FID[i]
		fnames       = [self.UFNAMESXML[fid]  for fid in fids]
		if not with_path:
			fnames = [os.path.split(s)[1]  for s in fnames]
		return fnames
	
	def get_xmlfilenames_from_subj(self, subj, with_path=True):
		fids   = np.unique(self.FID[self.SUBJ==subj])
		fnames = self.UFNAMESXML[fids]
		if not with_path:
			fnames = [os.path.split(s)[1]  for s in fnames]
		return fnames,fids
	
	def load_means(self, subj, stacked=False):
		dir0       = os.path.join(self.dir0, 'dbmeans')
		II         = []
		for i in range(4):
			fname  = os.path.join(dir0, 'subj%03d_mean%d.h5'%(subj,i))
			II.append(  pressure_module.load(fname)  )
		if stacked:
			I0     = np.hstack(II[:2])
			I1     = np.hstack(II[2:])
			II     = np.vstack([I0,I1])
		return II
	
	def load_pois(self):
		fname = os.path.join(self.dir0, '_poi.npy')
		return np.load(fname)
	
	def load_rollover(self, rollover, dbdir='db', max=True):
		dir0    = os.path.join(self.dir0, dbdir)
		fname   = os.path.join(dir0, 'rollover%05d.h5'%rollover)
		I       =  pressure_module.load(fname)
		if max:
			I = I.max(axis=2)
		return np.asarray(I, dtype=float)

	def load_rollovers(self, rollovers, dbdir='db', max=True):
		dir0    = os.path.join(self.dir0, dbdir)
		II      = []
		for i in rollovers:
			fname = os.path.join(dir0, 'rollover%05d.h5'%i)
			I     =  pressure_module.load(fname)
			if max:
				I = I.max(axis=2)
			II.append( np.asarray(I, dtype=float) )
		return II
		
	def load_registration_params(self):
		fname = os.path.join(self.dir0, '_registration_params.npy')
		return np.load(fname)

	def load_template_choices(self):
		fname = os.path.join(self.dir0, '_template_choices.npy')
		return np.load(fname)
	
	def save(self):
		fnameX           = os.path.join(self.dir0, '_X.npz')
		fnameXX          = os.path.join(self.dir0, '_XX.npz')
		np.savez(fnameX, SUBJ=self.SUBJ, DATE=self.DATE, TRIAL=self.TRIAL, FID=self.FID, ROLLOVER=self.ROLLOVER, MOVEMENT=self.MOVEMENT, STEP=self.STEP, SEQUENCE=self.SEQUENCE, GOOD=self.GOOD, LR=self.LR, FH=self.FH)
		np.savez(fnameXX, dir0=self.dir0, nDates=self.nDates, nSubj=self.nSubj, nFilesXML=self.nFilesXML, UDATE=self.UDATE, UFNAMESXML=self.UFNAMESXML, USUBJ=self.USUBJ)
		#X:  SUBJ, ROLLOVER, DATE, TRIAL, FID, MOVEMENT, STEP, GOOD, LR, FH
		#XX:  dir0, nDates, nSubj, nFilesXML, UDATE, UFNAMESXML, USUBJ
		
		
	def savexls(self):
		fnameXLS         = os.path.join(self.dir0, '_metadata.xls')
		xlswriter        = MetadataXLSWriter(self)
		xlswriter.write_database_sheet()
		xlswriter.write_keys()
		# xlswriter.write_subject_metadata_sheet()
		xlswriter.save(fnameXLS)

	def savexls_subjmetadata(self):
		fnameXLS         = os.path.join(self.dir0, '_metadata_subject.xls')
		xlswriter        = SubjectMetadataXLSWriter(self)
		xlswriter.write_subject_metadata_sheet()
		xlswriter.save(fnameXLS)
		
	def save_rollover(self, I, rollover, dbdir='dbr'):
		dir0             = os.path.join(self.dir0, dbdir)
		fname            = os.path.join(dir0, 'rollover%05d.h5'%rollover)
		pressure_module.save(fname, I)
	
	def save_pois(self, POI=None):
		if POI==None:
			# POI = -np.ones((self.nSubj,4,1,2), dtype=float)
			POI = [[None]*4]*self.nSubj
		else:
			pass
			# for i in range(self.nSubj):
			# 	for ii in range(4):
			# 		if POI[i][ii]==None:
			# 			POI[i][ii] = [-1,-1]
			# POI = np.asarray(POI, dtype=int)
		fname = os.path.join(self.dir0, '_poi.npy')
		np.save(fname, POI)

	def save_poi_extracted(self, fnameXLS, POI=None):
		xlswriter        = POIXLSWriter(self, POI)
		xlswriter.write_labels()
		xlswriter.write_data()
		xlswriter.save(fnameXLS)



	def save_registration_parameters(self, PARAMS=None):
		if PARAMS==None:
			PARAMS      = np.zeros((self.nRollovers,4))
			PARAMS[:,3] = 1
		else:
			PARAMS  = np.asarray(PARAMS)
		fname = os.path.join(self.dir0, '_registration_params.npy')
		np.save(fname, PARAMS)
		

	def save_template_choices(self, CHOICES=None):
		if CHOICES==None:
			CHOICES  = np.zeros((self.nSubj,4), dtype=int)
		else:
			CHOICES  = np.asarray(CHOICES, dtype=int)
		fname = os.path.join(self.dir0, '_template_choices.npy')
		np.save(fname, CHOICES)
		





class MetadataXLSWriter(object):
	def __init__(self, metadata):
		self.metadata = metadata
		self.sheet0   = None
		self.sheet1   = None
		self.style    = None
		self.workbook = None
		self._create_style()
		self._create_workbook()

	def _create_style(self):
		style           = xlwt.XFStyle() # Create Style
		alignment       = xlwt.Alignment()
		alignment.horz  = xlwt.Alignment.HORZ_CENTER  # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
		style.alignment = alignment # Add Alignment to Style
		self.style      = style

	def _create_workbook(self):
		self.workbook = xlwt.Workbook()
		self.sheet0   = self.workbook.add_sheet('Database')
		self.sheet1   = self.workbook.add_sheet('Keys')
		# self.sheet2   = self.workbook.add_sheet('Subject metadata')


	def write_database_sheet(self):
		#X:  SUBJ, ROLLOVER, DATE, TRIAL, FID, MOVEMENT, STEP, GOOD, LR, FH
		#XX:  dir0, nDates, nSubj, nFilesXML, UDATE, UFNAMESXML, USUBJ
		### column widths:
		fnamewidth = 5 + max([len(os.path.split(f)[-1]) for f in self.metadata.UFNAMESXML])
		widths     = [12]*8 + [8] + [12]*3 + [8] + [fnamewidth]
		for i,w in enumerate(widths):
			self.sheet0.col(i).width = 256*w
		### column labels:
		labels   = ['SUBJECT','ROLLOVER','DATE', 'TRIAL', 'FILE', 'MOVEMENT', 'STEP', 'SEQUENCE', '', 'GOOD','Left/Right','Fore/Hind', '','FILENAME']
		[self.sheet0.write(0,i,label, self.style)  for i,label in enumerate(labels)]
		### write contents:
		m = self.metadata
		for i,X in enumerate(zip(m.SUBJ, m.ROLLOVER, m.DATE, m.TRIAL, m.FID, m.MOVEMENT, m.STEP, m.SEQUENCE)):
			for ii,x in enumerate(X):
				self.sheet0.write(i+1, ii, int(x), style=self.style)
		### write identifier metadata:
		for i,X in enumerate(zip(m.GOOD, m.LR, m.FH)):
			for ii,x in enumerate(X):
				self.sheet0.write(i+1, ii+9, int(x), style=self.style)
		### write file names:
		for i,fid in enumerate(m.FID):
			self.sheet0.write(i+1, 13, os.path.split(m.UFNAMESXML[fid])[-1], style=self.style)


	def write_keys(self):
		#X:  SUBJ, ROLLOVER, DATE, TRIAL, FID, MOVEMENT, STEP, GOOD, LR, FH
		#XX:  dir0, nDates, nSubj, nFilesXML, UDATE, UFNAMESXML, USUBJ
		sheet1,style = self.sheet1, self.style
		widths     = [12, 25]*3
		for i,w in enumerate(widths):
			sheet1.col(i).width = 256*w
		### write key,value labels:
		keylabels  = ['SUBJECT', 'Left/Right', 'Fore/Hind']
		for i,label in enumerate(keylabels):
			col = 2*i
			sheet1.write(0, col,   label, style=style)
			sheet1.write(1, col,   'KEY', style=style)
			sheet1.write(1, col+1, 'VALUE', style=style)
		### write SUBJECT keys:
		m = self.metadata
		for i,usubj in enumerate(m.USUBJ):
			sheet1.write(3+i, 0, i, style=self.style)
			sheet1.write(3+i, 1, usubj, style=self.style)
		### write Left/Right keys:
		sheet1.write(3, 2, 0, style=style);    sheet1.write(3, 3, 'Left', style=style)
		sheet1.write(4, 2, 1, style=style);    sheet1.write(4, 3, 'Right', style=style)
		### write Fore/Hind keys:
		sheet1.write(3, 4, 0, style=style);    sheet1.write(3, 5, 'Fore', style=style)
		sheet1.write(4, 4, 1, style=style);    sheet1.write(4, 5, 'Hind', style=style)

	def save(self, fnameXLS):
		self.workbook.save(fnameXLS)




class POIXLSWriter(object):
	def __init__(self, metadata, POI):
		self.metadata = metadata
		self.POI      = POI
		self.nPOIs    = None
		self.sheets   = None
		self.style    = None
		self.workbook = None
		self._create_style()
		self._create_workbook()
		self._parse_nPOIs()

	def _create_style(self):
		style           = xlwt.XFStyle() # Create Style
		alignment       = xlwt.Alignment()
		alignment.horz  = xlwt.Alignment.HORZ_CENTER  # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
		style.alignment = alignment # Add Alignment to Style
		self.style      = style

	def _create_workbook(self):
		self.workbook = xlwt.Workbook()
		self.sheets   = [self.workbook.add_sheet('%d %s'%(i+1,label))  for i,label in enumerate(self.metadata.USUBJ)]

	def _parse_nPOIs(self):
		nPOIs = []
		for poi in self.POI:
			n = []
			for p in poi:
				if p==None:
					nn = 0
				else:
					nn = len(p)
				n.append(nn)
			nPOIs.append(n)
		self.nPOIs = nPOIs
	
	def write_data(self):
		for i,sheet in enumerate(self.sheets):
			Z  = self.metadata.extract_poi_data(i, self.POI[i])
			col     = 0
			for ii,z in enumerate(Z):
				if z!=None:
					for iii,zz in enumerate(z.T):
						for iii,zzz in enumerate(zz):
							sheet.write(iii+2, col, zzz, style=self.style)
						col += 1
				col += 1

	def write_labels(self):
		footlabels  = ['Fore Left', 'Fore Right', 'Hind Left', 'Hind Right']
		for i,sheet in enumerate(self.sheets):
			col     = 0
			for ii in range(4):
				n   = self.nPOIs[i][ii]
				### write foot label:
				sheet.write(0, col, footlabels[ii], style=self.style)
				### write poi labels:
				for iii in range(n):
					sheet.write(1, col+iii, 'POI-%d'%(iii+1), style=self.style)
				col = col + n + 1

	def save(self, fnameXLS):
		self.workbook.save(fnameXLS)




class SubjectMetadataXLSWriter(MetadataXLSWriter):
	def _create_workbook(self):
		self.workbook = xlwt.Workbook()
		self.sheet2   = self.workbook.add_sheet('Metadata')
	
	def write_subject_metadata_sheet(self):
		### column widths:
		widths     = [12, 24, 12,12]
		for i,w in enumerate(widths):
			self.sheet2.col(i).width = 256*w
		### column labels:
		labels   = ['SUBJECT','NAME','SEX','MASS']
		m        = self.metadata
		[self.sheet2.write(0,i,label, style=self.style)  for i,label in enumerate(labels)]
		[self.sheet2.write(1+i, 0, i, style=self.style)  for i in range(m.nSubj)]
		[self.sheet2.write(1+i, 1, s, style=self.style)  for i,s in enumerate(m.USUBJ)]
		[self.sheet2.write(1+i, 2, 0, style=self.style)  for i in range(m.nSubj)]
		[self.sheet2.write(1+i, 3, 0, style=self.style)  for i in range(m.nSubj)]





class MetadataXML(object):
	def __init__(self, root, UDATE, USUBJ, DATE, FNAMESXML, SUBJ, TRIAL):
		self.DATE        = np.asarray(DATE, dtype=np.uint8)
		self.FNAMESXML   = np.asarray(FNAMESXML)
		self.SUBJ        = np.asarray(SUBJ, dtype=np.uint8)
		self.TRIAL       = np.asarray(TRIAL, dtype=np.uint16)
		self.UDATE       = np.asarray(UDATE)
		self.USUBJ       = np.asarray(USUBJ)
		self.dir0        = root
		self.nDates      = self.UDATE.size
		self.nSubj       = self.USUBJ.size
		self.nFilesXML   = self.FNAMESXML.size
	




class PressureDatabaseInitializer(object):
	def __init__(self, root):
		self.FNAMESXML   = None
		self.dir0        = root
		self.isinitiated = False
		self.hasmetadata = False
		self.hasxmldir   = False
		self.hasdbdir    = False
		self.nFilesXML   = None
	
	def assemble_xml_filenames(self):
		### assemble all file names:
		FNAMES = []
		for dirpath, dirnames, fnames in os.walk( os.path.join(self.dir0, 'xml') ):
			for fname in natsort.natsorted(fnames):
				if os.path.splitext(fname)[1] == '.xml':
					FNAMES.append( os.path.join(dirpath, fname) )
		self.FNAMESXML = FNAMES
		self.nFilesXML = len(FNAMES)
	
	def check_for_metadatafiles(self):
		b0    = os.path.exists(  os.path.join(self.dir0, '_X.npz')  )
		b1    = os.path.exists(  os.path.join(self.dir0, '_XX.npz')  )
		b2    = os.path.exists(  os.path.join(self.dir0, '_metadata.npz')  )
		if (b0 and b1 and b2):
			self.hasmetadata = True

	def check_for_db_dir(self):
		self.hasdbdir = os.path.exists(  os.path.join(self.dir0, 'db')  )

	def check_for_xml_dir(self):
		self.hasxmldir = os.path.exists(  os.path.join(self.dir0, 'xml')  )
	
	def check_for_other_files(self):
		for (path,dirs,fnames) in os.walk(self.dir0):
			if path==self.dir0:
				for d in dirs:
					if not (d.startswith('db') or d=='xml'):
						raise( AttributeError('The project directory must only contain only an "xml" directory and directories named "db*".\nPlease remove the following directory:\n%s\n\n'%os.path.join(path,d)) )
				for fname in fnames:
					if fname.startswith('_metadata'):
						if not fname.endswith('.xls'):
							raise( AttributeError('The project directory must only "_metadata*" files which end with ".xls".  \nPlease remove the following file:\n%s\n\n'%os.path.join(path,fname)) )
					elif fname not in ['_X.npz', '_XX.npz', '_template_choices.npy', '_registration_params.npy', '_poi.npy', '.DS_Store']:
						raise( AttributeError('The project directory must only contain directories and the metadata files:  _X.npz, _XX.npz, _template_choices.npy and _metadata*.xls.  \nPlease remove the following file:\n%s\n\n'%os.path.join(path,fname)) )
			elif os.path.join(self.dir0, 'xml') in path:
				for fname in fnames:
					if fname != '.DS_Store':
						if os.path.splitext(fname)[1] != '.xml':
							raise( AttributeError('The xml directory must contain only .xml files.\nPlease remove the following file:\n%s\n\n'%os.path.join(path,fname)) )
			else:
				for fname in fnames:
					if fname != '.DS_Store':
						if os.path.splitext(fname)[1] not in ['.h5', '.npy']:
							raise( AttributeError('The db* directories must contain only .h5 and .npy files.\nPlease remove the following file:\n%s'%os.path.join(path,fname)) )

	def check_initiated(self):
		#check for XML directory
		self.check_for_xml_dir()
		if not self.hasxmldir:
			raise AttributeError('No "xml" directory inside the project directory') 
		#check for db directory:
		self.check_for_db_dir()
		if self.hasdbdir:
			self.isinitiated = True
	
	def check_xml_filenames(self):
		for fname in self.FNAMESXML:
			self.parse_filename_test(fname)

	def parse_filename_test(self, fnamefull):
		path,fname = os.path.split(fnamefull)
		fparts = fname.strip('.xml').split('_')
		if len(fparts)!=6:
			raise( AttributeError('xml files must have format: DD_MM_YYYY_SUBJECTNAME_TRIAL_X.xml\nPlease remove or rename the file:\n%s\n\n'%os.path.join(path,fname))  )
		
	def parse_filename(self, s):
		fparts = os.path.split(s)[1].strip('.xml').split('_')
		subj   = fparts[3]
		trial  = int(fparts[-1])
		date   = '%s_%s_%s' %tuple(fparts[:3])
		return subj,date,trial

	def parse_xml_filenames(self):
		USUBJ,UDATE = [],[]
		SUBJ,DATE,TRIAL = [],[],[]
		for fname in self.FNAMESXML:
			subj,date,trial = self.parse_filename(fname)
			if subj not in USUBJ:
				USUBJ.append(subj)
			if date not in UDATE:
				UDATE.append(date)
			SUBJ.append( USUBJ.index(subj) )
			DATE.append( UDATE.index(date) )
			TRIAL.append(trial)
		USUBJ0,UDATE0 = np.asarray(USUBJ), np.asarray(UDATE)
		SUBJ0,DATE0,TRIAL  = np.asarray(SUBJ), np.asarray(DATE), np.asarray(TRIAL)
		### initialize sorted subjects and dates:
		UDATE = UDATE0.copy()
		SUBJ,DATE = SUBJ0.copy(), DATE0.copy()
		### sort USUBJ:
		USUBJ = np.sort(USUBJ0)
		inds = np.argsort(USUBJ0)
		for i,ind in enumerate(inds):
			SUBJ[ SUBJ0==ind ] = i
		### sort UDATE:
		udates = [datetime.datetime.strptime(s, "%d_%m_%Y") for s in UDATE]
		UDATE  = np.sort(UDATE0)
		inds   = np.argsort(udates)
		for i,ind in enumerate(inds):
			DATE[ DATE0==ind ] = i
		return MetadataXML(self.dir0, UDATE, USUBJ, DATE, self.FNAMESXML, SUBJ, TRIAL)
		

		


class XMLImporter(object):
	def __init__(self, metadataXML, discard_edge_steps=False):
		self.metadata = metadataXML
		self.discard  = False
		self._create_dbdir()
		self._init_vars()
	
	def _create_dbdir(self):
		self.dirDB   = os.path.join(self.metadata.dir0, 'db')
		if not os.path.exists(self.dirDB):
			os.mkdir(self.dirDB)
			
	def _init_vars(self):
		self.SUBJ     = []
		self.DATE     = []
		self.TRIAL    = []
		self.FID      = []
		self.ROLLOVER = []
		self.MOVEMENT = []
		self.STEP     = []
		self.SEQUENCE = []
		self.rollover = 0
		self.filenum  = 0
		self.nFiles   = self.metadata.nFilesXML
		
	def import_all(self):
		for i in range(self.nFiles):
			self.filenum = i
			self.import_next()
		metadataH5 = self.finish()
		return metadataH5
	
	def import_next(self):
		if self.filenum < self.nFiles:
			i         = self.filenum
			fname     = self.metadata.FNAMESXML[i]
			date      = self.metadata.DATE[i]
			subj      = self.metadata.SUBJ[i]
			trial     = self.metadata.TRIAL[i]
			seq       = 0
			
			z         = zebrisXML.ZebrisXMLImporter(fname)
			for ii in range(z.nMovements):
				for iii in range(z.nEvents[ii]):
					#read rollover:
					I  = z.read_rollover(z.events[ii][iii],  self.discard)
					#save:
					fname = os.path.join(self.dirDB, 'rollover%05d.h5'%self.rollover)
					pressure_module.save(fname, I)
					#update metadata:
					self.SUBJ.append(subj)
					self.DATE.append(date)
					self.TRIAL.append(trial)
					self.FID.append(i)
					self.ROLLOVER.append(self.rollover)
					self.MOVEMENT.append(ii)
					self.STEP.append(iii)
					self.SEQUENCE.append(seq)
					self.rollover += 1
					seq           += 1
			self.filenum += 1
			
	def finish(self):
		nRollovers = len(self.SUBJ)
		GOOD = [False]*nRollovers
		LR   = [False]*nRollovers
		FH   = [False]*nRollovers
		return MetadataH5(self.SUBJ, self.DATE, self.TRIAL, self.FID, self.ROLLOVER, self.MOVEMENT, self.STEP, self.SEQUENCE, GOOD, LR, FH, metadataXML=self.metadata)
			





#
# def import_rollovers(metadataXML, discard_edge_steps=False):
# 	m = metadataXML
# 	#create db directory if needed:
# 	dirDB   = os.path.join(m.dir0, 'db')
# 	if not os.path.exists(dirDB):
# 		os.mkdir(dirDB)
# 	#initialize variables:
# 	SUBJ,DATE,TRIAL,FID = [],[],[],[]
# 	ROLLOVER,MOVEMENT,STEP = [],[],[]
# 	rollover = 0
# 	for i,(fname,date,subj,trial) in enumerate(  zip(m.FNAMESXML, m.DATE, m.SUBJ, m.TRIAL)  ):
# 		z      = zebrisXML.ZebrisXMLImporter(fname)
# 		for ii in range(z.nMovements):
# 			for iii in range(z.nEvents[ii]):
# 				#read rollover:
# 				I  = z.read_rollover(z.events[ii][iii],  discard_edge_steps)
# 				#save:
# 				fname = os.path.join(dirDB, 'rollover%05d.h5'%rollover)
# 				pressure_module.save(fname, I)
# 				#update metadata:
# 				SUBJ.append(subj)
# 				DATE.append(date)
# 				TRIAL.append(trial)
# 				FID.append(i)
# 				ROLLOVER.append(rollover)
# 				MOVEMENT.append(ii)
# 				STEP.append(iii)
# 				rollover += 1
# 	nRollovers = len(SUBJ)
# 	GOOD = [False]*nRollovers
# 	LR   = [False]*nRollovers
# 	FH   = [False]*nRollovers
# 	return MetadataH5(SUBJ, DATE, TRIAL, FID, ROLLOVER, MOVEMENT, STEP, GOOD, LR, FH, metadataXML=metadataXML)



def load_metadata(dir0):
	fnameX    = os.path.join(dir0, '_X.npz')
	fnameXX   = os.path.join(dir0, '_XX.npz')
	### load X:
	X         = np.load(fnameX)
	SUBJ      = X['SUBJ']
	DATE      = X['DATE']
	TRIAL     = X['TRIAL']
	FID       = X['FID']
	ROLLOVER  = X['ROLLOVER']
	MOVEMENT  = X['MOVEMENT']
	STEP      = X['STEP']
	SEQUENCE  = X['SEQUENCE']
	GOOD      = X['GOOD']
	LR        = X['LR']
	FH        = X['FH']
	X.close()
	### load XX:
	XX        = np.load(fnameXX)
	metadata  = MetadataH5(SUBJ, DATE, TRIAL, FID, ROLLOVER, MOVEMENT, STEP, SEQUENCE, GOOD, LR, FH, metadataXML=XX)
	XX.close()
	return metadata
	
	