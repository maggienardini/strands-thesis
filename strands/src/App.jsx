import { useState, useRef } from "react";
import Grid from "./components/Grid";
import { puzzle } from "./data/puzzle1";
import "./App.css";

function App() {
  const [selectedCells, setSelectedCells] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const gridRef = useRef(null);

  const [foundWords, setFoundWords] = useState([]);
  const [lastResult, setLastResult] = useState(null);
  const [foundPositions, setFoundPositions] = useState(new Set());
  const [foundPaths, setFoundPaths] = useState([]);
  const [hintsCount, setHintsCount] = useState(0);

  // puzzle data structures
  const puzzleGrid = puzzle.grid;
  // normalize grid to rows-first (array of rows): puzzle.grid is currently columns-first
  const transpose = (g) => {
    if (!g || !g.length) return g;
    const rows = g[0].length;
    const cols = g.length;
    const out = Array.from({ length: rows }, () => Array.from({ length: cols }));
    for (let c = 0; c < cols; c++) {
      for (let r = 0; r < rows; r++) {
        out[r][c] = g[c][r];
      }
    }
    return out;
  };
  const gridRows = transpose(puzzleGrid);
  const puzzleSet = new Set(puzzle.words.map(w => w.word.toUpperCase()));
  const puzzleTypeMap = new Map(puzzle.words.map(w => [w.word.toUpperCase(), w.type]));
  const MIN_LENGTH = 4;
  const dictionaryCache = useRef(new Map());

  //this function doesn't work! or the coordinates are working weird

  const isAdjacent = (r1, c1, r2, c2) => {
    // Return false if any coordinate is missing
    if (
      r1 === undefined || c1 === undefined ||
      r2 === undefined || c2 === undefined
    ) return false;

    const dr = Math.abs(Number(r1) - Number(r2));
    const dc = Math.abs(Number(c1) - Number(c2));

    // Adjacent if max distance along any axis is exactly 1 (includes diagonals)
    return Math.max(dr, dc) === 1;
  };

  async function validateWord(word) {
    const up = word.toUpperCase();
    if (!word || word.length < MIN_LENGTH) {
      return { status: "tooShort", word: up };
    }

    if (foundWords.includes(up)) {
      return { status: "alreadyFound", word: up };
    }

    if (puzzleSet.has(up)) {
      return { status: "foundInPuzzle", word: up, type: puzzleTypeMap.get(up) || "theme" };
    }

    if (dictionaryCache.current.has(up)) {
      return dictionaryCache.current.get(up);
    }

    try {
      const res = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${up.toLowerCase()}`);
      if (res.ok) {
        const out = { status: "validNotInPuzzle", word: up };
        dictionaryCache.current.set(up, out);
        return out;
      } else {
        const out = { status: "notAWord", word: up };
        dictionaryCache.current.set(up, out);
        return out;
      }
    } catch (e) {
      const out = { status: "notAWord", word: up };
      dictionaryCache.current.set(up, out);
      return out;
    }
  }
  // is this necessasry????
  // find the path (sequence of {row,col}) for a given word in gridRows
  function findPathForWord(word) {
    const W = word.toUpperCase();
    const R = gridRows.length;
    const C = gridRows[0].length;

    const dirs = [
      [-1, -1], [-1, 0], [-1, 1],
      [0, -1], /*self*/ [0, 1],
      [1, -1], [1, 0], [1, 1]
    ];

    const visited = Array.from({ length: R }, () => Array.from({ length: C }, () => false));

    function dfs(r, c, idx, path) {
      if (gridRows[r][c].toUpperCase() !== W[idx]) return null;
      if (idx === W.length - 1) return path.concat([{ row: r, col: c }]);

      visited[r][c] = true;
      for (const [dr, dc] of dirs) {
        const nr = r + dr;
        const nc = c + dc;
        if (nr < 0 || nr >= R || nc < 0 || nc >= C) continue;
        if (visited[nr][nc]) continue;
        const res = dfs(nr, nc, idx + 1, path.concat([{ row: r, col: c }]));
        if (res) {
          visited[r][c] = false;
          return res;
        }
      }
      visited[r][c] = false;
      return null;
    }

    for (let r = 0; r < R; r++) {
      for (let c = 0; c < C; c++) {
        const res = dfs(r, c, 0, []);
        if (res) return res;
      }
    }
    return null;
  }

  const handleMouseDown = (row, col) => {
    setIsDragging(true);
    setSelectedCells([{ row, col }]);
    setLastResult(null);
  };

  const handleGridMouseMove = (e) => {
    if (!isDragging) return;

    const elementUnderMouse = document.elementFromPoint(e.clientX, e.clientY);
    const cellElement = elementUnderMouse?.closest(".cell");
    // const cellLetter = cellElement?.textContent;
    // if (cellLetter) console.log("Hovering over:", cellLetter);

    if (!cellElement || !gridRef.current?.contains(cellElement)) return;

    const row = parseInt(cellElement.dataset.row);
    const col = parseInt(cellElement.dataset.col);

    if (isNaN(row) || isNaN(col)) return;

    setSelectedCells(prev => {
      const existingIndex = prev.findIndex(
        cell => cell.row === row && cell.col === col
      );

      // If cell is already selected, truncate to that point (backwards)
      if (existingIndex !== -1) {
        return prev.slice(0, existingIndex + 1);
      }

      // If adjacent to last cell, add it
      const last = prev[prev.length - 1];
      // Check if cell is validly adjacent to last cell
      console.log(isAdjacent(last.row, last.col, row, col));
      console.log(`Last cell: (${last.row}, ${last.col}), New cell: (${row}, ${col})`);
      if (isAdjacent(last.row, last.col, row, col)) {
        return [...prev, { row, col }];
      }

      return prev;
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    if (selectedCells.length === 0 || selectedCells.length === 1) return;
    // build word from selected cells using rows-first grid
    const word = selectedCells.map(({ row, col }) => (gridRows?.[row]?.[col] || "")).join("");

    (async () => {
      const result = await validateWord(word);
      setLastResult(result);
      if (result.status === "foundInPuzzle") {
        setFoundWords(prev => prev.includes(result.word) ? prev : [...prev, result.word]);
        // find positions for this word and add them to foundPositions
        const path = findPathForWord(result.word);
        if (path) {
          setFoundPositions(prev => {
            const next = new Set(prev);
            path.forEach(({ row, col }) => next.add(`${row}-${col}`));
            return next;
          });
          setFoundPaths(prev => (
            prev.some(p => p.word === result.word) ? prev : [...prev, { word: result.word, path, type: result.type }]
          ));
        }
        setSelectedCells([]);
      } else if (result.status === "validNotInPuzzle") {
        // valid word but not in this puzzle
        setHintsCount(prev => prev + 1);
        setSelectedCells([]);
      } else {
        // too short or not a word
        setSelectedCells([]);
      }
      console.log("Validation result:", result);
    })();
  };

  const getDisplayWord = () => {
    return selectedCells.map(({ row, col }) => (gridRows?.[row]?.[col] || "")).join("");
  };

  const getResultMessage = () => {
    if (!lastResult) return null;
    const { status, word, type } = lastResult;
    
    const messages = {
      foundInPuzzle: `${word}`,
      validNotInPuzzle: `+1 hint`,
      tooShort: "Too short",
      alreadyFound: `Already found`,
      notAWord: `Not in word list`
    };
    
    return messages[status] || status;
  };

  const displayWord = getDisplayWord();
  const shouldShowResult = !displayWord && lastResult;

  return (
    <div className="app" onMouseUp={handleMouseUp}>
      <div className="header-row">
        <h1>Strands</h1>
        <button className="hint-button">Hints: {hintsCount}/3</button>
      </div>
      <h3>Today's theme: {puzzle.theme}</h3>
      <div className="word-display-area">
        {displayWord && (
          <div className="current-word">{displayWord}</div>
        )}
        {shouldShowResult && (
          <div className={`result-message result-${lastResult.status}`}>
            {getResultMessage()}
          </div>
        )}
      </div>
      <Grid
        ref={gridRef}
        grid={gridRows}
        selectedCells={selectedCells}
        foundPositions={foundPositions}
        foundPaths={foundPaths}
        onMouseDown={handleMouseDown}
        onMouseMove={handleGridMouseMove}
      />
    </div>
  );
}


export default App;