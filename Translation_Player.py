﻿#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore  # PyQt4
#from yomi_base import japanese
#from yomi_base.preference_data import Preferences

from yomi_base.minireader import MiniReader
import sys, pysrt, pickle
from os import listdir
from os.path import isfile, join
from PySide.phonon import Phonon

class cSubsList(QtGui.QListWidget):
    def __init__(self):
        super(cSubsList, self).__init__()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            if qp.player.state() == Phonon.PausedState:
                qp.player.play()
            else:
                qp.player.pause()

    def loadSubs(self, file):
        self.subs = pysrt.open(file, encoding='utf-8')

        self.clear()
        g = 0
        for i in self.subs:
            self.insertItem(g, i.text)
            g = g + 1

        for i in xrange(self.count()):
            self.item(i).setFont(QtGui.QFont('Meiryo', 16))  # MS Mincho

        # back up 1:33
        # self.subs.shift(seconds=-30) # Move all subs 2 seconds earlier
        #self.subs.shift(minutes=-1)  # Move all subs 1 minutes later
        #self.subs.shift(milliseconds=-500 )

        i = self.subs[0]
        self.currentSubStart = i.start.ordinal
        self.currentSubEnd = i.end.ordinal
        self.currentRow = 0
        i = self.subs[1]
        self.nextSubStart = i.start.ordinal
        self.nextSubEnd = i.end.ordinal

    def gotoLine(self):
        self.item(self.currentRow).setBackground(QtGui.QColor('white'))

        g = self.currentIndex()
        self.currentRow = g.row()
        i = self.subs[g.row()]
        self.currentSubStart = i.start.ordinal
        self.currentSubEnd = i.end.ordinal
        qp.player.seek(self.currentSubStart)
        i = self.subs[g.row() + 1]
        self.nextSubStart = i.start.ordinal
        self.nextSubEnd = i.end.ordinal
        # self.lcdTimer.display("11:00")
        lookupLine.setPlainText(self.subs[g.row()].text)
        # lookupLine.appendPlainText(self.subs[g.row()].text)
        #self.textEditor.append(self.subs[g.row()].text)
        LineDefs.lookup(self.currentRow)

class QPlayer(QtGui.QWidget):
    def __init__(self):
        # QtGui.QWidget.__init__(self)
        super(QPlayer, self).__init__()
        self.audioOuptut = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.player = Phonon.MediaObject(self)
        Phonon.createPath(self.player, self.audioOuptut)

        # subtitles not working..
        #self.mController = Phonon.MediaController(self.player)
        #self.mController.setAutoplayTitles(True)

        self.videoWidget = cVideoWidget()
        #self.videoWidget = Phonon.VideoWidget(self)
        Phonon.createPath(self.player, self.videoWidget)

        self.player.setTickInterval(500)  #1000
        self.connect(self.player, QtCore.SIGNAL("tick(qint64)"), self.tick)

        self.seekSlider = Phonon.SeekSlider(self.player, self)
        self.volumeSlider = Phonon.VolumeSlider(self.audioOuptut, self)
        #self.volumeSlider.setMaximumVolume(0.35)

        self.buildGUI()
        self.setupConnections()
        self.init = True # used to test before loading file when PLAY is pushed


    def buildGUI(self):

        # self.fileLabel = QtGui.QLabel("File")
        # self.fileEdit = QtGui.QLineEdit()
        #self.fileLabel.setBuddy(self.fileEdit)
        self.fileEdit = ""
        self.lcdTimer = QtGui.QLCDNumber()
        self.lcdTimer.display("00:00")

        #self.browseButton = QtGui.QPushButton("Browse")
        #self.browseButton.setIcon(QtGui.QIcon(":/images/folder-music.png"))

        self.playButton = QtGui.QPushButton("Play")
        self.playButton.setIcon(QtGui.QIcon(":/images/play.png"))
        self.playButton.setEnabled(True)

        self.pauseButton = QtGui.QPushButton("Pause")
        self.pauseButton.setIcon(QtGui.QIcon(":/images/pause.png"))

        self.stopButton = QtGui.QPushButton("Stop")
        self.stopButton.setIcon(QtGui.QIcon(":/images/stop.png"))

        #self.fullScreenButton = QtGui.QPushButton("Full Screen")  ######

        #upperLayout = QtGui.QHBoxLayout()
        #upperLayout.addWidget(self.fileLabel)
        #upperLayout.addWidget(self.fileEdit)
        #upperLayout.addWidget(self.browseButton)

        midLayout = QtGui.QHBoxLayout()
        midLayout.addWidget(self.seekSlider)
        midLayout.addWidget(self.lcdTimer)

        lowerLayout = QtGui.QHBoxLayout()
        lowerLayout.addWidget(self.playButton)
        lowerLayout.addWidget(self.pauseButton)
        lowerLayout.addWidget(self.stopButton)
        #lowerLayout.addWidget(self.fullScreenButton)  #########
        lowerLayout.addWidget(self.volumeSlider)

        layout = QtGui.QVBoxLayout()
        #layout.addLayout(upperLayout)
        layout.addWidget(self.videoWidget)
        layout.addLayout(midLayout)
        layout.addLayout(lowerLayout)

        self.setLayout(layout)
        self.lcdTimer.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.seekSlider.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)


    def setupConnections(self):
        # self.browseButton.clicked.connect(self.browseClicked)
        self.playButton.clicked.connect(self.playClicked)
        self.pauseButton.clicked.connect(self.pauseClicked)
        self.stopButton.clicked.connect(self.stopClicked)
        # self.fileEdit.textChanged.connect(self.checkFileName)
        #self.fullScreenButton.clicked.connect(self.fullScreenClicked)
        #self.videoWidget.keyPressed.connect(self.fullScreenButton)
        #self.mController.availableSubtitlesChanged.connect(self.subsChanged)
        #self.videoWidget.stateChanged.connect(self.vidStateChanged)


    def subsChanged(self):
        pass

    def tick(self, time):  # transcript list hilight following
        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.lcdTimer.display(displayTime.toString('mm:ss'))
        """
        print "time             : ", time
        print
        print ">current row     : ", w.currentRow
        print " currentSubStart : ", w.currentSubStart
        print " currentSubEnd   : ", w.currentSubEnd
        print " nextSubStart    : ", w.nextSubStart
        print " nextSubEnd      : ", w.nextSubEnd
        print "***************"
        """

        if time > subsList.currentSubEnd:
            subsList.item(subsList.currentRow).setBackground(QtGui.QColor('grey'))

        if time > subsList.nextSubStart:
            subsList.currentRow = subsList.currentRow + 1
            i = subsList.subs[subsList.currentRow]
            subsList.currentSubStart = i.start.ordinal
            subsList.currentSubEnd = i.end.ordinal
            n = subsList.subs[subsList.currentRow + 1]
            subsList.nextSubStart = n.start.ordinal
            subsList.nextSubEnd = n.end.ordinal

            subsList.item(subsList.currentRow - 1).setBackground(QtGui.QColor('white'))
            subsList.item(subsList.currentRow).setBackground(QtGui.QColor('red'))

            # browser text
            # w.body.appendInside("<span>" + w.subs[w.currentRow].text + "</span>")
            #w.span.setPlainText( w.subs[w.currentRow].text)

            #scroll to option. should center current item in list though.
            subsList.ScrollHint = QtGui.QAbstractItemView.EnsureVisible
            subsList.scrollToItem(subsList.item(subsList.currentRow), subsList.ScrollHint)

            # Update LineDefs panel
            LineDefs.lookup(subsList.currentRow)


    def playClicked(self):  # Set video file at first play click
        if self.init:
            self.player.setCurrentSource(Phonon.MediaSource(self.fileEdit))
            self.init = False
        self.player.play()

    def pauseClicked(self):
        self.player.pause()

    def stopClicked(self):
        self.player.stop()
        self.lcdTimer.display("00:00")

    def browseClicked(self):
        f, _ = QtGui.QFileDialog.getOpenFileName(self)
        if f != "":
            self.fileEdit.setText(f)

    def checkFileName(self, s):
        if s != "":
            self.playButton.setEnabled(True)
        else:
            self.playButton.setEnabled(False)

class cVideoWidget(Phonon.VideoWidget):
    def __init__(self):
        super(cVideoWidget, self).__init__()
        self.FS = False

    def mouseDoubleClickEvent(self, event):  # Fullscreen toggle
        if self.FS == True:
            self.exitFullScreen()
            self.FS = False
        else:
            self.enterFullScreen()
            self.FS = True

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:  # Exit fullscreen
            if self.FS == True:
                self.exitFullScreen()
                self.FS = False
            else:
                self.enterFullScreen()
                self.FS = True
        if event.key() == QtCore.Qt.Key_Space:  # Pause with space
            if self.qp.player.state() == Phonon.PausedState:
                self.qp.player.play()
            else:
                self.qp.player.pause()

class cDockKanji(QtGui.QDockWidget):
    def __init__(self):
        super(cDockKanji, self).__init__()

        self.dockWidgetContents = QtGui.QWidget()

        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)

        self.textKanjiDefs = QtGui.QTextBrowser(self.dockWidgetContents)
        self.textKanjiDefs.setAcceptDrops(False)
        self.textKanjiDefs.setOpenLinks(False)

        self.verticalLayout.addWidget(self.textKanjiDefs)
        self.horizontalLayout = QtGui.QHBoxLayout()

        self.label = QtGui.QLabel(self.dockWidgetContents)

        self.horizontalLayout.addWidget(self.label)
        self.textKanjiSearch = QtGui.QLineEdit(self.dockWidgetContents)

        self.horizontalLayout.addWidget(self.textKanjiSearch)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setWidget(self.dockWidgetContents)
        self.setWindowTitle("Kanji")

class cDockVocab(QtGui.QDockWidget):
    def __init__(self):
        super(cDockVocab, self).__init__()

        self.dockWidgetContents = QtGui.QWidget()

        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)

        self.textVocabDefs = QtGui.QTextBrowser(self.dockWidgetContents)
        self.textVocabDefs.setAcceptDrops(False)
        self.textVocabDefs.setOpenLinks(False)

        self.verticalLayout.addWidget(self.textVocabDefs)
        self.horizontalLayout = QtGui.QHBoxLayout()

        self.label = QtGui.QLabel(self.dockWidgetContents)

        self.horizontalLayout.addWidget(self.label)
        self.textVocabSearch = QtGui.QLineEdit(self.dockWidgetContents)

        self.horizontalLayout.addWidget(self.textVocabSearch)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setWidget(self.dockWidgetContents)
        self.setWindowTitle("Vocabulary")

class cDockDirSelect(QtGui.QDockWidget):
    def __init__(self):
        super(cDockDirSelect, self).__init__()

        self.dockWidgetContents = QtGui.QWidget()
        self.horizontalLayout = QtGui.QHBoxLayout(self.dockWidgetContents)
        self.dockWidgetContents.setLayout(self.horizontalLayout)

        self.comboVideo = QtGui.QComboBox(self.dockWidgetContents)
        self.horizontalLayout.addWidget(self.comboVideo)
        self.btnVideo = QtGui.QPushButton(self.dockWidgetContents)
        self.btnVideo.setText("+")
        self.horizontalLayout.addWidget(self.btnVideo)
        self.btnVideo.clicked.connect(self.showDialogV)

        self.comboTranscr = QtGui.QComboBox(self.dockWidgetContents)
        self.horizontalLayout.addWidget(self.comboTranscr)
        self.btnTranscr = QtGui.QPushButton(self.dockWidgetContents)
        self.btnTranscr.setText("+")
        self.horizontalLayout.addWidget(self.btnTranscr)
        self.btnTranscr.clicked.connect(self.showDialogT)

        self.comboDefs = QtGui.QComboBox(self.dockWidgetContents)
        self.horizontalLayout.addWidget(self.comboDefs)
        self.btnDefs = QtGui.QPushButton(self.dockWidgetContents)
        self.btnDefs.setText("+")
        self.horizontalLayout.addWidget(self.btnDefs)
        self.btnDefs.clicked.connect(self.showDialogD)

        # enable Load/Save when file selected, set linedefs.filename
        self.comboDefs.editTextChanged.connect(self.setdefsfile)

        self.btnVideo.setMaximumWidth(20)
        self.btnTranscr.setMaximumWidth(20)
        self.btnDefs.setMaximumWidth(20)

        # load save create
        #self.btnLoad = QtGui.QPushButton(self.dockWidgetContents)
        #self.btnLoad.setText("Load")
        #self.horizontalLayout.addWidget(self.btnLoad)
        #self.btnLoad.clicked.connect(LineDefs.loaddefs)
        #self.btnLoad.setDisabled(True)

        self.btnSave = QtGui.QPushButton(self.dockWidgetContents)
        self.btnSave.setText("Save Def")
        self.horizontalLayout.addWidget(self.btnSave)
        self.btnSave.clicked.connect(LineDefs.savedefs)
        self.btnSave.setDisabled(True)

        self.btnCreate = QtGui.QPushButton(self.dockWidgetContents)
        self.btnCreate.setText("Create Def")
        self.horizontalLayout.addWidget(self.btnCreate)
        self.btnCreate.clicked.connect(LineDefs.createdefs)
        self.btnCreate.setDisabled(True)

        #self.btnLoad.setMaximumWidth(90)
        self.btnSave.setMaximumWidth(90)
        self.btnCreate.setMaximumWidth(90)

        self.setWidget(self.dockWidgetContents)
        self.setWindowTitle("Directory Select")
        self.setMinimumHeight(50)

        self.comboVideoDir = ""
        self.comboVideo.currentIndexChanged.connect(self.setvideofile)

        self.comboTranscrDir = ""
        self.comboTranscr.currentIndexChanged.connect(self.settranscrfile)

        self.comboDefsDir = ""
        self.comboDefs.currentIndexChanged.connect(self.setdefsfile)


    def setvideofile(self):
        if self.comboVideo.currentText() != "":
            qp.init = True  # reset video source
            qp.fileEdit = self.comboVideoDir + "/" + self.comboVideo.currentText()
            statusbar.showMessage("Video File Loaded: " + qp.fileEdit)

    def settranscrfile(self):
        if self.comboTranscr.currentText() != "":
            fn = self.comboTranscrDir + "/" + self.comboTranscr.currentText()
            subsList.loadSubs(fn)
            statusbar.showMessage("Transcript File Loaded: " + fn)

    def setdefsfile(self):
        if self.comboDefs.currentText() != "":
            LineDefs.filename = self.comboDefsDir + "/" + self.comboDefs.currentText()
            #self.btnLoad.setDisabled(False)
            self.btnSave.setDisabled(False)
            LineDefs.loaddefs()

    def showDialogV(self):
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        dirNames = QtGui.QFileDialog.getOpenFileName
        if dialog.exec_():
            dirNames = dialog.selectedFiles()
        onlyfiles = [f for f in listdir(dirNames[0]) if isfile(join(dirNames[0], f))]
        onlyvids = list()
        for x in onlyfiles:
            if x.split(".")[-1] in("mp4", "mkv") :
                onlyvids.append(x)
        self.comboVideo.clear()
        self.comboVideo.addItem("")
        self.comboVideo.addItems(onlyvids)
        self.comboVideoDir = dirNames[0]
        statusbar.showMessage("Video Folder set to: " + dirNames[0])

    def showDialogT(self):
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        dirNames = QtGui.QFileDialog.getOpenFileName
        if dialog.exec_():
            dirNames = dialog.selectedFiles()
        onlyfiles = [f for f in listdir(dirNames[0]) if isfile(join(dirNames[0], f))]
        onlysrts = list()
        for x in onlyfiles:
            if x.split(".")[-1] == "srt" :
                onlysrts.append(x)
        self.comboTranscr.clear()
        self.comboTranscr.addItem("")
        self.comboTranscr.addItems(onlysrts)
        self.comboTranscrDir = dirNames[0]
        statusbar.showMessage("Transcript Folder set to: " + dirNames[0])

    def showDialogD(self):
        # open file dialog, get folder, add folder files to combobox
        # set basedir, enable Create button
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        dirNames = QtGui.QFileDialog.getOpenFileName
        if dialog.exec_():
            dirNames = dialog.selectedFiles()
        onlyfiles = [f for f in listdir(dirNames[0]) if isfile(join(dirNames[0], f))] # should be .tdef !
        onlydefs = list()
        for x in onlyfiles:
            if x.split(".")[-1] == "tdef" :
                onlydefs.append(x)
        self.comboDefs.clear()
        self.comboDefs.addItem("")
        self.comboDefs.addItems(onlydefs)
        self.comboDefsDir = dirNames[0]
        LineDefs.basedir = dirNames[0]
        self.btnCreate.setDisabled(False)
        statusbar.showMessage("Definitions Folder set to: " + dirNames[0])

class cLineDefs(QtGui.QTextBrowser):
    def __init__(self):
        super(cLineDefs, self).__init__()
        self.TranscriptLine = list()
        self.Expression = list()
        self.Reading = list()
        self.Glossary = list()
        self.Result = ""
        self.filename = ""
        self.basedir = ""
        font = QtGui.QFont()
        font.setPointSize(16)
        self.setFont(font)

    def createdefs(self):
        # get new filename from input dialog
        # set as current filename(.tdef), create new empty file
        # add new file to combobox and set it as current
        text, ok = QtGui.QInputDialog.getText(self, "Create Definitions File", "File name:", QtGui.QLineEdit.Normal, "")
        if ok and text != '':
            self.filename = self.basedir + "/" + text + ".tdef"
            file = open(self.filename, 'w')
            data = {'TranscriptLine': self.TranscriptLine, 'Expression': self.Expression, 'Reading': self.Reading, 'Glossary': self.Glossary}
            pickle.dump(data, file)
            file.close()

            dockDirSelect.comboDefs.addItem(text + ".tdef") # hacky, avoids re-query of dir
            index = dockDirSelect.comboDefs.findText(text + ".tdef")
            dockDirSelect.comboDefs.setCurrentIndex(index)
            statusbar.showMessage("New Definitions File Created: " + self.filename)

    def loaddefs(self):
        file = open(self.filename, 'r')
        data = pickle.load(file)
        file.close()
        #print "file closed"
        self.TranscriptLine = data['TranscriptLine']
        self.Expression = data['Expression']
        self.Reading = data['Reading']
        self.Glossary = data['Glossary']
        statusbar.showMessage("Definitions File Loaded: " + self.filename)

    def savedefs(self):
        file = open(self.filename, 'w')
        data = {'TranscriptLine': self.TranscriptLine, 'Expression': self.Expression, 'Reading': self.Reading, 'Glossary': self.Glossary}
        pickle.dump(data, file)
        file.close()
        statusbar.showMessage("Definitions File Saved: " + self.filename, 2000)

    def add(self, expression, reading, glossary):
        line = subsList.currentRow
        self.TranscriptLine.append(line)
        self.Expression.append(expression)
        self.Reading.append(reading)
        self.Glossary.append(glossary)

        self.lookup(line)

    def lookup(self, line):
        self.clear() # clear linedefs and append matching defs for transcript line
        if line in self.TranscriptLine:
            index = list()
            for z in range(len(self.TranscriptLine)):
                if line == self.TranscriptLine[z]:
                    index.append(z)

            for z in range(len(index)):
                result = self.Expression[index[z]] + " [" + self.Reading[index[z]] + "] " + self.Glossary[index[z]] + "\n"
                LineDefs.append(result)


if __name__ == "__main__":
    qapp = QtGui.QApplication(sys.argv)
    w = QtGui.QMainWindow()
    w.setWindowTitle("Trans-Player-Desktop v0.2")
    statusbar = QtGui.QStatusBar(w)
    w.setStatusBar(statusbar)

# Video Player
    dockVideo = QtGui.QDockWidget("Translation Player")
    qp = QPlayer()
    dockVideo.setWidget(qp)
    w.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockVideo)
    dockVideo.setMinimumWidth(500)

# Transcript List
    subsList = cSubsList()
    subsList.itemDoubleClicked.connect(subsList.gotoLine)
    w.setCentralWidget(subsList)

# Vocab and Kanji
    dockVocab = cDockVocab()
    w.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockVocab)
    dockKanji = cDockKanji()
    w.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockKanji)
    dockKanji.hide()

# Line Defs -- add defs load/save
    LineDefs = cLineDefs()
    dockLineDefs = QtGui.QDockWidget("Line Defs")
    dockLineDefs.setWidget(LineDefs)
    LineDefs.setMinimumWidth(250) # sets the whole right side

# Lookup Line (Minireader)
    lookupLine = MiniReader(dockKanji, dockVocab, dockVocab.textVocabDefs, dockKanji.textKanjiDefs, LineDefs)
    dockLookupLine = QtGui.QDockWidget("Lookup Line")
    dockLookupLine.setWidget(lookupLine)
    dockLookupLine.setMaximumHeight(90)

    w.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockLookupLine)
    w.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockLineDefs)

# Directory Select
    dockDirSelect = cDockDirSelect()
    w.addDockWidget(QtCore.Qt.TopDockWidgetArea, dockDirSelect)

    w.showMaximized()
    qapp.exec_()
