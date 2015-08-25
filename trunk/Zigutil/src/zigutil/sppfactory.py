import os
import sys
from types import IntType, FloatType
from winhelpper import Readexcel

class Sppobject(object):
    '''Class instances represent a single Zonation input object (i.e. raster layer).
    Numerical parameters and file path are represented as properties.
    '''
    
    # Class variable keeps track of instantiated objects
    refcounter = 0
    # UID variable to be assigned as an id
    UID = 0
    
    #weight=1.0, alpha=1.0, bqp=1, bqp_b=1, cellrem=1.0, sppfile=None
    
    def __init__(self, params={'weight':[1.0], 'alpha':[1.0], 'bqp':[1], 
                               'bqp_b':[1], 'cellrem':[1.0], 'sppfile':[None]},
                               index=0):
        '''Constructor method has default values for parameters
        to enable batch creation of objects. However, these refer
        to dummy variables in Zonation manual.
        '''
    
        # Adjust reference counter and UID
        Sppobject.refcounte = Sppobject.refcounter + 1
        Sppobject.UID = Sppobject.UID + 1
        
        # Assign instance variables if given to the constructor
        self.__id = Sppobject.UID
        self.__weight = params['weight'][index]
        self.__alpha = params['alpha'][index]
        self.__bqp = params['bqp'][index]
        self.__bqp_b = params['bqp_b'][index]
        self.__cellrem = params['cellrem'][index]
        self.__sppfile = params['sppfile'][index]
        
        # A list holding the names for important parameters
        self.__params = ['id', 'weight', 'alpha', 'bqp', 'bqp_b',
                        'cellrem', 'sppfile']
        
        # Set local assertion warnings
        self.s_typeint = 'Value must be integer type >> current type: '
        self.s_typeintflt = 'Value must be integer or float type >> current type: '
        self.s_pos = 'Value must be positive >> current value: '
        self.s_path = 'File entered does not exist >> current path: '
        self.s_file = 'File entered is not an ASCII raster >> file extension: '
        
    def __str__(self):
        values = self.getparams()
        return '%s%s' % ('\n'.join((item + ':' + self.padding(item) *  
                                      '\t' + values[item]) for item in self.__params),
                          '\n')
        
    def __del__(self):
        # Release the unique id number
        Sppobject.refcounter = Sppobject.refcounter - 1
        
    # Accessor methods
    
    # ------ id -------
    def getid(self):
        return self.__id
    
    def setid(self, value):
        assert type(value) is IntType, '%s%s' % (self.s_typeint, type(value))
        self.__id = value
        
    def delid(self):
        del self.__id
    
    # ------ weight -------
    
    def setweight(self, value):
        assert type(value) in (IntType, FloatType), '%s%s' % (self.s_typeintflt, type(value))
        assert value > 0, '%s%s' % (self.s_pos, value)
        self.__weight = float(value)
        
    def getweight(self):
        return self.__weight
    
    def delweight(self):
        del self.__weight
    
    # ------ alpha -------
    
    def getalpha(self):
        return self.__alpha
    
    def setalpha(self, value):
        assert type(value) in (IntType, FloatType), '%s%s' % (self.s_typeintflt, type(value))
        assert value >= 0.0, '%s%s' % (self.s_pos, value)
        self.__alpha = value
        
    def delalpha(self):
        del self.__alpha
    
    # ------ bqp -------
    
    def getbqp(self):
        return self.__bqp

    def setbqp(self, value):
        assert type(value) in (IntType, FloatType), '%s%s' % (self.s_typeintflt, type(value))
        assert value > 0.0, '%s%s' % (self.s_pos, value)
        self.__bqp = value
        
    def delbqp(self):
        del self.__bqp
    
    # ------ bqp_b -------
    
    def getbqp_b(self):
        return self.__bqp_b
    
    def setbqp_b(self, value):
        assert type(value) in (IntType, FloatType), '%s%s' % (self.s_typeintflt, type(value))
        assert value > 0.0, '%s%s' % (self.s_pos, value)
        self.__bqp = value
        
    def delbqp_b(self):
        del self.__bqp
    
    # ------ cellrem -------
    
    def getcellrem(self):
        return self.__cellrem
    
    def setcellrem(self, value):
        assert type(value) in (IntType, FloatType), '%s%s' % (self.s_typeintflt, type(value))
        assert value > 0.0, '%s%s' % (self.s_pos, value)
        self.__cellrem = value
        
    def delcellrem(self):
        del self.__cellrem
    
    # ------ sppfile -------
    
    def getsppfile(self):
        return self.__sppfile
    
    def setsppfile(self, value):
        assert os.path.exists(value), '%s%s' % (self.s_path, value)
        self.__sppfile = value
        
    def delsppfile(self):
        del self.__sppfile
    
    id = property(getid, setid, delid, '')
    weight = property(getweight, setweight, delweight, '')
    alpha = property(getalpha, setalpha, delalpha, '')
    bqp = property(getbqp, setbqp, delbqp, '')
    bqp_b = property(getbqp_b, setbqp_b, delbqp_b, '')
    cellrem = property(getcellrem, setcellrem, delcellrem, '')
    sppfile = property(getsppfile, setsppfile, delsppfile, '')  
        
    # Helper methods    
    
    def getparams(self):
        """Returns a dictionary with paramters and corresponding values. Keys 
        are parameter names held in class list params, values are corresponding
        values. All values are given as strings. Exclude
        parameter defines a list of object parameters to be excluded.
        """
        return{self.__params[0]: str(self.getid()), self.__params[1]: str(self.getweight()), 
                self.__params[2]: str(self.getalpha()), self.__params[3]: str(self.getbqp()),
                self.__params[4]: str(self.getbqp_b()), self.__params[5]: str(self.getcellrem()),
                self.__params[6]: str(self.getsppfile())}
        
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
        selparams = self.__params
        for exc in exclude:
            if exc in selparams:
                selparams.remove(exc)
                
        return '%s%s' % (' '.join((values[item]) for item in selparams), '\n')
        
class Sppfactory(object):
    '''Class for creating input list file for Zonation. Instantiates individual
    Sppobjects.
    '''
    
    def __init__(self, name='specieslistfile'):
        # Counter variable to track the number of live Sppobjects
        self.sppobject = 0
        # List to hold created Sppobjects
        self.objectrack = []
        # Iteratot index
        self.index = 0 - 1
        # Object nam
        self.name = name
        
        self.envar = 'ZONATION_HOME'
        if os.environ.get(self.envar):
            self.home = os.environ.get(self.envar)
            #print 'Zonation home (%s) set to: %s' % (self.envar, self.home)
        else:
            print 'Environment variable (%s) not set.' % self.envar
        
    def __iter__(self):
        return self
    
    def next(self):
        if self.index == len(self.objectrack) - 1:
            raise StopIteration
        self.index = self.index + 1
        return self.objectrack[self.index]
    
    def add_to_rack(self, path, params={}, ext='.asc', sheet=None, duplicate=False,
                    weight=False, alpha=0, method=1, con=False):
        '''Method creates Sppobject(s) from input path. If path points
        to a single ASCII raster file only one Spp object is created and
        added to objectrack. If path points to a directory, all files in
        the directory receive a respective Sppobject representation. By
        deafult duplicate is off (False) -> if file already has an object
        in objectstack it will not be added.
        
        An additional Excel file can used a configuration reference, in
        this case the path passed as a parameter points to a valid Excel
        file. In this case also a correct sheet name must be provided.
        '''
        
        if os.path.exists(path) and path.endswith('.xls'):  
            # Read in the Excel file
            xl = Readexcel(path)
            
            # Parameter lists from the right sheet
            # TODO: column headers hard coded
            if weight == 1:
                params['weight'] = xl.getcol(sheet, 'Weight')
            elif weight == 2:
                params['weight'] = xl.getcol(sheet, 'localWeight')
            elif weight == 3:
                params['weight'] = xl.getcol(sheet, 'abcWeight')
            else:
                params['weight'] = xl.getcol(sheet, 'nonWeight')
            
            # TODO: this is dysfunctional
            alphas = {False: 'Alpha',
                      True: 'Alpha'}
            
            params['alpha'] = xl.getcol(sheet, alphas[alpha])
            
            params['bqp'] = map(int, xl.getcol(sheet, 'BQP'))
            params['bqp_b'] = map(int, xl.getcol(sheet, 'BQP_b'))
            
            if method == 1:
                params['cellrem'] = xl.getcol(sheet, 'Cellrem')
            elif method == 2:
                params['cellrem'] = xl.getcol(sheet, 'smallCellrem')
                
            # Check that the spp file specified exists
            ascii = xl.getcol(sheet, 'Filepath_ascii')
            error = False
            for file in ascii:
                if not os.path.exists(file):
                    print 'ASCII file %s does not exist.' % file
                    error = True
            if error:
                print 'One or more ASCII files did not exist, aborting.'
                sys.exit(0)
                    
            params['sppfile'] = ascii
                    
            for i in xrange(xl.nrows(sheet) - 1):
                self.objectrack.append(Sppobject(params, i))
        
        elif os.path.exists(path) and path.endswith(ext) and not duplicate:
            # Path points to a single file, no duplicate
            if path not in self.getpaths():
                params['sppfile'] = path
                self.objectrack.append(Sppobject(params))
        elif os.path.exists(path) and path.endswith(ext):
            # Path points to a single file, duplicate
            params['sppfile'] = path
            self.objectrack.append(Sppobject(params))
        elif os.path.exists(path):
            # Path is a directory path that exists
            files = self.listfiles(path, ext)
            for i, file in enumerate(files):
                if path != self.home:
                    file = os.path.join(path, file)
                    params['sppfile'].append(file)
                self.objectrack.append(Sppobject(params, i))
        else:
            print 'File / path entered does not exist.'
    
    def describe(self):
        '''Method descirbes object rack by printing string representations
        of individual objects.
        '''
        for obj in self:
            print str(obj)
        self.index = -1
            
    def getname(self):
        return self.name
        
    def getpaths(self):
        '''Methods returns a list holding all file paths in objectrack.
        
        Return list
        '''
        list = []
        for obj in self.objectrack:
            list.append(obj.sppfile)
        return list
    
    def listfiles(self, path, ext=None):
        '''Method lists all files in a directory specified by a file 
        extension.
        
        Return list
        '''
        return [file for file in os.listdir(path) if file.endswith(ext)]
    
    def printfile(self, dirname=None, exclude=None):
        '''Method to print object rack into a file. Exclude
        parameter defines a list of object parameters to be excluded.
        '''
        if not dirname:
            dirname = os.path.join(self.home, (self.name + '.spp'))
            
        if self.objectrack:
            
            outfile = open(dirname, 'w')
            # Loop through objectrack objects and pretty print parameters,
            # finally strip out trailing newline
            outfile.write(''.join(cont.pprint(exclude) for cont 
                                  in self).rstrip('\r\n'))
            outfile.close()

if __name__ == '__main__':
    #dir = 'E:\Data\Zonation\input_mh'
    factory = Sppfactory()
    
    weights = [5.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 1.0, 0.5, 5.0, 
               2.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 5.0, 10.0, 5.0, 1.0, 
               5.0, 2.0, 5.0, 5.0, 1.0, 10.0]
    
    weights_n = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 
               1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 
               1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    
    alpha = [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 
             0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 
             0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 
             0.001, 0.001, 0.001]
    
    bqp = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
           1, 1, 1, 1, 1, 1, 1, 1]
    
    bqp_b = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
             1, 1, 1, 1, 1, 1, 1, 1]
    
    cellrem = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 
               1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 
               1.0, 1.0, 1.0, 1.0]
    
    #alpha = [new*1000 for new in alpha]
    #cellrem = [new/4 for new in cellrem]
    
    dir = r'E:\Data\Zonation\ConfigureData.xls'
    params={'weight':weights_n, 'alpha':alpha, 'bqp':bqp, 
            'bqp_b':bqp_b, 'cellrem':cellrem, 'sppfile':[]}
    
    factory.add_to_rack(dir, params, sheet='Selected_mtm_loc_all')
    #factory.add_to_rack(dir, params)
    #factory.describe()
    factory.printfile(exclude=['id'])