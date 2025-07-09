import python.sudoku as sudoku
import time


GROUND_TRUTH = [[3, 5, 6, 8, 9, 7, 4, 1, 2], [8, 4, 1, 5, 2, 3, 7, 6, 9], [7, 2, 9, 4, 6, 1, 5, 8, 3], [1, 9, 2, 7, 3, 8, 6, 4, 5], [5, 3, 7, 9, 4, 6, 8, 2, 1], [6, 8, 4, 1, 5, 2, 3, 9, 7], [4, 7, 8, 3, 1, 9, 2, 5, 6], [2, 1, 5, 6, 7, 4, 9, 3, 8], [9, 6, 3, 2, 8, 5, 1, 7, 4]]


class LogicSolver(sudoku.SudokuSolver):
    def __init__(self, sudoku):
        super().__init__(sudoku)
        self.steps = []
        self.methods = [self.naked_single, self.hidden_single, self.naked_pair]

    def insert(self, row, col, num):
        self.sudoku.insert(row, col, num)
        self.update_options(row, col)

    def naked_single(self):
        for i in range(9):
            for j in range(9):
                if self.sudoku.grid[i][j] == 0 and len(self.options[(i, j)]) == 1:
                    self.steps.append({"loc": [(i, j)], "desc": None, "val": next(iter(self.options[(i, j)])), "strategy": "Naked Single"})
                    return True
        return False

    def hidden_single(self):
        for i in range(9):
            for j in range(9):
                if self.sudoku.grid[i][j] == 0:
                    row, col, box = sudoku.house_indices(i, j)
                    candidates = self.options[(i, j)]
                    for num in candidates:
                        if all(num not in self.options[cell] for cell in row) or \
                           all(num not in self.options[cell] for cell in col) or \
                           all(num not in self.options[cell] for cell in box):
                            self.steps.append({"loc": [(i, j)], "desc": None, "val": num, "strategy": "Hidden Single"})
                            self.options[(i, j)] = {num}
                            return True
        return False
    
    def naked_pair(self):
        for i in range(9):
            for j in range(9):
                if self.sudoku.grid[i][j] == 0 and len(self.options[i, j]) == 2:
                    pair = self.options[i, j]
                    for k, house in enumerate(sudoku.house_indices(i, j)):
                        for cell in house:
                            if self.sudoku.grid[cell[0]][cell[1]] == 0 and len(self.options[cell]) == 2:
                                if self.options[cell] == pair:
                                    for other_cell in house:
                                        if other_cell != cell and self.sudoku.grid[other_cell[0]][other_cell[1]] == 0 and self.options[(i, j)] & self.options[other_cell]:
                                            self.steps.append({"loc": [(i,j), cell], "desc": ["row", "column", "box"][k], "val": pair, "strategy": "Naked Pair"})
                                            return True
                    
                    # for cell in col:
                    #     if self.sudoku.grid[cell[0]][cell[1]] == 0 and len(self.options[cell]) == 2:
                    #         if tuple(sorted(self.options[cell])) == pair:
                    #             for other_cell in col:
                    #                 if other_cell != cell and self.sudoku.grid[other_cell[0]][other_cell[1]] == 0 and self.options[(i, j)] & self.options[other_cell]:
                    #                     self.steps.append(([(i,j), cell], "column", pair, "Naked Pair"))
                    #                     return True
                    # for cell in box:
                    #     if self.sudoku.grid[cell[0]][cell[1]] == 0 and len(self.options[cell]) == 2:
                    #         if tuple(sorted(self.options[cell])) == pair:
                    #             for other_cell in box:
                    #                 if other_cell != cell and self.sudoku.grid[other_cell[0]][other_cell[1]] == 0 and self.options[(i, j)] & self.options[other_cell]:
                    #                     self.steps.append(([(i,j), cell], "box", pair, "Naked Pair"))
                    #                     return True
        return False
    
    def solve(self):
        idx = 0
        start = time.time()
        while True:
            for method in self.methods:
                if method():
                    step = self.steps[idx]
                    print(f"Step {idx + 1: 3d}: {step['strategy']} at {step['loc']}, value(s) {step['val']}")
                    if step['strategy'] in ("Naked Single", "Hidden Single"):
                        self.insert(*(step['loc'][0]), step['val'])
                    elif step['strategy'] == "Naked Pair":
                        house = sudoku.house_indices(*step['loc'][0])
                        for i in range(3):
                            if step['loc'][1] in house[i]:
                                for cell in house[i]:
                                    if cell != step['loc'][1]:
                                        self.options[cell] -= step['val']
                        print(self.sudoku)
                    idx += 1
                    break
            else:
                if not self.sudoku.solved:
                    print("No more methods to apply.")
                    return False
                print(f"Sudoku solved in {(time.time() - start):.4f} seconds.")
                return True
            
    
if __name__ == "__main__":
    # Example usage
    grid = [
        [3, 0, 0, 0, 0, 7, 0, 1, 0,],
        [0, 4, 0, 5, 2, 0, 0, 0, 0,],
        [7, 0, 9, 4, 0, 0, 0, 0, 0,],
        [1, 0, 2, 0, 0, 0, 0, 0, 0,],
        [0, 0, 7, 9, 0, 6, 8, 0, 0,],
        [0, 0, 0, 0, 0, 0, 3, 0, 7,],
        [0, 0, 0, 0, 0, 9, 2, 0, 6,],
        [0, 0, 0, 0, 7, 4, 0, 3, 0,],
        [0, 6, 0, 2, 0, 0, 0, 0, 4,]
    ]

    sudoku_instance = sudoku.Sudoku(grid)
    print(sudoku_instance)
    solver = LogicSolver(sudoku_instance)
    if solver.solve():
        print("Sudoku solved:")
        print(solver.sudoku)
    else:
        print("No solution found.")
        print(solver.sudoku)
        print(solver.options)