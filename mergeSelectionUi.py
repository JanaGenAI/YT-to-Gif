import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.scrolledframe import ScrolledFrame
import os
import string 

class EncodeProgress(ttk.Frame):
  def __init__(self, master=None, *args, encodeRequestId=None, **kwargs):
    ttk.Frame.__init__(self, master)
    self.frameEncodeProgressWidget = self
    self.labelEncodeProgressLabel = ttk.Label(self.frameEncodeProgressWidget)
    self.labelEncodeProgressLabel.config(text='Encode request submitted', width='60')
    self.labelEncodeProgressLabel.pack(side='left')
    self.progressbarEncodeProgressLabel = ttk.Progressbar(self.frameEncodeProgressWidget)
    self.progressbarEncodeProgressLabel.config(mode='determinate', orient='horizontal')
    self.progressbarEncodeProgressLabel.pack(expand='true',padx=10, fill='x', side='left')

    self.frameEncodeProgressWidget.config(height='200', width='200')
    self.frameEncodeProgressWidget.pack(anchor='nw', expand='false',padx=10,pady=10, fill='x', side='top')

  def updateStatus(self,status,percent):
    self.labelEncodeProgressLabel.config(text=status)
    self.progressbarEncodeProgressLabel['value']=percent*100
    if percent >= 1:
      self.progressbarEncodeProgressLabel.config(style="Green.Horizontal.TProgressbar")
    else:
      self.progressbarEncodeProgressLabel.config(style="Blue.Horizontal.TProgressbar")

    self.winfo_toplevel().title('webmGenerator: encoding: {:0.2f}%'.format(percent*100))


class SequencedVideoEntry(ttk.Frame):
  def __init__(self, master,controller,sourceClip, *args, **kwargs):
    ttk.Frame.__init__(self, master)

    self.rid=sourceClip.rid
    self.s=sourceClip.s
    self.e=sourceClip.e
    self.controller=controller
    
    self.filename=sourceClip.filename
    self.filterexp=sourceClip.filterexp
    self.basename = sourceClip.basename
    self.previewImage=sourceClip.previewImage

    self.frameSequenceVideoEntry = self
    self.labelSequenceVideoName = ttk.Label(self.frameSequenceVideoEntry)
    self.labelSequenceVideoName.config(text='{} ({:0.2f}-{:0.2f}) {:0.2f}s'.format(self.basename,self.s,self.e,self.e-self.s))
    self.labelSequenceVideoName.pack(side='top')
    self.frameOrderingButtons = ttk.Frame(self.frameSequenceVideoEntry)
    self.buttonSequencePushEntryBack = ttk.Button(self.frameOrderingButtons)
    self.buttonSequencePushEntryBack.config(text='⯇', width='2')
    self.buttonSequencePushEntryBack.config(command=self.moveBack)
    self.buttonSequencePushEntryBack.pack(expand='true', fill='both', side='left')
    
    self.canvasSequencePreview = ttk.Label(self.frameOrderingButtons)
    self.canvasSequencePreview.config(image=self.previewImage)

    self.canvasSequencePreview.pack(side='left')
    self.buttonSequencePushEntryForwards = ttk.Button(self.frameOrderingButtons)
    self.buttonSequencePushEntryForwards.config(text='⯈', width='2')
    self.buttonSequencePushEntryForwards.config(command=self.moveForwards)
    self.buttonSequencePushEntryForwards.pack(expand='true', fill='both', side='left')
    self.frameOrderingButtons.config(height='200', width='200')
    self.frameOrderingButtons.pack(side='top')

    self.buttonSequenceEntryREmove = ttk.Button(self.frameSequenceVideoEntry)
    self.buttonSequenceEntryREmove.config(text='Remove')
    self.buttonSequenceEntryREmove.config(command=self.remove)
    self.buttonSequenceEntryREmove.pack(expand='true', fill='both', side='top')

    self.frameSequenceVideoEntry.config(height='200', padding='2', relief='groove', width='200')
    self.frameSequenceVideoEntry.pack(expand='false', fill='y', side='left')

  def moveForwards(self):
    self.controller.moveSequencedClip(self,1)    

  def moveBack(self):
    self.controller.moveSequencedClip(self,-1)

  def remove(self):
    self.controller.removeSequencedClip(self)

  def setPreviewImage(self,photoImage):
    self.previewImage=photoImage
    self.canvasSequencePreview.config(image=self.previewImage)

  def update(self,s,e,filterexp):
    self.s=s
    self.e=e
    self.filterexp=filterexp
    self.labelSequenceVideoName.config(text='{} ({:0.2f}-{:0.2f}) {:0.2f}s'.format(self.basename,self.s,self.e,self.e-self.s))
    self.controller.requestPreviewFrame(self.rid,self.filename,(self.e+self.s)/2,self.filterexp)


class GridColumn(ttk.Frame):
  def __init__(self, master,controller):
    ttk.Frame.__init__(self, master)
    self.master=master
    self.controller=controller
    self.selected  =False

    self.selectColumn = ttk.Button(self,text='Select Column',command=self.selectColumn)
    self.selectColumn.pack(expand='false', fill='x', side='bottom')

    self.removeColumn = ttk.Button(self,text='Remove Column',command=self.removeColumn)
    self.removeColumn.pack(expand='false', fill='x', side='bottom')

  def selectColumn(self):
    pass

  def removeColumn(self):
    pass


class SelectableVideoEntry(ttk.Frame):
  def __init__(self, master,controller,filename,rid,s,e,filterexp, *args, **kwargs):
    ttk.Frame.__init__(self, master)
    self.master=master
    self.rid=rid
    self.s=s
    self.e=e
    self.controller=controller
    self.filename=filename
    self.filterexp=filterexp
    self.basename = os.path.basename(filename)[:14]

    self.frameInputCutWidget = self
    self.labelInputCutName = ttk.Label(self.frameInputCutWidget)
    self.labelInputCutName.config(text='{} ({:0.2f}-{:0.2f}) {:0.2f}s'.format(self.basename,self.s,self.e,self.e-self.s))
    self.labelInputCutName.pack(side='top')
    
    self.previewData = "P5\n200 117\n255\n"+("0"*200*117)
    self.previewImage= tk.PhotoImage(data=self.previewData)  
    self.canvasInputCutPreview = ttk.Label(self.frameInputCutWidget)
    self.canvasInputCutPreview.config(text='No Preview loaded')
    self.canvasInputCutPreview.config(image=self.previewImage)
    self.canvasInputCutPreview.pack(side='top')

    self.controller.requestPreviewFrame(self.rid,self.filename,(self.e+self.s)/2,self.filterexp)

    self.buttonInputCutAdd = ttk.Button(self.frameInputCutWidget)
    self.buttonInputCutAdd.config(text='Add to Sequence')
    self.buttonInputCutAdd.config(command=self.addClipToSequence)

    
    self.buttonInputCutAdd.pack(expand='true', fill='both', side='top')
    self.frameInputCutWidget.config(padding='2', relief='groove', width='200')
    self.frameInputCutWidget.pack(anchor='nw', expand='false', fill='y', side='left')

  def setPreviewImage(self,photoImage):
    self.previewImage=photoImage
    self.canvasInputCutPreview.config(image=self.previewImage)

  def update(self,s,e,filterexp):
    self.s=s
    self.e=e
    self.filterexp=filterexp
    self.labelInputCutName.config(text='{} ({:0.2f}-{:0.2f}) {:0.2f}s'.format(self.basename,self.s,self.e,self.e-self.s))
    self.controller.requestPreviewFrame(self.rid,self.filename,(self.e+self.s)/2,self.filterexp)

  def addClipToSequence(self):
    self.controller.addClipToSequence(self)

class MergeSelectionUi(ttk.Frame):
  def __init__(self, master=None, *args, **kwargs):
    ttk.Frame.__init__(self, master)

    self.master=master
    self.controller=None
    self.frameMergeSelection = self

    self.mergeStyleFrame = ttk.Frame(self.frameMergeSelection)

    self.mergestyleLabel = ttk.Label(self.mergeStyleFrame,text='Merge Style')
    self.mergestyleLabel.pack(expand='false', fill='x', side='left')

    self.mergeStyleVar = tk.StringVar()
    self.mergeStyles   = ['Individual Files - Output each individual subclip as a separate file.',                          
                          'Sequence - Join the subclips into a sequence.',
                          'Grid - Expeimental still under development.',]

    self.mergeStyleVar.set(self.mergeStyles[0])
    

    self.mergeStyleCombo = ttk.OptionMenu(self.mergeStyleFrame,self.mergeStyleVar,self.mergeStyleVar.get(),*self.mergeStyles)
    self.mergeStyleCombo.pack(expand='true', fill='x', side='right')

    self.mergeStyleFrame.pack(expand='false', fill='x', padx='5', pady='5', side='top')

    self.labelframeInputCutSelection = ttk.Labelframe(self.frameMergeSelection)
    self.scrolledframeInputCustContainer = ScrolledFrame(self.labelframeInputCutSelection, scrolltype='horizontal')


    self.selectableVideosContainer = ttk.Frame(self.scrolledframeInputCustContainer.innerframe)

    self.selectableVideosContainer.pack(expand='true', fill='both', padx='0', pady='0', side='top')

    self.scrolledframeInputCustContainer.innerframe.config(padding='5')
    self.scrolledframeInputCustContainer.configure(usemousewheel=False)
    self.scrolledframeInputCustContainer.pack(anchor='n', expand='true', fill='x', padx='5', pady='5', side='top')

    self.labelframeInputCutSelection.config(height='80', text='Avalaible Cuts', width='500')
    self.labelframeInputCutSelection.pack(expand='false', fill='x', padx='5', pady='5', side='top')

    self.addAddClipsFrame = ttk.Frame(self.frameMergeSelection)

    self.addAllClipsbutton = ttk.Button(self.addAddClipsFrame,text='⯆ Add all clips in timeline order ⯆')
    self.addAllClipsbutton.config(command=self.addAllClipsInTimelineOrder)
    self.addAllClipsbutton.pack(expand='false', fill='x', padx='5', pady='0', side='top')

    self.addAddClipsFrame.pack(expand='false', fill='x', padx='5', pady='0', side='top')


    self.labelframeSequenceFrame = ttk.Labelframe(self.frameMergeSelection)

    self.outputPlanningContainer = ttk.Frame(self.labelframeSequenceFrame)
    self.outputPlanningContainer.pack(expand='true', fill='both', padx='0', pady='0', side='top')

    self.gridSequenceContainer = ttk.Frame(self.outputPlanningContainer)
    self.gridSequenceContainer.pack(expand='true', fill='both', padx='5', pady='5', side='top')
    self.gridSequenceContainerAddColumn = ttk.Button(self.gridSequenceContainer,text='Add Column')
    self.gridSequenceContainerAddColumn.pack(expand='false', fill='x', padx='5', pady='5', side='bottom')
    self.gridSequenceContainer.pack_forget()



    self.scrolledframeSequenceContainer = ScrolledFrame(self.outputPlanningContainer, scrolltype='horizontal')

    self.sequenceContainer = ttk.Frame(self.scrolledframeSequenceContainer.innerframe)
    self.sequenceContainer.pack(expand='true', fill='both', padx='0', pady='0', side='top')

    self.mergeStyleVar.trace('w',self.mergeStyleChanged)
    

    self.sequencedClips = []

    self.scrolledframeSequenceContainer.configure(usemousewheel=False)
    self.scrolledframeSequenceContainer.innerframe.config(padding='5')
    self.scrolledframeSequenceContainer.pack(expand='true', fill='both', padx='5', pady='5', side='top')
    self.frameSequenceSummary = ttk.Frame(self.labelframeSequenceFrame)
    self.labelSequenceSummary = ttk.Label(self.frameSequenceSummary)
    self.labelSequenceSummary.config(anchor='center', text='Number of Subclips: 0 Total subclip duration 0s Output Duration 0s')
    self.labelSequenceSummary.pack(expand='false', fill='x', side='top')
    self.frameSequenceSummary.config(height='200', width='200')
    self.frameSequenceSummary.pack(expand='false', fill='x', side='top')
    
    self.frameTransitionSettings = ttk.Frame(self.labelframeSequenceFrame)

    self.frameEncodeSettings = ttk.Frame(self.labelframeSequenceFrame)
    self.frameSequenceValues = ttk.Frame(self.frameEncodeSettings)

    self.automaticFileNamingVar  = tk.BooleanVar() 
    self.filenamePrefixVar    = tk.StringVar()
    self.outputFormatVar      = tk.StringVar()
    self.frameSizeStrategyVar = tk.StringVar()
    self.maximumSizeVar       = tk.StringVar()
    self.maximumWidthVar      = tk.StringVar()
    self.transDurationVar     = tk.StringVar()
    self.transStyleVar        = tk.StringVar()
    self.speedAdjustmentVar   = tk.StringVar() 
    self.audioChannelsVar     = tk.StringVar()


    self.automaticFileNamingVar.trace('w',self.valueChange)
    self.filenamePrefixVar.trace('w',self.valueChange)
    self.outputFormatVar.trace('w',self.valueChange)
    self.frameSizeStrategyVar.trace('w',self.valueChange)
    self.maximumSizeVar.trace('w',self.valueChange)
    self.maximumWidthVar.trace('w',self.valueChange)
    self.transDurationVar.trace('w',self.valueChange)
    self.transStyleVar.trace('w',self.valueChange)
    self.speedAdjustmentVar.trace('w',self.valueChange)
    self.audioChannelsVar.trace('w',self.valueChange)


    self.automaticFileNamingVar.set(True)
    self.filenamePrefixVar.set('Sequence')

    self.outputFormats = [
      'mp4:x264',
      'webm:VP8',
      'gif',      
    ]
    self.outputFormatVar.set(self.outputFormats[0])

    self.frameSizeStrategies = [
      'Rescale to largest with black bars',
      'Rescale to largest and center crop smaller',    
    ]
    self.frameSizeStrategyVar.set(self.frameSizeStrategies[0])

    self.maximumSizeVar.set('0.0')
    self.maximumWidthVar.set('1280')
    self.transDurationVar.set('0.0')       

    self.transStyles = ['fade','wipeleft','wiperight','wipeup'
    ,'wipedown','slideleft','slideright','slideup','slidedown'
    ,'circlecrop','rectcrop','distance','fadeblack','fadewhite'
    ,'radial','smoothleft','smoothright','smoothup','smoothdown'
    ,'circleopen','circleclose','vertopen','vertclose','horzopen'
    ,'horzclose','dissolve','pixelize','diagtl','diagtr','diagbl'
    ,'diagbr','hlslice','hrslice','vuslice','vdslice']
    self.transStyleVar.set('fade')
    self.speedAdjustmentVar.set(1.0)

    self.audioChannelsOptions = ['Stereo','Mono','No audio']
    self.audioChannelsVar.set(self.audioChannelsOptions[0])    

    self.frameSequenceActions = ttk.Frame(self.frameEncodeSettings)
    self.buttonSequenceClear = ttk.Button(self.frameSequenceActions)
    self.buttonSequenceClear.config(text='Clear Sequence')
    self.buttonSequenceClear.config(command=self.clearSequence)
    self.buttonSequenceClear.pack(side='top')
    self.buttonSequenceEncode = ttk.Button(self.frameSequenceActions)
    self.buttonSequenceEncode.config(text='Encode')
    self.buttonSequenceEncode.config(command=self.encodeCurrent)
    self.buttonSequenceEncode.pack(expand='true', fill='both', side='top')
    self.frameSequenceActions.config(height='200', width='200')
    self.frameSequenceActions.pack(expand='false', fill='both', side='right')

    self.frameTransitionSettings.config(height='200', padding='5', relief='groove', width='200')
    self.frameTransitionSettings.pack(fill='x', ipadx='3', side='top')

    self.frameEncodeSettings.config(height='200', padding='5', relief='groove', width='200')
    self.frameEncodeSettings.pack(fill='x', ipadx='3', side='top')

    self.frameSequenceValuesLeft = ttk.Frame(self.frameSequenceValues)
    self.frameSequenceValuesRight = ttk.Frame(self.frameSequenceValues)



    # two column menu below

    self.frameAutomaticFileNaming = ttk.Frame(self.frameSequenceValuesLeft)
    self.labelAutomaticFileNaming = ttk.Label(self.frameAutomaticFileNaming)
    self.labelAutomaticFileNaming.config(anchor='e', padding='2', text='Automatically name output files', width='25')
    self.labelAutomaticFileNaming.pack(side='left')
    self.entryAutomaticFileNaming = ttk.Checkbutton(self.frameAutomaticFileNaming,text='',onvalue=True, offvalue=False)
    self.entryAutomaticFileNaming.config(width='5',variable=self.automaticFileNamingVar)
    self.entryAutomaticFileNaming.pack(expand='true', fill='both', side='left')
    self.frameAutomaticFileNaming.config(height='200', width='10')
    self.frameAutomaticFileNaming.pack(expand='true', fill='x', side='top')


    self.frameFilenamePrefix = ttk.Frame(self.frameSequenceValuesRight)
    self.labelFilenamePrefix = ttk.Label(self.frameFilenamePrefix)
    self.labelFilenamePrefix.config(anchor='e', padding='2', text='Output filename prefix', width='25')
    self.labelFilenamePrefix.pack(side='left')
    self.entryFilenamePrefix = ttk.Entry(self.frameFilenamePrefix)
    self.entryFilenamePrefix.config(width='5',textvariable=self.filenamePrefixVar)
    self.entryFilenamePrefix.pack(expand='true', fill='both', side='left')
    self.frameFilenamePrefix.config(height='200', width='10')
    self.frameFilenamePrefix.pack(expand='true', fill='x', side='top')


    self.frameOutputFormat = ttk.Frame(self.frameSequenceValuesLeft)
    self.labelOutputFormat = ttk.Label(self.frameOutputFormat)
    self.labelOutputFormat.config(anchor='e', padding='2', text='Otuput format', width='25')
    self.labelOutputFormat.pack(side='left')  
    self.comboboxOutputFormat= ttk.OptionMenu(self.frameOutputFormat,self.outputFormatVar,self.outputFormatVar.get(),*self.outputFormats)
    self.comboboxOutputFormat.pack(expand='true', fill='x', side='top')
    self.frameOutputFormat.config(height='200', width='100')
    self.frameOutputFormat.pack(expand='true', fill='x', side='top')

    self.frameSizeStrategy = ttk.Frame(self.frameSequenceValuesRight)
    self.labelSizeStrategy = ttk.Label(self.frameSizeStrategy)
    self.labelSizeStrategy.config(anchor='e', padding='2', text='Size Match Strategy', width='25')
    self.labelSizeStrategy.pack(side='left')
    
    self.comboboxSizeStrategy = ttk.OptionMenu(self.frameSizeStrategy,self.frameSizeStrategyVar,self.frameSizeStrategyVar.get(),*self.frameSizeStrategies)
    self.comboboxSizeStrategy.pack(expand='true', fill='x', side='top')
    self.frameSizeStrategy.config(height='200', width='100')
    self.frameSizeStrategy.pack(expand='true', fill='x', side='top')


    self.frameMaximumSize = ttk.Frame(self.frameSequenceValuesLeft)
    self.labelMaximumSize = ttk.Label(self.frameMaximumSize)
    self.labelMaximumSize.config(anchor='e', padding='2', text='Maximum File Size (MB)', width='25')
    self.labelMaximumSize.pack(side='left')
    self.entryMaximumSize = ttk.Spinbox(self.frameMaximumSize, from_=0, to=float('inf'), increment=0.1)
    self.entryMaximumSize.config(textvariable=self.maximumSizeVar)
    self.entryMaximumSize.config(width='5')

    self.entryMaximumSize.pack(expand='true', fill='both', side='left')
    self.frameMaximumSize.config(height='200', width='100')
    self.frameMaximumSize.pack(expand='true', fill='x', side='top')


    self.frameMaximumWidth = ttk.Frame(self.frameSequenceValuesRight)
    self.labelMaximumWidth = ttk.Label(self.frameMaximumWidth)
    self.labelMaximumWidth.config(anchor='e', padding='2', text='Maximum Width', width='25')
    self.labelMaximumWidth.pack(side='left')
    self.entryMaximumWidth = ttk.Spinbox(self.frameMaximumWidth, 
                                         from_=0, 
                                         to=float('inf'), 
                                         increment=1,
                                         textvariable=self.maximumWidthVar)
    self.entryMaximumWidth.config(width='5')
    self.entryMaximumWidth.pack(expand='true', fill='both', side='left')
    self.frameMaximumWidth.config(height='200', width='300')
    self.frameMaximumWidth.pack(expand='true', fill='x', side='top')

    self.frameAudioChannels = ttk.Frame(self.frameSequenceValuesLeft)
    self.labelAudioChannels = ttk.Label(self.frameAudioChannels)
    self.labelAudioChannels.config(anchor='e', padding='2', text='Audio Channels', width='25')
    self.labelAudioChannels.pack(side='left')
    self.entryAudioChannels = ttk.OptionMenu(self.frameAudioChannels,self.audioChannelsVar,self.audioChannelsVar.get(),*self.audioChannelsOptions)
    
    self.entryAudioChannels.pack(expand='true', fill='both', side='left')
    self.frameAudioChannels.config(height='200', width='300')
    self.frameAudioChannels.pack(expand='true', fill='x', side='top')


    self.frameSpeedChange = ttk.Frame(self.frameSequenceValuesRight)
    self.labelSpeedChange = ttk.Label(self.frameSpeedChange)
    self.labelSpeedChange.config(anchor='e', padding='2', text='Speed adjustment', width='25')
    self.labelSpeedChange.pack(side='left')
    self.entrySpeedChange = ttk.Spinbox(self.frameSpeedChange, 
                                         from_=0.5, 
                                         to=2.0, 
                                         increment=0.01,
                                         textvariable=self.speedAdjustmentVar)
    self.entrySpeedChange.config(width='5')
    self.entrySpeedChange.pack(expand='true', fill='both', side='left')
    self.frameSpeedChange.config(height='200', width='100')
    self.frameSpeedChange.pack(expand='true', fill='x', side='top')

    self.frameTransDuration = ttk.Frame(self.frameTransitionSettings)
    self.labelTransDuration = ttk.Label(self.frameTransDuration)
    self.labelTransDuration.config(anchor='e', padding='2', text='Transition Duration', width='25')
    self.labelTransDuration.pack(side='left')
    self.entryTransDuration = ttk.Spinbox(self.frameTransDuration, 
                                          from_=0, 
                                          to=float('inf'), 
                                          increment=0.1,
                                          textvariable=self.transDurationVar)
    self.entryTransDuration.config(width='5')

    self.entryTransDuration.pack(expand='true', fill='both', side='left')
    self.frameTransDuration.config(height='200', width='100')
    self.frameTransDuration.pack(expand='true', fill='x', side='top')

    self.frameTransStyle = ttk.Frame(self.frameTransitionSettings)
    self.labelTransStyle = ttk.Label(self.frameTransStyle)
    self.labelTransStyle.config(anchor='e', padding='2', text='Transition Style', width='25')
    self.labelTransStyle.pack(side='left')
    
    self.comboboxTransStyle = ttk.OptionMenu(self.frameTransStyle,self.transStyleVar,self.transStyleVar.get(),*self.transStyles)

    self.comboboxTransStyle.pack(expand='true', fill='x', side='right')

    self.frameTransStyle.config(height='200', width='100')
    self.frameTransStyle.pack(expand='true', fill='x', side='top')

    self.frameSequenceValues.config(height='200', padding='2', width='200')
    self.frameSequenceValues.pack(anchor='nw', expand='true', fill='both', ipady='3', side='left')


    self.labelframeSequenceFrame.config(height='200', text='Output Plan', width='200')
    self.labelframeSequenceFrame.pack(expand='true',fill='both', padx='5', pady='5', side='top')

    self.frameSequenceValuesLeft.pack(expand='true', fill='x', side='left')
    self.frameSequenceValuesRight.pack(expand='true', fill='x', side='left')




    self.labelframeEncodeProgress = ScrolledFrame(self.labelframeSequenceFrame,usemousewheel=True,scrolltype='vertical',)

    self.encoderProgress=[
      
    ]

    self.labelframeEncodeProgress.config(height='200', width='200')
    self.labelframeEncodeProgress.pack(anchor='ne', expand='true', fill='both', padx='5', pady='5', side='top')
    self.frameMergeSelection.config(height='200', width='200')
    self.frameMergeSelection.pack(expand='true',fill='both', side='top')
    self.mainwindow = self.frameMergeSelection
    self.encodeRequestId=0
    self.selectableVideos={}

  def clearSequence(self):
    for sv in self.sequencedClips:
      sv.destroy()
    self.sequencedClips=[]


  def valueChange(self,*args):
    try:
      self.automaticFileNamingValue = self.automaticFileNamingVar.get()
      if self.automaticFileNamingValue:
        self.entryFilenamePrefix.state(["disabled"]) 
        self.labelFilenamePrefix.state(["disabled"]) 
      else:
        self.entryFilenamePrefix.state(["!disabled"]) 
        self.labelFilenamePrefix.state(["!disabled"]) 

    except:
      pass

    try:
      self.filenamePrefixValue = self.filenamePrefixVar.get()
    except:
      pass
    try:
      self.outputFormatValue = self.outputFormatVar.get()
    except:
      pass
    
    try:
      self.frameSizeStrategyValue = self.frameSizeStrategyVar.get()
    except:
      pass

    try:
      self.maximumSizeValue = float(self.maximumSizeVar.get())
    except:
      pass

    try:
      self.maximumWidthValue = int(float(self.maximumWidthVar.get()))
    except:
      pass

    try:
      self.transDurationValue = float(self.transDurationVar.get())
    except:
      pass

    try:
      self.transStyleValue = self.transStyleVar.get()
    except:
      pass

    try:
      self.speedAdjustmentValue = self.speedAdjustmentVar.get()
    except:
      pass

    try:
      self.audioChannels = self.audioChannelsVar.get()
    except:
      pass

    self.updatedPredictedDuration()
  
  def encodeCurrent(self):
    if self.mergeStyleVar.get().split('-')[0].strip() == 'Sequence':
      encodeSequence = []
      self.encodeRequestId+=1
      for clip in self.sequencedClips:
        definition = (clip.rid,clip.filename,clip.s,clip.e,clip.filterexp)
        encodeSequence.append(definition)
      if len(encodeSequence)>0:
        options={
          'frameSizeStrategy':self.frameSizeStrategyValue,
          'maximumSize':self.maximumSizeValue,
          'maximumWidth':self.maximumWidthValue,
          'transDuration':self.transDurationValue,
          'transStyle':self.transStyleValue,
          'speedAdjustment':self.speedAdjustmentValue,
          'outputFormat':self.outputFormatValue,
          'audioChannels':self.audioChannels
        }

        encodeProgressWidget = EncodeProgress(self.labelframeEncodeProgress.innerframe,encodeRequestId=self.encodeRequestId)
        self.encoderProgress.append(encodeProgressWidget)

        outputPrefix = self.filenamePrefixValue
        if self.automaticFileNamingValue:
          try:
            outputPrefix = self.convertFilenameToBaseName(self.sequencedClips[0].filename)
          except:
            pass

        self.controller.encode(self.encodeRequestId,
                               'CONCAT',
                               encodeSequence,
                               options,
                               outputPrefix,
                               encodeProgressWidget.updateStatus) 
        self.labelframeEncodeProgress.reposition()
    if self.mergeStyleVar.get().split('-')[0].strip() == 'Individual Files':
      
      for clip in self.sequencedClips:
        encodeSequence = []
        self.encodeRequestId+=1
        definition = (clip.rid,clip.filename,clip.s,clip.e,clip.filterexp)
        encodeSequence.append(definition)
        if len(encodeSequence)>0:
          options={
            'frameSizeStrategy':self.frameSizeStrategyValue,
            'maximumSize':self.maximumSizeValue,
            'maximumWidth':self.maximumWidthValue,
            'transDuration':self.transDurationValue,
            'transStyle':self.transStyleValue,
            'speedAdjustment':self.speedAdjustmentValue,
            'outputFormat':self.outputFormatValue
          }

          encodeProgressWidget = EncodeProgress(self.labelframeEncodeProgress.innerframe,encodeRequestId=self.encodeRequestId)
          self.encoderProgress.append(encodeProgressWidget)
          outputPrefix = self.filenamePrefixValue
          if self.automaticFileNamingValue:
            outputPrefix = self.convertFilenameToBaseName(clip.filename)

          self.controller.encode(self.encodeRequestId,
                                 'CONCAT',
                                 encodeSequence,
                                 options.copy(),
                                 outputPrefix,
                                 encodeProgressWidget.updateStatus) 
          self.labelframeEncodeProgress.reposition()

  def mergeStyleChanged(self,*args):
    if self.mergeStyleVar.get().split('-')[0].strip()=='Grid':
      self.scrolledframeSequenceContainer.pack_forget()
      self.gridSequenceContainer.pack(expand='true', fill='both', padx='5', pady='5', side='top')
    else:
      self.gridSequenceContainer.pack_forget()
      self.scrolledframeSequenceContainer.pack(expand='true', fill='both', padx='0', pady='0', side='top')
      
  def updatedPredictedDuration(self):
    totalTime=0
    timeTrimmedByFade=0
    for sv in self.sequencedClips:
      totalTime+=(sv.e-sv.s)
      timeTrimmedByFade+=self.transDurationValue*2 

    self.labelSequenceSummary.config(text='Number of Subclips: {n} Total subclip duration {td}s Output Duration {tdext}s'.format(
                                     n=len(self.sequencedClips),
                                     td=totalTime,
                                     tdext=totalTime-timeTrimmedByFade
                                    ))
    if self.filenamePrefixVar.get().strip() in ('','Sequence'):
      for sv in self.sequencedClips[:1]:        
        self.filenamePrefixVar.set( self.convertFilenameToBaseName(sv.filename) )

  def convertFilenameToBaseName(self,filename):
    usableChars = string.ascii_letters+string.digits+'-_'
    basename = ''.join(x for x in os.path.basename(filename).rpartition('.')[0] if x in usableChars)
    return basename

  def setController(self,controller):
    self.controller=controller

  def previewFrameCallback(self,requestId,imageData):
    photoImage = tk.PhotoImage(data=imageData)
    for sv in self.selectableVideos.values():
      if sv.rid==requestId:
        sv.setPreviewImage(photoImage)
    for sv in self.sequencedClips:
      if sv.rid==requestId:
        sv.setPreviewImage(photoImage)

    self.scrolledframeInputCustContainer.reposition()
    self.scrolledframeSequenceContainer.reposition()

  def requestPreviewFrame(self,rid,filename,timestamp,filterexp):
    self.controller.requestPreviewFrame(rid,filename,timestamp,filterexp,(-1,100),self.previewFrameCallback)

  def addClipToSequence(self,clip):
    self.sequencedClips.append(
      SequencedVideoEntry(self.sequenceContainer,self,clip),
    )
    self.scrolledframeInputCustContainer.xview(mode='moveto',value=0)
    self.scrolledframeSequenceContainer.xview(mode='moveto',value=0)
    self.scrolledframeInputCustContainer._scrollBothNow()
    self.scrolledframeSequenceContainer._scrollBothNow()
    self.updatedPredictedDuration()

  def moveSequencedClip(self,clip,move):
    currentIndex = self.sequencedClips.index(clip)
    print([x.rid for x in self.sequencedClips])
    
    if 0<=currentIndex+move<len(self.sequencedClips):
      self.sequencedClips[currentIndex],self.sequencedClips[currentIndex+move] = self.sequencedClips[currentIndex+move],self.sequencedClips[currentIndex]
      for c in self.sequencedClips:
        c.pack_forget()
      for c in self.sequencedClips:
        c.pack(expand='false', fill='y', side='left')

    self.scrolledframeInputCustContainer.reposition()
    self.scrolledframeSequenceContainer.reposition()
    self.scrolledframeInputCustContainer._scrollBothNow()
    self.scrolledframeSequenceContainer._scrollBothNow()
      
  def removeSequencedClip(self,clip):
    currentIndex = self.sequencedClips.index(clip)
    removedClip = self.sequencedClips.pop(currentIndex)
    removedClip.pack_forget()
    removedClip.destroy()
    self.scrolledframeSequenceContainer.xview(mode='moveto',value=0)
    self.scrolledframeInputCustContainer._scrollBothNow()
    self.scrolledframeSequenceContainer._scrollBothNow()
    self.updatedPredictedDuration()

  def tabSwitched(self,tabName):
    if str(self) == tabName:
      unusedRids=set(self.selectableVideos.keys())
      for filename,rid,s,e,filterexp in sorted(self.controller.getFilteredClips(),key=lambda x:(x[0],x[2]) ):
        if rid in self.selectableVideos:
          unusedRids.remove(rid)
        if rid not in self.selectableVideos:
          self.selectableVideos[rid] = SelectableVideoEntry(self.selectableVideosContainer,self,filename,rid,s,e,filterexp)
        elif self.selectableVideos[rid].s != s or self.selectableVideos[rid].e != e or self.selectableVideos[rid].filterexp != filterexp:
           self.selectableVideos[rid].update(s,e,filterexp)

        for sv in self.sequencedClips:
          if sv.rid==rid:
            sv.update(s,e,filterexp)

      for rid in unusedRids:
        self.selectableVideos[rid].destroy()
        del self.selectableVideos[rid]
      self.updatedPredictedDuration()
    self.scrolledframeInputCustContainer.xview(mode='moveto',value=0)
    self.scrolledframeSequenceContainer.xview(mode='moveto',value=0)

    self.scrolledframeInputCustContainer._scrollBothNow()
    self.scrolledframeSequenceContainer._scrollBothNow()


  def addAllClipsInTimelineOrder(self):
    self.clearSequence()
    for clip in sorted(self.selectableVideos.values(),key=lambda x:(x.filename,x.s)):
      self.addClipToSequence(clip)



if __name__ == '__main__':
  import webmGenerator
