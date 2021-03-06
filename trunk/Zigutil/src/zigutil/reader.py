import numpy as N
import pylab as P
import scipy as S
from scipy import stats
import os
import sys
import re
from types import TupleType

# Helper functions

def prune(array_a, array_b, nx):
    """ Returns a pair of ndarrays with outliers > n SD
        removed from array_a and corresponding value
        (coordinate) from array_b.
    """
    
    SD = S.std(array_a)
    mean = S.mean(array_a)
    upper = mean + nx * SD
    lower = mean - nx * SD
    pruned_a = []
    pruned_b = []
    for i, value in enumerate(array_a):
        if value > lower and value < upper:
            pruned_a.append(array_a[i])
            pruned_b.append(array_b[i])    
    print
    return N.asarray(pruned_a), N.asarray(pruned_b)

def read_array(filename, dtype, separator=' '):
    """ Read a file with an arbitrary number of columns.
        The type of data in each column is arbitrary
        It will be cast to the given dtype at runtime
    """
    
    cast = N.cast 
    data = [[] for dummy in xrange(len(dtype))]
    
    for line in open(filename, 'r'):
        # Clean out the white spaces
        p = re.compile('[\s]{1,}')
        line = p.sub(separator, line).strip()
        fields = line.split(separator)
        
        if fields[0].isdigit():
            fields = [item for item in fields if item != ""]
            # Leave zero area plots out
            if fields[1] != "0":
                for i, number in enumerate(fields):
                    data[i].append(number)
        # Empty line signifies change in data input
        elif 'Repeat' in fields:
            break
        
    try:
        for i in xrange(len(dtype)):
            data[i] = cast[dtype[i]](data[i])
    except ValueError, e:
        print e
        print data[i]
                        
    
    return N.rec.array(data, dtype=dtype)

def read_ascii_matrix(filename, skip=6, dtype=int):
    """Read in a ESRI ASCII grid skipping first 6 rows and using int as 
    a default dtype. Return a ndarray matrix.
    """
    sys.stdout.write('Reading file...')
    try:
        return N.loadtxt(filename, skiprows=skip, dtype=dtype)
    except IOError:
        print 'given filename <%s> invalid.' % filename
    finally:
        print 'done.'
    
# Different stats & analysis functions
        
def compare_multi_distributions(ND=-1, *args):
    """Comparers distributions for an arbitrary list of matrices. Function
    loops through all matrices and defines which elements overlap (=have value
    in all matrices). All matrices MUST be of same dimensions!
    """
    
    # Initialize the resulst list
    results = []
    
    # Check that all matrices have the same dimensions and type
    reftype = type (args[0])
    refdims = (N.size(args[0], 0), N.size(args[0], 1))
    
    for i, matrix in enumerate(args):
        dims = (N.size(matrix, 0), N.size(matrix, 1))
        try:
            assert type(matrix) is reftype, "Mismatch of type <%s> for matrix %s: %s"  \
                                        % (reftype, i+1, type(matrix))
            assert refdims == dims, "Mismatch of dimensions for matrix: " + \
                                    str(i+1) + " " + str(dims)
        except AssertionError, e:
            print '%s, exiting...' % e
            sys.exit(0)
        
        # Append an empty list to results list for later use
        results.append([])
    
    # Loop through matrices
    for i in refdims[0]:
        for j in refdims[1]:
            elems = []
            for i, matrix in enumerate(args):
                elems[i] = matrix[i, j]
        # for elems
            
def compare_distributions(matrix1, matrix2, NDs=[-1, -2]):
    """Comparers distributions for two matrices. Function
    loops through the two matrices and defines which elements overlap (=have value
    in all matrices). Both matrices MUST be of same dimensions! Also assumes
    that NoData values of an matrix are negative integers and actual values
    positive integers.
    """
    
    sys.stdout.write('Comparing distributions...')
    
    # Initialize the results dictionary: 
    results = {'matrix1': 0, 'both':0, 'matrix2': 0}
    
    # Check that all matrices have the same dimensions and type
    type1 = type(matrix1)
    dims1 = (N.size(matrix1, 0), N.size(matrix1, 1))
    dims2 = (N.size(matrix2, 0), N.size(matrix2, 1))
    try:
        assert type(matrix2) is type1, "Matrix types do not match"
        assert dims1 == dims2, "mismatch of dimensions for matrix"
    except AssertionError, e:
        print '%s, exiting...' % e
        sys.exit(0)

    # Loop through matrices
    for i in xrange(dims1[0]):
        for j in xrange(dims1[1]):
            val1 = matrix1[i, j]
            val2 = matrix2[i, j]
            if val1 not in NDs and  val2 in NDs:
                results['matrix1'] += 1
            elif val1 not in NDs and  val2 not in NDs:
                results['both'] += 1
            elif val1 in NDs and  val2 not in NDs:
                results['matrix2'] += 1
    
    print 'done.'
    return results

def create_matrix(x, y, p):
    
    randmat = N.random.rand(x, y)
    matrix = N.zeros((x, y), int)
    
    for i in xrange(x):
        for j in xrange(y):
            if randmat[i, j] < p:
                matrix[i, j] = 1
            else:
                matrix[i, j] = -1
    
    return matrix

def linregr():
    #Linear regression example
    # This is a very simple example of using two scipy tools 
    # for linear regression, polyfit and stats.linregress
    
    #Sample data creation
    #number of points 
    n = 50
    t = S.linspace(-5,5,n)
    #parameters
    a = 0.8; b=-4
    x = S.polyval([a,b],t)
    #add some noise
    xn = x + S.randn(n)
    
    #Linear regressison -polyfit - polyfit can be used other orders polys
    ar, br = S.polyfit(t, xn, 1)
    xr = S.polyval([ar, br], t)
    #compute the mean square error
    err = S.sqrt(sum((xr-xn)**2)/n)
    
    print('Linear regression using polyfit')
    print('parameters: a=%.2f b=%.2f \nregression: a=%.2f b=%.2f, ms error= %.3f' % (a,b,ar,br,err))
    
    #matplotlib ploting
    P.title('Linear Regression Example')
    P.plot(t, x,'g.--')
    P.plot(t, xn,'k.')
    P.plot(t, xr,'r.-')
    P.legend(['original','plus noise', 'regression'])
    
    #Linear regression using stats.linregress
    (a_s, b_s, r_value, p_value, stderr) = n.stats.linregress(t,xn)
    print 'Linear regression using stats.linregress'
    print 'parameters: a=%.2f b=%.2f \nregression: a=%.2f b=%.2f, std error= %.3f' % (a,b,a_s,b_s,stderr)
    print 'R-squared: %.2f' % r_value ** 2
    print 'p-value: ', p_value

    P.show()

def make_comparisons(wdir, basedir, files, sequence):
    """Function to go through all Z solution folders in a given wdir folder
    based on sequence provided by tuple sequence. Each folder is identified
    by integer id number in the beginning of the folder name. Single basedir
    is given followed by files which is a list of files in basedir that will
    work as reference for comaprison. 
    """
    # Determine whether the sequence is a list of folders or a range
    if type(sequence) is TupleType:
        folder_ids = range(sequence[0], sequence[1] + 1)
    # Else it is assumed that sequnce is already a list containing folder ids
    
    # List all folders in the working directory
    folders = os.listdir(wdir)
    # Create a dictionary where folder id is key and folder name value
    f_dict = {}
    
    for folder in folders:
        if '_' in folder:
            f_id = int(folder.split('_')[0])
            f_name = folder.replace(str(f_id) + '_', '')
            if f_id in folder_ids:
                f_dict[f_id] = f_name
            
    print f_dict
    

if __name__ == '__main__':
    
    wdir = r'E:\Data\Zonation\output\metsatalousmaa'
    basedir = r'45_20081113_A2_met_300_in_w_cds_abf_mask'
    files = ['output.ABF_MEABLP0.nwout.6.ras.asc']
    make_comparisons(wdir, basedir, files, (46, 48))
    
    '''file1 = r'E:\Data\Zonation\output\metsatalousmaa' + \
            r'\45_20081113_A2_met_300_in_w_cds_abf_mask' + \
            r'\output.ABF_MEABLP0.nwout.6.ras.asc'
            
    file2 = r'E:\Data\Zonation\output\metsatalousmaa' + \
            r'\45_20081113_A2_met_300_in_w_cds_abf_mask' + \
            r'\output.ABF_MEABLP0.nwout.7.ras.asc'
            
    file3 = r'C:\Data\Zonation\output\metsatalousmaa' + \
            r'\33_uusi_noBLP' + \
            r'\output.ABF_MEABLP2.nwout.6.ras.asc'
            
    matrix1, matrix2 = read_ascii_matrix(file1), read_ascii_matrix(file2)
    d = compare_distributions(matrix1, matrix2)
    msum = sum([s for s in d.values()])
    print
    print 'Union disribution sum of matrices is: %s' % msum
    print 'Itersection distribution sum of matrices is: %s' % d['both']
    print 'Overalap is: %s' % (float(d['both']) / float(msum))
    print 'Matrix1 has %s unique elements' % d['matrix1']
    print 'Matrix2 has %s unique elements' % d['matrix2']
    print
    
    #TODO: get headers right
    mydescr = N.dtype([('Network', 'int32'), 
                       ('Area', 'int32'), 
                       ('Mean-Rank', 'float32'), 
                       ('X', 'float32'),
                       ('Y', 'float32'),
                       ('Spp_distribution_sum', 'float32'),
                       ('spp occurring', 'int32'),
                       ('>10%', 'int32'),
                       ('>1%', 'int32'),
                       ('>0.1%', 'int32'),
                       ('>0.01%', 'int32')])
    
    file = r'E:\Data\Zonation\nwoutspp6.txt'
    if os.path.exists(file):
        myrecarray = read_array(file, mydescr, separator='\t')
    else:
        print 'Inputfile not valid!'
        sys.exit(0)
    
    dim = len(myrecarray)
    # Resolution in Km
    res = 0.5
    # Extents in YKJ, DO NOT CHANGE THESE!!!
    extents = {'north': [3243187.5, 7255237.5, 3628087.5, 7779737.5],
               'south': [3159087.5, 6620112.5, 3733087.5, 7378212.5],
               'whole': [3159087.5, 6620037.5, 3733187.5, 7779737.5],
               'metso': [3159087.5, 6620037.5, 3733187.5, 7372512.5],
               'local': [3514667.5, 7284110.5, 3614668.5, 7384111.5]} 
    area = 1
    av_rank = 2
    x_coord = 3
    y_coord = 4
    
    x = N.zeros(dim, dtype='float32')
    y = N.zeros(dim, dtype='float32')
    a = N.zeros(dim, dtype='float32')
    
    for i in xrange(dim):
        #x[i] = res * (myrecarray[i][x_coord] + extents['whole'][0])
        #y[i] = myrecarray[i][y_coord]/2
        #y[i] = res * (extents['whole'][3] - myrecarray[i][y_coord])
        x[i] = myrecarray[i][area]
        y[i] = myrecarray[i][av_rank]
    
    x, y = prune(x, y, 0.5)
    
    # the bestfit line from polyfit
    m1, b1 = S.polyfit(x, y, 1) # a line is 1st order polynomial...
    a_s, b_s, r_value, p_value, stderr = stats.linregress(x, y)
    #m2, b2 = N.polyfit(x, a, 1)
    
    print 'm1: %s' % m1
    print 'b1: %s' % b1
    print 'a_s: %s' % a_s
    print 'b_s: %s' % b_s
    print 'R-squared: %.6f' % r_value ** 2
    print 'p-value: ', p_value
    
    P.subplot(211)
    #p.plot(x, y, 'ro')
    P.plot(x, y, 'ro', x, a_s * x + b_s, '-k', linewidth=2)
    P.axis([min(x), max(x), min(y), max(y)])
    P.ylabel('Rank')
    P.xlabel('Area')
    P.grid(True)
    
    
    P.subplot(212)
    n, bins, patches = P.hist(x, 150, normed=1)
    P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
    
    #p.plot(x_flip, y_flip, 'bo')
    ##p.plot(x, y, 'ro', x, a_s * x + b_s, '-k', linewidth=2)
    #p.axis([0, x_range, 0, y_range])
    P.ylabel('Freq')
    P.xlabel('Area')
    P.grid(True)
    
    #p.subplot(212)
    #p.plot(x, a, 'bo', x, m2 * x + b2, '-k', linewidth=2)
    #p.ylabel('Area')
    #p.xlabel('Rank')
    #p.grid(True)
    
    P.show()
    
    linregr()'''
    
