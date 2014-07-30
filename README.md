ParanoiDF
=========

The swiss army knife of PDF Analysis Tools. 

Home Page 
-----------

https://github.com/patrickdw123/ParanoiDF
patrickdw123(at)gmail(dot)com
Linkedin - search for Patrick Wragg.

Features
-----------

See https://github.com/patrickdw123/ParanoiDF/wiki.

Dependances
-----------

* In order to crack passwords: PdfCrack needed (apt-get install pdfcrack)
* In order to remove DRM (editing, copying Etc.): Calibre's ebook-convert needed (apt-get install calibre)
* In order to decrypt PDFs: qpdf needed (apt-get install qpdf)
* In order to use the command redact:
	NLTK (Natural Language ToolKit) needed (apt-get install python-nltk)
	Java (Stanford parser is written in Java) needed (apt-get install default-jre)
* To support XML output "lxml" is needed:
    http://lxml.de/installation.html
* Included modules: lzw, colorama, jsbeautifier, ccitt, pythonaes (Thanks to all the developers!!)

Installation
-----------

No installation is needed apart of the commented dependencies, just execute:

	python paranoiDF.py

Execution
-----------

There are two important options when ParanoidF is executed:

-f: Ignores the parsing errors. Analysing malicious files propably leads to parsing errors, so this parameter should be set.
-l: Sets the loose mode, so does not search for the endobj tag because it's not obligatory. Helpful with malformed files.


* Simple execution

Shows the statistics of the file after being decoded/decrypted and analysed:

    python paranoiDF.py [options] pdf_file


* Interactive console

Executes the interactive console, giving a wide range of tools to play with.

    python paranoiDF.py -i 


* Batch execution

It's possible to use a commands file to specify the commands to be executed in the batch mode. This type of execution is good to automatise analysis of several files:

    python paranoiDF.py [options] -s commands_file 

Some Hints
-----------
If the information shown when a PDF file is parsed is not enough to know if it's harmful or not, the following commands can help to do it:

* tree

Shows the tree graph of the file or specified version. Here we can see suspicious elements.


* offsets 

Shows the physical map of the file or the specified version of the document. This is helpful to see unusual big objects or big spaces between objects.


* search

Search the specified string or hexadecimal string in the objects (decoded and encrypted streams included).


* object/rawobject

Shows the (raw) content of the object.


* stream/rawstream

Shows the (raw) content of the stream.


* The rest of commands, of course

> help




** Bugs **

Feel free to send bugs/criticisms/praises/comments to patrickdw123(at)gmail(dot)com.
