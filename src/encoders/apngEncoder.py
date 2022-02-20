
import os
import logging
import subprocess as sp

from ..encodingUtils import getFreeNameForFileAndLog
from ..encodingUtils import logffmpegEncodeProgress
from ..encodingUtils import isRquestCancelled

from ..optimisers.nelderMead import encodeTargetingSize as encodeTargetingSize_nelder_mead
from ..optimisers.linear     import encodeTargetingSize as encodeTargetingSize_linear

def encoder(inputsList, outputPathName,filenamePrefix, filtercommand, options, totalEncodedSeconds, totalExpectedEncodedSeconds, statusCallback,encodeStageFilter='null',requestId=None,globalOptions={},packageglobalStatusCallback=print):

  if options.get('maximumSize') == 0.0:
    sizeLimitMax = float('inf')
    sizeLimitMin = float('-inf')
  else:
    sizeLimitMax = options.get('maximumSize')*1024*1024
    sizeLimitMin = sizeLimitMax*(1.0-globalOptions.get('allowableTargetSizeUnderrun',0.25))

  videoFileName,logFilePath,tempVideoFilePath,videoFilePath = getFreeNameForFileAndLog(filenamePrefix, 'png', requestId)

  def encoderStatusCallback(text,percentage,**kwargs):
    statusCallback(text,percentage,**kwargs)
    packageglobalStatusCallback(text,percentage)

  def encoderFunction(width,passNumber,passReason,passPhase=0,requestId=None,widthReduction=0.0,bufsize=None):

    giffiltercommand = filtercommand+',[outv]scale=\'max({}\\,min({}\\,iw)):-1\':flags=bicubic[outvgif],[outa]anullsink'.format(0,width)

    ffmpegcommand=[]
    ffmpegcommand+=['ffmpeg' ,'-y']
    ffmpegcommand+=inputsList
    ffmpegcommand+=['-plays', '0']
    ffmpegcommand+=['-filter_complex',giffiltercommand]
    ffmpegcommand+=['-map','[outvgif]']
    ffmpegcommand+=["-vsync", '0'
                   ,"-shortest" 
                   ,"-copyts"
                   ,"-start_at_zero"
                   ,"-stats"
                   ,"-an"
                   ,'-psnr'
                   ,"-f","apng"
                   ,"-sn",tempVideoFilePath]

    encoderStatusCallback('Encoding final '+videoFileName,(totalEncodedSeconds)/totalExpectedEncodedSeconds)

    proc = sp.Popen(ffmpegcommand,stderr=sp.PIPE,stdin=sp.DEVNULL,stdout=sp.DEVNULL)
    psnr = logffmpegEncodeProgress(proc,'Pass {} {} {}'.format(passNumber,passReason,videoFileName),totalEncodedSeconds,totalExpectedEncodedSeconds,encoderStatusCallback,passNumber=0,requestId=requestId)
    if isRquestCancelled(requestId):
      return 0, psnr
    finalSize = os.stat(tempVideoFilePath).st_size
    encoderStatusCallback(None,None,lastEncodedSize=finalSize)
    return finalSize, psnr

  initialWidth = options.get('maximumWidth',1280)

  optimiser = encodeTargetingSize_linear
  if  'Nelder-Mead' in options.get('optimizer'):
    optimiser = encodeTargetingSize_nelder_mead

  finalFilenameConfirmed = optimiser(encoderFunction=encoderFunction,
                      tempFilename=tempVideoFilePath,
                      outputFilename=videoFilePath,
                      initialDependentValue=initialWidth,
                      sizeLimitMin=sizeLimitMin,
                      sizeLimitMax=sizeLimitMax,
                      maxAttempts=globalOptions.get('maxEncodeAttemptsGif',10),
                      dependentValueName='Width',
                      requestId=requestId,
                      optimiserName=options.get('optimizer'))

  encoderStatusCallback('Encoding final '+videoFileName,(totalEncodedSeconds)/totalExpectedEncodedSeconds )
  encoderStatusCallback('Encoding complete '+videoFilePath,1,finalFilename=finalFilenameConfirmed)