def house_indices(row, col):
    """Return the indices of the house (row, column, and box) for a given cell."""
    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    return (
        [(row, j) for j in range(9) if j != col],  # Row
        [(i, col) for i in range(9) if i != row],  # Column
        [(i, j) for i in range(box_row, box_row + 3) for j in range(box_col, box_col + 3) if (i, j) != (row, col)]  # Box
    )


class Sudoku:
    def __init__(self, grid=None):
        self.grid = [[0 for _ in range(9)] for _ in range(9)] if grid is None else grid
        self.solved = False

    def is_valid(self, row, col, num):
        """
        Check if we can add num to the board. Row and column must be 0-8.
        """
        assert 0 <= row < 9 and 0 <= col < 9, "Row and column must be between 0 and 8."
        # assert self.grid[row][col] == 0, "Cell must be empty."

        return all(self.grid[row][j] != num for j in range(9) if j != col) and \
        all(self.grid[i][col] != num for i in range(9) if i != row) and \
        num not in [self.grid[i][j] for i in range(3 * (row // 3), 3 * (row // 3) + 3)
                                                        for j in range(3 * (col // 3), 3 * (col // 3) + 3)
                                                        if (i, j) != (row, col)]
    
    def board_valid(self):
        """
        Check if the current board is valid.
        """
        return all(self.is_valid(row, col, self.grid[row][col]) for row in range(9) for col in range(9) if self.grid[row][col] != 0)

    
    def delete(self, row, col):
        assert 0 <= row < 9 and 0 <= col < 9, "Row and column must be between 0 and 8."
        self.grid[row][col] = 0

    def insert(self, row, col, num):
        if self.is_valid(row, col, num):
            self.grid[row][col] = num
        if all(all(cell != 0 for cell in row) for row in self.grid):
            self.solved = True

    def __str__(self):
        separator = list("-" * 25)
        for idx in [0, 8, 16, 24]:
            separator[idx] = "+"
        separator = "".join(separator)

        lines = [separator]
        for i, row in enumerate(self.grid):
            line = "| "
            for j, val in enumerate(row):
                cell = "." if val == 0 else str(val)
                sep = " | " if j in {2, 5} else " "
                line += cell + sep
            lines.append(line.rstrip() + " |")
            if i in {2, 5}:
                lines.append(separator)
        lines.append(separator)
        return "\n".join(lines)
    

class SudokuSolver:
    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.options = self.init_options()
        for row in range(9):
            self.update_options(row, 1)
    
    def init_options(self):
        options = {(i,j): set(range(1, 10)) for i in range(9) for j in range(9)}
        for i in range(9):
            for j in range(9):
                if self.sudoku.grid[i][j] != 0:
                    options[(i, j)] = {self.sudoku.grid[i][j]}
        return options


    def update_options(self, row, col):
        row, col, box = house_indices(row, col)
        for i, j in row:
            if self.sudoku.grid[i][j] == 0:
                for n in self.options[(i, j)].copy():
                    if not self.sudoku.is_valid(i, j, n):
                        self.options[(i, j)].discard(n)
        for i, j in col:
            if self.sudoku.grid[i][j] == 0:
                for n in self.options[(i, j)].copy():
                    if not self.sudoku.is_valid(i, j, n):
                        self.options[(i, j)].discard(n)
        for i, j in box:
            if i != row and j != col and self.sudoku.grid[i][j] == 0:
                for n in self.options[(i, j)].copy():
                    if not self.sudoku.is_valid(i, j, n):
                        self.options[(i, j)].discard(n)


class SudokuBackTracker(SudokuSolver):
    def __init__(self, sudoku):
        super().__init__(sudoku)

    def next_empty(self):
        return min(
            [(i, j) for i in range(9) for j in range(9) if self.sudoku.grid[i][j] == 0],
            key=lambda pos: len(self.options[pos])
        )
    
    # def solve_aux(self, row, col):
    #     if self.sudoku.solved:
    #         return
        
    #     if self.sudoku.grid[row][col] != 0:
    #         print('how did we get here?')
    #         return
        
    #     for num in self.options[(row, col)]:
    #         pass


    def solve_aux(self, row, col):
        if self.sudoku.solved:
            return
        
        if self.sudoku.grid[row][col] != 0:
            next_row, next_col = self.next_empty()
            self.solve_aux(next_row, next_col)
            return
        
        for num in self.options[(row, col)]:
            # print(f'Trying {num} at ({row}, {col})')
            if self.sudoku.is_valid(row, col, num):
                self.sudoku.insert(row, col, num)
                self.update_options(row, col)
                try:
                    next_row, next_col = self.next_empty()
                    self.solve_aux(next_row, next_col)
                finally:
                    if self.sudoku.solved:
                        return
                
                # Backtrack
                self.sudoku.delete(row, col)
                self.options = self.init_options()
                for r in range(9):
                    self.update_options(r, 1)
                

    
    def solve(self):
        return self.solve_aux(*self.next_empty())

    

if __name__ == '__main__':
    # legal sudoku grid:
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

    sudoku = Sudoku(grid)
    solver = SudokuBackTracker(sudoku)
    # for key in solver.options:
    #     print(f"{key}: {solver.options[key]}")

    print('*****')
    solver.solve()
    print(solver.sudoku)
