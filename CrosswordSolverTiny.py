import time

def CrosswordSolverTiny(grid, word_data):

    # Function to check if a word can be placed in the given direction at the specified position
    def CheckHorizontalVertical(word, row, col, direction):
        if direction == "ACROSS":
            if col + len(word) > len(grid[0]):
                return False
            for i in range(len(word)):
                if grid[row][col + i] != " " and grid[row][col + i] != word[i]:
                    return False
                if grid[row][col + i] == "#":
                    return False
        else:  # direction == "down"
            if row + len(word) > len(grid):
                return False
            for i in range(len(word)):
                if grid[row + i][col] != " " and grid[row + i][col] != word[i]:
                    return False
                if grid[row + i][col] == "#":
                    return False
        return True

    # Function to set a word in the grid at the specified position and direction
    def SetWord(word, row, col, direction):
        if direction == "ACROSS":
            for i in range(len(word)):
                grid[row][col + i] = word[i]
        else:  # direction == "down"
            for j in range(len(word)):
                grid[row + j][col] = word[j]

    # Function to clear a word from the grid at the specified position and direction
    def GetWord(word, row, col, direction):
        if direction == "ACROSS":
            for i in range(len(word)):
                grid[row][col + i] = " "
        else:  # direction == "down"
            for j in range(len(word)):
                grid[row + j][col] = " "

    # Recursive function to solve the crossword puzzle
    def Solve(grid, word_data):
        if not word_data:
            return True

        variable, start_cell, domain = word_data[0]
        for row, col in start_cell:
            for word in list(domain):
                if CheckHorizontalVertical(word, row, col, variable[1:]):
                    SetWord(word, row, col, variable[1:])
                    domain.remove(word)
                    if Solve(grid, word_data[1:]):
                        return True
                    GetWord(word, row, col, variable[1:])
                    domain.add(word)

        return False

    # Main function to solve the crossword puzzle and print the result
    start_time = time.time()
    if Solve(grid, word_data):
        for row in grid:
            print("".join(row))
        end_time = (time.time() - start_time)
        print(f'\n---Time taken for code execution %s seconds ---{end_time}')
    else:
        print("No solution found")


def main():
    # Example crossword grid and word data
    crossword_grid = [
        [" ", " ", " ", " ", " "],
        ["#", "#", " ", "#", " "],
        ["#", " ", " ", " ", " "],
        [" ", "#", " ", " ", " "],
        [" ", " ", " ", " ", " "],
        [" ", "#", "#", " ", "#"],
    ]

    word_data = [
        ("1ACROSS", [(0, 0)], {"HOSES", "LASER", "SAILS", "SHEET", "STEER"}),
        ("4ACROSS", [(2, 1)], {"HEEL", "HIKE", "KEEL", "KNOT", "LINE"}),
        ("7ACROSS", [(3, 2)], {"AFT", "ALE", "EEL", "LEE", "TIE"}),
        ("8ACROSS", [(4, 0)], {"HOSES", "LASER", "SAILS", "SHEET", "STEER"}),
        ("2DOWN", [(0, 2)], {"HOSES", "LASER", "SAILS", "SHEET", "STEER"}),
        ("3DOWN", [(0, 4)], {"HOSES", "LASER", "SAILS", "SHEET", "STEER"}),
        ("5DOWN", [(2, 3)], {"HEEL", "HIKE", "KEEL", "KNOT", "LINE"}),
        ("6DOWN", [(3, 0)], {"AFT", "ALE", "EEL", "LEE", "TIE"}),
    ]

    # Call the crossword solver function
    CrosswordSolverTiny(crossword_grid, word_data)


if __name__ == '__main__':
    main()
