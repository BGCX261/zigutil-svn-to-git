#!usr/bin python
# operator.py
# coding=utf-8

import os
import sppfactory as sf
import zigcom as zc
from datetime import date
import time

# Local variable
today = date.today().isoformat().replace('-', '')
output_parent = r'E:\Data\Zonation\output\metsatalousmaa'

# Check the environment
envar = 'ZONATION_HOME'
if os.environ.get(envar):
    HOME = os.environ.get(envar)
    print 'Zonation home (%s) set to: %s' % (envar, HOME)
    
else:
    print 'Environment variable (%s) not set.' % envar

# Helper functions

def print_timing(func):
    def wrapper(*arg, **kwargs):
        for i in range(1):
            t1 = time.time()
            func(*arg, **kwargs)
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

# Check if suitable outputfolder exists
def check_folder(today, suffix):
    # Get existing dirs in output_parent
    folders = os.listdir(output_parent)
    # Loop through folders and get id number
    ids = []
    for folder in folders:
        try:
            ids.append(int(folder[:2]))
        except ValueError:
            pass
    
    num = max(ids) + 1
        
    if num < 10:
        num = '0%s' % num
            
    target = os.path.join(output_parent, '%s_%s_%s' % (num, today, suffix))
    if not os.path.exists(target):
        os.mkdir(target)
    return target

def check_weight(item):
    if '_w_' in item:
        return 1
    elif '_wl_' in item:
        return 2
    elif '_abc_' in item:
        return 3
    else:
        return 0
    
def check_alpha(item):
    if '_ds_' in item:
        return True
    else:
        return False
    
def check_method(item):
    if 'caz' in item:
        return 1
    elif 'abf' in item:
        return 2
    elif 'tbp' in item:
        return 3
    else:
        return 4

@print_timing
def operate(runs, spp_xlfile, spp_xlsheet, mask_file=None, 
            pp_file=None, interact=None, conn=None, grps=None, blp=0.0):
    
    # Initiate the batch file for running Zonation
    batchfile = ''
    
    for run in runs:
        
        # Before starting, mark masks if used
        if mask_file is not None:
            run = run + '_mask'
            
        # First, create a Zigcommander object with which operations
        # are handlded
        com = zc.Zigcommander(run)
        
        # Second, create necessary sppfile(s)
        # Notice that process will be terminated if ASCII files do not exist
        spp = sf.Sppfactory(run)
        
        # Third, handle the right folder
        homefolder = check_folder(today, run)
        
        # Third, create run settings file (based on default)
        configfile = os.path.join(homefolder,(run + '.dat'))
        dat = com.create_config_file(configfile, use_default=True)
        dat.set_value('Settings', 'removal rule', check_method(run))
        
        if blp is not None:
            if blp > 0:
                dat.set_value('Settings', 'BLP', float(blp))
            else:
                print "BLP value must be positive: %s." % blp
        
        if mask_file is not None:
            if os.path.exists(mask_file):
                dat.set_value('Settings', 'use mask', '1')
                dat.set_value('Settings', 'mask file', mask_file)
            else:
                print "Mask file does not exist in path specified: %s." % mask_file
        
        # Fourth, create post processing capability if needed
        if pp_file is not None:
            if os.path.exists(pp_file):
                dat.set_value('Settings', 'post-processing list file', 
                              pp_file)
            else:
                print "Post processing file does not exist in path specified: %s." % mask_file
            
        if interact is not None:
            if os.path.exists(interact):
                dat.set_value('Settings', 'use interactions', 1)
                dat.set_value('Settings', 'interaction file', interact)
            else:
                print 'Interaction file does not exist in path specified: %s' % interact
                
        if conn is not None:
            if os.path.exists(conn):
                dat.set_value('Community analysis settings', 'load similarity matrix', 
                              1)
                dat.set_value('Community analysis settings', 'similarity matrix file', 
                              conn)
            else:
                print "Connectivity matrix file does not exist in path specified: %s." % conn
                
        if grps is not None:
            if os.path.exists(grps):
                dat.set_value('Settings', 'use groups', 
                              1)
                dat.set_value('Settings', 'groups file', 
                              grps)
            else:
                print "Groups file does not exist in path specified: %s." % grps
        
        # If 'dsb' -flag is found inside th edefinition string
        # create a spp file with same layers with and without DS
        if 'dsb' in run:
            spp.add_to_rack(path=spp_xlfile, 
                            sheet=spp_xlsheet,
                            weight=check_weight(run), 
                            alpha=check_alpha(run), 
                            method=check_method(run))
            spp.add_to_rack(path=spp_xlfile, 
                            sheet=spp_xlsheet,
                            weight=check_weight(run),
                            # Also the opposite of alpha 
                            alpha=(not check_alpha(run)), 
                            method=check_method(run))
        else:
            spp.add_to_rack(path=spp_xlfile, 
                            sheet=spp_xlsheet,
                            weight=check_weight(run), 
                            alpha=check_alpha(run), 
                            method=check_method(run))
        
        sppfile = os.path.join(homefolder,(run + '.spp'))
        spp.printfile(dirname=sppfile, exclude=['id'])
        
        # If everything was okay, write the dat file as well
        dat.write()
        
        # Sixth, create the batchrun capability
        batchname = today + '_run_all.bat'
        com.create_run_object(settings=configfile, 
                              sppfiles=sppfile,
                              output=os.path.join(homefolder, 'output.txt'),
                              DS=int(check_alpha(run)))
        
        batchfile = com.create_batch_file(output=batchname, 
                                          exclude=['id'], 
                                          append=True)
    # Finally, execute the batch file
    #os.system(batchfile)
        
if __name__ == '__main__':
    # Define runs by name
    spp_xlfile = r'E:\Data\Zonation\ConfigureData.xls'
    spp_xlsheet = 'A2_met_300_in'
    #spp_xlsheet = 'A2_met_DUMMY'
    prefix = spp_xlsheet.replace('Selected_', '')
    mask = r'E:\Data\Zonation\input_mh\Metso\res300\mh_all_300bin.asc'
    pp_file = r'E:\Data\Zonation\ppa_file.txt'
    interact = r'E:\Data\Zonation\interact.spp'
    conmatrix= r'E:\Data\Zonation\conn_mat_real.txt'
    groups = r'E:\Data\Zonation\hv_grps.txt'
    
    suffixes = ['_w_cds_caz']
    
    '''
    suffixes = ['_w_dsb_caz']
    '''
    runs = []
    for suffix in suffixes:
        runs.append(prefix + suffix)
    
    operate(runs, spp_xlfile, spp_xlsheet, 
            mask_file=mask, 
            pp_file=pp_file,
            interact=interact,
            conn=conmatrix,
            grps=groups,
            blp=0.003
            )
    print 'Done!'