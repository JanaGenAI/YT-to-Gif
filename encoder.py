
import subprocess as sp
import os
from datetime import datetime

maxWidth = 1280
targetSize_max = 4194304
targetSize_min = 3900000
audio_mp = 8
video_mp = 1024
crf=4
threads = 2
logo='logo.png'
footer='footer.png'
maxTriesBeforeAcceptingSmaller=10
maxTries=15

import json
try:
  config = json.loads(open('config.json','r'))
  maxWidth       = config.get('maxWidth',maxWidth) 
  targetSize_max = config.get('targetSize_max',targetSize_max) 
  targetSize_min = config.get('targetSize_min',targetSize_min) 
  crf            = config.get('crf',crf) 
  threads        = config.get('threads',threads)  
  maxTries       = config.get('maxTries',maxTries)  
  maxTriesBeforeAcceptingSmaller = config.get('maxTriesBeforeAcceptingSmaller',maxTriesBeforeAcceptingSmaller)
except:
  pass

def monitorFFMPEGProgress(proc,desc,a,b):

  print('Encoding (Starting)\r')
  ln=b''
  while 1:
    c = proc.stderr.read(1)
    if len(c)==0:
      break
    if c == b'\r':
      for p in ln.split(b' '):
        if b'time=' in p:
          pt = datetime.strptime(p.split(b'=')[-1].decode('utf8'),'%H:%M:%S.%f')
          total_seconds = pt.microsecond/1000000 + pt.second + pt.minute*60 + pt.hour*3600
          if total_seconds>0:
            print('Encoding (Actual) {:01.2f}%    '.format( (total_seconds/abs(a-b))*100 ),end='\r')
      ln=b''
    ln+=c
  print('Encoding Done')


def processClips(clips):
  for (cat,src,s,e),(incudelogo,includefooter),(cw,ch,cx,cy) in clips:
    
    cw,ch,cx,cy  = int(cw),int(ch),int(cx),int(cy)

    s = max(0,s)
    dur = abs(s-e)

    br = int( ((3.8*video_mp)/dur) - ((32 / audio_mp)/dur) ) *8


    brmult=1

    os.path.exists('out') or os.mkdir('out')
    if cat is not None:
      os.path.exists(os.path.join('out',cat)) or os.mkdir(os.path.join('out',cat))
    os.path.exists('temp') or os.mkdir('temp')

    if cat is not None:
      outFilename=os.path.join('out',cat,os.path.splitext(os.path.basename(src))[0]+'.'+str(int(s))+'.'+str(int(e))+".webm")
      tempname = os.path.join('temp',os.path.splitext(os.path.basename(src))[0]+'.'+str(int(s))+'.'+str(int(e))+".webm")
    else:
      outFilename=os.path.join('out',os.path.splitext(os.path.basename(src))[0]+'.'+str(int(s))+'.'+str(int(e))+".webm")
      tempname = os.path.join('temp',os.path.splitext(os.path.basename(src))[0]+'.'+str(int(s))+'.'+str(int(e))+".webm")

    print('Current File:',outFilename)
    print('Range',s,e)
    
    attempt=0

    filterString = '[0:v]'



    filterString = "movie='logo.png'[logo], movie='footer.png'[footer]"

    if cx!=0 and cy !=0 and cw!=0 and ch!=0:
      filterString += ",[0:v]crop={}:{}:{}:{}[cv]".format(cw,ch,cx,cy)
    else:
      filterString += ",[0:v]null[cv]".format(cw,ch,cx,cy)

    filterString += ",[cv] scale='min("+str(maxWidth)+"\\,iw):-1' [sv]"

    if incudelogo:
      filterString += ",[sv][logo]overlay='5:5'[vlogo]"
    else:
      filterString += ",[logo]nullsink,[sv]null[vlogo]"

    if includefooter:
      filterString += ",[vlogo][footer]overlay='(W-w)/2:(H-h)'"
    else:
      filterString += ",[footer]nullsink,[vlogo]null"

    while 1:
      attempt+=1
      print('Processing Pass 1 attempt',attempt)
      cmd = ["ffmpeg"
             ,"-y" 
           
             ,"-i"    , src 
             ,"-ss"   , "{:01.2f}".format(s) 
             ,"-t"    , "{:01.2f}".format(dur)
             ,"-c:v"  ,"libvpx" 
             ,"-stats"
             ,"-bufsize", "3000k"
             ,"-threads", str(threads)
             ,"-quality", "best" 
             ,"-auto-alt-ref", "1" 
             ,"-lag-in-frames", "16" 
             ,"-slices", "8"
             ,"-passlogfile", tempname+".log"
             ,"-cpu-used", "0"

             ,"-crf"  ,str(crf)
             ,"-b:v"  ,str(br*brmult)+'K' 
             ,"-ac"   ,"1" 
             ,"-an"

             ,"-filter_complex", filterString
             ,"-pix_fmt", "yuv420p"
             ,"-movflags", "faststart"
             ,"-pass" ,"1" 
             ,"-f"    ,"webm" 
             ,'nul']

      print(' '.join(cmd))
      proc = sp.Popen(cmd,stderr=sp.PIPE,stdout=sp.PIPE)
      print(proc.communicate())

      cmd = ["ffmpeg"
             ,"-y" 

             ,"-i"    , src
             ,"-ss"   , "{:01.2f}".format(s) 
             ,"-t"   , "{:01.2f}".format(dur)
             ,"-c:v"  ,"libvpx" 
             ,"-stats"
             ,"-bufsize", "3000k"
             ,"-threads", str(threads)
             ,"-quality", "best" 
             ,"-auto-alt-ref", "1" 
             ,"-lag-in-frames", "16" 
             ,"-slices", "8"
             ,"-passlogfile", tempname+".log"
             ,"-cpu-used", "0"

             ,"-crf"  ,str(crf) 
             ,"-b:v"  ,str(br*brmult)+'K'
             ,"-ac"   ,"1"            
             ,"-c:a"  ,"libvorbis"
             ,"-b:a"  ,"32k"  
             ,"-filter_complex", filterString
             ,"-pix_fmt", "yuv420p"
             ,"-movflags", "faststart"
             ,"-pass" ,"2"
             ,tempname]
      print(' '.join(cmd))
      proc = sp.Popen(cmd,stderr=sp.PIPE,stdout=sp.PIPE)
      monitorFFMPEGProgress(proc,'Encoding:',s,e)
      proc.communicate()

      finalSize = os.stat(tempname).st_size

      if targetSize_min<finalSize<targetSize_max or (finalSize<targetSize_max and attempt>10):
        print("Complete.")
        os.rename(tempname,outFilename)
        break
      else:        
        if finalSize<targetSize_min:
          print("File size too small",finalSize,targetSize_min-finalSize)
        elif finalSize>targetSize_max:
          print("File size too large",finalSize,finalSize-targetSize_max)
        brmult= brmult+(1.0-(finalSize/( (targetSize_min+targetSize_max)/2.0 ) ))