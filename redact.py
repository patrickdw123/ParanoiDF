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
#    This was written by Patrick Wragg.

'''
    This script calculates which words of a certain font/size will fit inside
    a redaction box. It requires the user to search through the objects of the
    PDF first using the Interactive Console to find the details about the font
    size, font and size of redaction box. Tutorial.pdf has a guide on this.

    If the user wishes, he/she can use the implemented grammar parser (Stanford
    Parser) to obtain a parsing score and the script will sort the list for them.
'''

import sys
import re
import difflib
import os
import json
import operator

try:
    import Image
    import ImageDraw
    import ImageFont
except:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont


def main(wordType, letterCase):

    successList=[]
    dirPath = os.path.dirname(os.path.abspath(sys.argv[0]))

    redactAreaX,redactAreaY = get_redaction_box() #Get redaction box size.
    fontName = get_font(dirPath) #Get font.
    fontSize = get_font_size() #Get font size.
    dictFile = open(dict_file_return(wordType, letterCase, dirPath))  #Input of dictionary.

    #Remove newline character from end of each word in dictionary.
    dictList = []
    lines = dictFile.readlines()
    for word in lines:
	if not word == '':
	    dictList.append(remove_newline(word))
    dictFile.close()

    #Draw word on blank canvas.
    #Calculate length in pixels from colour coordinates.
    #If word fits, add to List=<successList>.
    lengthOfDict = len(dictList)
    count = 1
    print 'Parsing words now...'
    for word in dictList:
	successWord = check_word(word, redactAreaX,
                       		redactAreaY, fontName,
                        	fontSize)
	if not successWord == 0:
	    successList.append(successWord)
	numberOfSuccesses = len(successList)

	#Print progress percentage.
	sys.stdout.write('\r{0:.0f}%'.format((float(count)/lengthOfDict)*100))
	count+=1
    if len(successList) > 0:
	print ''

        #If word cannot be grammar checked (country or name Etc.) print results and quit.
        if not is_word(wordType):
	    total_matches(numberOfSuccesses, lengthOfDict)
	    output_matches(dirPath, successList)
	    results_message(dirPath)
        else:
            total_matches(numberOfSuccesses, lengthOfDict)
  	    print ''
	    doGrammarParse = grammar_parse_query() #Ask user if they want to grammar parse.
	    if doGrammarParse:
	        #Start grammar parse.
	        print ''
	        sentance = raw_input('Enter sentance where $word is word: ')
	        file = open(dirPath + '/tempSentance.txt', 'w') #Sentance file for Stanford to parse.
	        for word in successList:
	            result = build_sentance(sentance, word)
	            file.write(result)
	        file.close()
	        scoreString = stanford_parser(dirPath) #Stanford parser execution.
	        scoreList = find_score(scoreString) #Find score in scoreString.
	        wordScoreDict = add_score_to_dict(scoreList, successList) #Put score and word in dict.
	        scoreList = sort_dict(wordScoreDict) #Sort dictonary.
	        total_matches(numberOfSuccesses, lengthOfDict) #Print total matches

	        counter = 1
	        numberOfResults = number_of_results_return() #Print N number of highest scoring words.
	        file = open(dirPath + '/results.txt','w+')
	        for score in scoreList:
		    file.write(' '.join(map(str, score)))
		    file.write('\n')
		    if counter == numberOfResults:
		        break
		        file.close()
		    counter+=1
	        results_message(dirPath)

	        #No need for these now.
	        os.remove(dirPath + '/tempScore.txt')
	        os.remove(dirPath + '/tempSentance.txt')
	        #End grammar parse.

	    else: #No grammar parse.
	        total_matches(numberOfSuccesses, lengthOfDict)
	        output_matches(dirPath, successList)
	        results_message(dirPath)
    else:
	print ''
	print ''
	print 'No matches. Are you sure you got the coordinates, font and font size correct?'


def grammar_parse_query(): #Ask user if they want to grammar parse.
    while True:
    	grammarQuery = raw_input('Would you like to do a grammar check? y/n: ')
	if grammarQuery.lower() == 'y':
		return True
		break
	elif grammarQuery.lower() == 'n':
		return False
		break


def number_of_results_return(): #Ask user how many results they want.
    while True:
	try:
	    numberOfResults = int(input('Number of results? '))
	    break
 	except ValueError:
	    print 'Invalid number, try again.'
    return numberOfResults


def remove_newline(word): #Remove newline from word.
    wordLength = len(word)
    wordLength = wordLength - 1
    newWord = word[:wordLength]
    return newWord


def sort_dict(wordScoreDict): #Sort dictonary and output to list 'scoreList'.
    scoreList = sorted(wordScoreDict.iteritems(), key=operator.itemgetter(1))
    return scoreList


def add_score_to_dict(scoreList, successList): #Put score and associated word in dictionary.
    i = 0
    wordScoreDict={}
    for score in scoreList:
	wordScoreDict[successList[i]] = score
	i+=1
    return wordScoreDict


def find_score(scoreString): #Find score in scoreString.
    scoreList=[]
    regex = ur'\bwith score -[0-9]{1,}.[0-9]{1,}\b'
    result = re.findall(regex, scoreString)
    for score in result:
	scoreList.append(score[12:])
    return scoreList


def stanford_parser(dirPath): #Stanford parser execution.
	os.system(dirPath + '/stanfordParser/' + './' + 'lexparser.sh ' + dirPath + '/tempSentance.txt > ' + dirPath + '/tempScore.txt')
	file = open(dirPath + '/tempScore.txt', 'r')
	scoreString = file.read()
	file.close()
	return scoreString


def is_word(wordType): #If not w, then grammar check not needed.
    if 'w' in wordType:
	return True
    else:
	return False


def dict_file_return(wordType, letterCase, dirPath): #Input of dictionary.
    if  wordType == 'f':
	if letterCase == 'u':
	    dictFile = dirPath + '/redactDict/upperCase/first.txt'
	elif letterCase == 'c':
	    dictFile = dirPath + '/redactDict/capitalised/first.txt'
	else:
	    dictFile = dirPath + '/redactDict/lowerCase/first.txt'
    elif wordType == 's':
	if letterCase == 'u':
	    dictFile = dirPath + '/redactDict/upperCase/surname.txt'
	elif letterCase == 'c':
	    dictFile = dirPath + '/redactDict/capitalised/surname.txt'
	else:
	    dictFile = dirPath + '/redactDict/lowerCase/surname.txt'
    elif wordType == 'c':
	if letterCase == 'u':
	    dictFile = dirPath + '/redactDict/upperCase/country.txt'
	elif letterCase == 'c':
	    dictFile = dirPath + '/redactDict/capitalised/country.txt'
	else:
	    dictFile = dirPath + '/redactDict/lowerCase/country.txt'
    elif wordType == 'w':
	if letterCase == 'u':
	    dictFile = dirPath + '/redactDict/upperCase/words.txt'
	elif letterCase == 'c':
	    dictFile = dirPath + '/redactDict/capitalised/words.txt'
	else:
	    dictFile = dirPath + '/redactDict/lowerCase/words.txt'
    return dictFile


def check_dict_files(filepath): #Check if dictionary file exists.
    try:
        file = open(filepath)
	file.close()
	return True
    except IOError:
        print 'Dictionary file not found, please check source repository.'
	return False


def build_sentance(sentance, word): #Build sentance.
    while True:
	if '$word' in sentance:
	    break
	else:
	    print '$word not found, try again. Example: \'The $word crossed the road.\''
    index = sentance.index('$word')
    startSentance = sentance[:index]
    index = index + 5 #remove '$word'
    endSentance = sentance[index:] + '. .'
    builtSentance = startSentance + word + endSentance
    return builtSentance


#Draw word on blank canvas.
#Calculate length in pixels from colour coordinates.
#If word fits, add to Array=<successList>.
def check_word(word, redactAreaX,
 		redactAreaY, fontName,
		fontSize):

    imageDimensionX = redactAreaX + 10
    imageDimensionY = redactAreaY + 5
    img = Image.new('RGB', (imageDimensionX, imageDimensionY))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(fontName, fontSize)
    d.text((0, 0), word, fill=(255,0,0), font=f)
    img = img.convert('P')

    xAndyCoord = []
    for x in range(img.size[1]): #Get coordinates.
	for y in range(img.size[0]):
    	    pixCol = img.getpixel((y,x))
    	    if pixCol == 16 or pixCol == 15 or \
	    pixCol == 14 or pixCol == 13 or \
	    pixCol == 12 or pixCol == 11 or \
	    pixCol == 10:
		xAndyCoord.append((y,x))

    #Convert list to string.
    str1 = ''.join(str(e) for e in xAndyCoord)

    #Strip X and Y value into seperate INT variable.
    xcoord = [int(element.split(",")[0].rstrip().lstrip()) for element in str1[1:-1].split(")(")]
    ycoord = [int(element.split(",")[1].rstrip().lstrip()) for element in str1[1:-1].split(")(")]

    #X and Y maximum length for word.
    maxValueX = max(xcoord)
    maxValueY = max(ycoord)
    minValueX = min(xcoord)
    minValueY = min(ycoord)
    xLength = maxValueX - minValueX
    yLength = maxValueY - minValueY

    #Maximum/minimum threshold for word.
    maxX = redactAreaX# + 1
    minX = redactAreaX - 3
    maxY = redactAreaY# + 1
    minY = redactAreaY - 10 #Big because a word might be all low letters such as "rear".

    #If X and Y dimension falls within threshold.
    if xLength <= maxX and xLength >= minX and yLength <= maxY and yLength >= minY:
	#Success.
	return word
    else:
	#No fit.
	return 0


def output_matches(dirPath, successList): #Writes results to results.txt.
    file = open(dirPath + '/results.txt', 'w')
    for word in successList:
	file.write(word)
	file.write('\n')
    file.close()


def total_matches(total, lengthOfDict): #Return total matches/successes.
    totalMatches = 'Total matches: ' + str(total) + '/' + str(lengthOfDict) + ' words.'
    print totalMatches


def results_message(dirPath):
    print 'Results written to ' + dirPath + '/results.txt.'


def get_font(dirPath): #Return fontName and check if exists.
    while True:
	try:
	    fontName = raw_input('Enter the font (Ext. not needed): ')
	    fontName = dirPath + '/fonts/' + fontName + '.ttf'
	    file = open(fontName)
	    file.close()
	    return fontName
	    break
	except IOError:
	    print 'Font file not found, please try again!'


def get_redaction_box(): #Return redaction box coordinates.
    while True:
	try:
	    print 'Enter 4 coordinates of BBox as shown in object: [n, n, n, n]'
	    lowerLeft = raw_input('')
	    lowerRight = raw_input(lowerLeft + ', ')
	    upperLeft = raw_input(lowerLeft + ', ' + lowerRight + ', ')
	    upperRight = raw_input(lowerLeft + ', ' + lowerRight + ', ' + upperLeft + ', ')
	    print 'Coordinates: ' + '[' + lowerLeft + ', ' + lowerRight + ', ' + upperLeft + ', ' + upperRight + ']'
	    redactAreaX = round(float(upperLeft)) - round(float(lowerLeft))
	    redactAreaY = round(float(upperRight)) - round(float(lowerRight))

	    redactAreaX = int(redactAreaX)
	    redactAreaY = int(redactAreaY)

	    print 'X = ', redactAreaX, ', Y = ', redactAreaY
	    return redactAreaX, redactAreaY
	    break
	except ValueError:
	    print 'Not a valid number, please try again.'


def get_font_size(): #Return fontSize and check if valid integer.
    while True:
	try:
	    fontSize = float(raw_input('Enter the font size: '))
	    fontSize = round(fontSize)
	    fontSize = int(fontSize)
	    if fontSize > 1 and fontSize < 51: #Font ok.
	        return fontSize
	        break
	    else:		 #Too small.
		print 'Positive value required, try again.'
	except ValueError:
	    print 'Not a valid number, please try again.'
