#!usr/bin python
# zigcom.py
# coding=utf-8

import pickle
import os
from configobj import ConfigObj

# Check the environment
envar = 'ZONATION_HOME'
if os.environ.get(envar):
    HOME = os.environ.get(envar)
    #OME = r'C:\Data\Zonation'
    #print 'Zonation home (%s) set to: %s' % (envar, HOME)
else:
    print 'Environment variable (%s) not set.' % envar

class Zigcommander(object):
    
    
    '''A class for creating batch-run capability for Zonation.
    '''
    
    def __init__(self, name=None, pickle_file=None, autosave=False):
         
        self.index = -1
        
        self.name = name
        
        # Set the DOS command parameters 'command name of .exe'
        self.doscommand = 'call %s ' % os.path.join(HOME, 'zig2')
        
        self.autosave = autosave
        if autosave:
            self.pickle_file = pickle_file
        
        # Create a batch-run container
        self.runs = []
        
        if pickle_file != None and os.path.exists(os.path.join(HOME, pickle_file)):
            print 'Using existing configuration file'
            # Open the shelf file
            pkl_file = open(os.path.join(self.home, pickle_file), 'rb')
            self.runs  = pickle.load(pkl_file)
            
            pkl_file.close()

    def __str__(self):
        return str(self.runs)
    
    def __iter__(self):
        return self
    
    def next(self):
        if self.index == len(self.runs) - 1:
            raise StopIteration
        self.index = self.index + 1
        return self.runs[self.index]

    def __del__(self):
        if self.autosave and self.runs != []:
                self.pickle_data(self.runs, self.pickle_file)
    
    def create_batch_file(self, output=None, exclude=None, append=False):
        '''Method to print batch file into a file. Exclude
        parameter defines a list of object parameters to be excluded.
        '''
        if not output:
            output = os.path.join(HOME, 'run_multiple.bat')
        else:
            output = os.path.join(HOME, output)
            
        if self.runs:
            if append:
                outfile = open(output, 'a')
            else:
                outfile = open(output, 'w')
            # Loop through self.runs objects and pretty print parameters,
            # finally strip out trailing newline
            outfile.write(''.join(self.doscommand + cont.pprint(exclude) 
                                   for cont in self))
            outfile.close()
            
            return output
    
    def create_config_file(self, filename='zig.dat', use_default=True):
        return Zigconfig(filename, use_default)
        
    def create_run_object(self, **kwargs):
        self.runs.append(Zigrun(**kwargs))
        
    def getname(self):
        return self.name
    
    def get_z_home(self):
        return HOME
        
    def pickle_data(self, data, pickle_file):
        output = open(os.path.join(HOME, pickle_file), 'wb')
        # Pickle the data using the highest protocol available.
        pickle.dump(data, output, -1)

class Zigconfig(object):
    
    '''A class for creating Zonation configuration files.
    '''

    def __init__(self, filename=None, use_default=False):
        
        self.default = os.path.join(HOME, 'set_zig_default.dat')
        if filename is None and os.path.exists(self.default) or use_default:
            self.config = ConfigObj(self.default)
        else:
            self.config = ConfigObj(filename)
        self.config.filename = os.path.join(HOME, filename)
        # Initiate sections, keywords and values
    
    def default_values(self):
        if os.path.exists(self.default):
            self.config = ConfigObj(self.default)
            self.config.filename = self.default
        else:
            print 'No default template available.'
    
    def get_all_sections(self):
        return self.config.keys()

    def get_all_keywords(self, section):
        return self.config[section].scalars
    
    def has_section(self, section):
        return section in self.config.keys()
        
    def has_keyword(self, section, keyword):
        return keyword in self.config[section].scalars
    
    def get_value(self, section, keyword):
        try:
            return self.config[section][keyword]
        except:
            return -1
    
    def set_value(self, section, keyword, value):
        if self.has_section(section) and self.has_keyword(section, keyword):
            self.config[section][keyword] = str(value)
    
    def write(self):
        outfile = open(self.config.filename, 'w')
        self.config.write(outfile)

class Ziginspector(object):
    '''A class for handling Zonation result files and plotting figures.
    '''
    
    def __init__(self, resultfile):
           
        try:
            self.file = open(resultfile, 'r')
            results = self.file.readlines()
            # First data list holds the used run parameters
            self.runparams = []
            self.curves =  []
            
            # Run parameters come first
            target = self.runparams
            
            # Iterate through the lines excluding the first line
            for line in results[1:]:
                target.append(line.split())
                # Change target when curve headers is reached
                if 'Prop_landscape_lost' in line:
                    target = self.curves
            
        except IOError:
            print 'Input result file name wrong!'

    def plot_data(self, species):
        
        import pylab as p
        
        data = []
        lost = []
        for line in self.curves[1:]:
            data.append(line[species+5])
            lost.append(line[0])
        p.plot(data, lost, color='red', lw=2)
        p.axis([0, 1.0, 0, 1.0])
        p.xlabel('Proportion of landscape lost')
        p.ylabel('Proportion of distribution remaining')
        p.show()

class Zigrun(object):
     
    '''A class representing single Zonation run in a batch mode.
    '''

    # Class variable keeps track of instantiated objects
    refcounter = 0
    # UID variable to be assigned as an id
    UID = 0
   
    def __init__(self, **kwargs):
        '''Constructor can have a shelf file (shelved object) as
        a parameter if previous configuration data exists.
        '''
          
        # Adjust reference counter and UID
        Zigrun.refcounter = Zigrun.refcounter + 1
        Zigrun.UID = Zigrun.UID + 1
        
        # Create a list holding the parameter names for order
        self._pnames = ['id', 'load', 'settings', 'sppfiles', 'output', 
                        'UCA', 'DS', 'alphamult', 'closewin']
        
        
        
        # Create a parameter dictionary with the right keys and default values
        self._params = {self._pnames[0]: Zigrun.UID,
                    # Previous solution loading
                    self._pnames[1]: '-r',
                    # Zonation run-settings file
                    self._pnames[2]: 'set.dat',
                    # Zonation species list file/files
                    self._pnames[3]: 'specieslist.spp',
                    # Name of the output file
                    self._pnames[4]: 'output.txt',
                    # Uncertainty analysis
                    self._pnames[5]: 0.0,
                    # Distribution smoothing
                    self._pnames[6]: 0,
                    # Dispersal kernel (alpha) multiplier
                    self._pnames[7]: 1.0,
                    # Should Zonation window be closed after each run
                    self._pnames[8]: 1}
        
        if kwargs != {}:
            for key in kwargs.keys():
                if self._params.has_key(key):
                    self._params[key] = kwargs[key]
                    
    def __str__(self):
        values = self.getparams()
        keys = self._params.keys()
        keys.sort()
        return '%s%s' % ('\n'.join((item + ':' + self.padding(item) *  
                                      '\t' + values[item]) for item in keys),
                          '\n')
        
    def __del__(self):
        # Release the unique id number
        Zigrun.refcounter = Zigrun.refcounter - 1
    
    def get_id(self):
        return self._params['id']
    
    def get_load(self):
        return self._params['load']

    def set_load(self, bool):
        self._params['load'] = bool
        
    def get_output(self):
        return self._params['output']
    
    def set_output(self, name):
        self._params['output'] = name
        
    def get_UCA(self):
        return self._params['UCA']
    
    def set_UCA(self, value):
        self._params['UCA'] = value
        
    def get_DS(self):
        return self._params['DS']
    
    def set_DS(self, value):
        self._params['DS'] = value
        
    def get_settings(self):
        return self._params['settings']
    
    def set_settings(self, value):
        self._params['settings'] = value  
        
    def get_sppfiles(self):
        return self._params['sppfiles']
    
    def set_sppfiles(self, value):
        self._params['sppfiles'] = value
        
    def get_alphamult(self):
        return self._params['alphamult']
    
    def set_alphamult(self, value):
        self._params['alphamult'] = value
        
    def get_closewin(self):
        return self._params['closewin']
    
    def set_closewin(self, value):
        self._params['closewin'] = value
        
    id = property(get_id)
    load = property(get_load, set_load, '')
    output = property(get_output, set_output, '')
    UCA = property(get_UCA, set_UCA, '')
    DS = property(get_DS, set_DS, '')
    settings = property(get_settings, set_settings, '')
    sppfiles = property(get_sppfiles, set_sppfiles, '')
    alphamult = property(get_alphamult, set_alphamult, '')
    closewin = property(get_closewin, set_closewin, '')
    
    # Helper methods    
    
    def getparams(self):
        """Returns a dictionary with paramters and corresponding values. Keys 
        are parameter names held in class list params, values are corresponding
        values. All values are given as strings.
        """
        return{'id': str(self.id), 'load': str(self.load), 
                'output': str(self.output), 'UCA': str(self.UCA),
                'DS': str(self.DS), 'settings': str(self.settings),
                'sppfiles': str(self.sppfiles), 'alphamult': str(self.alphamult),
                'closewin': str(self.closewin)}
        
    def padding(self, string):
        """Helper functions that return a factor for tab padding in string
        represntation."""
        if len(string) < 7:
            return 2
        else:
            return 1
        
    def pprint(self, exclude=None):
        '''Return a pretty print representation of object parameters. Exclude
        parameter defines a list of object parameters to be excluded.
        
        Return String
        '''
        values = self.getparams()
        selparams = self._pnames
        if exclude != None:
            for exc in exclude:
                if exc in selparams:
                    selparams.remove(exc)
                
        return '%s%s' % (' '.join((values[item]) for item in selparams), '\n')
            
if __name__ == '__main__':
    #zig = Zigcommander(pickle_file='config.pkl', autosave=False)
    #zig.create_run_object()
    #zig.create_run_object()('Settings',  'initial removal percent'
    #zig.create_batch_file(exclude=['id'])
    #del(zig)
    c = Zigconfig('set_zig_default.dat', True)
    #c.set_value('Settings',  'initial removal percent',  0.8)
    print c.get_value('Settings',  'mask file')
    #print c.get_all_sections()
    #print c.has_section('Settings')
    #print c.get_all_keywords('Settings')
    #print c.has_keyword('Settings',  'z')
    #c.write()
    #insp = Ziginspector('E:\Data\Zonation\output\metsatalousmaa\\' \
    #                    '20080712_mtm_metso_small_w_ds_abf\output.ABF_EAS100.curves.txt')
    #insp.plot_data(32)
