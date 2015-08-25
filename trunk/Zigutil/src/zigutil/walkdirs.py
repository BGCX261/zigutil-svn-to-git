import os
import sys
import winhelpper
import fileinput
            
def walkNaggrgate(dir, outworkspace):
    arc = winhelpper.Archelper()
    target_path = ''
    
    for root, rasters, files in os.walk(dir): 
        if rasters != [] and root != dir and 'sub' not in root:
            folder = os.path.basename(root)
            folder = folder.replace('25', '100')
            target_path = os.path.join(outworkspace, folder)
            os.mkdir(target_path)
            print
            print 'Created folder: %s' % folder
        elif rasters != [] and root != dir and 'sub' in root:
            subfolder = os.path.basename(root)
            subfolder = subfolder.replace('25', '100')
            target_sub_path = os.path.join(target_path, subfolder)
            os.mkdir(target_sub_path)
            print 'Created folder: %s' % subfolder
            arc.set_nodata_aggregation(root, 
                                       target_sub_path,
                                       cellfactor=4,
                                       extent='local')

def walkNcompare(dirA, dirB):
    '''Method to calculate local target biodiversity feature ditribution
    ratio to the whole country distribution. dirA is the local fodler,
    dirB is the whole country folder.
    '''
    arc = winhelpper.Archelper()
    
    # Check input
    for path in (dirA, dirB):
        if not os.path.exists(path):
            print 'Bad input paths: %s' % path
            sys.exit(0)
    
    for rootA, rastersA, filesA in os.walk(dirA): 
        
        # Following condition also skips lahopuu
        if rastersA != [] and rootA != dirA and 'lahopuu' not in rootA and 'sub' in rootA:
            sys.stdout.write('Processing folder: %s...' % rootA)
            outputname = os.path.join(rootA, 'ratios.txt')
            output = open(outputname, 'w')
            output.write('RasterLoc\tRasterFin\tRatio\n')
            # Remove info folder, all others are raster folders
            rastersA.remove('info')
            for rasterA in rastersA:
                # First get the raster name for comparison    
                rasterX = os.path.split(rootA)[-1]
                # Get the numerical (resolution) component
                num = ''.join([n for n in rasterX if n.isdigit()])
                # Get the plain raster name and suffix
                rasterX = rasterX.split(num)[0]
                # Set raster A
                rasterA = os.path.join(rootA, rasterA)
                # Go probing dirB
                rasterB = ''
                for rootB, rastersB, filesB in os.walk(dirB): 
                    if rastersB != [] and rootB != dirB and 'sub' in rootB:
                        if rasterX in rootB:
                            for rasterB in rastersB:
                                if rasterB == os.path.basename(rasterA):
                                    rasterB = os.path.join(rootB, rasterB)
                                    break
                            break
                # Local raster goes first
                ratio = arc.calculate_cell_ratios(rasterB, rasterA)
                output.write('%s\t%s\t%s\n' % \
                (os.path.basename(rasterB), os.path.basename(rasterA), ratio))
            output.close()
            print 'done.\n'
                
def walkNconvert(dir, outworkspace):
    arc = winhelpper.Archelper()
    
    for root, rasters, files in os.walk(dir): 
        if rasters != [] and root != dir and 'sub' in root:
            arc.batch_GRID_to_ASCII(root, outworkspace)
            
def walkNdelete_empty_rasters(dir):
    arc = winhelpper.Archelper()
    
    for root, rasters, files in os.walk(dir): 
        if rasters != [] and root != dir and 'sub' in root:
            print '\nEntering folder: %s' % root
            arc.batch_delete_empty(root)
            
def walkNdelete_files(dir, targets):
    if targets is None:
        print 'Please provide input!'
        sys.exit(0)

    for root, rasters, files in os.walk(dir):
        for file in files:
            if file in targets:
                os.remove(os.path.join(root, file))
                print 'Removed: %s' % os.path.join(root, file)
                
         
            
def walkNextract_by_mask(dir, outworkspace, mask, extent='whole', suffix=''):
    arc = winhelpper.Archelper()
    target_path = outworkspace
    
    for root, rasters, files in os.walk(dir): 
        if rasters != [] and root != dir and 'sub' not in root:
            folder = os.path.basename(root)
            folder = '%s' % (folder)
            target_path = os.path.join(target_path, folder)
            os.mkdir(target_path)
            print
            print 'Created folder: %s' % target_path
        elif rasters != [] and root != dir and 'sub' in root:
            subfolder = os.path.basename(root)
            subfolder = '%s' % (subfolder)
            target_sub_path = os.path.join(target_path, subfolder)
            os.mkdir(target_sub_path)
            print 'Created folder: %s' % target_sub_path
            arc.batch_extract_by_mask(root, 
                                      target_sub_path, 
                                      mask,
                                      extent=extent,
                                      suffix=suffix)
        
def walkNextract_by_pixel(dir, outworkspace, mask):
    arc = winhelpper.Archelper()
    target_path = ''
    
    for root, rasters, files in os.walk(dir): 
        if rasters != [] and root != dir and 'sub' not in root:
            folder = os.path.basename(root)
            folder = '%smm' % (folder)
            target_path = os.path.join(outworkspace, folder)
            os.mkdir(target_path)
            print
            print 'Created folder: %s' % folder
        elif rasters != [] and root != dir and 'sub' in root:
            subfolder = os.path.basename(root)
            subfolder = '%smm' % (subfolder)
            target_sub_path = os.path.join(target_path, subfolder)
            os.mkdir(target_sub_path)
            print 'Created folder: %s' % subfolder
            arc.batch_extract_by_pixel(root, 
                                       target_sub_path, 
                                       mask)

def walkNfix_nulldata(dir, outworkspace):
    arc = winhelpper.Archelper()
    target_path = ''
    for root, rasters, files in os.walk(dir): 
        if rasters != [] and root != dir and 'sub' not in root:
            folder = os.path.basename(root)
            target_path = os.path.join(outworkspace, folder)
            os.mkdir(target_path)
            print
            print 'Created folder: %s' % target_path
        elif rasters != [] and root != dir and 'sub' in root:
            subfolder = os.path.basename(root)
            target_sub_path = os.path.join(target_path, subfolder)
            os.mkdir(target_sub_path)
            print 'Created folder: %s' % target_sub_path
            arc.batch_fix_nulldata(root, 
                                   target_sub_path)

        
if __name__ == '__main__':
    #walkNconvert(r'E:\Data\Metsahallitus\AnalysisLayers\Target300\Metso\Metsatalousmaa', 
    #             r'E:\Data\Zonation\input_mh\Metso\res300')
    #walkNextract_by_pixel('E:\Data\Metsahallitus\AnalysisLayers\Target', 
    #                       'E:\Data\Metsahallitus\AnalysisLayers\Target_metsamaa', 
    #                       r'E:\Data\Metla\ProcessedGrids\500m\metsamaa_bin')
    #walkNextract_by_mask('E:\Data\Metsahallitus\AnalysisLayers\Target\Fin', 
    #                     'E:\Data\Metsahallitus\AnalysisLayers\Target\Metso_nd', 
    #                     'E:\Data\Metso\MetsoII.gdb\Alue\Metso_extent',
    #                     extent='metso')
    #walkNaggrgate(r'E:\Data\Metsahallitus\AnalysisLayers\Source\Local', 
    #              r'E:\Data\Metsahallitus\AnalysisLayers\Metsatalousmaa\Target_mtm_local')
    #batch_change_nodata_header(r'E:\Data\Zonation\input_mh\Metso', '-9999', '-1')
    #walkNfix_nulldata(r'E:\Data\Metsahallitus\AnalysisLayers\Target300\Metso\Metsatalousmaa', 
    #                  r'E:\Data\Metsahallitus\AnalysisLayers\Target300\Metso\Metsatalousmaa_nd')
    #walkNdelete_empty_rasters(r'E:\Data\Metsahallitus\AnalysisLayers\Metsatalousmaa\Target_mtm_local')
    #walkNcompare('E:\Data\Metsahallitus\Analysis    Layers\Source\Local', 
    #             'E:\Data\Metsahallitus\AnalysisLayers\Source\Fin')
    #walkNdelete_files('E:\Data\Metsahallitus\AnalysisLayers\Source\Local', 
    #                  ['ratios.txt', 'cell_counts.txt'])