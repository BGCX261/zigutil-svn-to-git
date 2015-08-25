#!usr/var/env python
# coding=utf-8

class Nfifeats(object):
    """Container class for MS-NFI features. Supports internationalization. Can
    also be used to create a generic template for a given number of parameters.
    """
    
    def __init__(self):
    # Initializes the core dictionary default (fin) values
        self._features = {}     
            
    def _get_feats(self, lang='fin'):
        
        if lang != 'fin':
            self._set_feats(lang)
            
        self._features = {0: self.XCOORD,
                         1: self.YCOORD,
                         2: self.V3,
                         3: self.V4,
                         4: self.V5,
                         5: self.V6,
                         6: self.V7,
                         7: self.V8,
                         8: self.V9,    
                         9: self.V10,
                         10: self.V11,
                         11: self.V12,
                         12: self.V13,
                         13: self.V14,
                         14: self.V15,
                         15: self.V16,
                         16: self.V17,
                         17: self.V18}
        return self._features
    
    def _get_genfeats(self):
        return self._features
    
    def _set_feats(self, lang):
        if lang == 'fin':
            self.XCOORD = 'X-koordinaatti'
            self.YCOORD = 'Y-koordinaatti'
            self.V3 = 'Turvetuotantoalue'
            self.V4 = 'Pilvi tai varjo'
            self.V5 = 'Muu rakennettu maa'
            self.V6 = 'Asutus'
            self.V7 = 'Tie'
            self.V8 = 'Vesi'
            self.V9 = 'Pelto'
            self.V10 = 'Ruudun nullvalue-pikseleiden lkm'
            self.V11 = 'Metsämaan pikseleiden lkm'
            self.V12 = 'Metsämaan muuttujan arvon summa'
            self.V13 = 'Kitumaan pikseleiden lkm'
            self.V14 = 'Kitumaan muuttujan arvon summa'
            self.V15 = 'Joutomaan pikseleiden lkm'
            self.V16 = 'Joutomaan muuttujan arvon summa'
            self.V17 = 'Metsätalousmaan pikseleiden lkm'
            self.V18 = 'Metsätalousmaan muuttujan arvon summa'
        elif lang == 'eng':
            self.XCOORD = 'X-coordinate'
            self.YCOORD = 'Y-coordinate'
            self.V3 = 'Peat production area'
            self.V4 = 'Cloud or a shadow'
            self.V5 = 'Other built land'
            self.V6 = 'Residence'
            self.V7 = 'Road'
            self.V8 = 'Water'
            self.V9 = 'Agricultural field'
            self.V10 = 'Number of nullvalue pixels'
            self.V11 = 'Number of forest land pixels'
            self.V12 = 'Sum of forest land variable'
            self.V13 = 'Number of scrub land pixels'
            self.V14 = 'Sum of scrub land variable'
            self.V15 = 'Number of waste land pixels'
            self.V16 = 'Sum of waste land variable'
            self.V17 = 'Number of forestry land pixels'
            self.V18 = 'Sum of forestry land variable'
            
    def _set_genfeats(self, generic):
        """Methods for creating a generic feature dictionary with 
        variable numbers as names.
        """
        # First format features dictionary
        self._features = {}
        # Then populate it with variable numbers
        for i in xrange(generic):
            self._features[i] = i + 1
            
    def _del_feats(self):
        del self._features
    
    def _del_genfeats(self):
        del self._features
        
    def set_language(self, lang):
        self._set_feats(lang)
            
    features = property(_get_feats, _set_feats, _del_feats, "")
    generics = property(_get_genfeats, _set_genfeats, _del_genfeats, "")
    
if __name__ == '__main__':
    fin = Nfifeats()
    eng = Nfifeats()
    eng.features = 'eng'
    fin.features = 'fin'
    print fin.features
    gen = Nfifeats()
    gen.generics = 8
    print gen.generics
    