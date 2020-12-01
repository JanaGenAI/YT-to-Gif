
import os
import json

class MergeSelectionController:

  def __init__(self,ui,videoManager,ffmpegService,filterController):
    self.ui=ui
    
    self.videoManager=videoManager
    self.ffmpegService=ffmpegService
    self.filterController=filterController
    self.profileSpecPath = 'customEncodeProfiles'

    self.stdProfileSpecs = [ 
      {'name':'None','editable':False},
      {'name':'Default max quality mp4','editable':False,'outputFormat':'mp4:x264','maximumSize':'0.0'},
      {'name':'Sub 4M max quality vp8 webm','editable':False,'outputFormat':'webm:VP8','maximumSize':'4.0'},
      {'name':'Sub 100M max quality mp4','editable':False,'outputFormat':'mp4:x264','maximumSize':'100.0'}
    ]

    self.customProfileSpecs = [{'name':'Custom Profile 1','editable':False,'outputFormat':'mp4:x264','maximumSize':'200.0'}]

    if os.path.exists(self.profileSpecPath):
      for profileFile in os.listdir(self.profileSpecPath):
        profileFilename = os.path.join(self.profileSpecPath,profileFile)
        if os.path.exists(profileFilename) and os.path.isfile(os.path.exists(profileFilename)):
          try:
            profile = json.loads( open(profileFilename,'r').read() )
            profile['filename'] = profileFile
            self.customProfileSpecs.append( profile )
          except:
            pass

    self.ui.setController(self)

  def getFilteredClips(self):
    return self.filterController.getClipsWithFilters()

  def requestPreviewFrame(self,rid,filename,timestamp,filterexp,size,callback):
    self.ffmpegService.requestPreviewFrame(rid,filename,timestamp,filterexp,size,callback)

  def encode(self,requestId,mode,seq,options,filenamePrefix,statusCallback):
    print('encode',requestId,mode,seq,options,filenamePrefix)
    self.ffmpegService.encode(requestId,mode,seq,options,filenamePrefix,statusCallback)

  def cancelEncodeRequest(self,requestId):
    self.ffmpegService.cancelEncodeRequest(requestId)

  def deleteCustomProfile(self,profileName):
    return ''

  def saveCustomProfile(self,profile):
    os.path.exists(self.profileSpecPath) or os.mkdir(self.profileSpecPath)
    return ''

  def getProfiles(self):
    return self.stdProfileSpecs + self.customProfileSpecs

if __name__ == '__main__':
  import webmGenerator
