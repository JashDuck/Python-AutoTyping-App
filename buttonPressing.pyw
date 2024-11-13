import keyboard
from pynput.keyboard import Listener
import mouse

import pickle
from time import sleep
from threading import Thread
import sys
import os

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QTextEdit, QLabel, QPushButton,
                             QDoubleSpinBox, QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QFont

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
file = os.path.join(__location__, "keybind.pk")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # name the window and set its width
        self.setWindowTitle("Auto Actions")
        self.setFixedWidth(400)

        # create a tab group
        self.tabs = QTabWidget()

        # add tabs to the tab group
        self.addTab1()
        self.addTab2()
        self.addHotkeyTab()

        #set the central widget to tabs
        self.setCentralWidget(self.tabs)

    def addTab1(self):
        # create a textbox with a height of 40
        textBox = QTextEdit()
        textBox.setFixedHeight(40)

        # create a number box and label and put them in a V group
        numBoxLabel = QLabel("Button Hold Length (sec):")
        numBox = QDoubleSpinBox()
        numBox.setValue(1)

        numLayout = QVBoxLayout()
        numLayout.addWidget(numBoxLabel)
        numLayout.addWidget(numBox)

        # combine the textbox and the numLayout
        topLayout = QHBoxLayout()
        topLayout.addWidget(textBox)
        topLayout.addLayout(numLayout)

        # create start and stop buttons
        startButton = QPushButton("Start")
        stopButton = QPushButton("Stop")
        stopButton.setDisabled(True)

        # connect the buttons to the tab 1 update function
        startButton.clicked.connect(lambda: self.tab1Update(textBox, startButton, stopButton, numBox, True))
        stopButton.clicked.connect(lambda: self.tab1Update(textBox, startButton, stopButton, numBox, False))

        # add the buttons to a layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(startButton)
        buttonLayout.addWidget(stopButton)

        # add the textbox and the button layout to a tab widget
        tab = QWidget()
        tab.layout = QVBoxLayout()
        tab.layout.addLayout(topLayout)
        tab.layout.addLayout(buttonLayout)
        tab.setLayout(tab.layout)

        # add the tab to the tab group under the name Auto Typer
        self.tabs.addTab(tab, "Auto Typer")

        # whenever the tab is changed make sure everything turns off
        self.tabs.currentChanged.connect(lambda: self.tab1Update(textBox, startButton, stopButton, numBox, False))

    def tab1Update(self, textBox, startButton, stopButton, numBox, on):
        # if there isn't something in the box then don't do anything
        if textBox.toPlainText() != "":
            # the textbox and start button will be disabled at the same time
            textBox.setDisabled(on)
            numBox.setDisabled(on)
            startButton.setDisabled(on)
            stopButton.setDisabled(not on)

            # if on is true start the loop
            if on:
                self.tab1LoopVar = Thread(target=lambda: self.tab1Loop(textBox, numBox.value()))
                self.tab1LoopVar.start()

            # if on is false then end the loop
            if not on: self.tab1LoopVar.join()

    def tab1Loop(self, textBox, sleepLength):
        # loop until stopped 
        while not textBox.isEnabled():
            for letter in textBox.toPlainText():
                # if stopped then exit the for loop
                if textBox.isEnabled(): break

                # press the inputted buttons
                keyboard.press(letter)
                sleep(sleepLength)
                keyboard.release(letter)
                

    def addTab2(self):
        # record mouse events
        self.tab2MouseEvents = []

        # creates the record start and stop buttons
        recordButton = QPushButton("Record")
        recordStopButton = QPushButton("Stop")
        recordStopButton.setDisabled(True)

        # add actions to the record buttons
        recordButton.clicked.connect(lambda: self.tab2RecordUpdate(startButton, recordButton, recordStopButton, True))
        recordStopButton.clicked.connect(lambda: self.tab2RecordUpdate(startButton, recordButton, recordStopButton, False))

        # add the record buttons to a layout
        recordLayout = QHBoxLayout()
        recordLayout.addWidget(recordButton)
        recordLayout.addWidget(recordStopButton)

        # create start and stop buttons
        startButton = QPushButton("Start")
        stopButton = QPushButton("Stop")
        stopButton.setDisabled(True)

        # add actions to the start and stop buttons
        startButton.clicked.connect(lambda: self.tab2Update(recordButton, startButton, stopButton, True))
        stopButton.clicked.connect(lambda: self.tab2Update(recordButton, startButton, stopButton, False))

        # add the start and stop buttons to a layout
        startLayout = QHBoxLayout()
        startLayout.addWidget(startButton)
        startLayout.addWidget(stopButton)

        # add the layouts to a tab
        tab = QWidget()
        tab.layout = QVBoxLayout()
        tab.layout.addLayout(recordLayout)
        tab.layout.addLayout(startLayout)
        tab.setLayout(tab.layout)

        # add the tab to the tab group under the name Auto Actions
        self.tabs.addTab(tab, "Auto Actions")

        # whenever the tab is changed make sure everything turns off
        self.tabs.currentChanged.connect(lambda: self.tab2Update(recordButton, startButton, stopButton, False))
        self.tabs.currentChanged.connect(lambda: self.tab2RecordUpdate(startButton, recordButton, recordStopButton, False))

    def tab2Update(self, recordButton, startButton, stopButton, on):
        # if the record button hasn't been clicked
        if recordButton.isEnabled():
            # disable certain buttons
            startButton.setDisabled(on)
            stopButton.setDisabled(not on)

            # try to start or stop the loop
            try:
                if on:
                    self.tab2LoopVar = Thread(target=lambda: self.tab2Loop(startButton))
                    self.tab2LoopVar.start()
                if not on:
                    self.tab2LoopVar.join()
            except: pass

    def tab2RecordUpdate(self, startButton, recordButton, stopButton, on):
        # if the start wasn't pressed button
        if startButton.isEnabled():
            # disable certain buttons
            recordButton.setDisabled(on)
            stopButton.setDisabled(not on)

            # try to add or remove the mouse hook
            try:
                if on: mouse.hook(self.tab2MouseEvents.append)
                if not on: mouse.unhook(self.tab2MouseEvents.append)
            except: pass

    def tab2Loop(self, startButton):
        # loop until stopped
        while not startButton.isEnabled():
            mouse.play(self.tab2MouseEvents)


    def addHotkeyTab(self):
        try:
            self.hotkey = self.readHotkeyData()
        except:
            self.writeHotKeyData("f6")
            self.hotkey = self.readHotkeyData()
        
        # create a start/stop button
        startStopButton = QPushButton("Start/Stop")
        startStopButton.setFixedSize(QSize(100, 20))

        # create a textbox that will hold the text value
        hotkeyTextBox = QTextEdit()
        hotkeyTextBox.setDisabled(True)
        hotkeyTextBox.setFixedSize(QSize(100, 30))

        # set the font size
        hotkeyTextBox.setFont(QFont("arial", 12))

        # write the hotkey to the box
        hotkeyTextBox.setHtml(self.hotkey)

        # set the set hotkey function to the startstopbutton
        startStopButton.clicked.connect(lambda: self.setHotkey(startStopButton, hotkeyTextBox))

        # create a tab and add the layouts to it
        tab = QWidget()
        tab.layout = QHBoxLayout()
        tab.layout.addWidget(startStopButton)
        tab.layout.addWidget(hotkeyTextBox)
        tab.setLayout(tab.layout)

        # add the tab to the tab group
        self.tabs.addTab(tab, "Hotkeys")

    def setHotkey(self, button, textBox):
        button.setDisabled(button.isEnabled())

        self.button = button
        self.textBox = textBox

        listener = Listener(on_press=self.on_press)
        listener.start()


    def on_press(self, key):
        self.hotKey = key.char
        self.writeHotKeyData(self.hotKey)
        return

    def writeHotKeyData(self, data):
        with open(file, 'wb') as fi:
            pickle.dump(data, fi)

    def readHotkeyData(self):
        with open(file, "rb") as fileData:
            return pickle.load(fileData)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()