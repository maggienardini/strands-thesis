import { forwardRef, useEffect, useRef, useState } from "react";
import Cell from "./Cell";

const Grid = forwardRef(({ grid, selectedCells, onMouseDown, onMouseMove }, ref) => {
  // The data is stored as an array of 6 arrays each with 8 letters
  // Visual layout should be 6 columns × 8 rows, so we render transposed
  const cols = grid ? grid.length : 6; // expected 6
  const rows = grid && grid[0] ? grid[0].length : 8; // expected 8

  const [points, setPoints] = useState("");
  const svgRef = useRef(null);

  useEffect(() => {
    if (!ref?.current || selectedCells.length === 0) {
      setPoints("");
      return;
    }

    const gridRect = ref.current.getBoundingClientRect();

    const pts = selectedCells.map(({ row, col }) => {
      const cell = ref.current.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
      if (!cell) return null;
      const r = cell.getBoundingClientRect();
      const x = r.left - gridRect.left + r.width / 2;
      const y = r.top - gridRect.top + r.height / 2;
      return `${x},${y}`;
    }).filter(Boolean);

    setPoints(pts.join(" "));
  }, [selectedCells, ref]);

  return (
    <div
      className="grid"
      ref={ref}
      onMouseMove={onMouseMove}
      style={{ gridTemplateColumns: `repeat(${cols}, 60px)` }}
    >
      {/* SVG overlay for connectors */}
      <svg
        ref={svgRef}
        className="grid-overlay"
        style={{ position: "absolute", left: 0, top: 0, width: "100%", height: "100%", pointerEvents: "none" }}
      >
        {points && (
          <polyline points={points} fill="none" stroke="#aedfee" strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
        )}
      </svg>

      {Array.from({ length: rows }).map((_, rowIndex) =>
        Array.from({ length: cols }).map((_, colIndex) => {
          const letter = grid?.[colIndex]?.[rowIndex];
          return (
            <Cell
              key={`${rowIndex}-${colIndex}`}
              letter={letter}
              row={rowIndex}
              col={colIndex}
              selected={selectedCells.some(
                cell => cell.row === rowIndex && cell.col === colIndex
              )}
              onMouseDown={onMouseDown}
            />
          );
        })
      )}
    </div>
  );
});

Grid.displayName = "Grid";
export default Grid;