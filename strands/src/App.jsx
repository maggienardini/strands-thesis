import { useEffect, useState, useRef } from "react";
import Grid from "./components/Grid";
import { puzzle } from "./data/v2_gemini_potential_grid";
import "./App.css";

function App() {
  const [selectedCells, setSelectedCells] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const gridRef = useRef(null);
  const selectedCellsRef = useRef([]);
  const isSubmittingRef = useRef(false);

  const [foundWords, setFoundWords] = useState([]);
  const [lastResult, setLastResult] = useState(null);
  const [foundPositions, setFoundPositions] = useState(new Set());
  const [foundPaths, setFoundPaths] = useState([]);
  const [hintsCount, setHintsCount] = useState(0);
  const [activeHint, setActiveHint] = useState(null); // { word, stage: 'highlight' | 'bounce' }
  const [hintedWords, setHintedWords] = useState([]);

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
  const usedNonThemeWords = useRef(new Set());

  useEffect(() => {
    selectedCellsRef.current = selectedCells;
  }, [selectedCells]);

  const setSelectedCellsSync = (updater) => {
    setSelectedCells(prev => {
      const next = typeof updater === "function" ? updater(prev) : updater;
      selectedCellsRef.current = next;
      return next;
    });
  };

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

    if (usedNonThemeWords.current.has(up)) {
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

  const submitSelectedWord = async (cells = selectedCellsRef.current) => {
    if (cells.length < 2) return;
    if (isSubmittingRef.current) return;
    isSubmittingRef.current = true;

    const word = cells.map(({ row, col }) => (gridRows?.[row]?.[col] || "")).join("");
    try {
      const result = await validateWord(word);
      setLastResult(result);
      if (result.status === "foundInPuzzle") {
        setFoundWords(prev => prev.includes(result.word) ? prev : [...prev, result.word]);
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
        if (activeHint && activeHint.word === result.word) {
          setActiveHint(null);
        }
        setSelectedCellsSync([]);
      } else if (result.status === "validNotInPuzzle") {
        usedNonThemeWords.current.add(result.word);
        setHintsCount(prev => prev + 1);
        setSelectedCellsSync([]);
      } else {
        setSelectedCellsSync([]);
      }
      console.log("Validation result:", result);
    } finally {
      isSubmittingRef.current = false;
    }
  };

  const handleMouseDown = (row, col, e) => {
    e.preventDefault();

    // Single click: extend path if adjacent, backtrack, or start new path.
    // Clicking the current endpoint submits, with no timing dependency.
    setLastResult(null);

    const cells = selectedCellsRef.current;

    if (cells.length > 0) {
      const lastCell = cells[cells.length - 1];

      if (lastCell.row === row && lastCell.col === col) {
        if (cells.length > 1) {
          void submitSelectedWord(cells);
        } else {
          setSelectedCellsSync([]);
        }
        return;
      }

      // Check if clicking a cell already in the path (backtrack)
      const existingIndex = cells.findIndex(c => c.row === row && c.col === col);
      if (existingIndex !== -1) {
        setSelectedCellsSync(prev => prev.slice(0, existingIndex + 1));
        return;
      }

      // Check if adjacent to last cell (extend path)
      if (isAdjacent(lastCell.row, lastCell.col, row, col)) {
        setSelectedCellsSync(prev => [...prev, { row, col }]);
        return;
      }
    }

    // Non-adjacent cell or no prior selection: start new path (also enables drag)
    setIsDragging(true);
    setSelectedCellsSync([{ row, col }]);
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

    setSelectedCellsSync(prev => {
      // Defensive guard: selection can be cleared by another interaction while
      // drag events are still in flight; restart path from current cell.
      if (!prev.length) {
        return [{ row, col }];
      }

      const existingIndex = prev.findIndex(
        cell => cell.row === row && cell.col === col
      );

      // If cell is already selected, truncate to that point (backwards)
      if (existingIndex !== -1) {
        return prev.slice(0, existingIndex + 1);
      }

      // If adjacent to last cell, add it
      const last = prev[prev.length - 1];
      if (isAdjacent(last.row, last.col, row, col)) {
        return [...prev, { row, col }];
      }

      return prev;
    });
  };

  const handleMouseUp = () => {
    // Only validate on mouseUp if we were actually dragging
    // (not for single-click mode, which validates on double-click)
    if (!isDragging) {
      setIsDragging(false);
      return;
    }
    
    setIsDragging(false);
    const cells = selectedCellsRef.current;
    if (cells.length < 3) return;
    
    // build word from selected cells using rows-first grid
    const word = cells.map(({ row, col }) => (gridRows?.[row]?.[col] || "")).join("");

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
        // Clear hint if this was the hinted word
        if (activeHint && activeHint.word === result.word) {
          setActiveHint(null);
        }
        setSelectedCellsSync([]);
      } else if (result.status === "validNotInPuzzle") {
        // valid word but not in this puzzle
        usedNonThemeWords.current.add(result.word);
        setHintsCount(prev => prev + 1);
        setSelectedCellsSync([]);
      } else {
        // too short or not a word
        setSelectedCellsSync([]);
      }
      console.log("Validation result:", result);
    })();
  };

  const getDisplayWord = () => {
    return selectedCells.map(({ row, col }) => (gridRows?.[row]?.[col] || "")).join("");
  };

  const getResultMessage = () => {
    if (!lastResult) return null;
    const { status, word } = lastResult;
    
    const messages = {
      foundInPuzzle: `${word}`,
      validNotInPuzzle: `+1 hint`,
      tooShort: "Too short",
      alreadyFound: `Already found`,
      notAWord: `Not in word list`
    };
    
    return messages[status] || status;
  };

  const getNextUnhintedWord = () => {
    // Get all theme words (not spangram)
    const themeWords = puzzle.words
      .filter(w => {
        const upper = w.word.toUpperCase();
        return w.type === 'theme' && !foundWords.includes(upper) && !hintedWords.includes(upper);
      })
      .map(w => w.word.toUpperCase());
    
    // Get spangram if not found
    const spangram = puzzle.words.find(w => w.type === 'spangram');
    const spangramUpper = spangram ? spangram.word.toUpperCase() : null;
    const spangramWord = spangramUpper && !foundWords.includes(spangramUpper) && !hintedWords.includes(spangramUpper)
      ? spangramUpper
      : null;
    
    // Return first unhinted theme word, or spangram if all themes found
    return themeWords[0] || spangramWord;
  };

  const handleHintClick = () => {
    if (hintsCount < 3) return; // Not enough hints

    // If there's an active hint in bounce stage, user must find the word first
    if (activeHint && activeHint.stage === 'bounce') return;

    // If there's an active highlight hint, upgrade to bounce
    if (activeHint && activeHint.stage === 'highlight') {
      setActiveHint({ ...activeHint, stage: 'bounce' });
      setHintsCount(prev => Math.max(0, prev - 3)); // Cost 3 hints to upgrade to bounce
      return;
    }

    // No active hint: start a new hint
    const nextWord = getNextUnhintedWord();
    if (!nextWord) return; // No words left to hint

    setActiveHint({ word: nextWord, stage: 'highlight' });
    setHintedWords(prev => (prev.includes(nextWord) ? prev : [...prev, nextWord]));
    setHintsCount(prev => Math.max(0, prev - 3)); // Cost 3 hints
  };

  const displayWord = getDisplayWord();
  const shouldShowResult = !displayWord && lastResult;

  // Calculate hint path for visualization
  const hintPath = activeHint ? findPathForWord(activeHint.word) : null;

  return (
    <div className="app" onMouseUp={handleMouseUp}>
      <div className="header-row">
        <h1>Strands</h1>
        <button 
          className="hint-button" 
          onClick={handleHintClick}
          disabled={hintsCount < 3 || (activeHint && activeHint.stage === 'bounce')}
        >
          Hints: {hintsCount}/3{activeHint && '*'}
        </button>
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
        hintPath={hintPath}
        activeHint={activeHint}
        onMouseDown={handleMouseDown}
        onMouseMove={handleGridMouseMove}
      />
    </div>
  );
}


export default App;