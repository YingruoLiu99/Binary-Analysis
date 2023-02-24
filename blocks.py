#!/usr/bin/env python3
from __future__ import print_function
import glob
import argparse
import pickle
import csv
import os
import sys
import bisect

jimaHome= os.getenv('JIMA_HOME')

if(jimaHome is None or not os.path.isdir(jimaHome+'/src')):
   print('You must set the JIMA_HOME enviroment variable to the JIMA directory')
   print('such as "export JIMA_HOME=/home/jimaf/cgc/cgcsc/JIMA"')
   sys.exit(-1)
sys.path.append(jimaHome+'/src')

from jilLib import *
checkVersion()

import instructs
from print_jil import printInst

toolName='JIMA'
opSet=set()

def processFile(fileName):
    missing=[]
    instructs._init_()
    with open(fileName,'rb') as fn:
        jil=pickle.load(fn)


    cnt = 0

    ins = jil['ins']
    lastIdx=ins[len(ins)-1]['idx']
    funcs=jil['functions']
    secs=jil['Sections']

    addresses={}
    calls=sorted(jil['calls'].keys())
    currentCall=0
    jumps=sorted(jil['cndJumps'])
    currentJmp=0

    #basic block initialization


    #brief notation for basic blocks
    Bjumps=jil['jumps']
    BjumpedBy=jil['jumpedBy']
    BjumpPtrs=jil['jumpPtrs']
    Bcalls=jil['calls']
    BcalledBy=jil['calledBy']
    BcallPtrs=jil['callPtrs']
    
    
    for funcId in funcs:
       addresses[funcs[funcId]['startAddr']]=funcId

    for addr in sorted(list(addresses.keys())):
       func=funcs[addresses[addr]]
       basicBlocks={}
       bbCnt=0
       bb={}       
       inBB=endBB=False
       
       for insId in range(func['startIndex'],func['endIndex']+1):
          inst = ins[insId]
          addr = inst['addr']
          idx=inst['idx']

          # What is our logic here???
          # For each instruction:
          # No we need to know:
          #  Does this instruction start a NEW block?
          #     If so, make sure we end the previous block (if it exists)
          #     If not, just do nothing and continue
          #     When do we sart a new block?  If this is the target of
          #     a jump or call, or we were not in a current block.
          #  Does this insruction end the current block
          #     If so, the save the block data.

          if(addr in BjumpedBy or addr in BcalledBy or not inBB):
             #if we are start of a block
             if(inBB):
                #last address is the end of previous block

                bb['end']=lastAddr
                bb['endId']=lastIdx
                basicBlocks[bbCnt]=bb
                bbCnt+=1

                bb={}

             inBB=True
             endBB=False
             bb['start']=addr
             bb['startId']=idx


          #then we check if it's the end of block
          if(instructs.is_ret(inst) or addr in Bjumps or addr in Bcalls):
             bb['end']=addr
             bb['endId']=idx
             basicBlocks[bbCnt]=bb
             bbCnt+=1
             bb={}
             #store the block
             #then we set that we're out of basic block check
             inBB=endBB=False
          lastAddr=addr
          lastIdx=idx
         
#          printInst(inst,jil,sys.stdout)
#          print('*{:18s}:{:10,d}'.format('Block count',bbCnt))

       print('\nFunction id {:d} at address 0x{:x} has {:d} basic blocks'.format(func['id'],func['startAddr'],bbCnt))
       for bbId in basicBlocks.keys():
          bb = basicBlocks[bbId]
          print('*{:18s}: {:d} {:0x} {:0x}'.format('id BB', bbId, bb['start'], bb['end']))
                   
def main():
   global opSet
   formatter = argparse.ArgumentDefaultsHelpFormatter
   parser = argparse.ArgumentParser(description='JIMA Results Interface',
                                    formatter_class=formatter)

   parser.add_argument('file', type=str,
                         help='file name')

   args = parser.parse_args()
   fileName=args.file
   
   jilRes=processFile(fileName)
    
    
if __name__ == "__main__":
   main()
