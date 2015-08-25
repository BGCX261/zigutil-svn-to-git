#!usr/var/env python
# coding=utf-8  

import time

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

class ArcTables(object):
    '''ArcTables class contains methods to extract and manipulate data stored in database
    tables through ArcGIS. Each instance of this class represents one db table.
    '''
    
    def __init__(self, inlayer, parent=None):
        # Try to create the Geoprocessor
        try:
            import arcgisscripting
            self.gp = arcgisscripting.create()
            
            # Make a in-memory layer out of the target feature
            #self.table = 'targettable'
            self.table = self.gp.MakeTableView(inlayer, 'targettable')
            # Get the number of records in the table
            self.records = self.gp.GetCount_management(self.table)
            # Set the dict for fields and values
            self.values = {}
            
        except ImportError:
            # If ArcGIS is unavailable, delegate error message back 
            if parent:
                parent.log("ArcGIS unavailable.")
                raise
            else:
                print "ArcGIS unavailable."
                
    def getfields(self):
        desc = self.gp.Describe(self.table)
        fldnames = []
        fields = desc.Fields
        field = fields.next()
        while field:
            fldnames.append(field.Name)
            field = fields.next()
        return fldnames
    
    def getvalues(self, field):
        if not self.values.has_key(field):
            fldvalues = []
            rows = self.gp.SearchCursor(self.table)
            row = rows.next()
            
            while row:
                try:
                    if row.GetValue(field) not in fldvalues:
                        fldvalues.append(str(row.GetValue(field)))
                        row = rows.next()
    
                except:
                    fldvalues.append('NA')
                    break
                
            self.values[field] = fldvalues
            
        return self.values[field]    
            
    
    fields = property(getfields)
                
if __name__ == '__main__':
    target = r'E:\Data\Metsahallitus\ArcGIS\Geodatabases\MH_data_classes_SEL.mdb\FLD_KASV_TYYPPI'
    table = ArcTables(target)
    print table.fields
    print table.getvalues('Koodi')