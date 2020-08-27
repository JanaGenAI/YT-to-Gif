
from datetime import datetime
from queue import Queue
import copy
import hashlib
import numpy as np
import os
import string
import subprocess as sp
import threading
import time
import ffmpegInfoParser

packageglobalStatusCallback=print

def idfunc(s):return s

getShortPathName = idfunc

try:
  import win32api
  getShortPathName=win32api.GetShortPathName
except Exception as e:
  print(e)

def cleanFilenameForFfmpeg(filename):
  return getShortPathName(os.path.normpath(filename))

def encodeTargetingSize(encoderFunction,outputFilename,initialDependentValue,sizeLimitMin,sizeLimitMax,maxAttempts,twoPassMode=False,dependentValueName='BR'):
  val = initialDependentValue
  targetSizeMedian = (sizeLimitMin+sizeLimitMax)/2
  smallestFailedOverMaximum=None
  largestFailedUnderMinimum=None
  passCount=0
  passReason='Initial Pass'
  while 1:
    val=int(val)
    passCount+=1

    if twoPassMode:
      _         = encoderFunction(val,passCount,passReason,passPhase=1)
      finalSize = encoderFunction(val,passCount,passReason,passPhase=2)
    else:
      finalSize = encoderFunction(val,passCount,passReason)
    
    if sizeLimitMin<finalSize<sizeLimitMax or (passCount>maxAttempts and finalSize<sizeLimitMax) or passCount>maxAttempts+2:
      break
    elif finalSize<sizeLimitMin:
      passReason='File too small, {} increase'.format(dependentValueName)
      if largestFailedUnderMinimum is None or val>largestFailedUnderMinimum:
        largestFailedUnderMinimum=val
    elif finalSize>sizeLimitMax:
      passReason='File too large, {} decrease'.format(dependentValueName)
      if smallestFailedOverMaximum is None or val<smallestFailedOverMaximum:
        smallestFailedOverMaximum=val
    print(val,finalSize,targetSizeMedian)
    val =  val * (1/(finalSize/targetSizeMedian))
    if largestFailedUnderMinimum is not None and smallestFailedOverMaximum is not None:
      val = (largestFailedUnderMinimum+smallestFailedOverMaximum)/2


def logffmpegEncodeProgress(proc,processLabel,initialEncodedSeconds,totalExpectedEncodedSeconds,statusCallback):
  currentEncodedTotal=0
  ln=b''
  while 1:
    try:
      c = proc.stderr.read(1)
      if len(c)==0:
        break
      if c == b'\r':
        print(ln)
        for p in ln.split(b' '):
          if b'time=' in p:
            try:
              pt = datetime.strptime(p.split(b'=')[-1].decode('utf8'),'%H:%M:%S.%f')
              currentEncodedTotal = pt.microsecond/1000000 + pt.second + pt.minute*60 + pt.hour*3600
              if currentEncodedTotal>0:
                statusCallback('Encoding '+processLabel,(currentEncodedTotal+initialEncodedSeconds)/totalExpectedEncodedSeconds )
            except Exception as e:
              print(e)
        ln=b''
      ln+=c
    except Exception as e:
      print(e)
  statusCallback('Complete '+processLabel,(currentEncodedTotal+initialEncodedSeconds)/totalExpectedEncodedSeconds )


def webmvp8Encoder(inputsList, outputPathName,filenamePrefix, filtercommand, options, totalEncodedSeconds, totalExpectedEncodedSeconds, statusCallback):
  
  audio_mp  = 8
  video_mp  = 1024*1024
  initialBr = 16777216
  dur       = totalExpectedEncodedSeconds-totalEncodedSeconds

  if options.get('maximumSize') == 0.0:
    sizeLimitMax = float('inf')
    sizeLimitMin = float('-inf')
    initialBr    = 16777216
  else:
    sizeLimitMax = options.get('maximumSize')*1024*1024
    sizeLimitMin = sizeLimitMax*0.85
    targetSize_guide =  (sizeLimitMin+sizeLimitMax)/2
    initialBr        = ( ((targetSize_guide)/dur) - ((64 / audio_mp)/dur) )*8



  fileN=0
  while 1:
    fileN+=1
    finalOutName = '{}_WmG_{}.webm'.format(filenamePrefix,fileN)
    finalOutName = os.path.join(outputPathName,finalOutName)
    outLogFilename = os.path.join('tempVideoFiles','encoder_{}.log'.format(fileN))
    if not os.path.exists(finalOutName):
      break

  
  def encoderStatusCallback(text,percentage):
    statusCallback(text,percentage)
    packageglobalStatusCallback(text,percentage)

  def encoderFunction(br,passNumber,passReason,passPhase=0):
    
    ffmpegcommand=[]
    ffmpegcommand+=['ffmpeg' ,'-y']
    ffmpegcommand+=inputsList

    if options.get('audioChannels') == 'No audio':
      ffmpegcommand+=['-filter_complex',filtercommand+',[outa]anullsink']
      ffmpegcommand+=['-map','[outv]']
    else:
      ffmpegcommand+=['-filter_complex',filtercommand]
      ffmpegcommand+=['-map','[outv]','-map','[outa]']  


    if passPhase==1:
      ffmpegcommand+=['-pass', '1', '-passlogfile', outLogFilename ]
    elif passPhase==2:
      ffmpegcommand+=['-pass', '2', '-passlogfile', outLogFilename ]

    ffmpegcommand+=["-shortest", "-slices", "8", "-copyts"
                   ,"-start_at_zero", "-c:v","libvpx","-c:a","libvorbis"
                   ,"-stats","-pix_fmt","yuv420p","-bufsize", "3000k"
                   ,"-threads", str(4),"-crf"  ,'4',"-speed", "0"
                   ,"-auto-alt-ref", "1", "-lag-in-frames", "25"
                   ,"-tune","ssim"]
    
    if sizeLimitMax == 0.0:
      ffmpegcommand+=["-b:v","0","-qmin","0","-qmax","10"]
    else:
      ffmpegcommand+=["-b:v",str(br)]

    if options.get('audioChannels') == 'No audio' or passPhase==1:
      ffmpegcommand+=["-an"]    
    elif options.get('audioChannels') == 'Stereo':
      ffmpegcommand+=["-ac","2"]    
    else:
      ffmpegcommand+=["-ac","1"]

    ffmpegcommand+=["-sn"]

    if passPhase==1:
      ffmpegcommand += ['-f', 'null', os.devnull]
    else:
      ffmpegcommand += [finalOutName]

    print(' '.join(ffmpegcommand))
    proc = sp.Popen(ffmpegcommand,stderr=sp.PIPE,stdin=sp.DEVNULL,stdout=sp.DEVNULL)
    logffmpegEncodeProgress(proc,'Pass {} {} {}'.format(passNumber,passReason,finalOutName),totalEncodedSeconds,totalExpectedEncodedSeconds,encoderStatusCallback)
    
    if passPhase==1:
      return 0
    else:
      finalSize = os.stat(finalOutName).st_size
      return finalSize

  encoderStatusCallback('Encoding final '+finalOutName,(totalEncodedSeconds)/totalExpectedEncodedSeconds)



  encodeTargetingSize(encoderFunction=encoderFunction,
                      outputFilename=finalOutName,
                      initialDependentValue=initialBr,
                      twoPassMode=True,
                      sizeLimitMin=sizeLimitMin,
                      sizeLimitMax=sizeLimitMax,
                      maxAttempts=10)

  encoderStatusCallback('Encoding final '+finalOutName,(totalEncodedSeconds)/totalExpectedEncodedSeconds )
  encoderStatusCallback('Encoding complete '+finalOutName,1)


def mp4x264Encoder(inputsList, outputPathName,filenamePrefix, filtercommand, options, totalEncodedSeconds, totalExpectedEncodedSeconds, statusCallback):

  audio_mp  = 8
  video_mp  = 1024*1024
  initialBr = 16777216
  dur       = totalExpectedEncodedSeconds-totalEncodedSeconds

  if options.get('maximumSize') == 0.0:
    sizeLimitMax = float('inf')
    sizeLimitMin = float('-inf')
    initialBr    = 16777216
  else:
    sizeLimitMax = options.get('maximumSize')*1024*1024
    sizeLimitMin = sizeLimitMax*0.85
    targetSize_guide =  (sizeLimitMin+sizeLimitMax)/2
    initialBr        = ( ((targetSize_guide)/dur) - ((64 / audio_mp)/dur) )*8

  fileN=0
  while 1:
    fileN+=1
    finalOutName = '{}_WmG_{}.mp4'.format(filenamePrefix,fileN)
    finalOutName = os.path.join(outputPathName,finalOutName)
    if not os.path.exists(finalOutName):
      break

  def encoderStatusCallback(text,percentage):
    statusCallback(text,percentage)
    packageglobalStatusCallback(text,percentage)

  def encoderFunction(br,passNumber,passReason,passPhase=0):

    ffmpegcommand=[]
    ffmpegcommand+=['ffmpeg' ,'-y']
    ffmpegcommand+=inputsList

    if options.get('audioChannels') == 'No audio':
      ffmpegcommand+=['-filter_complex',filtercommand+',[outa]anullsink']
      ffmpegcommand+=['-map','[outv]']
    else:
      ffmpegcommand+=['-filter_complex',filtercommand]
      ffmpegcommand+=['-map','[outv]','-map','[outa]']  

    ffmpegcommand+=["-shortest"
                   ,"-copyts"
                   ,"-start_at_zero"
                   ,"-c:v","libx264" 
                   ,"-stats"
                   ,"-pix_fmt","yuv420p"
                   ,"-bufsize", "3000k"
                   ,"-threads", str(4)
                   ,"-crf"  ,'17'
                   ,"-preset", "slow"
                   ,"-tune", "film"
                   ,"-movflags","+faststart"]

    if options.get('audioChannels') == 'No audio':
      ffmpegcommand+=["-an"]
    elif options.get('audioChannels') == 'Stereo':
      ffmpegcommand+=["-c:a"  ,"aac"]
      ffmpegcommand+=["-ac","2"]
    else:
      ffmpegcommand+=["-c:a"  ,"aac"]
      ffmpegcommand+=["-ac","1"]


    ffmpegcommand += ["-sn",finalOutName]

    print(' '.join(ffmpegcommand))

    encoderStatusCallback('Encoding final '+finalOutName,(totalEncodedSeconds)/totalExpectedEncodedSeconds)
    proc = sp.Popen(ffmpegcommand,stderr=sp.PIPE,stdin=sp.DEVNULL,stdout=sp.DEVNULL)
    logffmpegEncodeProgress(proc,'Pass {} {} {}'.format(passNumber,passReason,finalOutName),totalEncodedSeconds,totalExpectedEncodedSeconds,encoderStatusCallback)
    finalSize = os.stat(finalOutName).st_size
    return finalSize

  encodeTargetingSize(encoderFunction=encoderFunction,
                      outputFilename=finalOutName,
                      initialDependentValue=initialBr,
                      sizeLimitMin=sizeLimitMin,
                      sizeLimitMax=sizeLimitMax,
                      maxAttempts=10)

  encoderStatusCallback('Encoding final '+finalOutName,(totalEncodedSeconds)/totalExpectedEncodedSeconds )
  encoderStatusCallback('Encoding complete '+finalOutName,1)

def gifEncoder(inputsList, outputPathName,filenamePrefix, filtercommand, options, totalEncodedSeconds, totalExpectedEncodedSeconds, statusCallback):

  if options.get('maximumSize') == 0.0:
    sizeLimitMax = float('inf')
    sizeLimitMin = float('-inf')
  else:
    sizeLimitMax = options.get('maximumSize')*1024*1024
    sizeLimitMin = sizeLimitMax*0.85

  fileN=0
  while 1:
    fileN+=1
    finalOutName = '{}_WmG_{}.gif'.format(filenamePrefix,fileN)    
    finalOutName = os.path.join(outputPathName,finalOutName)
    if not os.path.exists(finalOutName):
      break

  def encoderStatusCallback(text,percentage):
    statusCallback(text,percentage)
    packageglobalStatusCallback(text,percentage)


  def encoderFunction(width,passNumber,passReason,passPhase=0):

    giffiltercommand = filtercommand+',[outv]fps=fps=24,scale=\'max({}\\,min({}\\,iw)):-1\',split[pal1][outvpal],[pal1]palettegen=stats_mode=diff[plt],[outvpal][plt]paletteuse=dither=floyd_steinberg:[outvgif],[outa]anullsink'.format(0,width)

    ffmpegcommand=[]
    ffmpegcommand+=['ffmpeg' ,'-y']
    ffmpegcommand+=inputsList
    ffmpegcommand+=['-filter_complex',giffiltercommand]
    ffmpegcommand+=['-map','[outvgif]']
    ffmpegcommand+=["-vsync", '0'
                   ,"-shortest" 
                   ,"-copyts"
                   ,"-start_at_zero"
                   ,"-stats"
                   ,"-an"
                   ,"-sn",finalOutName]

    encoderStatusCallback('Encoding final '+finalOutName,(totalEncodedSeconds)/totalExpectedEncodedSeconds)

    proc = sp.Popen(ffmpegcommand,stderr=sp.PIPE,stdin=sp.DEVNULL,stdout=sp.DEVNULL)
    logffmpegEncodeProgress(proc,'Pass {} {} {}'.format(passNumber,passReason,finalOutName),totalEncodedSeconds,totalExpectedEncodedSeconds,encoderStatusCallback)
    finalSize = os.stat(finalOutName).st_size
    return finalSize

  initialWidth = options.get('maximumWidth',1280)
  encodeTargetingSize(encoderFunction=encoderFunction,
                      outputFilename=finalOutName,
                      initialDependentValue=initialWidth,
                      sizeLimitMin=sizeLimitMin,
                      sizeLimitMax=sizeLimitMax,
                      maxAttempts=10,
                      dependentValueName='Width')
  encoderStatusCallback('Encoding final '+finalOutName,(totalEncodedSeconds)/totalExpectedEncodedSeconds )
  encoderStatusCallback('Encoding complete '+finalOutName,1)

encoderMap = {
   'webm:VP8':webmvp8Encoder
  ,'mp4:x264':mp4x264Encoder
  ,'gif':gifEncoder
}


class FFmpegService():

  def __init__(self,globalStatusCallback=print(),imageWorkerCount=2,encodeWorkerCount=1,statsWorkerCount=1):
    

    self.cache={}
    self.imageRequestQueue = Queue()
    self.responseRouting = {}
    self.globalStatusCallback=globalStatusCallback
    global packageglobalStatusCallback
    packageglobalStatusCallback = globalStatusCallback
    def imageWorker():
      while 1:
        try:
          requestKey = self.imageRequestQueue.get()
          requestId,filename,timestamp,filters,size = requestKey
          if filters == '':
            filters='null'
          w,h=size
          if type(timestamp) != float and '%' in timestamp:
            pc = float(timestamp.replace('%',''))/100.0
            videoInfo = ffmpegInfoParser.getVideoInfo(cleanFilenameForFfmpeg(filename))
            timestamp = videoInfo.duration*pc


          cmd=['ffmpeg','-y',"-loglevel", "quiet","-noaccurate_seek",'-ss',str(timestamp),'-i',cleanFilenameForFfmpeg(filename), '-filter_complex',filters+',scale={w}:{h}'.format(w=w,h=h),"-pix_fmt", "rgb24",'-vframes', '1', '-an', '-c:v', 'ppm', '-f', 'rawvideo', '-']
          print(' '.join(cmd))
          proc = sp.Popen(cmd,stdout=sp.PIPE)
          outs,errs = proc.communicate()
          self.postCompletedImageFrame(requestKey,outs)
        except Exception as e:
          print(imageWorker,e)


    self.imageWorkers=[]
    for _ in range(imageWorkerCount):
      imageWorkerThread = threading.Thread(target=imageWorker,daemon=True)
      imageWorkerThread.start()
      self.imageWorkers.append(imageWorkerThread)

    self.encodeRequestQueue = Queue()

    def encodeWorker():
      tempPathname='tempVideoFiles'
      outputPathName='finalVideos'
      runNumber=int(time.time())

      while 1:
        try:
          requestId,mode,seqClips,options,filenamePrefix,statusCallback = self.encodeRequestQueue.get()

          expectedTimes = []
          processed={}
          fileSequence=[]
          clipDimensions = []
          infoOut={}

          print(requestId,mode,seqClips,options,filenamePrefix,statusCallback)
          for i,(rid,clipfilename,s,e,filterexp) in enumerate(seqClips):
            print(i,(rid,clipfilename,s,e,filterexp))
            expectedTimes.append(e-s)
            videoInfo = ffmpegInfoParser.getVideoInfo(cleanFilenameForFfmpeg(clipfilename))
            infoOut[rid] = videoInfo
            videoh=videoInfo.height
            videow=videoInfo.width
            clipDimensions.append((videow,videoh))

          largestclipDimensions = sorted(clipDimensions,key=lambda x:x[0]*x[1],reverse=True)[0]

          expectedTimes.append(sum(expectedTimes))
          totalExpectedEncodedSeconds = sum(expectedTimes)
          totalEncodedSeconds = 0

          for i,(etime,(videow,videoh),(rid,clipfilename,start,end,filterexp)) in enumerate(zip(expectedTimes,clipDimensions,seqClips)):
            print(i,(etime,(videow,videoh),(rid,clipfilename,start,end,filterexp)))
            if filterexp=='':
              filterexp='null'  

            #Black Bars
            #scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2
            
            #Crop
            #scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720

            filterexp+=",scale='max({}\\,min({}\\,iw)):-2'".format(0,options.get('maximumWidth',1280))
            filterexp += ',pad=ceil(iw/2)*2:ceil(ih/2)*2'

            key = (rid,clipfilename,start,end,filterexp)

            basename = os.path.basename(clipfilename)

            os.path.exists(tempPathname) or os.mkdir(tempPathname)

            m = hashlib.md5()
            m.update(filterexp.encode('utf8'))
            filterHash = m.hexdigest()[:10]

            basename = ''.join([x for x in basename if x in string.digits+string.ascii_letters+' -_'])[:10]

            outname = '{}_{}_{}_{}_{}_{}.mp4'.format(i,basename,start,end,filterHash,runNumber)
            outname = os.path.join( tempPathname,outname )

            if os.path.exists(outname):
              processed[key]=outname
              fileSequence.append(processed[key])
              totalEncodedSeconds+=etime
              statusCallback('Cutting clip {}'.format(i+1),(totalEncodedSeconds)/totalExpectedEncodedSeconds )
              self.globalStatusCallback('Cutting clip {}'.format(i+1),(totalEncodedSeconds)/totalExpectedEncodedSeconds )

            elif key not in processed:
              statusCallback('Cutting clip {}'.format(i+1), totalEncodedSeconds/totalExpectedEncodedSeconds)
              self.globalStatusCallback('Cutting clip {}'.format(i+1), totalEncodedSeconds/totalExpectedEncodedSeconds)
              
              if infoOut[rid].hasaudio:
                comvcmd = ['ffmpeg','-y'                                
                          ,'-ss', str(start)
                          ,'-i', cleanFilenameForFfmpeg(clipfilename)
                          ,'-t', str(end-start)
                          ,'-filter_complex', filterexp
                          ,'-c:v', 'libx264'
                          ,'-crf', '0'
                          ,'-ac', '1',outname]
              else:
                comvcmd = ['ffmpeg','-y'
                          ,'-f', 'lavfi', '-i', 'anullsrc'                                
                          ,'-ss', str(start)
                          ,'-i', cleanFilenameForFfmpeg(clipfilename)
                          ,'-t', str(end-start)
                          ,'-filter_complex', filterexp
                          ,'-c:v', 'libx264'
                          ,'-crf', '0'
                          ,'-map', '0:a', '-map', '1:v' 
                          ,'-shortest'
                          ,'-ac', '1',outname]

              proc = sp.Popen(comvcmd,stderr=sp.PIPE,stdin=sp.DEVNULL,stdout=sp.DEVNULL)
              
              currentEncodedTotal=0
              ln=b''
              while 1:
                  c = proc.stderr.read(1)
                  if len(c)==0:
                    break
                  if c == b'\r':
                    print(ln)
                    for p in ln.split(b' '):
                      if b'time=' in p:
                        try:
                          pt = datetime.strptime(p.split(b'=')[-1].decode('utf8'),'%H:%M:%S.%f')
                          currentEncodedTotal = pt.microsecond/1000000 + pt.second + pt.minute*60 + pt.hour*3600
                          if currentEncodedTotal>0:
                            statusCallback('Cutting clip {}'.format(i+1), (currentEncodedTotal+totalEncodedSeconds)/totalExpectedEncodedSeconds)
                            self.globalStatusCallback('Cutting clip {}'.format(i+1), (currentEncodedTotal+totalEncodedSeconds)/totalExpectedEncodedSeconds)
                        except Exception as e:
                          print(e)
                    ln=b''
                  ln+=c
              totalEncodedSeconds+=etime
              statusCallback('Cutting clip {}'.format(i+1),(totalEncodedSeconds)/totalExpectedEncodedSeconds)
              self.globalStatusCallback('Cutting clip {}'.format(i+1),(totalEncodedSeconds)/totalExpectedEncodedSeconds)

              processed[key]=outname
              fileSequence.append(outname)
            else:
              fileSequence.append(processed[key])
              totalEncodedSeconds+=etime
              statusCallback('Cutting clip {}'.format(i+1),(totalEncodedSeconds)/totalExpectedEncodedSeconds )
              self.globalStatusCallback('Cutting clip {}'.format(i+1),(totalEncodedSeconds)/totalExpectedEncodedSeconds )

          fadeDuration=0.25
          try:
            fadeDuration= float(options.get('transDuration',0.5))
          except Exception as e:
            print('invalid fade duration',e)

          print(fadeDuration)

          if fadeDuration > 0.0:
            inputsList = []

            for vi,v in enumerate(fileSequence):
              inputsList.extend(['-i',v])

            transition = options.get('transStyle','smoothleft')
            offset=fadeDuration*2
            expectedFadeDurations = expectedTimes[:-1]

            videoSplits=[]
            transitionFilters=[]
            audioSplits=[]
            crossfades=[]
            crossfadeOut=''

            splitTemplate='[{i}:v]split[vid{i}a][vid{i}b];'
            xFadeTemplate='[vid{i}a][vid{n}b]xfade=transition={trans}:duration={fdur}:offset={o}[fade{i}];'
            fadeTrimTemplate  = '[fade{i}]trim={preo}:{dur},setpts=PTS-STARTPTS[fadet{i}];'
            asplitTemplate    = '[{i}:a]asplit[ata{i}][atb{i}];[ata{i}]atrim={preo}:{dur}[atat{i}];'
            crossfadeTemplate = '[atat{i}][atb{n}]acrossfade=d={preo},atrim=0:{o}[audf{i}];'

            for i,dur in enumerate(expectedFadeDurations):
              n=0 if i==len(expectedFadeDurations)-1 else i+1
              o=dur-offset
              preo=offset          
              videoSplits.append(splitTemplate.format(i=i))
              transitionFilters.append(xFadeTemplate.format(i=i,n=n,o=o,fdur=fadeDuration,trans=transition))
              audioSplits.append(fadeTrimTemplate.format(i=i,preo=preo,dur=dur))
              audioSplits.append(asplitTemplate.format(i=i,preo=preo,dur=dur))
              crossfades.append(crossfadeTemplate.format(i=i,preo=preo,dur=dur,n=n,o=o))
              crossfadeOut+='[fadet{i}][audf{i}]'.format(i=i)
            crossfadeOut+='concat=n={}:v=1:a=1[concatOutV][concatOutA]'.format(len(expectedFadeDurations))

            try:
              speedAdjustment= float(options.get('speedAdjustment',1.0))
            except Exception as e:
              print('invalid speed Adjustment',e)

            if speedAdjustment==1.0:
              crossfadeOut += ',[concatOutV]null[outvpre],[concatOutA]anull[outa]'
            else:
              try:
                vfactor=1/speedAdjustment
                afactor=speedAdjustment
                crossfadeOut += ',[concatOutV]setpts={vfactor}*PTS,minterpolate=\'mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=30\'[outvpre],[concatOutA]atempo={afactor}[outa]'.format(vfactor=vfactor,afactor=afactor)
              except Exception as e:
                print(e)
                crossfadeOut += ',[concatOutV]null[outvpre],[concatOutA]anull[outa]'

            filtercommand = ''.join(videoSplits+transitionFilters+audioSplits+crossfades+[crossfadeOut])
          else:
            inputsList   = []
            filterInputs = ''
            for vi,v in enumerate(fileSequence):
              inputsList.extend(['-i',v])
              filterInputs += '[{i}:v][{i}:a]'.format(i=vi)
            filtercommand = filterInputs + 'concat=n={}:v=1:a=1[outvpre][outa]'.format(len(inputsList)//2)
          
          if os.path.exists('post-filters.txt'):
            filtercommand += open('post-filters.txt','r').read()
          else:
            filtercommand += ',[outvpre]null[outv]'

          print(filtercommand)

          os.path.exists(outputPathName) or os.mkdir(outputPathName)

          outputFormat  = options.get('outputFormat','webm:VP8')
          finalEncoder  = encoderMap.get(outputFormat,encoderMap.get('webm:VP8'))
          finalEncoder(inputsList, 
                       outputPathName,
                       filenamePrefix, 
                       filtercommand, 
                       options, 
                       totalEncodedSeconds, 
                       totalExpectedEncodedSeconds, 
                       statusCallback)
        except Exception as e:
          print(e)
          import traceback
          traceback.print_exc()

    self.encodeWorkers=[]
    for _ in range(encodeWorkerCount):
      encodeWorkerThread = threading.Thread(target=encodeWorker,daemon=True)
      encodeWorkerThread.start()
      self.encodeWorkers.append(encodeWorkerThread)

    self.statsRequestQueue = Queue()
    def statsWorker():
      while 1:
        try:
          filename,requestType,options,callback = self.statsRequestQueue.get()
          if requestType == 'MSESearchImprove':
            print('error seatch srtart')
            filename = options.get('filename')
            start = options.get('start')
            end   = options.get('end')
            searchDistance=options.get('secondsChange')

            halfclipDur = (end-start)/2

            if searchDistance>halfclipDur:
              searchDistance=halfclipDur

            cropRect = options.get('cropRect')
            rid = options.get('rid')
            


            od=224
            nbytes = 3 * od * od
            frameDistance=0.01

            if cropRect is None:
              videofilter = "scale={}:{}".format(od,od)
            else:
              x,y,w,h = cropRect
              videofilter = "crop={}:{}:{}:{},scale={}:{}".format(x,y,w,h,od,od)

            popen_params = {
              "bufsize": 10 ** 5,
              "stdout": sp.PIPE,
              #"stderr": sp.DEVNULL,
            }

            startCmd = ["ffmpeg"
                      ,'-ss',str(start-searchDistance)
                      ,"-i", cleanFilenameForFfmpeg(filename)  
                      ,'-s', '{}x{}'.format(od,od)
                      ,'-ss',str(start-searchDistance)
                      ,'-t', str(searchDistance*2)
                      ,"-filter_complex", videofilter
                      ,"-copyts"
                      ,"-f","image2pipe"
                      ,"-an"
                      ,"-pix_fmt","bgr24"
                      ,"-vcodec","rawvideo"
                      ,"-vsync", "vfr"
                      ,"-"]
            endCmd = ["ffmpeg"
                      ,'-ss',str(end-searchDistance)
                      ,"-i", cleanFilenameForFfmpeg(filename) 
                      ,'-s', '{}x{}'.format(od,od)
                      ,'-ss',str(end-searchDistance)
                      ,'-t', str(searchDistance*2)
                      ,"-filter_complex", videofilter
                      ,"-copyts"
                      ,"-f","image2pipe"
                      ,"-an"
                      ,"-pix_fmt","bgr24"
                      ,"-vcodec","rawvideo"
                      ,"-vsync", "vfr"
                      ,"-"]

            startFrames = np.frombuffer(sp.Popen(startCmd,**popen_params).stdout.read(), dtype="uint8")
            endFrames   = np.frombuffer(sp.Popen(endCmd,**popen_params).stdout.read(), dtype="uint8")

            startFrames.shape = (-1,od,od,3)
            endFrames.shape = (-1,od,od,3)

            distances = []
            sframeDistance = ((searchDistance*2)/startFrames.shape[0])
            eframeDistance = ((searchDistance*2)/endFrames.shape[0])

            for si,frame in enumerate(startFrames):
              
              self.globalStatusCallback('Finding closest frame match',si/startFrames.shape[0])

              mse = ((startFrames[si] - endFrames)**2).mean(axis=(1,2,3))
              argmin = np.argmin(mse)  
              matchStart = (start-searchDistance)+(si*sframeDistance)
              matchEnd   = (end-searchDistance)+(argmin*eframeDistance)
              distances.append( (mse[argmin],matchStart,matchEnd) )
              print(mse[argmin],matchStart,matchEnd)

            finalmse,finals,finale = sorted(distances)[0]
            print(finalmse,finals,finale)
            self.globalStatusCallback('Found closest matches, updating',1)
            callback(filename,rid,mse,finals,finale)

          elif requestType == 'SceneChangeSearch':
            expectedLength = options.get('duration',0)
            self.globalStatusCallback('Starting scene change detection ',0/expectedLength)
            proc = sp.Popen(
              ['ffmpeg','-i',cleanFilenameForFfmpeg(filename),'-filter_complex', 'select=gt(scene\\,0.3),showinfo', '-f', 'null', 'NUL']
              ,stderr=sp.PIPE)
            ln=b''
            while 1:
              c=proc.stderr.read(1)
              if len(c)==0:
                break
              if c in b'\r\n':
                if b'pts_time' in ln:
                  for e in ln.split(b' '):
                    if b'pts_time' in e:
                      ts = float(e.split(b':')[-1])
                      self.globalStatusCallback('Scene change detection ',ts/expectedLength)
                      callback(filename,ts)
                ln=b''
              else:
                ln+=c
        except Exception as e:
          print(e)

    self.statsWorkers=[]
    for _ in range(statsWorkerCount):
      statsWorkerThread = threading.Thread(target=statsWorker,daemon=True)
      statsWorkerThread.start()
      self.statsWorkers.append(statsWorkerThread)

  def encode(self,requestId,mode,seq,options,filenamePrefix,statusCallback):
    self.encodeRequestQueue.put((requestId,mode,seq,options,filenamePrefix,statusCallback))

  def requestPreviewFrame(self,requestId,filename,timestamp,filters,size,callback):
    requestKey = (requestId,filename,timestamp,filters,size)
    self.responseRouting[requestKey]=callback
    if requestKey in self.cache:
      callback(requestId,self.cache[requestKey])
    self.imageRequestQueue.put( requestKey )

  def postCompletedImageFrame(self,requestKey,responseImage):
    self.cache[requestKey] = responseImage
    requestId,filename,timestamp,filters,size = requestKey
    self.responseRouting[requestKey](requestId,responseImage)

  def runSceneChangeDetection(self,filename,duration,callback):
    self.statsRequestQueue.put( (filename,'SceneChangeSearch',dict(filename=filename,
                                                             duration=duration),callback) )

  def findLowerErrorRangeforLoop(self,filename,start,end,rid,secondsChange,cropRect,callback):
    self.statsRequestQueue.put( (filename,'MSESearchImprove',dict(filename=filename,
                                                             start=start,
                                                             end=end,
                                                             rid=rid,
                                                             cropRect=cropRect,
                                                             secondsChange=secondsChange),callback) )

if __name__ == '__main__':
  import webmGenerator