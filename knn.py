#!/usr/bin/env python2

from joerntools.shelltool.PipeTool import PipeTool
from joerntools.mlutils.EmbeddingLoader import EmbeddingLoader
from joerntools.mlutils.EmbeddingSaver import EmbeddingSaver

from sklearn.metrics.pairwise import pairwise_distances
from argparse import FileType

import sys

DESCRIPTION = """ Calculate the k nearest neighbors to a data point
based on an embedding. """

DEFAULT_DIRNAME = 'embedding'
DEFAULT_K = 10

class KNN(PipeTool):
    
    def __init__(self):
        PipeTool.__init__(self, DESCRIPTION)
        self.loader = EmbeddingLoader()
        self.saver = EmbeddingSaver()

        self.argParser.add_argument('-k', '--k', nargs='?', type=int,
                                    help =""" number of nearest
                                    neighbors to determine""",
                                    default = DEFAULT_K)

        self.argParser.add_argument('-d', '--dirname', nargs='?',
                                    type = str, help="""The directory containing the embedding""",
                                    default = DEFAULT_DIRNAME)

        self.argParser.add_argument('-n', '--no-cache',
                                    action='store_false', default=False,
                                    help= """Cache calculated
                                    distances on disk. """)

        self.argParser.add_argument('-l', '--limit', type = FileType('r'), default=None,
                                    help = """ Limit possible
                                    neighbours to those specified in
                                    the provided file.""")
        

    def _loadEmbedding(self, dirname):
        self.saver.setEmbeddingDir(dirname)
        try:
            return self.loader.load(dirname, tfidf=False, svd_k=0)
        except IOError:
            sys.stderr.write('Error reading embedding.\n')
            sys.exit()

    # @Override
    def streamStart(self):
        self.emb = self._loadEmbedding(self.args.dirname)
        if self.args.limit:
            self._loadValidNeighbors()

    def _loadValidNeighbors(self):
        self.validNeighbors = [int(x) for x in
                                   self.args.limit.readlines()]


    # @Override
    def processLine(self, line):
        self.calculateDistances()
        
        try:
            dataPointIndex = self.emb.rTOC[line]
        except KeyError:
            sys.stderr.write('Warning: no data point found for %s\n' %
                             (line))
            
        nReturned = 0
            
        for i in self.emb.NNI[:, dataPointIndex]:
            
            if self.args.limit:
                if not int(self.emb.TOC[i]) in self.validNeighbors:
                    continue

            print self.emb.TOC[i]
            nReturned += 1
            
            if nReturned == self.args.k:
                break

    def calculateDistances(self):
        if not self.emb.dExists():
            self.emb.D = self._calculateDistanceMatrix()
     
            if not self.args.no_cache:
                self.saver.saveDistanceMatrix(self.emb)
            
        if not self.emb.nnExists():
            self._calculateNearestNeighbors()
            if not self.args.no_cache:
                self.saver.saveNearestNeighbors(self.emb)
            
    def _calculateNearestNeighbors(self):
        self.emb.NNV = self.emb.D.copy()
        self.emb.NNI = self.emb.D.argsort(axis=0)
        self.emb.NNV.sort(axis=0)
        
    def _calculateDistanceMatrix(self):
        return pairwise_distances(self.emb.x, metric='cosine')


if __name__ == '__main__':
    tool = KNN()
    tool.run()
