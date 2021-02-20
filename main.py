import sys
import string
import os
import tempfile
import shutil
import subprocess

def NextVersion(FileName: object):
    next_version = FileName + '_1'
    Number = 1
    while os.path.exists(next_version):
        Number = Number + 1
        next_version = FileName + '_' + str(Number)
    return next_version


#  Defaults

UseAscii = False
UseMacRoman = False
UseLatin1 = False
UseUtf8 = False
CheckEncoding = True
ArgsValid = True

#  First, just check we have the necessary filename, and see if an encoding
#  was specified.

NumberArgs = len(sys.argv)
if NumberArgs < 2:
    print("Usage: FixUnprintable filename <encoding>")
    print("eg: FixUnprintable P10-3.tex")
    ArgsValid = False
if NumberArgs > 2:
    CheckEncoding = False
    Encoding = sys.argv[2]
    if Encoding.lower() == "ascii":
        UseAscii = True
    elif Encoding.lower() == "macroman":
        UseMacRoman = True
    elif Encoding.lower() == "latin1":
        UseLatin1 = True
    elif Encoding.lower() == "utf-8":
        UseUtf8 = True
    else:
        print("Encoding must be one of: ASCII, MacRoman, Latin1, UTF-8")
        ArgsValid = False
    if ArgsValid: print("Will assume file is encoded using", Encoding)

if ArgsValid:
    TexFileName = sys.argv[1]

    if not os.path.exists(TexFileName):
        print("Cannot find file '" + TexFileName + "'")
    else:

        #  Unless we've been asked to use a specific encoding, try to determine
        #  the encoding automatically. GetFileEncoding() will do this.

        EncodingOK = True
        if CheckEncoding:
            Report = []
            Encodings = []
            Certainty = AdassChecks.GetFileEncoding(TexFileName, Encodings, Report)
            if len(Encodings) == 1:
                print("")
                if Encodings[0] == "ASCII":
                    print("File is encoded in standard ASCII")
                else:
                    if Certainty == 100:
                        print("File is encoded using", Encodings[0])
                    else:
                        print("File appears to be encoded using", Encodings[0])
                        for Line in Report:
                            print(Line)
                        print("")
                        print("If necessary, restore the saved version an re-run")
                        print("specifying a different encoding explicitly, eg:")
                        if Encodings[0] == "Latin1":
                            print("FixUnprintable", TexFileName, "MacRoman")
                        else:
                            print("FixUnprintable", TexFileName, "Latin1")
                Encoding = Encodings[0].lower()

            else:
                EncodingOK = False
                Message = "File could be encoded using any of: "
                for Encoding in Encodings:
                    Message = Message + ' ' + Encoding
                print(Message)
                for Line in Report:
                    print(Line)
                print("")
                print("Re-run, specifying a different encoding explicitly.")
                print("For example, use one of:")
                for Encoding in Encodings:
                    print("FixUnprintable", TexFileName, Encoding)

        if EncodingOK:

            #  An initial pass to see if we need to do anything. CheckCharacter()
            #  doesn't output any messages - it returns any it generates in Details,
            #  which we ignore - and returns True or False depending on whether
            #  it found any problem characters.

            LineNumber = 0
            FileOK = True
            InputFile = open(TexFileName, "r")
            for Line in InputFile:
                LineNumber = LineNumber + 1
                Details = []
                if AdassChecks.CheckCharacters(Line, LineNumber, Details, Encoding):
                    FileOK = False
                    break

            #  If nothing needed doing, just close the file.

            if FileOK:
                print("Nothing needs doing,", TexFileName, "left unchanged")
                InputFile.close()
            else:

                #  A second pass, if necessary, to actually do the fixing.
                #  FixCharacters() returns a fixed line, and prints out details of
                #  what it did. If no changes were made, it returns None.

                InputFile.seek(0)
                WorkFileName = NextVersion("Work.tex")
                OutputFile = open(WorkFileName, "w")
                LineNumber = 0
                for Line in InputFile:
                    LineNumber = LineNumber + 1
                    FixedLine = AdassChecks.FixCharacters(Line, LineNumber, Encoding)
                    if FixedLine != None: Line = FixedLine
                    OutputFile.write(Line)
                OutputFile.close()
                InputFile.close()

                #  We now need to rename the files, so the original file becomes a
                #  saved version, and the work file we just created replaces the
                #  original file.

                SavedFileName = NextVersion(TexFileName)
                os.rename(TexFileName, SavedFileName)
                os.rename(WorkFileName, TexFileName)
                print("Original file saved as", SavedFileName)
