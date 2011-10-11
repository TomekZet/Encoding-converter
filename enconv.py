#!/usr/bin/python
# -*- coding: UTF-8 -*-

import argparse
import sys
import re
import os
import wx
from wx.lib.wordwrap import wordwrap


def detectEncoding(inputFile, quiet):

  cp = 0
  iso = 0
  utf = 0

  cpCharacters = []
  isoCharacters = []
  utfCharacters = []
  utfOrdCharacters = []

  nationalCharacters = [u"ą", u"Ą", u"ć", u"Ć", u"ę", u"Ę", u"ł", u"Ł", u"ń", u"Ń", u"ó", u"Ó", u"ś", u"Ś", u"ż", u"Ż", u"ź", u"Ż"]

  for nChar in nationalCharacters:
    cpCharacters.append(ord(nChar.encode("cp1250", "replace")))
    isoCharacters.append(ord(nChar.encode("iso8859_2", "replace")))
    utfCharacters.append(nChar.encode("utf_8", "replace"))
    for c in nChar.encode("utf_8", "replace"):
      utfOrdCharacters.append(ord(c))

  for line in inputFile:
    for word in line.split():
      for character in word:
	#print ord(character)
	if ord(character) in cpCharacters:
	  cp += 1
	if ord(character) in isoCharacters:
	  iso += 1
	if ord(character) in utfOrdCharacters:
	  utf += 1


  guess = max(cp, utf, iso)
  if guess == cp == iso or guess == cp == utf or guess == iso == utf:
    if not quiet:
        print "Cannot define encoding!"
  else:
    if guess == cp:
      return "windows-1250"
    elif guess == iso:
      return "iso-8859-2"
    elif guess == utf:
      return "utf8"


def convertEncoding(sourceEncoding, targetEncoding, inputFile, outputFile, replace):

  htmlEncodings = {"utf8":"utf-8", "iso-8859-2":"iso-8859-2", "windows-1250":"windows-1250"}

  count = 0

  for line in inputFile:
    uLine = unicode(line, sourceEncoding, 'replace')
    if replace:
      uLine, count = re.subn(r"(charset|encoding)\s*=\s*(?P<quote>\"|)?(ISO-8859-2|utf-8|windows-1250)(?P<quote2>\"|)?", r"\1=\g<quote>"+htmlEncodings[targetEncoding]+"\g<quote2>", uLine, flags=re.IGNORECASE)
      if count > 0:
        replace = False
    outLine = uLine.encode(targetEncoding, 'replace')
    outputFile.write(outLine)

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        self.size = (300,250)
        wx.Frame.__init__(self, parent, title=title, size = self.size )
        
        self.inputPath = None
        self.outputPath = None
        
        self.helpProvider = wx.SimpleHelpProvider()
        wx.HelpProvider.Set(self.helpProvider)
        
        self.openButton = wx.Button(self, label = "Input File", pos = (10, 10))
        self.openButton.SetHelpText("Choose a source file to open.\nProgram will try to detect encoding automatically and set it.")
                
        self.infileLabel = wx.StaticText(self, label = "No file choosen",
					  pos = (self.openButton.GetPosition().x + self.openButton.GetSize().GetWidth() + 10, self.openButton.GetPosition().y)) 
        
        allEncodings = ["utf8", "iso-8859-2", "windows-1250"]        
        self.sourceChoice = wx.Choice(self, choices = allEncodings, pos = (10, 45), name="source")
        self.targetChoice = wx.Choice(self, choices = allEncodings, pos = (10, 75), name="target")
        self.sourceLabel = wx.StaticText(self, label = "Source encoding", pos = (self.sourceChoice.GetPosition().x + self.sourceChoice.GetSize().GetWidth() + 10, self.sourceChoice.GetPosition().y)) 
        self.targetLabel = wx.StaticText(self, label = "Target encoding", pos = (self.targetChoice.GetPosition().x + self.targetChoice.GetSize().GetWidth() + 10, self.targetChoice.GetPosition().y)) 
        
        self.replaceCheckBox = wx.CheckBox(self, label = "Replace \"charset\" parameter", pos = (10, 120))
        self.replaceCheckBox.SetHelpText("Replace first found encoding information in the output file (ex. \"charset=utf-8\" is converted to \"charset=windows-1250\". Looks for \"encoding\" and \"charset\" substrings.")
        self.saveButton = wx.Button(self, label = "Convert", pos = (10, 160))
        self.saveButton.SetHelpText("Choose a file to save convertion results to and convert")
        self.statusBar  = self.CreateStatusBar() 
        
        cBtn = wx.ContextHelpButton(self, pos = (10, 195))
        cBtn.SetHelpText("wx.ContextHelpButton")

        filemenu= wx.Menu()
        helpmenu = wx.Menu()

        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        menuOpen = filemenu.Append(wx.ID_OPEN,"Open"," Open source File")
        menuSave = filemenu.Append(wx.ID_SAVE,"Convert"," Convert a file")
        menuContextHelp = helpmenu.Append(wx.ID_ANY, "Context help", "Starts context menu mode")
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        menuBar.Append(helpmenu,"&Help")
        self.SetMenuBar(menuBar) 
        
        
        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnContextHelp, menuContextHelp)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.openButton)
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.saveButton)
        self.Show(True)

    def OnAbout(self,e):
             
        info = wx.AboutDialogInfo()
        info.Name = "Encoding converter"
        info.Version = "0.3"
        info.Copyright = "(C) 2011 Tomasz Ziętkiewicz"
        info.Description = wordwrap(
            "Encoding converter.\nFor command line help run with argument \"-h\"",
            350, wx.ClientDC(self))
        info.WebSite = ("mailto:tomek.zietkiewicz@gmail.com", "Email")
        info.Developers = [ "Tomasz Ziętkiewicz" ]

        info.License = wordwrap("This is free software: you are free to change and redistribute it.\n\nThere is NO WARRANTY, to the extent permitted by law.", 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)
    
    def OnContextHelp(self, e):
	contextHelp = wx.ContextHelp()
	contextHelp.BeginContextHelp()
            
        
    def OnOpen(self,e):
      """ Open a file"""
      dirname = ''
      dlg = wx.FileDialog(self, "Choose a source file", dirname, "", "*.*", wx.OPEN)
      if dlg.ShowModal() == wx.ID_OK:
	  filename = dlg.GetFilename()
	  dirname = dlg.GetDirectory()
	  self.inputPath = os.path.join(dirname, filename)
	  self.infileLabel.SetLabel(filename)
      dlg.Destroy()
      
      if self.inputPath == None:
	return
      infile = open(self.inputPath, "r")
      detectedEncoding = detectEncoding(infile, True)
      if detectedEncoding in self.sourceChoice.GetStrings():
	self.sourceChoice.SetSelection(self.sourceChoice.FindString(detectedEncoding))
	self.statusBar.SetStatusText("Detected encoding: %s" % detectedEncoding)
      else:
	self.statusBar.SetStatusText("Can not detect encoding")
      infile.close()


    def OnSave(self,e):
      """ Open a file"""
      if self.inputPath == None:
	message = wx.MessageDialog(self, style = wx.OK|wx.ICON_INFORMATION, caption = "Information", message = "First, specify input file.")
	message.ShowModal()
	message.Destroy()
	return
      else:	      	
	source = self.sourceChoice.GetStringSelection()
	infile = open(self.inputPath, "r")
	detectedEncoding = detectEncoding(infile, True)
	if detectedEncoding != None and detectedEncoding != source:
	    message = wx.MessageDialog(self, style = wx.YES_NO|wx.ICON_QUESTION|wx.CANCEL, caption = "Warning!", message = "Detected encoding different than choosen one!\nUse detedted encoding instead of choosen one?")
	    answer = message.ShowModal()
	    if answer == wx.ID_OK:
		print "OK"
		source = detectedEncoding
		self.sourceChoice.SetSelection(self.sourceChoice.FindString(detectedEncoding))
	    elif answer == wx.ID_CANCEL:
		infile.close()
		message.Destroy()
		return
	    message.Destroy()
	infile.close()
	
	dirname = ''
	dlg = wx.FileDialog(self, "Choose an output file", dirname, "", "*.*", wx.SAVE)
	
	
	if dlg.ShowModal() == wx.ID_OK:
	    filename = dlg.GetFilename()
	    dirname = dlg.GetDirectory()
	    self.outputPath = os.path.join(dirname, filename)
	    dlg.Destroy()
	    if self.outputPath == self.inputPath:
	      	message = wx.MessageDialog(self, style = wx.OK|wx.ICON_EXCLAMATION, caption = "Information", message = "Output file must be differrent than input file!")
		message.ShowModal()
		message.Destroy()
		return
	    	    
	    target = self.targetChoice.GetStringSelection()
	    infile = open(self.inputPath, "r")
	    outfile = open(self.outputPath, "w")
	    replace = self.replaceCheckBox.IsChecked()
	    convertEncoding(source, target, infile, outfile, replace)
	    print "Convertion finished!"
	    self.statusBar.SetStatusText("Convertion finished!")
	    infile.close()
	    outfile.close()

    def OnExit(self,e):
        self.Close(True)  # Close the frame.


if __name__ == '__main__':

    if len (sys.argv) == 1 or len(sys.argv) > 1 and (sys.argv[1] == "-g" or sys.argv[1] == "--gui"):
      print "Entered GUI mode"
      app = wx.App(False)
      frame = MainWindow(None, "Encoding converter")
      app.MainLoop()
      sys.exit()
    
    #winEncodings = ["cp1250", "windows-1250"]
    #isoEncodings = ["iso8859_2", "iso-8859-2", "latin2", "L2"]
    #utfEncodings = ["utf_8", "U8", "UTF", "utf8"]
    allEncodings = ["utf8", "iso-8859-2", "windows-1250"]

    #encodingsText = "Should be one of: \"" +"\", \"".join(winEncodings) + "\" for Windows CP-1250 encoding, \"" + "\", \"".join(isoEncodings) + "\" for iso-8859-2 encoding, \"" + "\", \"".join(utfEncodings) + "\" for UTF-8 encoding"

    parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description = "Converts encoding of a file between popular encodings standards\nTo run in GUI mode run without any parameters\nGiving source encoding is optional - program will try to guess encoding of an input file.",
      prog="enconv",
      epilog="Author:\t\tTomasz Ziętkiewicz. 2011\nCopyright:\tThis is free software: you are free to change and redistribute it.\n\t\tThere is NO WARRANTY, to the extent permitted by law."
      )
    parser.add_argument('-s', '--source', help="Source encoding. If not given, program tries to guess encoding basing on statistics.", choices=allEncodings)
    parser.add_argument('-t', '--target', help='Target encoding', choices=allEncodings, default="utf8")
    parser.add_argument('-g', '--gui', help='GUI mode')
    parser.add_argument('-d', '--detect', action='store_true', help="Only detect encoding, do not convert")
    parser.add_argument('-f', '--force', action='store_true', help="Force using given encoding instead of detected encoding")
    parser.add_argument('-q', '--quiet', action='store_true', help="Warnings and other messages are not printed.")
    parser.add_argument('-r', '--replace', action='store_true', help="Replace first found encoding information in the output file (ex. \"charset=utf-8\" is converted to \"charset=windows-1250\". Looks for \"encoding\" and \"charset\" substrings.")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.3')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="Path to the input file. If not given, standard input will be used")
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="Path to the output file. If not given, standard output will be used")
    args = parser.parse_args()

    if args.infile != sys.stdin:
        detectedEncoding = detectEncoding(args.infile, args.quiet)
        args.infile.seek(0)
        if args.source == None or args.detect:
            args.source = detectedEncoding
            if args.source == None:
                args.infile.close()
                args.outfile.close()
                sys.exit()
            elif not args.quiet:
                print "Detected encoding: %s" % args.source
        elif args.source != detectedEncoding and detectedEncoding != None and not args.quiet:
            print "Warning: detected encoding is different from the given one!"
            if not args.force:
                args.source = detectedEncoding
                print "Using detected encoding"
    elif args.source == None:
        print "You must specify source encoding if stdin is used as input"
        args.infile.close()
        args.outfile.close()
        sys.exit()
    if not args.detect:
      convertEncoding(args.source, args.target, args.infile, args.outfile, args.replace)

    args.infile.close()
    args.outfile.close()