import time
import nltk
from collections import deque

# Load words from a file and filter for English words
def LoadDictionary(file_path):
    with open(file_path, 'r') as file:
        all_words = set(word.strip().lower() for word in file.readlines())

    english_words = set(w.lower() for w in nltk.corpus.words.words())

    return all_words.intersection(english_words)

# Check if a given word is valid based on the loaded dictionary
def IsValidWord(word, dictionary):
    return word.lower() in dictionary

# Check if a word can be placed on the board at a specific location and direction
def IsValidLocation(board, row, col, word, direction, dictionary):
    if direction == 'horizontal':
        for i in range(len(word)):
            if (
                col + i >= 13 or
                (board[row][col + i] != 0 and board[row][col + i] != word[i]) or
                not IsValidWord(word[i], dictionary)
            ):
                return False
    elif direction == 'vertical':
        for i in range(len(word)):
            if (
                row + i >= 12 or
                (board[row + i][col] != 0 and board[row + i][col] != word[i]) or
                not IsValidWord(word[i], dictionary)
            ):
                return False
    else:
        return False

    return True

# Solve the puzzle using backtracking
def SolvePuzzleBacktracking(board, dictionary, remaining_words):
    empty = EmptyLocations(board)
    if not empty:
        return True

    row, col = empty

    for word in remaining_words[row][col].copy():
        for direction in ['horizontal', 'vertical']:
            if IsValidLocation(board, row, col, word, direction, dictionary):
                PlaceWords(board, row, col, word, direction)

                # Update the remaining words after placing a word
                UpdateWords(board, remaining_words, dictionary)

                if SolvePuzzleBacktracking(board, dictionary, remaining_words):
                    return True

                RemoveWords(board, row, col, word, direction)

    return False

# Update the set of remaining words for each empty cell on the board
def UpdateWords(board, remaining_words, dictionary):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                remaining_words[i][j] = GetValidWords(board, i, j, dictionary)

# Get the set of valid words for a specific location on the board
def GetValidWords(board, row, col, dictionary):
    valid_words = set()

    for word in dictionary:
        for direction in ['horizontal', 'vertical']:
            if IsValidLocation(board, row, col, word, direction, dictionary):
                valid_words.add(word)

    return valid_words

# Find the first empty location on the board
def EmptyLocations(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

# Place a word on the board at a specific location and direction
def PlaceWords(board, row, col, word, direction):
    if direction == 'horizontal':
        for i in range(len(word)):
            board[row][col + i] = word[i]
    elif direction == 'vertical':
        for i in range(len(word)):
            board[row + i][col] = word[i]

# Remove a word from the board at a specific location and direction
def RemoveWords(board, row, col, word, direction):
    if direction == 'horizontal':
        for i in range(len(word)):
            board[row][col + i] = 0
    elif direction == 'vertical':
        for i in range(len(word)):
            board[row + i][col] = 0

# Load the puzzle from a file
def LoadGrid(file_path):
    with open(file_path, 'r') as file:
        return [list(line.strip()) for line in file.readlines()]

if __name__ == "__main__":
    start_time = time.time()

    # Load puzzle and dictionary
    pattern = LoadGrid("grid_hard.txt")
    dictionary = LoadDictionary("Words.txt")

    # Initialize the puzzle, replacing '-' with 0
    puzzle = [[0 if cell == '-' else cell for cell in row] for row in pattern]

    # Initialize the remaining_words variable
    remaining_words = [
        [GetValidWords(puzzle, i, j, dictionary) if puzzle[i][j] == 0 else set() for j in range(13)] for i in range(12)
    ]

    # Solve the puzzle and print the result
    if SolvePuzzleBacktracking(puzzle, dictionary, remaining_words):
        for row in puzzle:
            print(" ".join(map(str, row)))
        print("\n---Time taken for code execution %s seconds ---" % (time.time() - start_time))
    else:
        print("No solution exists.")
