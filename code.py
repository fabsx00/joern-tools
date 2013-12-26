#!/usr/bin/env python2

import sys, argparse
from joern.all import JoernSteps
from joerntools.view.ParseLocationString import parseLocationOrFail
from joerntools.shelltool.PipeTool import PipeTool

DESCRIPTION = """Read filename:startLine:startPos:startIndex:stopIndex
from standard input and output the respective code."""

class CodeTool(PipeTool):
    
    def __init__(self):
        PipeTool.__init__(self, DESCRIPTION)

    # @Override
    def processLine(self, line):
        (filename, startLine, startPos, startIndex, stopIndex)\
            = parseLocationOrFail(line)
        
        f = self._openFileOrFail(filename)
        content = self._extractContent(f, startIndex, stopIndex)
        self.output(content + '\n')

    def _openFileOrFail(self, filename):
        try:
            f = file(filename)
        except IOError:
            sys.stderr.write('Error: %s: no such file or directory\n'
                             % filename)
            sys.exit()
        return f
        
    def _extractContent(self, f, startIndex, stopIndex):
        f.seek(startIndex)
        content = f.read(stopIndex - startIndex + 1)
        f.close()
        return content        

if __name__ == '__main__':
    tool = CodeTool()
    tool.run()
