import time
import nltk
from collections import deque

def load_dictionary(file_path):
    with open(file_path, 'r') as file:
        all_words = set(word.strip().lower() for word in file.readlines())

    english_words = set(w.lower() for w in nltk.corpus.words.words())

    return all_words.intersection(english_words)

def is_valid_intersection(board, row, col, word, direction, dictionary):
    if direction == 'horizontal':
        for i in range(len(word)):
            if col + i >= 13 or (board[row][col + i] != 0 and board[row][col + i] != word[i]):
                return False
    elif direction == 'vertical':
        for i in range(len(word)):
            if row + i >= 12 or (board[row + i][col] != 0 and board[row + i][col] != word[i]):
                return False
    return True


def is_valid(board, row, col, word, direction, dictionary):
    if direction == 'horizontal':
        for i in range(len(word)):
            if (
                col + i >= 13 or
                (board[row][col + i] != 0 and board[row][col + i] != word[i]) or
                not is_valid_word(word[i], dictionary) or
                not is_valid_intersection(board, row, col + i, word, direction, dictionary)
            ):
                return False
    elif direction == 'vertical':
        for i in range(len(word)):
            if (
                row + i >= 12 or
                (board[row + i][col] != 0 and board[row + i][col] != word[i]) or
                not is_valid_word(word[i], dictionary) or
                not is_valid_intersection(board, row + i, col, word, direction, dictionary)
            ):
                return False
    else:
        return False

    return True

def solve_puzzle(board, dictionary, remaining_words):
    empty = find_empty_location(board)
    if not empty:
        return True

    row, col = empty

    for word in remaining_words[row][col].copy():
        for direction in ['horizontal', 'vertical']:
            if is_valid(board, row, col, word, direction, dictionary):
                place_word(board, row, col, word, direction)

                # Update the remaining words after placing a word
                update_remaining_words(board, remaining_words, dictionary)

                if solve_puzzle(board, dictionary, remaining_words):
                    return True

                remove_word(board, row, col, word, direction)

    return False

def update_remaining_words(board, remaining_words, dictionary):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                remaining_words[i][j] = get_valid_words(board, i, j, dictionary)

def get_valid_words(board, row, col, dictionary):
    valid_words = set()

    for word in dictionary:
        for direction in ['horizontal', 'vertical']:
            if is_valid(board, row, col, word, direction, dictionary):
                valid_words.add(word)

    return valid_words

def find_empty_location(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

def place_word(board, row, col, word, direction):
    if direction == 'horizontal':
        for i in range(len(word)):
            board[row][col + i] = word[i]
    elif direction == 'vertical':
        for i in range(len(word)):
            board[row + i][col] = word[i]

def remove_word(board, row, col, word, direction):
    if direction == 'horizontal':
        for i in range(len(word)):
            board[row][col + i] = 0
    elif direction == 'vertical':
        for i in range(len(word)):
            board[row + i][col] = 0


def load_puzzle(file_path):
    with open(file_path, 'r') as file:
        return [list(line.strip()) for line in file.readlines()]

def is_valid_word(word, dictionary):
    return word.lower() in dictionary


if __name__ == "__main__":
    start_time = time.time()

    pattern = load_puzzle("grid_hard.txt")
    dictionary = load_dictionary("Words.txt")

    puzzle = [[cell if cell != '#' else '-' for cell in row] for row in pattern]


    # Initialize the remaining_words variable
    remaining_words = [
        [get_valid_words(puzzle, i, j, dictionary) if puzzle[i][j] == 0 else set() for j in range(13)] for i in range(12)
    ]

    if solve_puzzle(puzzle, dictionary, remaining_words):
        for row in puzzle:
            print(" ".join(map(str, row)))
        print("\n---Time taken for code execution %s seconds ---" % (time.time() - start_time))
    else:
        print("No solution exists.")
