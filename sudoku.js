function houseIndices(row, col) {
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;
    const rowIndices = [...Array(9).keys()].filter(j => j !== col).map(j => [row, j]);
    const colIndices = [...Array(9).keys()].filter(i => i !== row).map(i => [i, col]);
    const boxIndices = [];
    for (let i = boxRow; i < boxRow + 3; i++) {
      for (let j = boxCol; j < boxCol + 3; j++) {
        if (i !== row || j !== col) boxIndices.push([i, j]);
      }
    }
    return [rowIndices, colIndices, boxIndices];
  }
  
  class Sudoku {
    constructor(grid = null) {
      this.grid = grid ? grid.map(row => [...row]) : Array.from({ length: 9 }, () => Array(9).fill(0));
      this.solved = false;
    }
  
    isValid(row, col, num) {
      for (let j = 0; j < 9; j++) if (j !== col && this.grid[row][j] === num) return false;
      for (let i = 0; i < 9; i++) if (i !== row && this.grid[i][col] === num) return false;
      const boxRow = Math.floor(row / 3) * 3;
      const boxCol = Math.floor(col / 3) * 3;
      for (let i = boxRow; i < boxRow + 3; i++) {
        for (let j = boxCol; j < boxCol + 3; j++) {
          if ((i !== row || j !== col) && this.grid[i][j] === num) return false;
        }
      }
      return true;
    }
  
    boardValid() {
      for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
          const val = this.grid[row][col];
          if (val !== 0 && !this.isValid(row, col, val)) return false;
        }
      }
      return true;
    }
  
    delete(row, col) {
      this.grid[row][col] = 0;
    }
  
    insert(row, col, num) {
      if (this.isValid(row, col, num)) {
        this.grid[row][col] = num;
        if (this.grid.every(row => row.every(cell => cell !== 0))) {
          this.solved = true;
        }
      }
    }
  
    toString() {
      const lines = ["+-------+-------+-------+"];
      for (let i = 0; i < 9; i++) {
        let line = "|";
        for (let j = 0; j < 9; j++) {
          const cell = this.grid[i][j] === 0 ? "." : this.grid[i][j];
          line += ` ${cell}`;
          if ((j + 1) % 3 === 0) line += " |";
        }
        lines.push(line);
        if ((i + 1) % 3 === 0) lines.push("+-------+-------+-------+");
      }
      return lines.join("\n");
    }
  }
  
  class SudokuSolver {
    constructor(sudoku) {
      this.sudoku = sudoku;
      this.options = this.initOptions();
      for (let row = 0; row < 9; row++) {
        this.updateOptions(row, 1); // just trigger pruning
      }
    }
  
    initOptions() {
      const options = {};
      for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
          const val = this.sudoku.grid[i][j];
          options[`${i},${j}`] = val !== 0 ? new Set([val]) : new Set([1,2,3,4,5,6,7,8,9]);
        }
      }
      return options;
    }
  
    updateOptions(row, col) {
      const [rowSet, colSet, boxSet] = houseIndices(row, col);
      const all = [...rowSet, ...colSet, ...boxSet];
      for (const [i, j] of all) {
        if (this.sudoku.grid[i][j] === 0) {
          for (const n of Array.from(this.options[`${i},${j}`])) {
            if (!this.sudoku.isValid(i, j, n)) {
              this.options[`${i},${j}`].delete(n);
            }
          }
        }
      }
    }
  }
  
  class SudokuBackTracker extends SudokuSolver {
    constructor(sudoku) {
      super(sudoku);
    }
  
    nextEmpty() {
      const empty = [];
      for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
          if (this.sudoku.grid[i][j] === 0) {
            empty.push([i, j]);
          }
        }
      }
      return empty.reduce((a, b) => (
        this.options[`${a[0]},${a[1]}`].size <= this.options[`${b[0]},${b[1]}`].size ? a : b
      ));
    }
  
    solveAux(row, col) {
      if (this.sudoku.solved) return;
      if (this.sudoku.grid[row][col] !== 0) {
        const [nextRow, nextCol] = this.nextEmpty();
        return this.solveAux(nextRow, nextCol);
      }
  
      for (const num of this.options[`${row},${col}`]) {
        if (this.sudoku.isValid(row, col, num)) {
          this.sudoku.insert(row, col, num);
          this.updateOptions(row, col);
          try {
            const [nextRow, nextCol] = this.nextEmpty();
            this.solveAux(nextRow, nextCol);
          } finally {
            if (this.sudoku.solved) return;
            this.sudoku.delete(row, col);
            this.options = this.initOptions();
            for (let r = 0; r < 9; r++) this.updateOptions(r, 1);
          }
        }
      }
    }
  
    solve() {
      const [row, col] = this.nextEmpty();
      this.solveAux(row, col);
      return this.sudoku.solved;
    }
  }
 
  class LogicSolver extends SudokuSolver {
    constructor(sudoku) {
      super(sudoku);
      this.steps = [];
      this.methods = [this.nakedSingle.bind(this), this.hiddenSingle.bind(this), this.nakedPair.bind(this)];
    }
  
    insert(row, col, num) {
      this.sudoku.insert(row, col, num);
      this.updateOptions(row, col);
    }
  
    nakedSingle() {
      for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
          const key = `${i},${j}`;
          if (this.sudoku.grid[i][j] === 0 && this.options[key].size === 1) {
            const val = [...this.options[key]][0];
            this.steps.push({ loc: [[i, j]], desc: null, val, strategy: "Naked Single" });
            return true;
          }
        }
      }
      return false;
    }
  
    hiddenSingle() {
      for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
          if (this.sudoku.grid[i][j] === 0) {
            const [row, col, box] = houseIndices(i, j);
            const candidates = this.options[`${i},${j}`];
            for (const num of candidates) {
              const notInRow = row.every(cell => !this.options[`${cell[0]},${cell[1]}`]?.has(num));
              const notInCol = col.every(cell => !this.options[`${cell[0]},${cell[1]}`]?.has(num));
              const notInBox = box.every(cell => !this.options[`${cell[0]},${cell[1]}`]?.has(num));
              if (notInRow || notInCol || notInBox) {
                this.steps.push({ loc: [[i, j]], desc: null, val: num, strategy: "Hidden Single" });
                this.options[`${i},${j}`] = new Set([num]);
                return true;
              }
            }
          }
        }
      }
      return false;
    }
  
    nakedPair() {
      for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
          const key = `${i},${j}`;
          const pair = this.options[key];
          if (this.sudoku.grid[i][j] === 0 && pair.size === 2) {
            const [row, col, box] = houseIndices(i, j);
            const houses = [row, col, box];
            for (let k = 0; k < 3; k++) {
              for (const cell of houses[k]) {
                const otherKey = `${cell[0]},${cell[1]}`;
                const otherSet = this.options[otherKey];
                if (this.sudoku.grid[cell[0]][cell[1]] === 0 && this.options[otherKey]?.size === 2 && this.setsEqual(this.options[otherKey], pair)) {
                    for (const other_cell of houses[k]) {
                        const [oi, oj] = other_cell;
                        if ((oi !== cell[0] || oj !== cell[1]) &&
                            this.sudoku.grid[oi][oj] === 0 &&
                            [...pair].some(n => this.options[`${oi},${oj}`]?.has(n))) {
                            this.steps.push({ loc: [[i,j], cell], desc: ["row", "column", "box"][k], val: new Set(pair), strategy: "Naked Pair" });
                            return true;
                        }
                    }
                }
              }
            }
          }
        }
      }
      return false;
    }
  
    setsEqual(a, b) {
      if (a.size !== b.size) return false;
      for (const val of a) if (!b.has(val)) return false;
      return true;
    }
  
    solve() {
      let idx = 0;
      const start = performance.now();
      while (true) {
        let applied = false;
        for (const method of this.methods) {
          if (method()) {
            const step = this.steps[idx];
            console.log(`Step ${idx + 1}: ${step.strategy} at ${JSON.stringify(step.loc)}, value(s): ${[step.val]}`);
            if (step.strategy === "Naked Single" || step.strategy === "Hidden Single") {
              this.insert(step.loc[0][0], step.loc[0][1], step.val);
            } else if (step.strategy === "Naked Pair") {
              const [a, b] = step.loc;
              const [row, col, box] = houseIndices(a[0], a[1]);
              const house = { row, column: col, box }[step.desc];
              for (const cell of house) {
                const key = `${cell[0]},${cell[1]}`;
                if ((cell[0] !== a[0] || cell[1] !== a[1]) && (cell[0] !== b[0] || cell[1] !== b[1])) {
                  for (const val of step.val) {
                    this.options[key]?.delete(val);
                  }
                }
              }
            }
            idx++;
            applied = true;
            break;
          }
        }
        if (!applied) {
          if (!this.sudoku.solved) {
            console.log("No more methods to apply.");
            return false;
          }
          console.log(`Sudoku solved in ${(performance.now() - start).toFixed(4)} ms.`);
          return true;
        }
      }
    }
  }
  
function createGrid() {
    const grid = [
        [3, 0, 0, 0, 0, 7, 0, 1, 0],
        [0, 4, 0, 5, 2, 0, 0, 0, 0],
        [7, 0, 9, 4, 0, 0, 0, 0, 0],
        [1, 0, 2, 0, 0, 0, 0, 0, 0],
        [0, 0, 7, 9, 0, 6, 8, 0, 0],
        [0, 0, 0, 0, 0, 0, 3, 0, 7],
        [0, 0, 0, 0, 0, 9, 2, 0, 6],
        [0, 0, 0, 0, 7, 4, 0, 3, 0],
        [0, 6, 0, 2, 0, 0, 0, 0, 4]
      ];
    return grid;
}


  // --- Example ---
  const grid = createGrid();
  
  const sudoku = new Sudoku(grid);
  console.log(sudoku.toString());
  const solver = new LogicSolver(sudoku);
  if (solver.solve()) {
    console.log("Sudoku solved:");
    console.log(sudoku.toString());
  } else {
    console.log("No solution found.");
    console.log(sudoku.toString());
    console.log(solver.options);
  }
  