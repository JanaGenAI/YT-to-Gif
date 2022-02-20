
import os
import logging
import subprocess as sp

from ..encodingUtils import getFreeNameForFileAndLog
from ..encodingUtils import logffmpegEncodeProgress
from ..encodingUtils import isRquestCancelled

from ..optimisers.nelderMead import encodeTargetingSize as encodeTargetingSize_nelder_mead
from ..optimisers.linear     import encodeTargetingSize as encodeTargetingSize_linear

def encoder(inputsList, outputPathName,filenamePrefix, filtercommand, options, totalEncodedSeconds, totalExpectedEncodedSeconds, statusCallback,requestId=None,encodeStageFilter='null',globalOptions={},packageglobalStatusCallback=print):

  audoBitrate = 8
  for abr in ['48','64','96','128','192']:
    if abr in options.get('audioChannels',''):
      audoBitrate = int(abr)*1024

  audio_mp  = 8
  video_mp  = 1024*1024
  initialBr = globalOptions.get('initialBr',16777216)
  dur       = totalExpectedEncodedSeconds-totalEncodedSeconds

  if options.get('maximumSize') == 0.0:
    sizeLimitMax = float('inf')
    sizeLimitMin = float('-inf')
    initialBr    = globalOptions.get('initialBr',16777216)
  else:
    sizeLimitMax = options.get('maximumSize')*1024*1024
    sizeLimitMin = sizeLimitMax*(1.0-globalOptions.get('allowableTargetSizeUnderrun',0.25))
    targetSize_guide =  (sizeLimitMin+sizeLimitMax)/2
    initialBr        = ( ((targetSize_guide)/dur) - ((audoBitrate / 1024 / audio_mp)/dur) )*8


  videoFileName,logFilePath,tempVideoFilePath,videoFilePath = getFreeNameForFileAndLog(filenamePrefix, 'webm', requestId)
  
  def encoderStatusCallback(text,percentage,**kwargs):
    statusCallback(text,percentage,**kwargs)
    packageglobalStatusCallback(text,percentage)

  def encoderFunction(br,passNumber,passReason,passPhase=0, requestId=None,widthReduction=0.0, bufsize=None):
    
    ffmpegcommand=[]
    ffmpegcommand+=['ffmpeg' ,'-y']
    ffmpegcommand+=inputsList

    if widthReduction>0.0:
      encodefiltercommand = filtercommand+',[outv]{encodeStageFilter},scale=iw*(1-{widthReduction}):ih*(1-{widthReduction}):flags=bicubic[outvfinal]'.format(encodeStageFilter=encodeStageFilter,widthReduction=widthReduction)
    else:
      encodefiltercommand = filtercommand+',[outv]{encodeStageFilter},null[outvfinal]'.format(encodeStageFilter=encodeStageFilter)

    if options.get('audioChannels') == 'No audio':
      ffmpegcommand+=['-filter_complex',encodefiltercommand+',[outa]anullsink']
      ffmpegcommand+=['-map','[outvfinal]']
    else:
      ffmpegcommand+=['-filter_complex',encodefiltercommand]
      ffmpegcommand+=['-map','[outvfinal]','-map','[outa]']

    if passPhase==1:
      ffmpegcommand+=['-pass', '1', '-passlogfile', logFilePath ]
    elif passPhase==2:
      ffmpegcommand+=['-pass', '2', '-passlogfile', logFilePath ]



    if bufsize is None:
      bufsize = 3000000
      if sizeLimitMax != 0.0:
        bufsize = str(min(2000000000.0,br*2))
    threadCount = globalOptions.get('encoderStageThreads',4)
    metadataSuffix = globalOptions.get('titleMetadataSuffix',' WmG')

    audioCodec = ["-c:a","libvorbis"]
    if 'Copy' in options.get('audioChannels',''):
      audioCodec = []

    ffmpegcommand+=["-shortest", "-slices", "8", "-copyts"
                   
                   ,"-start_at_zero", "-c:v","libvpx"] + audioCodec + [

                    "-stats","-pix_fmt","yuv420p","-bufsize", str(bufsize)
                   ,"-threads", str(threadCount),"-crf"  ,'4'
                   ,"-auto-alt-ref", "1", "-lag-in-frames", str(globalOptions.get('vp8lagInFrames',25))
                   ,"-deadline","best",'-slices','8','-cpu-used','16','-psnr','-movflags','+faststart','-f','webm'
                   ,"-metadata", 'title={}'.format(filenamePrefix.replace('-',' -') + metadataSuffix) ]
    
    print(ffmpegcommand)
    if sizeLimitMax == 0.0:
      ffmpegcommand+=["-b:v","0","-qmin","0","-qmax","10"]
    else:
      ffmpegcommand+=["-b:v",str(br)]


    if 'No audio' in options.get('audioChannels','') or passPhase==1:
      ffmpegcommand+=["-an"]    
    elif 'Stereo' in options.get('audioChannels',''):
      ffmpegcommand+=["-ac","2"]    
      ffmpegcommand+=["-ar",str(44100)]
      ffmpegcommand+=["-b:a",str(audoBitrate)]
    elif 'Mono' in options.get('audioChannels',''):
      ffmpegcommand+=["-ac","1"]
      ffmpegcommand+=["-ar",str(44100)]
      ffmpegcommand+=["-b:a",str(audoBitrate)]
    elif 'Copy' in options.get('audioChannels',''):
      ffmpegcommand+=["-c:a copy"]
    else:
      ffmpegcommand+=["-an"]    

    ffmpegcommand+=["-sn"]

    if passPhase==1:
      ffmpegcommand += ['-f', 'null', os.devnull]
    else:
      ffmpegcommand += [tempVideoFilePath]

    logging.debug("Ffmpeg command: {}".format(' '.join(ffmpegcommand)))
    proc = sp.Popen(ffmpegcommand,stderr=sp.PIPE,stdin=sp.DEVNULL,stdout=sp.DEVNULL)
    
    encoderStatusCallback(None,None, lastEncodedBR=br, lastEncodedSize=None, lastBuff=bufsize, lastWR=widthReduction)

    psnr = logffmpegEncodeProgress(proc,'Pass {} {} {}'.format(passNumber,passReason,tempVideoFilePath),totalEncodedSeconds,totalExpectedEncodedSeconds,encoderStatusCallback,passNumber=passPhase,requestId=requestId)
    if isRquestCancelled(requestId):
      return 0, psnr
    if passPhase==1:
      return 0, psnr
    else:
      finalSize = os.stat(tempVideoFilePath).st_size
      encoderStatusCallback(None,None,lastEncodedSize=finalSize)
      return finalSize, psnr

  encoderStatusCallback('Encoding final '+videoFileName,(totalEncodedSeconds)/totalExpectedEncodedSeconds)

  minimumPSNR = 0.0
  try:
    minimumPSNR = float(options.get('minimumPSNR',0.0))
  except:
    pass

  optimiser = encodeTargetingSize_linear
  if  'Nelder-Mead' in options.get('optimizer'):
    optimiser = encodeTargetingSize_nelder_mead

  finalFilenameConfirmed = optimiser(encoderFunction=encoderFunction,
                      tempFilename=tempVideoFilePath,
                      outputFilename=videoFilePath,
                      initialDependentValue=initialBr,
                      twoPassMode=True,
                      sizeLimitMin=sizeLimitMin,
                      sizeLimitMax=sizeLimitMax,
                      maxAttempts=globalOptions.get('maxEncodeAttempts',6),
                      requestId=requestId,
                      minimumPSNR=minimumPSNR,
                      optimiserName=options.get('optimizer') )

  encoderStatusCallback('Encoding final '+videoFileName,(totalEncodedSeconds)/totalExpectedEncodedSeconds )
  encoderStatusCallback('Encoding complete '+videoFilePath,1,finalFilename=finalFilenameConfirmed)
