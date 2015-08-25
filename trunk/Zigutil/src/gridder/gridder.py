import time
import features

def print_timing(func):
    def wrapper(*arg, **kwargs):
            for i in range(1):
                t1 = time.time()
                res = func(*arg, **kwargs)
                t2 = time.time()
                elapsed = ''
                if t2 - t1 < 1.0:
                    print t2 - t1
                    elapsed =  '%0.1f ms' % ((t2 - t1) * 1000.0)
                elif t2 - t1 < 60.0:
                    elapsed = '%0.1f s' % (t2 - t1)
                else:
                    elapsed = '%s m %s s' % (int((t2 - t1) / 60), int((t2 - t1) % 60))
                print str(i + 1) + ': %s took %s' % (func.func_name, elapsed)
    return wrapper
 
class Grid(object):
    
    #@print_timing
    def __init__(self, input, output, variable, memlevel=8, parent=None, 
                dimensions=None):
        '''__init__ method can be provided with dimensions [list] so that they
        do not have to be calculated again.'''
        
        try:
        # If psyco is installed this script runs much faster...
            import psyco
            psyco.full()
            parent.log('Psyco available and used.')
        except ImportError:
            # Oh, well, it's not installed. We don't need it.
            pass
        
        self.input = input
        self.fout = output
        self.res = None
        self.ZVALUE = variable
        print 'Zvalue: %s' % self.ZVALUE
        self.memlevel = memlevel
        
        # Set parent if one is provided
        self.parent = parent
        print parent
        
        # Set dimesions of the grid -> they can be provided by the user as a
        # list dimensions or they can be calculated from the data
        self.dims = None
        self.YOFFSET = 0.0
        self.setdimensions(dimensions)
        
        self.locs = []
        self.loclength = None
        self.locindex = None
        # Temporary container for uneven iteration in grid rows
        self.temp_hold = []
        self.YCOORD = 0
        self.XCOORD = 1
        self.NODATA = '-1'
        
        # Set progress update interval
        self.interval = 10000
        
        # Variable tells which read-in block iteration is under way
        self.block = 1
        self.dealt = None
        self.coldif = 0
        
        # Variable to hold current REAL positions in grid loop
        self.r = 0
        
        # Create a features object to track variables in MS-NFI data
        # Default language is Finnish
        self.vars = features.Nfifeats()
        # Read input and build the grid
        
        # Open input file for reading
        fin = open(self.input, 'r')
        
        if self.parent:
                self.parent.showProg(max=self.dims['rows'], message =
                'Processing input block: %s' % self.block)        
        
        if self.memlevel is None:
            lines = fin.readlines()
            self.readinput(lines)
        else:
            while 1:
                # Read the lines in chunks from the file objects, the amount
                # of memory is determined by memelevel (* 1 Mb)
                lines = fin.readlines(self.memlevel * 1000000)
                if not lines:
                    break
                self.dealt = True
                self.first = True
                self.readinput(lines)
                
                self.block = self.block + 1
            
    #@print_timing
    def readinput(self, lines):
        # If memory runs out, it will cause an exception here as the lists
        # are built, use local variables for performance, avoid dots
        XCOORD, YCOORD, ZVALUE = self.XCOORD, self.YCOORD, self.ZVALUE
        yl = []
        y_app = yl.append
        xl = []
        x_app = xl.append
        zl = []
        z_app = zl.append
        interval = self.interval
        
        try:
            for line in lines:
                blist = line.split()
                # Get the wanted variables
                # Zvalue get -1 because on zero-indexing
                (y, x, z) = (blist[YCOORD], blist[XCOORD], blist[ZVALUE - 1])
                y_app(y)
                x_app(x)
                z_app(z)
                #if self.parent:
                #    interval = interval - 1
                #    if interval == 0:
                #        self.parent.updateProg(message='Reading in data on input segment: %s' % self.block)
                #        interval = self.interval
            y_list = map(float, yl)
            del yl
            x_list = map(float, xl)
            del xl
            z_list = map(int, zl)
            del zl

        except MemoryError:
            if self.parent:
                self.parent.delProg()
            raise

        minx = self.dims['minx']
        maxy = self.dims['maxy']
        cols = self.dims['cols']
        res = self.res
        
        # If something is left from the previous loop assign it to locs
        locs = self.temp_hold
        currow = 0
        # Then clear local hold
        self.temp_hold = []
        locs_app = locs.append
        
        # Set the parent Progress Bar upadate interval
        interval = self.interval
        # Variable to track current row in local loop
        row_i = None
            
        newitems = len(x_list)
        
        for i in xrange(newitems):
            # Calculate absolute locations instead of coordinate locations
            y_loc = (maxy - (y_list[i] - self.YOFFSET) + res) / res - 1
            x_loc = abs((minx - x_list[i] + res) / res - 1)
            # Append locs list with absolute locations and z value
            locs_app((y_loc, x_loc, z_list[i]))
            
            #if self.parent:    
            #    interval = interval - 1
            #    if interval == 0:
            #        self.parent.updateProg('Processing coordinates on input' + 
            #                               'segment: %s...' % self.block)
            #        interval = self.interval
        
        # Fresh count for rows
        olditems = len(locs)
        for i in xrange(olditems):
            if locs[i][0] != locs[i - 1][0]:
                currow = currow + 1
                row_i = i
        
        hitter = 0
        if row_i != None and olditems - (row_i + 1) < cols:
            hitter = hitter + 1
            self.temp_hold = locs[row_i:]
            #print 'locs before del: %s' % len(locs)
            del locs[row_i:]
            #print 'locs after del: %s' % len(locs)
            #print 'temp_hold after del: %s' % len(self.temp_hold)
            #print 'hitter: %s' % hitter
            currow = currow - 1

        grid = []
        grid_app = grid.append
        
        #if self.first: 
        #        print 'Sets first triplet: ' + str(locs[0])
        #        print 'Sets last triplet: ' + str(locs[-11]) 
        #        self.first = False
                
        #print 'cols: %s' % cols
        #print 'currow: %s' % currow
        
        self.locindex = 0
        self.loclength = len(locs)

        for r in xrange(currow):
            
            # Loop through column items (c) on a row (r) and get z value 
            # based on c, r AND coordinate location and z value (last in
            # locs list because of popping
            # If locs = [] --> iteration has reached an end
            # r must first be adjusted based on previous loop
            r_i = r + self.r

            grid_app('\t'.join([self.getz(r_i, c, locs[self.locindex]) 
                                for c in xrange(cols)]))
            
        if self.temp_hold != []:
            self.coldif = len(self.temp_hold)
            
        
        #if grid != []:
        #    print 'Grid row length: %s, row length: %s' % (len(grid), len(grid[-1]))
        #    print 'Block: %s' % self.block
        #    print 'Rows so far: %s / %s' % ((self.r + currow), self.dims['rows'])
        
        # Adjust r.self for next loop
        self.r = self.r + currow
        
        if self.parent:
            self.parent.updateProg(step=self.r + 1,
            message='Processing row %s/%s' % (self.r, self.dims['rows']))        
        
        if self.block == 1:
            outfile = open((self.fout), 'w')
        else:
            outfile = open((self.fout), 'a')
            
            outfile = open((self.fout), 'a')
        
        if self.block == 1:
            self.writeheader(outfile)

        # Then itarate through the grid
        for row in grid:
            outfile.write(row + '\n')
        outfile.close()
    
    # Helper methods
    #@print_timing    
    def setdimensions(self, dimensions=None):
        '''Method set the dimensions provided by the user or calculated by 
        the program, dimensions is given as:
            dimensions[0] = maxy
            dimensions[1] = miny
            dimensions[2] = maxx
            dimensions[3] = minx
            dimensions[4] = resolution'''
            
        if dimensions is None:
            dimensions = self.getdimensions()
        
        if self.parent:
            self.parent.log(dimensions) 
        
        self.dims = {'maxy': dimensions[0] - self.YOFFSET, 
                     'miny': dimensions[1] - self.YOFFSET, 
                     'maxx': dimensions[2], 
                     'minx': dimensions[3]}
        
        if self.parent:
            self.parent.log(dimensions)
        
        self.res = dimensions[4]
            
        # Calculate the number of rows and columns            
        self.dims['cols'] = int((self.dims['maxx'] - self.dims['minx'] + \
                            self.res) / self.res)
        self.dims['rows'] = int((self.dims['maxy'] - self.dims['miny'] + \
                            self.res) / self.res)
    
        #print self.dims
    
    def getdimensions(self):
        '''Method to calculate geographical dimensions of a given input
        data file.'''
        if self.parent:
            print self.parent
            self.parent.log('Calculating dimensions...')
            
        xmax_t = None
        xmin_t = None
        ymax_t = None
        ymin_t = None
        res = None
        infile = open(self.input, 'r')
        
        #if self.parent:
        #   self.parent.updateProg('Calculating dimensions...')
        
        while 1:
            y_list = []
            x_list = []
            # Read in a limited block on data
            lines = infile.readlines(self.memlevel * 1000000)
            if not lines:
                break
            for line in lines:
                blist = line.split()
                # Get the wanted variables
                (y, x) = (blist[0], blist[1])
                y_list.append(y)
                x_list.append(x)
            
            # Convert string to float
            y_list = map(float, y_list)
            x_list = map(float, x_list)
            
            # Resolution has to determined only once
            if res is None and x_list[-2] != x_list[-1]:
                res = x_list[-1] - x_list[-2]
            
            # Calculate local maxs and mins
            ymax, ymin = max(y_list), min(y_list)
            xmax, xmin = max(x_list), min(x_list)
            
            # Compare local maxs and mins to global ones
            if ymax_t is None or ymax_t < ymax:
                ymax_t = ymax
            if ymin_t is None or ymin_t > ymin:
                ymin_t = ymin
            if  xmax_t is None or xmax_t < xmax:
                xmax_t = xmax
            if xmin_t is None or xmin_t > xmin:
                xmin_t = xmin
        
        # Create a string containing spatial extents
        # and write it
        outtext = '%s, %s, %s, %s, %s' % (ymax_t, ymin_t, xmax_t, xmin_t, res)  
        outfile = open('spatial_extent.txt', 'w')
        outfile.write(outtext)
        outfile.close()
        
        return [ymax_t, ymin_t, xmax_t, xmin_t, res]

    def getz(self, r, c, triplet):
        # Check if grid coordinates correspond to absolute coordinate
        if self.locindex < self.loclength:
            if (r, c) == (triplet[0], triplet[1]):
                # If so, pop the triplet from the locs list
                if self.locindex != self.loclength - 1:
                    self.locindex = self.locindex + 1
                #if self.dealt:
                #    print 'Block: %s -> hit!' % self.block
                #    self.dealt = False
                # Return the right z value
                return str(triplet[2])
            else:
                return self.NODATA
        else:
            return self.NODATA
        
    def writeheader(self, outfile, rows=None):
        # First construct the header if it's the first iteration block, 
        # additional (non-tab) whitespaces are added
        # TODO: deal with top-left <-> bottom-left switch more properly
        #if self.block == 1:
        outfile.write('ncols' + ((14 - len('ncols')) * ' ') + \
                      str(self.dims['cols']) + '\n')
        if rows is None:
            outfile.write('nrows' + ((14 - len('nrows')) * ' ') + \
                      str(self.dims['rows']) + '\n')
        else:
            outfile.write('nrows' + ((14 - len('nrows')) * ' ') + \
                      str(rows) + '\n')
        outfile.write('xllcorner' + ((14 - len('xllcorner')) * ' ') + \
                      str(self.dims['minx']) + '\n')
        # Coordinates in the MSNFI data are top-left while ASCII grid is
        # low-left
        outfile.write('yllcorner' + ((14 - len('yllcorner')) * ' ') + \
                      str(self.dims['miny'] - self.res) + '\n')
        outfile.write('cellsize' + ((14 - len('cellsize')) * ' ') + \
                      str(self.res) + '\n')
        outfile.write('NODATA_value' + ((14 - len('NODATA_value')) * ' ') \
                      + str(self.NODATA) + '\n')


if __name__ == '__main__':
    #dimensions_p = [7779737.5, 7255237.5, 3628087.5, 3243187.5, 100.0]
    #dimensions_e = [7378212.5, 6620112.5, 3733087.5, 3159087.5, 100.0]
    g = Grid(r'E:\Data\Metla\Raw\ika.txt', 
             'E:\Data\Metla\ProcessedGrids\msnfi_ika.asc',
             11, memlevel=2, dimensions=None)
            # '/home/euchrid/Data/Metla/VMI9_lappi/ika-la.txt'
            # '/home/euchrid/Data/Metla/VMI10/ika.txt'
            # '/home/euchrid/CodeVault/scrapYard/ika_first100000.txt'