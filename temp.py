def load_words_from_file(filename):
    with open(filename, 'r') as file:
        return set(line.strip().upper() for line in file)

def solve_crossword(crossword, words):
    rows, cols = len(crossword), len(crossword[0])

    def is_valid(word, row, col, direction):
        if direction == 'across':
            return (
                col + len(word) <= cols and
                all(
                    crossword[row][col + i] == word[i] or crossword[row][col + i] == '0'
                    for i in range(len(word))
                )
            )
        else:
            return (
                row + len(word) <= rows and
                all(
                    crossword[row + i][col] == word[i] or crossword[row + i][col] == '0'
                    for i in range(len(word))
                )
            )

    def place_word(word, row, col, direction):
        if direction == 'across':
            for i in range(len(word)):
                crossword[row] = crossword[row][:col + i] + word[i] + crossword[row][col + i + 1:]
        else:
            for i in range(len(word)):
                crossword[row + i] = crossword[row + i][:col] + word[i] + crossword[row + i][col + 1:]

    def remove_word(word, row, col, direction):
        if direction == 'across':
            for i in range(len(word)):
                crossword[row] = crossword[row][:col + i] + '0' + crossword[row][col + i + 1:]
        else:
            for i in range(len(word)):
                crossword[row + i] = crossword[row + i][:col] + '0' + crossword[row + i][col + 1:]

    def get_mrv_cell():
        min_remaining = float('inf')
        mrv_cell = None
        for row in range(rows):
            for col in range(cols):
                if crossword[row][col] == '0':
                    remaining_options = 0
                    for word in words:
                        for direction in ['across', 'down']:
                            if is_valid(word, row, col, direction):
                                remaining_options += 1
                    if remaining_options < min_remaining:
                        min_remaining = remaining_options
                        mrv_cell = (row, col)
        return mrv_cell

    def get_lcv_values(cell):
        row, col = cell
        lcv_values = []
        for word in words:
            if word not in used_words:
                for direction in ['across', 'down']:
                    if is_valid(word, row, col, direction):
                        remaining_options = 0
                        for r in range(rows):
                            for c in range(cols):
                                if crossword[r][c] == '0':
                                    for other_word in words:
                                        for other_direction in ['across', 'down']:
                                            if (r, c) != cell and is_valid(other_word, r, c, other_direction):
                                                if (r == row and other_direction == 'down') or (c == col and other_direction == 'across'):
                                                    remaining_options += 1
                        lcv_values.append((word, remaining_options))
        lcv_values.sort(key=lambda x: x[1])
        return [x[0] for x in lcv_values]

    def solve():
        cell = get_mrv_cell()
        if cell is None:
            return True  # All cells filled; puzzle solved

        row, col = cell
        for word in get_lcv_values(cell):
            if word not in used_words:
                for direction in ['across', 'down']:
                    if is_valid(word, row, col, direction):
                        used_words.add(word)
                        place_word(word, row, col, direction)
                        if solve():
                            return True
                        remove_word(word, row, col, direction)
                        used_words.remove(word)
        return False

    used_words = set()
    return solve()

crossword = [
    "##000000##",
    "##0#####0#",
    "##0#####0#",
    "##0##0000#",
    "##0###0##0",
    "###0#0###0",
    "###0#0#0##",
    "0###000#0#",
    "0##0#0###0",
    "000000#0##",
    "##0###0###"
]

dictionary_file = "Words.txt"
word_list = load_words_from_file(dictionary_file)

if solve_crossword(crossword, word_list):
    for row in crossword:
        print(row)
else:
    print("No solution found.")
