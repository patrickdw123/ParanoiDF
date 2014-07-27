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

# V0.1 2008/05/23
# make-pdf-javascript, use it to create a PDF document with embedded JavaScript that will execute automatically when the document is opened
# requires module mPDF.py
# Source code put in public domain by Didier Stevens, no Copyright
# https://DidierStevens.com
# Use at your own risk
#
# History:
#  
#  2008/05/29: continue
#  2008/11/09: cleanup for release

import mPDF

def main(option, outputFile):
	oPDF = mPDF.cPDF(outputFile)

	oPDF.header()

	oPDF.indirectobject(1, 0, '<<\n /Type /Catalog\n /Outlines 2 0 R\n /Pages 3 0 R\n /OpenAction 7 0 R\n>>')
	oPDF.indirectobject(2, 0, '<<\n /Type /Outlines\n /Count 0\n>>')
	oPDF.indirectobject(3, 0, '<<\n /Type /Pages\n /Kids [4 0 R]\n /Count 1\n>>')
	oPDF.indirectobject(4, 0, '<<\n /Type /Page\n /Parent 3 0 R\n /MediaBox [0 0 612 792]\n /Contents 5 0 R\n /Resources <<\n             /ProcSet [/PDF /Text]\n             /Font << /F1 6 0 R >>\n            >>\n>>')
	oPDF.stream(5, 0, 'BT /F1 12 Tf 100 700 Td 15 TL (JavaScript example) Tj ET')
	oPDF.indirectobject(6, 0, '<<\n /Type /Font\n /Subtype /Type1\n /Name /F1\n /BaseFont /Helvetica\n /Encoding /MacRomanEncoding\n>>')

	if option == 0:
	    javascript = """app.alert({cMsg: 'Hello from PDF JavaScript', cTitle: 'Testing PDF JavaScript', nIcon: 3});"""
	else:
	    javaScriptFile = option
	    try:
		fileJavasScript = open(javaScriptFile, 'rb')
	    except:
		print "File %s not found." % javaScriptFile
		return

	    try:
		javascript = fileJavasScript.read()
	    except:
		print "Error reading %s" % javaScriptFile
		return
	    finally:
		fileJavasScript.close()

	oPDF.indirectobject(7, 0, '<<\n /Type /Action\n /S /JavaScript\n /JS (%s)\n>>' % javascript)

	oPDF.xrefAndTrailer('1 0 R')

