#    ParanoiDF. A combination of several PDF analysis/manipulation tools to 
#    produce one of the most technically useful PDF analysis tools.
#    
#    Idea proposed by Julio Hernandez-Castro, University of Kent, UK.
#    By Patrick Wragg
#    University of Kent
#    21/07/2014
#    
#    With thanks to:
#    Julio Hernandez-Castro, my supervisor. 
#    Jose Miguel Esparza for writing PeePDF (the basis of this tool).
#    Didier Stevens for his "make-PDF" tools.
#    Blake Hartstein for Jsunpack-n.
#    Yusuke Shinyama for Pdf2txt.py (PDFMiner)
#    Nacho Barrientos Arias for Pdfcrack.
#    Kovid Goyal for Calibre (DRM removal).
#    Jay Berkenbilt for QPDF.
#
#    Copyright (C) 2014-2018 Patrick Wragg
#
#    This file is part of ParanoiDF.
#
#        ParanoiDF is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        (at your option) any later version.
#
#        ParanoiDF is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with ParanoiDF. If not, see <http://www.gnu.org/licenses/>.
#
#    This was written by Didier Stevens, but has been modified by Patrick
#    Wragg to be used inside ParanoiDF Interactive Console, 22/07/2014.

__description__ = 'tool to create a PDF document with an embedded file'
__author__ = 'Didier Stevens'
__version__ = '0.5.0'
__date__ = '2011/07/01'

"""
Source code put in public domain by Didier Stevens, no Copyright
https://DidierStevens.com
Use at your own risk

History:
  2008/05/18: V0.1
  2008/05/19: Refactoring
  2008/05/23: Refactoring
  2008/05/27: Refactoring
  2008/06/27: V0.2, Refactoring, options, cleanup
  2008/11/09: V0.3, added autostart and button
  2009/06/15: V0.4.0: added stego
  2011/07/01: V0.5.0: added support for Python 3
  
Todo:
"""

import mPDF
import optparse

def ReadBinaryFile(name):
    """Read a binary file and return the content, return None if error occured
    """
    
    try:
        fBinary = open(name, 'rb')
    except:
        return None
    try:
        content = fBinary.read()
    except:
        return None
    finally:
        fBinary.close()
    return content

def CreatePDFWithEmbeddedFile(pdfFileName, embeddedFileName, embeddedFileContent, filters, nobinary, autoopen, button, stego, text):
    """Create a PDF document with an embedded file
    """
    
    oPDF = mPDF.cPDF(pdfFileName)

    oPDF.header()
    
    if not nobinary:
        oPDF.binary()

    if stego:
        embeddedFiles = 'Embeddedfiles'
    else:
        embeddedFiles = 'EmbeddedFiles'
    if autoopen:
        openAction = ' /OpenAction 9 0 R\n'
    else:
        openAction = ''
    oPDF.indirectobject(1, 0, '<<\n /Type /Catalog\n /Outlines 2 0 R\n /Pages 3 0 R\n /Names << /%s << /Names [(%s) 7 0 R] >> >>\n%s>>' % (embeddedFiles, embeddedFileName, openAction))
    oPDF.indirectobject(2, 0, '<<\n /Type /Outlines\n /Count 0\n>>')
    oPDF.indirectobject(3, 0, '<<\n /Type /Pages\n /Kids [4 0 R]\n /Count 1\n>>')
    if button:
        annots = ' /Annots [10 0 R]\n'
    else:
        annots = ''
    oPDF.indirectobject(4, 0, '<<\n /Type /Page\n /Parent 3 0 R\n /MediaBox [0 0 612 792]\n /Contents 5 0 R\n /Resources <<\n             /ProcSet [/PDF /Text]\n             /Font << /F1 6 0 R >>\n            >>\n%s>>' % annots)
    if text == '':
        text = 'This PDF document embeds file %s' % embeddedFileName
    textCommands = '/F1 12 Tf 70 700 Td 15 TL (%s) Tj' % text
    if button:
        textCommands += " () ' () ' (Click inside the rectangle to save %s to a temporary folder and launch it.) ' () ' (Click here) '" % embeddedFileName
    oPDF.stream(5, 0, 'BT %s ET' % textCommands)
    oPDF.indirectobject(6, 0, '<<\n /Type /Font\n /Subtype /Type1\n /Name /F1\n /BaseFont /Helvetica\n /Encoding /MacRomanEncoding\n>>')
    oPDF.indirectobject(7, 0, '<<\n /Type /Filespec\n /F (%s)\n /EF << /F 8 0 R >>\n>>' % embeddedFileName)
    oPDF.stream2(8, 0, embeddedFileContent, '/Type /EmbeddedFile', filters)
    if autoopen or button:
        oPDF.indirectobject(9, 0, '<<\n /Type /Action\n /S /JavaScript\n /JS (this.exportDataObject({ cName: "%s", nLaunch: 2 });)\n>>' % embeddedFileName)
    if button:
        oPDF.indirectobject(10, 0, '<<\n /Type /Annot\n /Subtype /Link\n /Rect [65 620 130 640]\n /Border [16 16 1]\n /A 9 0 R\n>>')

    oPDF.xrefAndTrailer("1 0 R")

def main(options, embeddedFileName, pdfFileName):

	nobinary = False
	autoopen = False
	button = False
	stego = False
	filters = 'f'
	message = ''
	if options != 0:
		optionList = options.split(",")
		for option in optionList:
			if option.lower() == "t":
				nobinary = True
			elif option.lower() == "a":
				autoopen = True
			elif option.lower() == "b":
				button = True
			elif option.lower() == "s":
				stego = True
			elif "f=" in option:
				filters = option[2:]
			elif "m=" in option:
				message = option[2:]
			else:
				print 'Option "%s" not recognised.' % option
    
        embeddedFileContent = ReadBinaryFile(embeddedFileName)
        if embeddedFileContent == None:
            print('Error opening/reading file %s' % embeddedFileName)
        else:
            CreatePDFWithEmbeddedFile(pdfFileName, embeddedFileName, embeddedFileContent, filters, nobinary, autoopen, button, stego, message)

if __name__ == '__main__':
    Main()
