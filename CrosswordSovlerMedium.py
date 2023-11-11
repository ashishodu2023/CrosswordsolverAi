import copy
import multiprocessing
import random
import signal

import numpy as np
import time


###########
### CLASSES
###########

class Intersection:
    def __init__(self, coord, index, intersectedID):
        self.coord = coord
        self.index = index
        self.intersectedID = intersectedID


class Word:
    def __init__(self, pos, horizontal, length, remainingValues, idN):
        self.pos = pos
        self.horizontal = horizontal
        self.length = length
        self.remainingValues = remainingValues
        self.letters = [0] * length
        self.id = idN
        self.intersections = []
        self.intersectionsNumber = 0


#################
### FETCHING DATA
#################

# Reading crossword and turning it into a nparray
def read_crossword(crossword):
    table = []
    for line in open(crossword):
        noTabs = list(line.split())
        for i, v in enumerate(noTabs):
            if v == "#":
                noTabs[i] = "35"
        table.append(noTabs)
    npTable = np.array(table, dtype=np.uint8)
    return npTable


# function to get the ID of a vertical word from given coordinates
# returns -1 if the word is not found
def getVerticalIdByCoordinate(coord, verticalWords):
    for w in verticalWords:
        if w.pos[1] == coord[1]:
            if w.pos[0] <= coord[0] <= w.pos[0] + w.length:
                return w.id
    return -1


# function to get the ID of a horizontal word from given coordinates
# returns -1 if the word is not found
def getHorizontalIdByCoordinate(coord, horizontalWords):
    for w in horizontalWords:
        if w.pos[0] == coord[0]:
            if w.pos[1] <= coord[1] <= w.pos[1] + w.length:
                return w.id
    return -1


# Looks for all horizontal words to fill in the crossword
def lookupHorizontalVariables(npTable, idN):
    foundWords = []

    for x in range(0, npTable.shape[0]):
        len = 0
        for y in range(1, npTable.shape[1]):
            if len == 0:
                if npTable[x][y - 1] != 35 and npTable[x][y] != 35:
                    len = 2
                    continue
            if len > 1:
                if npTable[x][y] != 35:
                    len += 1
                    continue
                else:
                    pos = (x, y - len)
                    foundWords.append(Word(pos, 1, len, len, idN))
                    idN += 1
                    len = 0

        if len > 1:
            pos = (x, npTable.shape[1] - len)
            word = Word(pos, 1, len, len, idN)
            idN += 1
            foundWords.append(word)
    return foundWords


# Looks for all vertical words to fill in the crossword
def lookupVerticalVariables(npTable, idN):
    foundWords = []
    for y in range(0, npTable.shape[1]):
        len = 0
        for x in range(1, npTable.shape[0]):
            if len == 0:
                if npTable[x - 1][y] != 35 and npTable[x][y] != 35:
                    len = 2
                    continue

            if len > 1:
                if npTable[x][y] != 35:
                    len += 1
                    continue
                else:
                    pos = (x - len, y)
                    foundWords.append(Word(pos, 0, len, len, idN))
                    idN += 1
                    len = 0
        if len > 1:
            pos = (npTable.shape[0] - len, y)
            word = Word(pos, 0, len, len, idN)
            idN += 1
            foundWords.append(word)
    return foundWords


# From a set of given words and the board, it finds all the intersections
# and stores them in an attribute in its corresponding word
def lookupIntersections(words, horizontalWords, verticalWords, crossword):
    for w in words:
        if w.horizontal == 1:
            yStart = w.pos[1]
            yEnd = yStart + w.length - 1
            for y in range(yStart, yEnd + 1):
                if w.pos[0] > 0:
                    if crossword[w.pos[0] - 1][y] == 0:
                        index = y - w.pos[1]
                        intersectedId = getVerticalIdByCoordinate((w.pos[0], y), verticalWords)
                        w.intersections.append(Intersection((w.pos[0], y), index, intersectedId))
                        continue
                if w.pos[0] < crossword.shape[0] - 1:
                    if crossword[w.pos[0] + 1][y] == 0:
                        index = y - w.pos[1]
                        intersectedId = getVerticalIdByCoordinate((w.pos[0], y), verticalWords)
                        w.intersections.append(Intersection((w.pos[0], y), index, intersectedId))
        else:
            xStart = w.pos[0]
            xEnd = xStart + w.length - 1
            for x in range(xStart, xEnd + 1):
                if w.pos[1] > 0:
                    if crossword[x][w.pos[1] - 1] == 0:
                        index = x - w.pos[0]
                        intersectedId = getHorizontalIdByCoordinate((x, w.pos[1]), horizontalWords)
                        w.intersections.append(Intersection((x, w.pos[1]), index, intersectedId))
                        continue
                if w.pos[1] < crossword.shape[1] - 1:
                    if crossword[x][w.pos[1] + 1] == 0:
                        index = x - w.pos[0]
                        intersectedId = getHorizontalIdByCoordinate((x, w.pos[1]), horizontalWords)
                        w.intersections.append(Intersection((x, w.pos[1]), index, intersectedId))
        w.intersectionsNumber = len(w.intersections)

    return words


# Fetching words from the given file
def fillupDictionary(dictPath):
    # Dictionary with all the words.
    # Each key is the size of the word.
    # Each value is a 2D numpy array. The first dimension is the word,
    # the second dimension contains the letter from each word.

    dict = {}

    for line in open(dictPath, encoding="Windows-1252"):
        word = line[:-1]
        size = len(word)
        byteArr = bytearray(word, 'Windows-1252')
        asciiWord = list(byteArr)

        if size in dict:
            dict[size].append(asciiWord)
        else:
            dict[size] = [asciiWord]

    # Transforming list into numpy array
    for k, v in dict.items():
        random.shuffle(v)
        numpyArr = np.array(v, dtype=np.uint8)
        dict[k] = numpyArr

    return dict


# Returns the domain of a given variable
def domain(var, d):
    return d[var.id]


######################################
### WRITING VARIABLES AND SHOWING DATA
######################################

# Write lva values to crossword in a readable format
def storeLvaToCrossword(lva, crossword):
    for word in lva.values():
        index = 0
        if word.horizontal == 1:
            x = word.pos[0]
            for y in range(word.pos[1], word.pos[1] + word.length):
                crossword[x][y] = word.letters[index]
                index += 1
        else:
            y = word.pos[1]
            for x in range(word.pos[0], word.pos[0] + word.length):
                crossword[x][y] = word.letters[index]
                index += 1
    return crossword


# Writes a single word to the crossword
def storeWordToCrossword(word, crossword):
    index = 0
    if word.horizontal == 1:
        x = word.pos[0]
        for y in range(word.pos[1], word.pos[1] + word.length):
            crossword[x][y] = word.letters[index]
            index += 1
    else:
        y = word.pos[1]
        for x in range(word.pos[0], word.pos[0] + word.length):
            crossword[x][y] = word.letters[index]
            index += 1
    return crossword


# Formatting and printing the crossword
def printCrossword(crossword):
    print('\n'.join([''.join(['{:4}'.format(chr(item))
                              for item in row]) for row in crossword]))

#################################
### MAIN FUNCTIONS OF THE PROGRAM
#################################

# From a given value, checks all restrictions from other variables
def restrictionsOK(var, cWord, lva, r):
    intersections = var.intersections

    for i in intersections:
        if i.intersectedID not in lva:
            continue

        intersectedWord = lva[i.intersectedID]
        candidateValue = cWord[i.index]

        if intersectedWord.horizontal == 1:
            intersectionIndex = i.coord[1] - intersectedWord.pos[1]
            intersectedValue = intersectedWord.letters[intersectionIndex]
        else:
            intersectionIndex = i.coord[0] - intersectedWord.pos[0]
            intersectedValue = intersectedWord.letters[intersectionIndex]

        if intersectedValue != candidateValue:
            return False

    return True


# writing to LVA list a new variable with a (so far) correct value
def insertLva(lva, var, cWord):
    var.letters = cWord.tolist()
    lva[var.id] = var
    return lva


# main function of the backtracking algorithm
def backtracking(lva, lvna, d, r, crossword):
    # crossword = storeLvaToCrossword(lva, crossword)
    # printCrossword(crossword)

    if not lvna:
        return lva, 1

    var = lvna[0]

    domainValues = domain(var, d)
    for cWord in domainValues:

        if restrictionsOK(var, cWord, lva, 0):

            lva = insertLva(lva, var, cWord)
            lva, r = backtracking(lva, lvna[1:], d, r, crossword)
            if r == 1:
                return lva, r

    # deleting the found value for current var if
    # it was  a dead-end on deeper calls of the function
    if r == 0 and var.id in lva:
        lva.pop(var.id)

    return lva, 0


# Used in forward checking, it updates all the domains that
# variables restricted by the current one will have
def updateDomains(var, lvna, cr, d):
    isDomainOk = True
    dTemp = copy.copy(d)

    idDict = {}
    for i, vna in enumerate(lvna):
        idDict[vna.id] = i

    for inter in var.intersections:
        if inter.intersectedID not in idDict:
            continue

        intersectedWordIndex = idDict[inter.intersectedID]

        wordIntersected = lvna[intersectedWordIndex]
        tempDomain = dTemp[wordIntersected.id]

        x = inter.coord[0]
        y = inter.coord[1]

        indexInter = 0
        for inte in wordIntersected.intersections:
            if inte.intersectedID == var.id:
                indexInter = inte.index

        existingValue = cr[x][y]
        if existingValue > 64:  # is a letter
            subIndex = np.where(tempDomain[:, indexInter] == existingValue)
            tempDomain = tempDomain[subIndex]
            if tempDomain.shape[0] == 0:
                isDomainOk = False
                break

        dTemp[wordIntersected.id] = tempDomain
        lvna[intersectedWordIndex].remainingValues = tempDomain.shape[0]

    if not isDomainOk:
        return None
    else:
        return dTemp


# main function for the backtracking forward checking algorithm
def backtrackingForwardChecking(lva, lvna, d, r, crosswordRestrictions):
    if not lvna:
        printCrossword(crosswordRestrictions)
        return lva, 1

    lvna.sort(key=lambda x: x.remainingValues)

    var = lvna[0]

    domainValues = domain(var, d)

    for cWord in domainValues:
        if not restrictionsOK(var, cWord, lva, 0):
            continue

        var.letters = cWord.tolist()
        crosswordRestrictionsBackup = copy.copy(crosswordRestrictions)
        crosswordRestrictions = storeWordToCrossword(var, crosswordRestrictions)

        updateDomainsResult = updateDomains(var, lvna, crosswordRestrictions, d)

        if updateDomainsResult is None:
            var.letters = [0] * var.length
            crosswordRestrictions = crosswordRestrictionsBackup
            continue

        lva = insertLva(lva, var, cWord)
        lva, r = backtrackingForwardChecking(lva, lvna[1:], updateDomainsResult, r, crosswordRestrictions)
        if r == 1:
            return lva, r

    # deleting the found value for current var if
    # it was  a dead-end on deeper calls of the function
    if r == 0 and var.id in lva:
        lva.pop(var.id)

    return lva, 0


# Creating a domain for each variable
def createDomains(dict, words):
    domains = {}
    for w in words:
        domains[w.id] = dict[w.length]
        w.remainingValues = dict[w.length].shape[0]

    return domains, words


def shuffleDomains(d):
    for k, v in d.items():
        np.random.shuffle(v)
        d[k] = v
    return d

# Handler used on signal
def handler(signum, frame):
    raise Exception("end of time")


# Handling function timeout using SIGALRM
def handlingLongCrosswordSignal(words, domains, crossword):

    # only works on UNIX

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    try:
        backtrackingForwardChecking({}, copy.deepcopy(words), copy.deepcopy(domains), 0, copy.deepcopy(crossword))
    except Exception as exc:
        print(exc)
        handlingLongCrosswordSignal(words, domains, crossword)


# Handling function timeout using Process.join()
def handlingLongCrosswordJoin(words, domains, crossword):

    # Using processes and not threads because formers don't share variables.

    p = multiprocessing.Process(target=backtrackingForwardChecking, args=({}, words, domains, 0, crossword))
    p.start()

    p.join(1)

    if p.is_alive():
        p.kill()
        p.join()
        domains = shuffleDomains(domains)
        handlingLongCrosswordJoin(words, domains, crossword)


def main(crosswordName, dicName, isForwardChecking):
    startTime = time.time()

    crossword = read_crossword(crosswordName)

    horizontalWords = lookupHorizontalVariables(crossword, 0)
    verticalWords = lookupVerticalVariables(crossword, len(horizontalWords))
    words = horizontalWords + verticalWords
    words = lookupIntersections(words, horizontalWords, verticalWords, crossword)

    dict = fillupDictionary(dicName)
    domains, words = createDomains(dict, words)

    if not isForwardChecking:
        BTstart = time.time()

        lva, r = backtracking({}, words, domains, 0, crossword)
        crossword = storeLvaToCrossword(lva, crossword)
        printCrossword(crossword)

        BTend = time.time()
        BTelapsedTime = BTend - BTstart
        print("\nBacktracking: ", BTelapsedTime, "seconds")

    else:
        FCstart = time.time()
        if crosswordName == "grid.txt":
            handlingLongCrosswordJoin(words, domains, crossword)
        else:

            lva, r = backtrackingForwardChecking({}, words, domains, 0, crossword)
        FCend = time.time()
        FCelapsedTime = FCend - FCstart
        print("\nForward Checking: ", FCelapsedTime, "seconds")

    endTime = time.time()
    totalElapsedTime = endTime - startTime

    print("Total elapsed time: ", totalElapsedTime, "seconds\n\n")


if __name__ == '__main__':

    print("Crossword solution\n")
    main("grid.txt", "Words.txt", True)
