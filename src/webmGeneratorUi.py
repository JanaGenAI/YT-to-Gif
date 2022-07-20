#!/usr/bin/env python3

from tkinter import Tk,Menu,END,LEFT,PhotoImage,CENTER,BOTTOM
import tkinter.ttk as ttk
import webbrowser
from tkinter.filedialog import askopenfilename,asksaveasfilename
import sys
import logging
import urllib.request
import json
import threading
import time
import os
import psutil
import random
from math import sin,cos,floor
from .modalWindows import SubtitleExtractionModal, OptionsDialog, AdvancedDropModal
import colorsys
import numpy as np


RELEASE_NUMVER = 'v3.28.0'

class WebmGeneratorUi:

  def __init__(self,controller,master=None):

    bg='#181e37'
    lbg='#2f344b'
    fg='#69dbdb'

    self.controller = controller

    self.style = ttk.Style()
    self.style.theme_use('clam')
    self.style.configure('PlayerFrame.TFrame', 
                           background='#282828',
                           foreground=fg,
                           border=0,
                           highlightcolor=bg,
                           activehighlightcolor=bg,
                           relief='flat')

    darkMode = self.controller.globalOptions.get('darkMode',False)


    self.style.configure ("Bold.TLabel", font = ('Sans','10','bold'))


    self.style.configure ("warning.TLabel", font = ('Sans','10','bold'),color='red')

    
    self.style.configure("frameButtons.TFrame", 
                           border=0,relief='flat')

    self.style.configure("selectedCommandFrame.TFrame", 
                          background='#a8e4a0',lightcolor='#a8e4a0',darkcolor='#a8e4a0')
    self.style.configure("selectedCommandFrame.TLabel",background='#a8e4a0')

    self.style.configure("SelectedColumn.TFrame", 
                          background='blue',lightcolor='blue',darkcolor='blue')

    self.style.configure("Red.Horizontal.TProgressbar", 
                           background='red',lightcolor='red',darkcolor='red',border=0,relief='flat')
    self.style.configure("Blue.Horizontal.TProgressbar", 
                           background='blue',lightcolor='blue',darkcolor='blue',border=0,relief='flat')
    self.style.configure("Green.Horizontal.TProgressbar", 
                           background='green',lightcolor='green',darkcolor='green',border=0,relief='flat')

    self.style.configure("PlayerLabel.TLabel",background='#282828',padding=(0,-600))

    self.style.configure("filterDisabled.TButton",background='#e4a8a0',lightcolor='#e4a8a0',darkcolor='#e4a8a0')
    self.style.configure("filterDisabled.TFrame",background='#e4a8a0',lightcolor='#e4a8a0',darkcolor='#e4a8a0')
    self.style.configure("filterDisabled.TLabel",background='#e4a8a0',lightcolor='#e4a8a0',darkcolor='#e4a8a0')
    
    self.style.configure('small.TMenubutton',padding=0)

    self.style.configure('subtle.TEntry', highlightbackground="#282828", highlightcolor="#282828",border=0,borderwidth =0,highlightthickness=0, padding=(0,0),bordercolor='#282828',
                                          background='#282828',foreground='white',lightcolor='#282828',darkcolor='#282828',fieldbackground='#282828',relief='flat')
    
    self.style.map('subtle.TEntry',bordercolor=[('active', '#282828')])


    self.style.configure('smallVideoSub.TButton', padding=0,background='#282828',activebackground='#282828',activeforeground='#282828',foreground='#69bfdb',highlightcolor='#282828',
                                                  lightcolor='#282828',darkcolor='#282828',fieldbackground='#282828',highlightbackground='#69bfdb',relief='flat')

    self.style.map('smallVideoSub.TButton',background=[('active', '#69bfdb')], foreground=[('active', '#282828')] )

    self.style.configure('abortLoad.TButton', padding=0,background='#195467',activebackground='#195467',activeforeground='#195467',foreground='#69bfdb',highlightcolor='#195467',
                                                  lightcolor='#195467',darkcolor='#195467',fieldbackground='#195467',highlightbackground='#69bfdb',relief='flat')

    self.style.map('abortLoad.TButton',background=[('active', '#69bfdb')], foreground=[('active', '#195467')] )



    self.style.configure('small.TButton', padding=0)
    self.style.configure('smallSlim.TButton',padding=(-10,0))
    self.style.configure('smallMid.TButton',padding=(-5,0))
    self.style.configure('smallOnechar.TButton', padding=(-28,0))
    self.style.configure('smallOnecharenabled.TButton', padding=(-28,0),background='green',foreground='white',lightcolor='green',darkcolor='green')

    
    self.style.configure('smallTallSlim.TButton', padding=(-8,10))
    self.style.configure('smallTallSlimMid.TButton', padding=(-10,10))
    
    self.style.configure('smallTall.TButton', padding=(0,10))
    self.style.configure('smallBlue.TButton', padding=0,background='blue',foreground='white',lightcolor='blue',darkcolor='blue',border=0)
    self.style.configure('smallextra.TButton', padding=-20)
    self.style.configure('Horizontal.TProgressbar', thickness=20)

    self.style.configure('PSNRTerrible.TLabel',foreground='red')
    self.style.configure('PSNRExcellent.TLabel',foreground='green')
    self.style.configure('PSNRGood.TLabel',foreground='green')
    self.style.configure('PSNRFair.TLabel',foreground='dark orange')
    self.style.configure('PSNRPoor.TLabel',foreground='red')
    
    self.style.configure('boringMode.TLabel',foreground='white',background='black',font = 'TkFixedFont' )

    self.style.configure ("verticalPack.TLabel",padding=(2,-2))
    self.style.configure ("verticalPack.TSpinbox",padding=(2,-8))
    self.style.configure ("disabledListing.TFrame",color='#000',borderwidth=0,foreground='#000',background='#000',bordercolor='#000',highlightbackground='#000')

    self.style.configure ("dropMessage.TLabel",background='#282828',activebackground='#282828',activeforeground='#282828',foreground='#69bfdb',highlightcolor='#282828')

    if darkMode:
      #self.style.theme_use('black')
      self.style.configure (".",color='white',foreground='white',background='#0f0f0f',bordercolor='#000000',highlightbackground='#0f0f0f',troughcolor='#0f0f0f',border=0)
      self.style.map('.',background=[('active', '#69bfdb'),('disabled', '#060B0C')], foreground=[('active', '#282828'),('disabled', '#4c4c4c')] )


      self.style.configure ("TMenu",color='white',foreground='white',background='#0f0f0f',bordercolor='#000000',highlightbackground='#0f0f0f',troughcolor='#0f0f0f')
      

      self.style.configure ("TToolbutton",color='white',foreground='white',background='#1f1f1f',activeforeground='white',activebackground='#1f1f1f',bordercolor='#1f1f1f',lightcolor='white',darkcolor='#1f1f1f',highlightbackground='#1f1f1f',highlightcolor='#282828')
      self.style.configure ("TToolbutton.button",color='white',foreground='white',background='#1f1f1f',activeforeground='white',activebackground='#1f1f1f',bordercolor='#1f1f1f',lightcolor='white',darkcolor='#1f1f1f',highlightbackground='#1f1f1f',highlightcolor='#282828')


      self.style.map('TToolbutton',background=[('active', '#1f1f1f')], foreground=[('active', '#282828')] )
      self.style.map('TRadiobutton',background=[('active', '#1f1f1f')], foreground=[('active', '#282828')] )

      self.style.map('TToolbutton.button',background=[('active', '#69bfdb')], foreground=[('active', '#282828')] )


      self.style.configure ("TProgressbar.trough",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f',highlightbackground='#0f0f0f')
      
      self.style.configure ("TMenu",color='white',foreground='white',background='#0f0f0f')
      self.style.configure ("TNotebook",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f',highlightbackground='#0f0f0f')
      
      self.style.configure ("TNotebook.Tab",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f',highlightbackground='#0f0f0f',lightcolor='#0f0f0f')
      self.style.map("TNotebook.Tab",
                            background=[("selected", '#2f2f2f'),("disabled", '#0f0f0f')], foreground=[("selected", 'white'),("disabled", '#0f0f0f')]
                     )

      self.style.configure ("TNotebook.Tab.Label",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f',highlightbackground='#0f0f0f',lightcolor='#0f0f0f')

      self.style.configure ("TNotebook.label",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f',highlightbackground='#0f0f0f',lightcolor='#0f0f0f')

      self.style.configure ("TNotebook.Pane",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f',highlightbackground='#0f0f0f')

      self.style.configure ("TLabel",color='white',foreground='white',background='#0f0f0f')
      self.style.configure ("TFrame",color='white',foreground='white',background='#0f0f0f',bordercolor='#1f1f1f',highlightbackground='#0f0f0f')




      self.style.configure ("TLabelframe",color='white',foreground='white',background='#0f0f0f',bordercolor='#1f1f1f',highlightbackground='#0f0f0f',relief='flat')

      self.style.configure ("TLabelframe.Label",color='white',foreground='white',background='#0f0f0f',bordercolor='#1f1f1f')

      self.style.configure ("TLabelframe.Frame",color='white',foreground='white',background='#0f0f0f',bordercolor='#1f1f1f',highlightbackground='#0f0f0f')
      
      self.style.configure ("TButton",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f',activebackground='#282828',activeforeground='#282828',highlightcolor='#282828',lightcolor='#282828',darkcolor='#282828',fieldbackground='#282828',highlightbackground='#69bfdb')
      self.style.map('TButton',background=[('active', '#69bfdb')], foreground=[('active', '#282828')] )

      self.style.configure ("TCheckbutton",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f')
      self.style.configure ("TCheckbutton.Label",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f')
      self.style.configure ("TEntry",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f')

      self.style.configure ("TMenubutton",color='white',foreground='white',background='#0f0f0f',bordercolor='#0f0f0f')

      self.style.configure ("TSpinbox",color='white',foreground='white',fieldbackground='#1f1f1f',background='#0f0f0f',bordercolor='darkgrey',buttonbackground='white')
      self.style.configure ("TEntry",color='white',foreground='white',fieldbackground='#1f1f1f',background='#0f0f0f',bordercolor='darkgrey')
      self.style.configure ("TCombobox",color='white',foreground='white',fieldbackground='#0f0f0f',background='#0f0f0f',bordercolor='#0f0f0f')



    self.panes=[]
    self.master=master

    self.master.title('WebmGenerator')
    self.master.minsize(1024,720)

    self.iconLookup = {}

    try:
      for iconFileName in os.listdir(os.path.join("resources","icons")):
        key = iconFileName[:-4]
        try:
          self.iconLookup[key] = PhotoImage(file=os.path.join("resources","icons","{}.png".format(key)))
        except Exception as e:
          print(e)
    except Exception as e:
      print(e)

    try:
      self.master.state('zoomed')
    except Exception as e:
      logging.error('Zoomed state not avaliable, possibly on some linux distros?',exc_info=e)
      try:
        m = self.master.maxsize()
        self.master.geometry('{}x{}+0+0'.format(*m))
      except Exception as e:
        logging.error('self.master.geometryException',exc_info=e)

    self.menubar = Menu(self.master)
    
    self.filemenu = Menu(self.menubar, tearoff=0, postcommand=self.updateDownloadCounts)
    self.filemenu.add_command(label="New Project",  command=self.newProject   ,image=self.iconLookup.get('icons8-file-24'), compound=LEFT)
   
    self.filemenu.add_command(label="Open Project", command=self.openProject  ,image=self.iconLookup.get('icons8-file-24'), compound=LEFT)
    self.filemenu.add_command(label="Save Project", command=self.saveProject  ,image=self.iconLookup.get('icons8-file-24'), compound=LEFT)
    self.filemenu.add_separator()

    if self.controller.autoSaveExists():
      self.filemenu.add_command(label="Load last autosave", command=self.controller.loadAutoSave)
    else:
      self.filemenu.add_command(label="Load last autosave", command=self.controller.loadAutoSave, state='disabled')

    self.filemenu.add_separator()
    self.filemenu.add_command(label="Load Video from File", command=self.loadVideoFiles,image=self.iconLookup.get('file-video-solid'), compound=LEFT)
    self.filemenu.add_command(label="Load Video from youtube-dlp supported url", command=self.loadVideoYTdl,image=self.iconLookup.get('youtube-brands'), compound=LEFT)
    self.filemenu.add_command(label="Load Image as static video", command=self.loadImageFile,image=self.iconLookup.get('file-image-solid'), compound=LEFT)
    self.filemenu.add_separator()
    
    if hasattr(os.sys, 'winver'):
      self.filemenu.add_command(label="Start screen capture", command=self.startScreencap)
    else:
      self.filemenu.add_command(label="Start screen capture", command=self.startScreencap, state='disabled')

    self.filemenu.add_separator()
    self.filemenu.add_command(label="Extract .srt subtitles from video file", command=self.extractSubs)
    self.filemenu.add_separator()
    self.filemenu.add_command(label="Toggle fullscreen", command=self.toggleFullscreen)
    self.filemenu.add_separator()
    self.filemenu.add_command(label="Watch clipboard and automatically add urls", command=self.loadClipboardUrls)
    self.filemenu.add_separator()
    self.filemenu.add_command(label="Cancel current youtube-dlp download", command=self.cancelCurrentYoutubeDl)
    self.filemenu.add_command(label="Update youtube-dlp", command=self.updateYoutubeDl)
    self.filemenu.add_separator()
    self.filemenu.add_command(label="Delete all downloaded files", command=self.clearDownloadedfiles)
    self.clearTempMenuIndex = self.filemenu.index(END) 
    self.filemenu.entryconfigure(self.clearTempMenuIndex, label="Delete all downloaded files")
    self.filemenu.add_separator()
    self.filemenu.add_command(label="Preferences", command=self.updatePreferences)
    self.filemenu.add_separator()
    self.filemenu.add_command(label="Exit", command=self.exitProject)
    self.menubar.add_cascade(label="File",  menu=self.filemenu)

    self.showStreamPreviews = False

    self.commandmenu = Menu(self.menubar, tearoff=0)
    


    self.commandSplitmenu = Menu(self.menubar, tearoff=0)
    self.commandSplitmenu.add_command(label="Split clip into n equal Subclips",      command=self.splitClipIntoNEqualSections)
    self.commandSplitmenu.add_command(label="Split clip into subclips of n seconds", command=self.splitClipIntoSectionsOfLengthN)
    self.commandSplitmenu.add_separator()
    self.commandSplitmenu.add_command(label="Fill gaps between subclips", command=self.fillGapsBetweenSublcips)

    self.commandmenu.add_cascade(label="Split clip", menu=self.commandSplitmenu)
    

    self.commandDetectormenu = Menu(self.menubar, tearoff=0)
    self.commandDetectormenu.add_command(label="Run scene change detection and add Marks", command=self.controller.runSceneChangeDetection)
    self.commandDetectormenu.add_command(label="Run scene change detection and add SubClips", command=self.controller.runSceneChangeDetectionCuts)
    self.commandDetectormenu.add_separator()
    self.commandDetectormenu.add_command(label="Run search for any perfect loops.", command=self.controller.runFullLoopSearch)
    self.commandDetectormenu.add_separator()
    self.commandDetectormenu.add_command(label="Run representative scene centeres detection and add SubClips", state='disabled', command=self.controller.runSceneCentreDetectionCuts)
    self.commandDetectormenu.add_separator()
    self.commandDetectormenu.add_command(label="Run audio loudness threshold detection", command=self.scanAndAddLoudSections)
    self.commandDetectormenu.add_command(label="Run voice activity detection", command=self.controller.runVoiceActivityDetection)
    
    self.commandmenu.add_cascade(label="Content detectors", menu=self.commandDetectormenu)


    self.commandspectramenu = Menu(self.menubar, tearoff=0)

    self.commandspectramenu.add_command(label="Generate general audio spectra", command=self.generateSoundWaveBackgrounds)
    
    voiceModelEnabled = 'normal' if os.path.exists(os.path.join('resources','voiceModel','model.rnnn')) else 'disabled'
    self.commandspectramenu.add_command(label="Generate voice spectra", command=self.generateSoundVoiceBackgrounds,state=voiceModelEnabled)

    speechModelEnabled = 'normal' if os.path.exists(os.path.join('resources','speechModel','model.rnnn')) else 'disabled'
    self.commandspectramenu.add_command(label="Generate speech spectra", command=self.generateSoundSpeechBackgrounds,state=speechModelEnabled)
    
    self.commandmenu.add_cascade(label="Audio spectra", menu=self.commandspectramenu)

    self.commandmenu.add_separator()
    self.commandmenu.add_command(label="Clear all SubClips on current clip", command=self.clearAllSubclipsOnCurrentClip)
    self.commandmenu.add_command(label="Clear all Interest Marks on current clip", command=self.clearAllInterestMarksOnCurrentClip)
    self.commandmenu.add_separator()
    self.commandmenu.add_command(label="Screenshot to {}".format(self.controller.tempFolder), command=self.takeScreenshot)
    self.commandmenu.add_separator()
    self.commandmenu.add_command(label="Add subclip by text range", command=self.addSubclipByTextRange)
    self.menubar.add_cascade(label="Commands", menu=self.commandmenu)

    self.helpmenu = Menu(self.menubar, tearoff=0)
    self.helpmenu.add_command(label="Open Check for new version", command=self.versioncheck)
    self.helpmenu.add_command(label="Open Documentation", command=self.openDocs)
    self.menubar.add_cascade(label="Help", menu=self.helpmenu)

    self.commandmenu.add_separator()

    self.commandmenu.add_command(label="Show sequence editor",command=self.showSequencePreview)
    self.commandmenu.add_command(label="Show audio slice planner",command=self.showSlicePlanner,state='disabled')


    self.menubar.add_command(label="Checking free space...",state='disabled')
    self.freeSpaceIndex = self.commandmenu.index(END) 


    def checkFreeSpaceWorker():
      try:
        while 1:
          drive,_ = os.path.splitdrive( os.path.abspath( self.controller.globalOptions.get('tempFolder') ) )
          usage = psutil.disk_usage('/')
          self.menubar.entryconfigure(self.freeSpaceIndex, label="{drive} {percent:.1f}% free ({freespace}) ".format(drive=drive,freespace=self.sizeof_fmt(usage.free),percent=100-usage.percent))
          time.sleep(60)
      except Exception as e:
        print(e)

    self.freeSpaceThread = threading.Thread(target=checkFreeSpaceWorker,daemon=True)
    self.freeSpaceThread.start()


    self.master.config(menu=self.menubar)
    
    self.notebook = ttk.Notebook(self.master)
    
    self.statusFrame = ttk.Frame(self.master,height='20')

    self.statusCancel = ttk.Button(self.statusFrame,text='Stop',state='disabled',style='smallextra.TButton',command=self.cancelAction)
    self.statusCancel.pack(expand=False, fill='y',side='left')    

    self.statusSplit = ttk.Button(self.statusFrame,text='Split',state='disabled',style='smallextra.TButton',command=self.splitStream)
    self.statusSplit.pack(expand=False, fill='y',side='left')   

    self.statusPreview = ttk.Button(self.statusFrame,text='Preview',state='disabled',style='small.TButton',command=self.togglePreview)
    self.statusPreview.pack(expand=False, fill='y',side='left')    

    self.statusLabel = ttk.Label(self.statusFrame,text='Idle no background task')
    self.statusLabel.pack(expand=True, fill='both',side='left')

    self.statusProgress = ttk.Progressbar(self.statusFrame)
    self.statusProgress['value'] = 0
    self.statusProgress.pack(expand=1,side='right', fill='x')
    self.statusProgress.config(style="Green.Horizontal.TProgressbar")

    self.fullscreen = self.controller.globalOptions.get('startFullscreen',False)
    try:
      self.master.attributes("-fullscreen", self.fullscreen)
    except Exception as e:
      print('root -fullscreen attribute set Exception',e)

    self.statusFrame.pack(expand=0, fill='x',side='bottom')



    self.notebook.pack(expand=1, fill='both')
    self.notebook.bind('<<NotebookTabChanged>>',self._notebokSwitched)

    self.boringw=1000
    self.boringh=600
    self.boringscale=1
    self.boringSteps=1

    self.boringImageHeader = bytes("P6\n{} {}\n255\n".format(self.boringw,self.boringh),encoding='ascii')
    self.boringImageArray  = bytearray([0]*(self.boringw * self.boringh *3))
    self.boringImage       = PhotoImage(data= self.boringImageHeader+bytes(self.boringImageArray))
    self.boringImageScaled = self.boringImage.zoom(self.boringscale,self.boringscale)

    self.boringText = ttk.Label(self.master,text='',style='boringMode.TLabel',cursor='X_cursor',compound=BOTTOM,justify=CENTER,anchor=CENTER,image=self.boringImageScaled)
    self.boringText.bind('<Button-1>',self.resetBoringText)
    self.boringText.bind('<MouseWheel>',self.adjustToneMap)
    self.boringMode=False
    
    self.boringFloats   = [[0]*self.boringw for _ in range(self.boringh)]
    self.boringVelocity = [[0]*self.boringw for _ in range(self.boringh)]

    self.algorithms = {
      'Clifford Attractor':(        lambda x,y,a,b,c,d:sin(a*y)+c*cos(a*x),       lambda x,y,a,b,c,d:sin(b*x)+d*cos(b*y)  ,8,8),
      'Jason Rampe 1':(             lambda x,y,a,b,c,d:cos(y*b)+c*sin(x*b),       lambda x,y,a,b,c,d:cos(x*a)+d*sin(y*a)  ,8,8),
      'Jason Rampe 2':(             lambda x,y,a,b,c,d:cos(y*b)+c*cos(x*b),       lambda x,y,a,b,c,d:cos(x*a)+d*cos(y*a)  ,8,8),
      'Jason Rampe 3':(             lambda x,y,a,b,c,d:sin(y*b)+c*cos(x*b),       lambda x,y,a,b,c,d:cos(x*a)+d*sin(y*a)  ,8,8),
      'Johnny Svensson Attractor':( lambda x,y,a,b,c,d:d*sin(x*a)-sin(y*b),       lambda x,y,a,b,c,d:c*cos(x*a)+cos(y*b)  ,8,8),
      'Peter DeJong Attractor':(    lambda x,y,a,b,c,d:sin(y*a)-cos(x*b),         lambda x,y,a,b,c,d:sin(x*c)-cos(y*d)    ,6,6),

    }

    self.algo='Peter DeJong Attractor'

    self.boringi=0

    self.boringx = 0.1
    self.boringy = 0.1

    self.lastboringx = 0.1
    self.lastboringx = 0.1

    self.boringa = 0.0
    self.boringb = 0.0
    self.boringc = 0.0
    self.boringd = 0.0
    self.tonemapScale=1000

    self.boringFloats = np.array([[0]*self.boringw for _ in range(self.boringh)])
    self.boringMax = 0.0

    self.versioncheckResultIndex=None

  def getFileLoadOptions(self):
    data = {}
    self.fileModal = AdvancedDropModal(self.master,dataDestination=data)

    self.master.wait_window(self.fileModal)
    print(data)
    return data

  def setLoadLabel(self,text):
    try:
      self.dropLabel.configure(text=text,font= ("Helvetica 20"))
      self.master.update()
      self.master.update_idletasks()
    except Exception as e:
      print(e) 

  def showDrop(self):
    self.dropLabel = ttk.Label(self.master,style="dropMessage.TLabel",text='Drop files to load\nHold CTRL for advanced options.',justify='center',anchor='center',font= ("Helvetica 50"))
    
    self.dropLabel.place(bordermode ='inside',relheight=1,relwidth=1,x=0,y=0)

    self.dropAbort = ttk.Button(self.master,text='Cancel Load',command=self.abortLoad,style="abortLoad.TButton")
    
    self.dropAbort.place(bordermode ='inside',relheight=0.1,relwidth=1,x=0,rely=0.9)
    
  def hideDrop(self):
    try:
      self.dropLabel.place_forget()
    except Exception as e:
      print(e)

    try:
      self.dropAbort.place_forget()
    except Exception as e:
      print(e)  

  def abortLoad(self):
    self.controller.abortCurrentLoad()

  def showSlicePlanner(self):
    self.controller.showSlicePlanner()

  def showSequencePreview(self):
    self.controller.showSequencePreview()


  def adjustToneMap(self,e):
    ctrl  = e and ((e.state & 0x4) != 0)
    if ctrl:
      alist = sorted(self.algorithms.keys())
      algind = (alist.index(self.algo)+1)%len(alist)
      self.algo = alist[algind]
      self.resetBoringText()
    else:
      if e.delta>0:
        self.tonemapScale -= 125
      else:
        self.tonemapScale += 125
      self.tonemapScale = max(0,self.tonemapScale)

  def regenerateBoringText(self):

    E_map = np.empty_like(self.boringFloats,dtype='float32')
    E_min = self.boringFloats.min()
    E_max = self.boringFloats.max()
    E_map = ((self.boringFloats - E_min) / (E_max - E_min))*self.tonemapScale

    tonemap = np.clip(E_map, 0.0, 255.0).astype('uint8')
    tonemap = bytearray(np.dstack([tonemap,tonemap,tonemap]).flatten().tobytes())

    if tonemap == self.boringImageArray:
      self.boringi+=1
    else:
      self.boringi=0

    boringTextContent=''
    boringTextContent += '\nBoring "{}" Strange Attractor Render\n'.format(self.algo)
    boringTextContent += 'CLICK TO RANDOMISE ATTRACTOR, SCROLL TO ADJUST WHITEPOINT, CTRL-SCROLL to switch algorithms\n'
    boringTextContent += 'PRESS CTRL-N TO RESET WMG - CHANGES WILL BE LOST\n'
    boringTextContent += 'PRESS CTRL-B TO RESTORE WMG - WILL RESTORE LAST WORKING SESSION\n'
    boringTextContent += 'x:{:+0.5f} y:{:+0.4f} frozenSteps:{:03d} whitepoint:{}\na:{:0.5f} b:{:0.5f} c:{:0.5f} d:{:0.5f}\n'.format(self.boringx,self.boringy,self.boringi,self.tonemapScale,self.boringa,self.boringb,self.boringc,self.boringd)


    if self.boringi>10:
      self.resetBoringText()

    self.boringImageArray = tonemap

    self.boringImage       = PhotoImage(data= self.boringImageHeader+bytes(self.boringImageArray))
    #self.boringImageScaled = self.boringImage.zoom(self.boringscale,self.boringscale)
    self.boringText.configure(image=self.boringImage)


    self.boringSteps = min(self.boringSteps+10,1530)
    
    algx,algy,xscale,yscale = self.algorithms[self.algo]

    for i in range(self.boringSteps):
      
      xnew = algx(self.boringx,self.boringy,self.boringa,self.boringb,self.boringc,self.boringd)
      ynew = algy(self.boringx,self.boringy,self.boringa,self.boringb,self.boringc,self.boringd)


      self.boringx = xnew
      self.boringy = ynew

      xnew = int((self.boringw//2)+ (xnew*(self.boringw/xscale)))
      ynew = int((self.boringh//2)+ (ynew*(self.boringh/yscale)))

      if 0<xnew<self.boringw and 0<ynew<self.boringh: 
        newVal = self.boringFloats[ynew][xnew]+1
        self.boringMax = max(self.boringMax,newVal)
        self.boringFloats[ynew][xnew] = newVal
      else:
        self.boringi+=1


      self.lastboringx = xnew
      self.lastboringx = ynew



    self.boringText.configure(text=boringTextContent)
    if self.boringMode:
      self.master.after(100, self.regenerateBoringText)

  def resetBoringText(self,e=None):
    self.boringi=0
    self.boringx=0.1
    self.boringy=0.1
    self.boringa=random.uniform(-3,3)
    self.boringb=random.uniform(-3,3)
    self.boringc=random.uniform(-3,3)
    self.boringd=random.uniform(-3,3)  
    self.boringFloats = np.array([[0]*self.boringw for _ in range(self.boringh)])
    self.boringImageArray  = bytearray([0]*(self.boringw * self.boringh *3))
    self.boringMax = 0.0
    self.boringSteps = 1


  def updatePreferences(self):
    changedOptions = {}
    optionsScreen = OptionsDialog(optionsDict=self.controller.globalOptions.copy(), changedProperties=changedOptions ,changeCallback=self.controller.updateGlobalOptions)
    optionsScreen.mainloop()

  def extractSubs(self):
    subsScreen = SubtitleExtractionModal()
    subsScreen.mainloop()

  def sizeof_fmt(self,num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

  def versioncheck(self):
    try:
      if self.versioncheckResultIndex is not None:
        self.menubar.delete(self.versioncheckResultIndex)
        self.versioncheckResultIndex=None
      req = urllib.request.Request('https://api.github.com/repos/dfaker/WebmGenerator/releases')
      req.add_header('Referer', 'http://localhost/dfaker/WebmGenerator/updateCheck')
      with urllib.request.urlopen(req) as f:
        data = json.loads(f.read())
        leadTag = data[0]['tag_name']
        if leadTag != RELEASE_NUMVER:
          self.menubar.add_command(label="New Version {} avaliable!".format(leadTag), command=self.gotoReleasesPage, background='red',activeforeground='red', foreground='red')
          self.versioncheckResultIndex = self.menubar.index(END) 
        else:
          self.menubar.add_command(label="You're on the most recent version {}".format(leadTag), command=self.gotoReleasesPage, background='red',activeforeground='red', foreground='red')
          self.versioncheckResultIndex = self.menubar.index(END)
    except Exception as e:
      logging.error('versioncheck',exc_info=e)
      self.menubar.add_command(label="Version check failed!", command=self.gotoReleasesPage, background='red',activeforeground='red', foreground='red')
      self.versioncheckResultIndex = self.menubar.index(END)

  def updateDownloadCounts(self):
    count,sz = self.controller.getDownloadFilesCountAndsize()
    if count==0:
      self.filemenu.entryconfigure(self.clearTempMenuIndex, label="Delete all downloaded files (Downloads empty)")
      self.filemenu.entryconfigure(self.clearTempMenuIndex, state='disabled')
    else:
      self.filemenu.entryconfigure(self.clearTempMenuIndex, label="Delete all downloaded files ({} files {})".format(count,self.sizeof_fmt(sz)))
      self.filemenu.entryconfigure(self.clearTempMenuIndex, state='normal')

  def toggleFullscreen(self):
    self.fullscreen = not self.fullscreen
    self.master.attributes("-fullscreen", self.fullscreen)

  def takeScreenshot(self):
    selectedTab = self.notebook.select()
    self.controller.takeScreenshotToFile(selectedTab)

  def fillGapsBetweenSublcips(self):
    self.controller.fillGapsBetweenSublcips()

  def splitClipIntoNEqualSections(self):
    self.controller.splitClipIntoNEqualSections()

  def scanAndAddLoudSections(self):
    self.controller.scanAndAddLoudSections()

  def splitClipIntoSectionsOfLengthN(self):
    self.controller.splitClipIntoSectionsOfLengthN()

  def generateSoundVoiceBackgrounds(self):
    self.controller.generateSoundWaveBackgrounds(style='VOICE')

  def generateSoundSpeechBackgrounds(self):
    self.controller.generateSoundWaveBackgrounds(style='SPEECH')

  def generateSoundWaveBackgrounds(self):
    self.controller.generateSoundWaveBackgrounds(style='GENERAL')

  def clearAllSubclipsOnCurrentClip(self):
    self.controller.clearAllSubclipsOnCurrentClip()

  def clearAllInterestMarksOnCurrentClip(self):
    self.controller.clearAllInterestMarksOnCurrentClip()

  def addSubclipByTextRange(self):
    self.controller.addSubclipByTextRange()

  def gotoReleasesPage(self):
    webbrowser.open('https://github.com/dfaker/WebmGenerator/releases', new=2)

  def loadVideoFiles(self):
    self.controller.cutselectionUi.loadVideoFiles()

  def loadClipboardUrls(self):
    self.controller.cutselectionUi.loadClipboardUrls()

  def cancelCurrentYoutubeDl(self):
    self.controller.cancelCurrentYoutubeDl()

  def clearDownloadedfiles(self):
    self.controller.clearDownloadedfiles()
    self.updateDownloadCounts()

  def loadVideoYTdl(self):
    self.controller.cutselectionUi.loadVideoYTdl()

  def startScreencap(self):
    self.controller.cutselectionUi.startScreencap()

  def loadImageFile(self):
    self.controller.cutselectionUi.loadImageFile()

  def switchTab(self,ind):
    self.notebook.select(ind)

  def newProject(self):
    self.controller.newProject()
    self.notebook.select(0)
    self.statusLabel['text']='Idle no background task'
    self.statusProgress['value'] = 0


  def openProject(self):
    filename = askopenfilename(title='Open WebmGenerator Project',filetypes=[('WebmGenerator Project','*.webgproj')])
    self.controller.openProject(filename)

  def saveProject(self):
    filename = asksaveasfilename(title='Save WebmGenerator Project',filetypes=[('WebmGenerator Project','*.webgproj')])
    if filename is not None:
      if not filename.endswith('.webgproj'):
        filename = filename+'.webgproj'
      self.controller.saveProject(filename)

  def splitStream(self):
    self.controller.splitStream()

  def togglePreview(self):
    self.showStreamPreviews = not self.showStreamPreviews
    self.controller.toggleYTPreview(self.showStreamPreviews)
    
    if self.showStreamPreviews:
      self.controller.cutselectionUi.updateProgressPreview("P5\n220 130\n255\n" + ("127" * 220 * 130))
    else:
      self.controller.cutselectionUi.updateProgressPreview(None)

  def updateYoutubeDl(self):
    self.controller.updateYoutubeDl()

  def exitProject(self):
    sys.exit()

  def openDocs(self):
    webbrowser.open('https://github.com/dfaker/WebmGenerator/blob/master/README.md', new=2)

  def cancelAction(self):
    self.controller.cancelCurrentYoutubeDl()
    self.statusCancel['state']='disabled'

  def updateGlobalStatus(self,message,percentage,progressPreview=None):

    if progressPreview is not None and self.showStreamPreviews:
      self.controller.cutselectionUi.updateProgressPreview(progressPreview)
    elif message is not None and 'streaming' not in message:
      self.controller.cutselectionUi.updateProgressPreview(None)

    if message is not None:
      if 'streaming' in message:
        self.statusPreview['state']='enabled'
        self.statusSplit['state']='enabled'
      else:
        self.statusPreview['state']='disabled'
        self.statusSplit['state']='disabled'
        
      if 'Download progress' in message or 'streaming' in message or 'Running loop scan' in message:
        self.statusCancel['state']='enabled'
      else:
        self.statusCancel['state']='disabled'
      self.statusLabel['text']=message

    if percentage is not None:
      if percentage < 0:
        self.statusProgress['mode']='indeterminate'
        self.statusProgress.start()
      else:
        self.statusProgress.stop()
        self.statusProgress['mode']='determinate'
        self.statusProgress['value'] = max(0,min(100,percentage*100))

  def addPane(self,pane,name):
    self.panes.append(pane)
    self.notebook.add(pane, text=name)
  
  def _notebokSwitched(self,e):
    selectedTab = self.notebook.select()
    for pane in self.panes:
      pane.tabSwitched(selectedTab)

  def run(self):
    self.master.mainloop()
  
  def close_ui(self):
    self.controller.cancelCurrentYoutubeDl()
    try:
      self.master.destroy()
      del self.master
      logging.debug('webmGeneratorUi destroyed')
    except:
      pass

  def toggleBoringMode(self):
    self.boringMode = not self.boringMode
    
    if(self.boringMode):
      self.controller.cutselectionController.setVolume(0)
      self.controller.filterSelectionController.setVolume(0)
      self.notebook.pack_forget()
      self.statusFrame.pack_forget()
      self.boringText.pack(expand=True, fill='both',side='top')
      self.master.title('Boring Strange Attractor Renderer')
      self.master.config(menu='')
      self.resetBoringText()
      self.regenerateBoringText()
    else:
      self.boringText.pack_forget()
      self.notebook.pack(expand=1, fill='both')
      self.statusFrame.pack(expand=0, fill='x',side='bottom')
      self.master.title('WebmGenerator')
      self.master.config(menu=self.menubar)

if __name__ == '__main__':
  import webmGenerator