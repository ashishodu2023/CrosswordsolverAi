import time 

def load_dictionary(file_path):
    with open(file_path, 'r') as file:
        return set(word.strip().lower() for word in file.readlines())

def is_valid_word(word, dictionary):
    return word.lower() in dictionary

def is_valid(board, row, col, word, direction, dictionary):
    # Check if the word can be placed in the given position (row, col) and direction
    if direction == 'h':  # horizontal
        for i in range(len(word)):
            if (
                col + i >= 13 or
                (board[row][col + i] != 0 and board[row][col + i] != word[i]) or
                not is_valid_word(word[i], dictionary)
            ):
                return False
    elif direction == 'v':  # vertical
        for i in range(len(word)):
            if (
                row + i >= 12 or
                (board[row + i][col] != 0 and board[row + i][col] != word[i]) or
                not is_valid_word(word[i], dictionary)
            ):
                return False
    else:
        return False

    return True


def forward_check(board, row, col, word, direction, dictionary):
    # Perform forward checking to reduce domain values for neighbors
    if direction == 'h':
        for i in range(len(word)):
            if board[row][col + i] == 0:
                board[row][col + i] = -word[i]
    elif direction == 'v':
        for i in range(len(word)):
            if board[row + i][col] == 0:
                board[row + i][col] = -word[i]

def undo_forward_check(board, row, col, word, direction):
    # Undo forward checking for the given position and direction
    if direction == 'h':
        for i in range(len(word)):
            if board[row][col + i] < 0:
                board[row][col + i] = 0
    elif direction == 'v':
        for i in range(len(word)):
            if board[row + i][col] < 0:
                board[row + i][col] = 0

def solve_puzzle(board, dictionary):
    empty = find_empty_location(board)
    if not empty:
        return True  # Puzzle is solved

    row, col = empty

    for word in dictionary:
        for direction in ['h', 'v']:
            if is_valid(board, row, col, word, direction, dictionary):
                place_word(board, row, col, word, direction)
                forward_check(board, row, col, word, direction, dictionary)

                if solve_puzzle(board, dictionary):
                    return True  # If the puzzle is solved, return True

                # If placing 'word' in the current position leads to an invalid solution,
                # backtrack by undoing the current move and forward checking
                remove_word(board, row, col, word, direction)
                undo_forward_check(board, row, col, word, direction)

    return False  # No valid word was found for the current position

def find_empty_location(board):
    # Find the first empty position in the board
    for i in range(12):
        for j in range(13):
            if board[i][j] == 0:
                return (i, j)  # Return row and column indices

    return None  # If no empty position is found, return None


def place_word(board, row, col, word, direction):
    # Place the word in the board at the given position and direction
    if direction == 'h':
        for i in range(len(word)):
            board[row][col + i] = word[i]
    elif direction == 'v':
        for i in range(len(word)):
            board[row + i][col] = word[i]

def remove_word(board, row, col, word, direction):
    # Remove the word from the board at the given position and direction
    if direction == 'h':
        for i in range(len(word)):
            board[row][col + i] = 0
    elif direction == 'v':
        for i in range(len(word)):
            board[row + i][col] = 0

def load_puzzle(file_path):
    with open(file_path, 'r') as file:
        return [list(line.strip()) for line in file.readlines()]

if __name__ == "__main__":
    start_time = time.time()

    pattern = load_puzzle("grid_hard.txt")
    # Load the dictionary from the file
    dictionary = load_dictionary("Words.txt")

    # Initialize the puzzle with the given pattern
    puzzle = [[0 if cell == '-' else cell for cell in row] for row in pattern]

    # Solve the puzzle
    if solve_puzzle(puzzle, dictionary):
        for row in puzzle:
            print(" ".join(map(str, row)))
        print("\n---Time taken for code execution %s seconditions ---" % (time.time() - start_time))
    else:
        print("No solution exists.")
