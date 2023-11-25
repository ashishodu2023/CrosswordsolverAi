import time

class Variable:
    def __init__(self, direction, row, col, length, domain):
        self.word = ""
        self.direction = direction
        self.row = row
        self.col = col
        self.length = length
        self.domain = domain
        self.removed_domain = {}

def ShowBoard(grid, assignment):
    board = grid.split("\n")
    board = [list(row) for row in board]
    for v in assignment:
        val = assignment[v]
        if v.direction == "horizontal":
            for i in range(v.length):
                board[v.row][v.col + i] = val[i]
        else:
            for i in range(v.length):
                board[v.row + i][v.col] = val[i]
    for row in board:
        print(row)

def SatisfyConstraint(V, assignment, Vx, val):
    for v in V:
        Cxv = MakeConstraint(Vx, v)
        if v != Vx and v in assignment and Cxv:
            if val[Cxv[0]] != assignment[v][Cxv[1]]:
                return False
    return True

def MostConstrainedVariable(V, assignment):
    unassigned = [v for v in V if v not in assignment]
    unassigned.sort(key=lambda x: len(x.domain))
    return unassigned[0] if unassigned else None

def OrderDomainValues(V, assignment, Vx):
    return sorted(Vx.domain, key=lambda val: CountConflicts(V, assignment, Vx, val))

def CountConflicts(V, assignment, Vx, val):
    conflicts = 0
    for v in V:
        Cxv = MakeConstraint(Vx, v)
        if v != Vx and v in assignment and Cxv:
            if val[Cxv[0]] != assignment[v][Cxv[1]]:
                conflicts += 1
    return conflicts

def UnassignedVariable(V, assignment):
    return MostConstrainedVariable(V, assignment)

def DomainReduction(V, assignment, Vx, val):
    for v in V:
        Cxv = MakeConstraint(Vx, v)
        if v != Vx and v not in assignment and Cxv:
            for word in v.domain.copy():
                if val[Cxv[0]] != word[Cxv[1]]:
                    v.domain.remove(word)
                    if v not in Vx.removed_domain:
                        Vx.removed_domain[v] = []
                    Vx.removed_domain[v].append(word)

def OriginalDomain(V, assignment, Vx, val):
    for v in V:
        Cxv = MakeConstraint(Vx, v)
        if v != Vx and v not in assignment and Cxv:
            if v in Vx.removed_domain:
                for word in Vx.removed_domain[v]:
                    if val[Cxv[0]] != word[Cxv[1]]:
                        v.domain.append(word)
                        Vx.removed_domain[v].remove(word)

def BacktrackingAlgo(V, assignment, depth_limit):
    #print("Current Assignment:", assignment)
    if len(assignment) == len(V) or depth_limit == 0:
        return True
    Vx = UnassignedVariable(V, assignment)
    #print("Selected Variable:", Vx)
    for val in OrderDomainValues(V, assignment, Vx):
        if val in assignment.values():
            continue
        if SatisfyConstraint(V, assignment, Vx, val):
            assignment[Vx] = val
            DomainReduction(V, assignment, Vx, val)
            #print(f"Assigned {Vx}: {val}")
            result = BacktrackingAlgo(V, assignment, depth_limit - 1)
            if result:
                return True
        assignment.pop(Vx, None)
        OriginalDomain(V, assignment, Vx, val)
    return False

def Revised(Vx, Vy, Cxy):
    if not Cxy:
        return False
    Revisedd = False
    for x in Vx.domain:
        satisfied = any(x[Cxy[0]] == y[Cxy[1]] for y in Vy.domain)
        if not satisfied:
            Vx.domain.remove(x)
            Revisedd = True
    return Revisedd

def MRVArc(V, arcs):
    mrv_arcs = []
    for arc in arcs:
        X, Y, Cxy = arc
        if X in V and Y in V:
            mrv_arcs.append(arc)
    return mrv_arcs

def MRVBacktrackingAlgo(V, assignment, depth_limit):
    #print("Current Assignment:", assignment)
    if len(assignment) == len(V) or depth_limit == 0:
        return True
    Vx = MostConstrainedVariable(V, assignment)
    #print("Selected Variable:", Vx)
    mrv_arcs = MRVArc(V, MakeArc(V))
    for val in OrderDomainValues(V, assignment, Vx):
        if val in assignment.values():
            continue
        if SatisfyConstraint(V, assignment, Vx, val):
            assignment[Vx] = val
            ForwardChecking(V, assignment, Vx, val)
            #print(f"Assigned {Vx}: {val}")
            result = BacktrackingAlgo(V, assignment, depth_limit - 1)
            if result:
                return True
        assignment.pop(Vx, None)
        OriginalDomain(V, assignment, Vx, val)
    return False

def ForwardChecking(V, assignment, Vx, val):
    for v in V:
        Cxv = MakeConstraint(Vx, v)
        if v != Vx and v not in assignment and Cxv:
            v.domain = [word for word in v.domain if val[Cxv[0]] == word[Cxv[1]]]
    #print("After Forward Checking:", [v.domain for v in V])

def MakeArc(V):
    arcs = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if i != j:
                Cij = MakeConstraint(V[i], V[j])
                if len(Cij) > 0:
                    arcs.append((V[i], V[j], Cij))
    return arcs

def MakeConstraint(Vx, Vy):
    constraint = ()
    if Vx.direction != Vy.direction:
        if Vx.direction == "horizontal":
            if Vy.col >= Vx.col and Vy.col <= Vx.col + Vx.length - 1:
                if Vx.row >= Vy.row and Vx.row <= Vy.row + Vy.length - 1:
                    constraint = (Vy.col - Vx.col, Vx.row - Vy.row)
        else:
            if Vy.row >= Vx.row and Vy.row <= Vx.row + Vx.length - 1:
                if Vx.col >= Vy.col and Vx.col <= Vy.col + Vy.length - 1:
                    constraint = (Vy.row - Vx.row, Vx.col - Vy.col)
    return constraint

def MakeVariables(grid, words):
    variables = []
    board = grid.split("\n")
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == "-":
                if col == 0 or board[row][col - 1] == "#":
                    length = 0
                    for i in range(col, len(board[row])):
                        if board[row][i] == "-":
                            length += 1
                        else:
                            break
                    if length == 1:
                        condition = True
                        try:
                            if board[row][col + 1] == "-":
                                condition = False
                        except IndexError:
                            pass
                        try:
                            if board[row][col - 1] == "-" and col - 1 >= 0:
                                condition = False
                        except IndexError:
                            pass
                        try:
                            if board[row - 1][col] == "-" and row - 1 >= 0:
                                condition = False
                        except IndexError:
                            pass
                        try:
                            if board[row + 1][col] == "-":
                                condition = False
                        except IndexError:
                            pass
                        if condition:
                            domain = []
                            for word in words:
                                if len(word) == length:
                                    domain.append(word)
                            variables.append(Variable(
                                "horizontal",
                                row,
                                col,
                                length,
                                domain
                            ))

                    if length > 1:
                        domain = []
                        for word in words:
                            if len(word) == length:
                                domain.append(word)
                        variables.append(Variable(
                            "horizontal",
                            row,
                            col,
                            length,
                            domain
                        ))
                if row == 0 or board[row - 1][col] == "#":
                    length = 0
                    for i in range(row, len(board)):
                        if board[i][col] == "-":
                            length += 1
                        else:
                            break
                    if length > 1:
                        domain = []
                        for word in words:
                            if len(word) == length:
                                domain.append(word)
                        variables.append(Variable(
                            "vertical",
                            row,
                            col,
                            length,
                            domain
                        ))
    return variables

def GetGrid(file_path):
    with open(file_path) as file:
        return file.read()

def main():
    assignment = {}
    grid = GetGrid("grid_hard.txt")
    words = GetGrid("Words.txt").splitlines()
    words = [word.upper() for word in words]

    variables = MakeVariables(grid, words)
    depth_limit = 50  # Set a depth limit
    MRVBacktrackingAlgo(variables, assignment, depth_limit)
    ShowBoard(grid, assignment)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("\n---Time taken for code execution %s seconds ---" %
          (time.time() - start_time))
