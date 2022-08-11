

import threading
import os
import logging
from datetime import datetime
import math
from collections import deque

filesPlannedForCreation = set()
fileExistanceLock = threading.Lock()

cancelledEncodeIds = set()

def isRquestCancelled(requestId):
  global cancelledEncodeIds
  return requestId in cancelledEncodeIds or -1 in cancelledEncodeIds

packageglobalStatusCallback=print

def idfunc(s):return s

getShortPathName = idfunc

try:
  import win32api
  getShortPathName=win32api.GetShortPathName
except Exception as e:
  logging.error("win32api getShortPathName Exception",exc_info=e)

def cleanFilenameForFfmpeg(filename):
  return getShortPathName(os.path.normpath(filename))

def cancelCurrentEncodeRequest(requestId):
  global cancelledEncodeIds
  cancelledEncodeIds.add(requestId)


def getFreeNameForFileAndLog(filenamePrefix,extension,initialFileN=1):

  try:
    fileN=int(initialFileN)
  except Exception as e:
    print(e)
    fileN=1

  with fileExistanceLock:
    while True:
      
      videoFileName = '{}_{}.{}'.format(filenamePrefix,fileN,extension)
      outLogFilename = 'encoder_{}.log'.format(fileN)
      outFilterFilename = 'filters_{}.txt'.format(fileN)

      logFilePath        = os.path.join('tempVideoFiles',outLogFilename)
      tempVideoFilePath  = os.path.join('tempVideoFiles',videoFileName)
      filterFilePath     = os.path.join('tempVideoFiles',outFilterFilename)
      videoFilePath      = os.path.join('finalVideos',videoFileName)
      

      if not os.path.exists(tempVideoFilePath) and not os.path.exists(filterFilePath) and not os.path.exists(videoFilePath) and not os.path.exists(logFilePath) and videoFileName not in filesPlannedForCreation:
        filesPlannedForCreation.add(videoFileName)
        return videoFileName,logFilePath,filterFilePath,tempVideoFilePath,videoFilePath

      fileN+=1

def logffmpegEncodeProgress(proc,processLabel,initialEncodedSeconds,totalExpectedEncodedSeconds,statusCallback,passNumber=0,requestId=None,tempVideoPath=None,options={}):
  currentEncodedTotal=0
  psnr = None
  ln=b''
  logging.debug('Encode Start')

  earlyExitOnLowPSNR    = options.get('earlyPSNRWidthReduction',False)
  
  minimumPSNR           = -1
  try:
    minimumPSNR           = int(float(options.get('minimumPSNR',-1)))
  except:
    pass

  earlyPSNRWindowLength = options.get('earlyPSNRWindowLength',5)
  earlyPSNRSkip         = options.get('earlyPSNRSkipSamples',5)
  psnrSamplesSkipped    = 0

  psnrQ = deque([],max(2,earlyPSNRWindowLength))
  psnrAve = None
  while 1:
    try:
      if isRquestCancelled(requestId):
        proc.kill()
        outs, errs = proc.communicate()
        return 0,0
      c = proc.stderr.read(1)
      if len(c)==0:
        break
      if c == b'\r':
        print(ln)
        for p in ln.split(b' '):
          if b'*:' in p:
            try:
              tpsnr = float(p.split(b':')[-1]) 
              if (not math.isnan(tpsnr)) and tpsnr != float('inf'):
                psnr = tpsnr

                if psnrSamplesSkipped > earlyPSNRSkip:
                  psnrQ.append(psnr)
                
                psnrSamplesSkipped+=1

                if len(psnrQ) == earlyPSNRWindowLength and earlyExitOnLowPSNR:
                  psnrAve = sum(psnrQ)/earlyPSNRWindowLength
                  print('psnrAve',psnrAve,minimumPSNR,psnrQ)

                  if psnrAve is not None and psnrAve < minimumPSNR:

                    proc.kill()
                    outs, errs = proc.communicate()
                    statusCallback('Rolling PSNR too Low '+processLabel,0,lastEncodedPSNR=psnr,encodeStage='PSNR Too Low', encodePass='PSNR {} ({} samples)'.format(psnrAve,earlyPSNRWindowLength) )
                    return psnrAve,1

            except Exception as e:
              logging.error("Encode capture psnr Exception",exc_info=e)
          if b'time=' in p:
            try:
              pt = datetime.strptime(p.split(b'=')[-1].decode('utf8'),'%H:%M:%S.%f')
              currentEncodedTotal = pt.microsecond/1000000 + pt.second + pt.minute*60 + pt.hour*3600
              if currentEncodedTotal>0:
                if passNumber == 0:
                  statusCallback('Encoding '+processLabel,(currentEncodedTotal+initialEncodedSeconds)/totalExpectedEncodedSeconds,lastEncodedPSNR=psnr,encodeStage='Encoding Final', encodePass='Single Pass Mode')
                elif passNumber == 1:
                  statusCallback('Encoding '+processLabel,((currentEncodedTotal/2)+initialEncodedSeconds)/totalExpectedEncodedSeconds,lastEncodedPSNR=psnr,encodeStage='Encoding Final', encodePass='Two Pass Mode Pass 1' )
                elif passNumber == 2:

                  sizeNow = None

                  print(tempVideoPath)
                  try:
                    if tempVideoPath is not None:
                      sizeNow = os.stat(tempVideoPath).st_size
                  except Exception as sze:
                    print(sze)

                  statusCallback('Encoding '+processLabel,( ((totalExpectedEncodedSeconds-initialEncodedSeconds)/2) + (currentEncodedTotal/2)+initialEncodedSeconds)/totalExpectedEncodedSeconds,lastEncodedPSNR=psnr,encodeStage='Encoding Final',currentSize=sizeNow, encodePass='Two Pass Mode Pass 2' )

            except Exception as e:
              logging.error("Encode progress Exception",exc_info=e)
        ln=b''
      ln+=c
    except Exception as e:
      logging.error("Encode progress Exception",exc_info=e)

  outs, errs = proc.communicate()

  if proc.returncode == 1:
    statusCallback('Encode Failed '+processLabel,1,lastEncodedPSNR=psnr,encodeStage='Encode Failed', encodePass='Error code {}'.format(proc.returncode) )

  if passNumber == 0:
    statusCallback('Complete '+processLabel,(currentEncodedTotal+initialEncodedSeconds)/totalExpectedEncodedSeconds,lastEncodedPSNR=psnr )
  elif passNumber == 1:
    statusCallback('Complete '+processLabel,((currentEncodedTotal/2)+initialEncodedSeconds)/totalExpectedEncodedSeconds,lastEncodedPSNR=psnr )
  elif passNumber == 2:
    statusCallback('Complete '+processLabel,( ((totalExpectedEncodedSeconds-initialEncodedSeconds)/2) + (currentEncodedTotal/2)+initialEncodedSeconds)/totalExpectedEncodedSeconds,lastEncodedPSNR=psnr )
  
  return psnr,proc.returncode