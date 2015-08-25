#!usr/var/env python
# coding=utf-8

import os
from types import *
import datetime
import wx
from wx.lib.wordwrap import wordwrap
import features
import gridder, mailer

# Class variable to store the version number'
# Last upgrade 24-08-2008
version = "0.3"

class XyzForm(wx.Panel):
    ''' The XyzForm class is a wx.Panel that creates a bunch of controls
        and handlers for call backs. Doing the layout of the controls is 
        the responsibility of subclasses (by means of the doLayout()
        method). '''

    def __init__(self, *args, **kwargs):
        super(XyzForm, self).__init__(*args, **kwargs)
        # Set the variables
        self.vars = features.Nfifeats()
        # TODO: handle the variable real value / display value offset better
        self.referrers = [(str(key - 1) + ' - ' + str(value)) for key, 
                                 value in self.vars.generics.iteritems()]
        self.createControls()
        self.bindEvents()
        self.doLayout()
        
        # Create a parameter dictionary that is passed to gridding
        # Memlevel will be set to 100 % by default
        self.params = {'infiles': [],
                       'outdir': None,
                       'variable': None,
                       'memlevel': 8,
                       'extent': None}
                    
        # Define a file containing 
        
        # Establish wild cards used in file browsing
        self.wildcard = "Text files (*.txt)|*.txt|"     \
           "ASCII files (*.asc)|*.asc|" \
           "All files (*.*)|*.*"

        # Helper variable to indicate infile loop status
        self.no_files = None
        self.inloop = 1
        
        # Helper variable for progress bar
        self.prog = 0
        
        # Helper variable to contain number of variables in the input file
        self.varno = 0
        
        # Is email notification used
        self.email = False

    def createControls(self):
        
        # Helper decoration variables
        rheight = 32
        bsize = (90, rheight)
        
        self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY, 
                                  size=(300, 200))
        self.convertButton = wx.Button(self, wx.ID_APPLY)
        self.browseInButton = wx.Button(self, wx.ID_OPEN, size=bsize)
        self.browseOutButton = wx.Button(self, label='browse', size=bsize)
        self.addButton = wx.Button(self, wx.ID_ADD, size=(90, 28))
        self.removeButton = wx.Button(self, wx.ID_REMOVE, size=(90, 28))
        self.inNameLabel = wx.StaticText(self, label="Input XYZ file(s):")
        self.selectedLabel = wx.StaticText(self, label="Selected files:")
        self.outNameLabel = wx.StaticText(self, label="Output ASCII folder:")	
        self.varLabel = wx.StaticText(self, label="Z-variable:")
        self.inTextCtrl = wx.TextCtrl(self, value="", size=(300, rheight))
        self.outTextCtrl = wx.TextCtrl(self, value="", size=(300, rheight))
        self.selectedListBox = wx.ListBox(self, size=(320, 150))
        self.standardCheckBox = wx.CheckBox(self, -1, "Use Standard Variables")
        self.referrerChoice = wx.Choice(self, -1, (100, 50), choices='')
            
        png1 = wx.Image('images/applications-system.png', 
                            wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.pngDeco = wx.StaticBitmap(self, -1, png1)

    def bindEvents(self):
        for control, event, handler in \
            [(self.convertButton, wx.EVT_BUTTON, self.onConvert),
             (self.browseInButton, wx.EVT_BUTTON, self.onBrowseIn),
             (self.addButton, wx.EVT_BUTTON, self.onAddItem),
             (self.removeButton, wx.EVT_BUTTON, self.onRemoveItem),
             (self.browseOutButton, wx.EVT_BUTTON, self.onBrowseOut),
             (self.inTextCtrl, wx.EVT_TEXT, self.onInNameEntered),
             (self.inTextCtrl, wx.EVT_CHAR, self.onInNameChanged),
             (self.outTextCtrl, wx.EVT_TEXT, self.onOutNameEntered),
             (self.outTextCtrl, wx.EVT_CHAR, self.onOutNameChanged),
             (self.referrerChoice, wx.EVT_CHOICE, self.onReferrerEntered),
             (self.standardCheckBox, wx.EVT_CHECKBOX, self.onStandardChanged)
             ]:
            control.Bind(event, handler)

    def doLayout(self):
        ''' Layout the controls that were created by createControls(). 
            XyzForm.doLayout() will raise a NotImplementedError because it 
            is the responsibility of subclasses to layout the controls. '''
        raise NotImplementedError

    # Callback methods:

    def onReferrerEntered(self, event):
        self.params['variable'] = event.GetString()
        self.log('Selected variable: ' + self.params['variable'])
        
    def onStandardChanged(self, event):
        self.set_variables(event.IsChecked())

    def onConvert(self, event):
        aok = True
        self.inloop = 1
        self.no_files = None
        for key, value in self.params.iteritems():
            if value is None and key != 'memlevel' and key != 'extent':
                self.log(str(key) + ' is not defined!')
                aok = False
        
        # If everything is ok, start looping through selected files,
        # ouput filenames are automatically generated
        if aok:
            self.no_files = len(self.params['infiles'])
            for file in self.params['infiles']:
                try:
                    inVar = int(self.params['variable'].split()[0])
                    outfile = os.path.join(self.params['outdir'], 
                                           self.getoutputname(file))
                    self.grid = gridder.Grid(file, outfile,
                                             inVar, self.params['memlevel'], 
                                             parent=self,
                                             dimensions=self.params['extent'])
                    self.log('Conversion of file no %s/%s complete!' 
                             % (self.inloop, self.no_files))
                    if self.email:
                        self.sendmail('Conversion of file %s/%s complete.'
                            % (self.inloop, self.no_files))
                    self.inloop += 1
                except MemoryError:
                    self.showError('Not enough memory for reading the data\n' \
                                  'and building data lists.')
                    self.log(sys.exc_info)
                    break
        
    def onBrowseIn(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=self.wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()

            for path in paths:
                if self.__check_input(path):
                    self.inTextCtrl.SetValue(path)
                    
        dlg.Destroy()
        
    def onBrowseOut(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.outTextCtrl.SetValue(path)
            self.params['outdir'] = path

        dlg.Destroy()
    
    def onAddItem(self, event):
        val = self.inTextCtrl.GetValue()
        if val != '':
            # Append to file list if not there yet
            if val not in self.params['infiles']:
                # Also set the client data
                self.selectedListBox.Insert(val, 0)
                self.selectedListBox.SetClientData(0, val)
                self.params['infiles'].append(val)

    def onRemoveItem(self, event):
        selItem = self.selectedListBox.GetSelections()
        if selItem:
            value = self.selectedListBox.GetClientData(selItem[0])
            # Remove from file list if there
            if value in self.params['infiles']:
                self.params['infiles'].remove(value)
                self.selectedListBox.Delete(selItem[0])
    
    def onInNameEntered(self, event):
        #self.log('User entered name: %s' % event.GetString())
        pass

    def onInNameChanged(self, event):
        event.Skip()
        
    def onOutNameEntered(self, event):
        pass

    def onOutNameChanged(self, event):
        event.Skip()

    # Helper method(s):

    def log(self, message):
        ''' Private method to append a string to the logger text
            control. '''
        self.logger.AppendText('%s\n' % datetime.datetime.now().ctime())    
        self.logger.AppendText('%s\n' % message)
        self.logger.AppendText('\n')
        
    def __check_input(self, path):
        ''' Private method to check that selected infile *seems* ok.'''
        firstline = open(path, 'r').readline()
        self.varno = len(firstline.split())
        if self.varno < 3:
            self.logger.AppendText('WARNING! First line of the file has ' + \
            'less than 3 entries or is empty. You need at least 3 ' + \
            'variables (x, y and z) to proceed.\n\n')
            return False
        else:
            self.logger.AppendText('Input file has %s variables.\n\n' % self.varno)
            # Set variable choice to generic variable numbers
            self.set_variables(False)
            return True
        
    def set_variables(self, status):
        valuelist = []
        values = {}
        if status:
            # Set the described variables 
            self.vars.features = 'fin'
            # Clear the wxChoice widget
            self.referrerChoice.Clear()
            # Get right values (features)
            values = self.vars.features
        else:
            # Set the generic variables
            self.vars.generics = self.varno
            # Clear the wxChoice widget
            self.referrerChoice.Clear()
            # Get right values (generics)
            values = self.vars.generics
        # Populate wxChoice with new values
        for i in range(len(values)):
            valuelist.append(str(values[i]))
        self.referrerChoice.AppendItems(valuelist)
            
    
    def set_emailnotif(self, status):
        ''' Private method to toggle between email notification'''
        if status:
            self.email = True
            self.log('E-mail notification enbled')
        else:
            self.email = False
            self.log('E-mail notification disabled')
            
    def set_extent(self, extent):
        ''' Private method to set geographical extent. In parameter is a
        tuple.'''
        if extent:
            self.params['extent'] = extent[1]
            self.log('Using custom extent: %s' % extent[0])
        else:
            self.params['extent'] = None
            self.log('Extent will be calculated from the data.')
    
    def set_memlevel(self, level):
        ''' Private method to set the memory level as needed'''
        self.params['memlevel'] = level
        if level:
            self.log('Max input read RAM changed to %s Mb' % level)
        else:
            self.log('Max input read RAM not constrained')
        self.params['memlevel'] = level
        
    def showProg(self, max=1, message=''):
        self.progDlg = wx.ProgressDialog("Converting file %s/%s" % 
                               (self.inloop, self.no_files),
                               message,
                               maximum = max,
                               parent=self,
                               style = wx.PD_CAN_ABORT
                                | wx.PD_APP_MODAL
                                | wx.PD_ELAPSED_TIME
                                | wx.PD_AUTO_HIDE
                                | wx.PD_REMAINING_TIME
                                )
                                
    def updateProg(self, step=None, message=None):
        self.prog = self.prog + 1
        if step is not None and message is not None:
            self.progDlg.Update(step, message)
        else:
            self.progDlg.Pulse(message)
        
    def delProg(self):
        if self.progDlg:
            self.progDlg.Destroy()
            
    def showError(self, message):
        self.errDlg = wx.MessageDialog(self, message,
                               'Error',
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        self.errDlg.ShowModal()
        self.errDlg.Destroy()
        if self.email:
            self.sendmail(message)
        
    def sendmail(self, message):
        info = ['smtp.helsinki.fi:587', 'joona.lehtomaki@helsinki.fi',
                'joona.lehtomaki@helsinki.fi']
        sentry = mailer.MailSentry(info)
        sentry.sendmail('jlehtoma', 'nEzz3qvi', message)
        sentry.savelog(os.path.abspath(sys.path[0]))
                
    def getoutputname(self, file):
        if self.params['outdir'] and file and self.params['variable']:
            infile = os.path.basename(file).split('.')
            date =  datetime.date.today().isoformat()
            date = date.replace('-', '_') 
            var = self.params['variable'].split(' ')[0]
            outfile = '%s_v%s_%s.%s'  % (infile[0], var, date, 'asc')
            return outfile

class XyzFormLayout(XyzForm):
    def doLayout(self):
        ''' Layout the controls by means of sizers. '''

        # A vertical BoxSizer will contain the GridSizer (on the top)
        # and the logger text control (on the bottom):
        boxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        
        # Another vertical BoxSizer to hold add and remove buttons for the 
        # ListBox
        addBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        
        # A GridSizer will contain the other controls:  
        gridSizer = wx.FlexGridSizer(rows=5, cols=3, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)
    
        # Add the controls to the sizers:

        for control, options in \
            [(self.addButton, dict(border=5, flag=wx.ALIGN_RIGHT)),
                 (self.removeButton, dict(border=5, flag=wx.ALIGN_RIGHT))]:
            addBoxSizer.Add(control, **options)
        
        for control, options in \
                [(self.inNameLabel, noOptions),
                 (self.inTextCtrl, expandOption),
                 (self.browseInButton, dict(flag=wx.ALIGN_RIGHT)),
                 (self.selectedLabel, noOptions),
                 (self.selectedListBox, dict(flag=wx.ALIGN_CENTER)),
                 (addBoxSizer, noOptions),
                 (self.outNameLabel, noOptions),
                 (self.outTextCtrl, expandOption),
                 (self.browseOutButton, dict(flag=wx.ALIGN_RIGHT)),
                 (self.varLabel, noOptions),
                 (self.referrerChoice, expandOption),
                  emptySpace,
                  emptySpace,
                  (self.standardCheckBox, noOptions),
                  emptySpace,
                  emptySpace,
                 (self.convertButton, dict(flag=wx.ALIGN_CENTER)),
                 (self.pngDeco, dict(flag=wx.ALIGN_RIGHT)),
                  emptySpace]:
            gridSizer.Add(control, **options)
        
        for control, options in \
                [(gridSizer, dict(border=5, flag=wx.ALL)),
                 (self.logger, dict(border=5, flag=wx.ALL|wx.EXPAND,
                    proportion=1))]:
            boxSizer.Add(control, **options)
        
        self.SetSizerAndFit(boxSizer)

class ExtractorForm(wx.Panel):
    ''' The ExtractorForm class is a wx.Panel that creates a bunch of controls
        and handlers for callbacks. Doing the layout of the controls is 
        the responsibility of subclasses (by means of the doLayout()
        method). '''

    def __init__(self, *args, **kwargs):
        super(ExtractorForm, self).__init__(*args, **kwargs)
        # Set the variables
        self.createControls()
        self.bindEvents()
        self.doLayout()
        
        # Create a parameter dictionary that is passed to gridding
        self.params = {'infile': None,
                       'outfile': None,
                       'rows': 0}
        
        # Establish wildcards used in file browsing
        self.wildcard = "Text files (*.txt)|*.txt|"     \
           "All files (*.*)|*.*"

    def createControls(self):
        self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY, 
                                  size=(300, 200))
        self.extractButton = wx.Button(self, label="Extract")
        self.browseInButton = wx.Button(self, label="browse")
        self.browseOutButton = wx.Button(self, label="browse")
        self.inNameLabel = wx.StaticText(self, label="Input XYZ file:")
        self.outNameLabel = wx.StaticText(self, label="Output XYZ file:")
        self.rowsNameLabel = wx.StaticText(self, label="Extracted lines:")	
        
        self.inTextCtrl = wx.TextCtrl(self, value="", size=(300,1))
        self.outTextCtrl = wx.TextCtrl(self, value="", size=(300,1))
        self.rowsTextCtrl = wx.TextCtrl(self, value="", size=(300,30))

        png1 = wx.Image('images/view-fullscreen.png', 
                            wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.pngDeco = wx.StaticBitmap(self, -1, png1)

    def bindEvents(self):
        for control, event, handler in \
            [(self.extractButton, wx.EVT_BUTTON, self.onExtract),
             (self.browseInButton, wx.EVT_BUTTON, self.onBrowseIn),
             (self.browseOutButton, wx.EVT_BUTTON, self.onBrowseOut),
             (self.inTextCtrl, wx.EVT_TEXT, self.onInNameEntered),
             (self.inTextCtrl, wx.EVT_CHAR, self.onInNameChanged),
             (self.outTextCtrl, wx.EVT_TEXT, self.onOutNameEntered),
             (self.outTextCtrl, wx.EVT_CHAR, self.onOutNameChanged),
             (self.rowsTextCtrl, wx.EVT_TEXT, self.onRowsNameEntered),
             (self.rowsTextCtrl, wx.EVT_CHAR, self.onRowsNameChanged)]:
            control.Bind(event, handler)

    def doLayout(self):
        ''' Layout the controls that were created by createControls(). 
            XyzForm.doLayout() will raise a NotImplementedError because it 
            is the responsibility of subclasses to layout the controls. '''
        raise NotImplementedError

    # Callback methods:

    def onExtract(self, event):
        try:
            rowvalue = int(self.rowsTextCtrl.GetValue())
            assert rowvalue > 0, self.log("Value must be positive!")
            if None not in self.params.values():
                self.exDlg = wx.ProgressDialog("Work in progress",
                               "Lines are being extracted...",
                               maximum = rowvalue,
                               parent=self,
                               style = wx.PD_CAN_ABORT
                                | wx.PD_APP_MODAL
                                | wx.PD_ELAPSED_TIME
                                | wx.PD_AUTO_HIDE
                                | wx.PD_REMAINING_TIME
                               )
                keepGoing = True
                count = 0
                infile = open(self.params['infile'], 'r')
                outfile = open(self.params['outfile'], 'w')
    
                for i in xrange(rowvalue):
                    count += 1
                    outfile.write(infile.readline())
                    (keepGoing, skip) = self.exDlg.Update(count)
                    if not keepGoing:
                        break
                infile.close()
                outfile.close                
                self.exDlg.Destroy()
                if keepGoing:
                    self.log("Extraction complete!")
                else:
                    self.log("Extraction aborted by user.")
        except ValueError:
            self.log("Value must be integer!")
        
    def onBrowseIn(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=self.wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        # TODO: modify so that multiple files can be processed

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()

            for path in paths:
                self.inTextCtrl.SetValue(path)
                self.params['infile'] = path
                    
        dlg.Destroy()
        
    def onBrowseOut(self, event):
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=self.wildcard, style=wx.SAVE
            )

        # This sets the default filter that the user will initially see. Otherwise,
        # the first filter in the list will be used by default.
        dlg.SetFilterIndex(0)

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.outTextCtrl.SetValue(path)
            self.params['outfile'] = path

        dlg.Destroy()
    
    def onInNameEntered(self, event):
        #self.log('User entered name: %s' % event.GetString())
        event.Skip()

    def onInNameChanged(self, event):
        #self.log('User typed character: %d' % event.GetKeyCode())
        event.Skip()
        
    def onOutNameEntered(self, event):
        #self.log('User entered name: %s' % event.GetString())
        event.Skip()

    def onOutNameChanged(self, event):
        #self.log('User typed character: %d' % event.GetKeyCode())
        event.Skip()
        
    def onRowsNameEntered(self, event):
        event.Skip()

    def onRowsNameChanged(self, event):
        event.Skip()

    # Helper method(s):

    def log(self, message):
        ''' Private method to append a string to the logger text
            control. '''
        self.logger.AppendText('%s\n' % datetime.datetime.now().ctime())    
        self.logger.AppendText('%s\n' % message)
        self.logger.AppendText('\n')
        
    def __extractLines(self):
        ''' Private method to extract certain number of lines from target
            XYZ-file.'''
        pass

class ExtractorFormLayout(ExtractorForm):
    def doLayout(self):
        ''' Layout the controls by means of sizers. '''

        # A horizontal BoxSizer will contain the GridSizer (on the left)
        # and the logger text control (on the right):
        boxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        # A GridSizer will contain the other controls:
        gridSizer = wx.FlexGridSizer(rows=5, cols=3, vgap=10, hgap=10)

        # Prepare some reusable arguments for calling sizer.Add():
        expandOption = dict(flag=wx.EXPAND)
        noOptions = dict()
        emptySpace = ((0, 0), noOptions)
        
        # Add the controls to the sizers:
        for control, options in \
                [(self.inNameLabel, noOptions),
                 (self.inTextCtrl, expandOption),
                 (self.browseInButton, dict(flag=wx.ALIGN_RIGHT)),
                 (self.outNameLabel, noOptions),
                 (self.outTextCtrl, expandOption),
                 (self.browseOutButton, dict(flag=wx.ALIGN_RIGHT)),
                 (self.rowsNameLabel, noOptions),
                 (self.rowsTextCtrl, expandOption),
                  emptySpace,
                  emptySpace,
                 (self.extractButton, dict(flag=wx.ALIGN_CENTER)),
                 (self.pngDeco, dict(flag=wx.ALIGN_RIGHT)),
                  emptySpace]:
            gridSizer.Add(control, **options)

        for control, options in \
                [(gridSizer, dict(border=5, flag=wx.ALL)),
                 (self.logger, dict(border=5, flag=wx.ALL|wx.EXPAND,
                    proportion=1))]:
            boxSizer.Add(control, **options)
        
        self.SetSizerAndFit(boxSizer)

class FrameWithForms(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(FrameWithForms, self).__init__(pos=(300, 100), *args, **kwargs)
            
        menuFile = wx.Menu()
        menuFile.AppendSeparator()
        menuFile.Append(2, "E&xit", "Exit the program")
        
        menuTools = wx.Menu()
        menuTools.Append(3, "Use email alert", "Send email notifications in " + 
        "case of an exception", wx.ITEM_CHECK)
        subMemMenu = wx.Menu()
        subMemMenu.Append(41, "8 Mb (default)", "Limit file read to 8 Mb (default)", wx.ITEM_RADIO)
        subMemMenu.Append(42, "2 Mb", "Limit file read to 2 Mb", wx.ITEM_RADIO)
        subMemMenu.Append(43, "4 Mb", "Limit file read to 4 Mb", wx.ITEM_RADIO)
        subMemMenu.Append(44, "16 Mb", "Limit file read to 16 Mb", wx.ITEM_RADIO)
        subMemMenu.Append(45, "32 Mb", "Limit file read to 32 Mb", wx.ITEM_RADIO)

        # Create a dcitionary which will have the following structure
        # key: control id
        # value: a tuple -> (name of the extent, extent list)
        self.extents = {}
        menuTools.AppendMenu(4, "Max memory", subMemMenu)
        subExtMenu = wx.Menu()
        self.setextentmenu(subExtMenu)
        menuTools.AppendMenu(5, "Custom extent", subExtMenu)
        
        
        menuHelp = wx.Menu()
        menuHelp.Append(1, "&About...")
        
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        menuBar.Append(menuTools, "&Tools")
        menuBar.Append(menuHelp, "&Help")
        
        self.SetMenuBar(menuBar)
        self.CreateStatusBar()
        self.SetStatusText("Welcome to Gridder!")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=1)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=2)
        self.Bind(wx.EVT_MENU_RANGE, self.OnEmailNotif, id=3) 
        self.Bind(wx.EVT_MENU, self.OnMemoryMax, id=41)
        self.Bind(wx.EVT_MENU, self.OnMemoryMax, id=42)
        self.Bind(wx.EVT_MENU, self.OnMemoryMax, id=43)
        self.Bind(wx.EVT_MENU, self.OnMemoryMax, id=44)
        self.Bind(wx.EVT_MENU, self.OnMemoryMax, id=45)
        
        # Create a notebook to hold different tabs
        notebook = wx.Notebook(self)
        # First one is be XYZtoGrid
        self.xyz2grid = XyzFormLayout(notebook)
        notebook.AddPage(self.xyz2grid, 'XYZtoASCII')
        # Second one is sample extractor
        self.sampleExtractor = ExtractorFormLayout(notebook)
        notebook.AddPage(self.sampleExtractor, 'Sample Extractor')
        # We just set the frame to the right size manually. This is feasible
        # for the frame since the frame contains just one component. If the
        # frame had contained more than one component, we would use sizers
        # of course, as demonstrated in the XyzFormLayout class above.
        self.SetClientSize(notebook.GetBestSize())
        
    def setextentmenu(self, submenu):
        try:
            # Open the file holding extents
            content = eval(''.join(open('extents.dat', 'r').readlines()))
            itemids = []
            # Populate target submenu
            for i, item in enumerate(content):
                d_extent = 'N = %s S = %s E = %s W = %s Res = %s' \
                % (item[1][0], item[1][1], item[1][2], item[1][3], item[1][4])
                submenu.Append((51 + i), item[0], d_extent, wx.ITEM_RADIO)
                itemids.append(51 + i)
                self.extents[(51 + i)] = (item[0], item[1])
            # Add possibility to edit extents
            submenu.AppendSeparator()
            itemids.append(itemids[-1] + 1)
            submenu.Append((itemids[-1]), "Edit...", "Edit custom extents")

            # Bind menus to handlers, all but edit command
            for cid in itemids[:-1]:
                self.Bind(wx.EVT_MENU, self.OnSetExtent, id=cid)
            # Bind edit... command
            self.Bind(wx.EVT_MENU, self.OnEditExtent, id=itemids[-1])
        except:
            submenu.Append(51, "Not available")
        
    def OnAbout(self, evt):
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = "Gridder"
        info.Version = version
        info.Copyright = "(C) 2008 Programmers and Coders Everywhere"
        info.Description = wordwrap(
            "...",
            350, wx.ClientDC(self))
        info.WebSite = ("http://www.helsinki.fi/science/metapop/english/Software.htm", 
                        "MRG software page")
        info.Developers = [ "Joona Lehtomäki"]

        try:
            licenseText = ''.join([line for line in open('license.txt', 'r').readlines()])
        except IOError:
            licenseText = "License file not present in installation folder, " + \
            "licensed according to MIT license."
        info.License = wordwrap(licenseText, 600, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)
        
    def OnEmailNotif(self, event):
        if event.IsChecked():
            self.xyz2grid.set_emailnotif(True)
        else:
            self.xyz2grid.set_emailnotif(False)
        
    def OnMemoryMax(self, evt):
        id = evt.GetId()
        levels = {41: 8, 42: 2, 43: 4, 44: 16, 45:32}
        self.xyz2grid.set_memlevel(levels[id])    
    
    def OnEditExtent(self, evt):
        print 'Editing'
    
    def OnSetExtent(self, evt):
        id = evt.GetId()
        if id == 51:
            self.xyz2grid.set_extent(None)
        else:
            self.xyz2grid.set_extent(self.extents[id])
    
    def OnQuit(self, event):
        self.Close()

class ExtentDialog(wx.Dialog):
    '''Custom dialog for setting custom extents.'''
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):
       
        # Custom decorations instead of invocing wx.Dialog __init__ directly
        # See demos dialog for explanation
        self.pre = wx.PreDialog()
        self.pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        self.pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(self.pre)
            
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(self, label="Adjust memory allocation")
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
       
        # Create slider
        self.slider = wx.Slider(self, 100, 100, 1, 100, (30, 60), (250, -1), 
            wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS 
            )
        self.slider.SetTickFreq(5, 1)
        
        # Create ok button
        self.okButton = wx.Button(self, wx.ID_OK, " OK ")
        
        self.sizer.Add(self.slider, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.sizer.Add(self.okButton, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        
    def getValue(self):
        print self.slider.GetValue()
        return self.slider.GetValue()
        
if __name__ == '__main__':
    app = wx.App(0)
    frame = FrameWithForms(None, title='Gridder %s' % version)
    frame.Show()
    app.MainLoop()
