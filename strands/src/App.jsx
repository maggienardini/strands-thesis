import { useState, useRef } from "react";
import Grid from "./components/Grid";
import { puzzle } from "./data/puzzle1";
import "./App.css";

function App() {
  const [selectedCells, setSelectedCells] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const gridRef = useRef(null);

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

  const handleMouseDown = (row, col) => {
    setIsDragging(true);
    setSelectedCells([{ row, col }]);
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
    console.log("Selected path:", selectedCells);
  };

  return (
    <div className="app" onMouseUp={handleMouseUp}>
      <h1>Strands</h1>
      <Grid
        ref={gridRef}
        grid={puzzle}
        selectedCells={selectedCells}
        onMouseDown={handleMouseDown}
        onMouseMove={handleGridMouseMove}
      />
    </div>
  );
}


export default App;