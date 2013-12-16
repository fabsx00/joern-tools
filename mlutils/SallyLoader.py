#!/usr/bin/env python2

from sklearn.datasets import load_svmlight_file
from gzip import GzipFile
from Embedding import Embedding

LEN_BIN = len(' bin=')

EMBEDDING_FILENAME = '/embedding.libsvm'
FEATURE_FILENAME = '/feats.gz'
TOC_FILENAME = '/TOC'
D_FILENAME = '/D.pickl'

class SallyLoader:
    
    def __init__(self):
        self.emb = Embedding()
        
    def load(self, dirname):
        self.dirname = dirname
        self.emb.x, self.emb.y = load_svmlight_file(dirname + EMBEDDING_FILENAME)
        
        self._loadFeatureTable()
        self._loadTOC()
        return self.emb
    
    def _loadFeatureTable(self):
        
        filename = self.dirname + FEATURE_FILENAME
        f  = GzipFile(filename)
        
        # discard first line
        f.readline()

        while True:
            line = f.readline().rstrip()
            if line == '': break
            
            (feat, n) = self._parseHashTableLine(line)
            
            self.emb.featTable[feat] = n
            self.emb.rFeatTable[n] = feat
            
        f.close()
    
    def _parseHashTableLine(self, line):
        n, feat = line[LEN_BIN+1:].split(':')
        n = int(n , 16)
        feat = feat.lstrip().rstrip()
        return (feat, n)

    def _loadTOC(self):
        filename = self.dirname + TOC_FILENAME
        f = file(filename)
        self.emb.TOC = [x.rstrip() for x in f.readlines()]
        f.close()
        
        for i in range(len(self.emb.TOC)):
            self.emb.rTOC[self.emb.TOC[i]] = i

if __name__ == '__main__':
    import sys
    s = SallyLoader()
    s.load(sys.argv[1])
    