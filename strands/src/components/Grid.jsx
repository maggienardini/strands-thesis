import { forwardRef, useEffect, useRef, useState } from "react";
import Cell from "./Cell";

const Grid = forwardRef(({ grid, selectedCells, foundPositions, foundPaths = [], onMouseDown, onMouseMove }, ref) => {
  // grid is rows-first: grid[rowIndex][colIndex]
  const rows = grid ? grid.length : 8; // expected 8
  const cols = grid && grid[0] ? grid[0].length : 6; // expected 6

  const [points, setPoints] = useState("");
  const [foundPolylines, setFoundPolylines] = useState([]);
  const svgRef = useRef(null);

  useEffect(() => {
    if (!ref?.current) {
      setPoints("");
      setFoundPolylines([]);
      return;
    }

    const gridRect = ref.current.getBoundingClientRect();

    const getCenter = (row, col) => {
      const cell = ref.current.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
      if (!cell) return null;
      const r = cell.getBoundingClientRect();
      const x = r.left - gridRect.left + r.width / 2;
      const y = r.top - gridRect.top + r.height / 2;
      return `${x},${y}`;
    };

    const selPts = selectedCells.map(({ row, col }) => getCenter(row, col)).filter(Boolean);
    setPoints(selPts.join(" "));

    const fp = foundPaths.map(fp => {
      const pts = (fp.path || []).map(({ row, col }) => getCenter(row, col)).filter(Boolean);
      return { points: pts.join(" "), type: fp.type };
    }).filter(p => p.points.length > 0);
    setFoundPolylines(fp);
  }, [selectedCells, foundPaths, ref]);

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
        {foundPolylines.map((p, idx) => (
          <polyline
            key={`found-${idx}`}
            points={p.points}
            fill="none"
            className={p.type === 'spangram' ? 'line-spangram' : 'line-found'}
            strokeWidth={8}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        ))}

        {points && (
          <polyline points={points} fill="none" className="line-selected" strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
        )}
      </svg>

      {grid?.map((row, rowIndex) =>
        row.map((letter, colIndex) => (
          <Cell
            key={`${rowIndex}-${colIndex}`}
            letter={letter}
            row={rowIndex}
            col={colIndex}
            selected={selectedCells.some(cell => cell.row === rowIndex && cell.col === colIndex)}
            type={
              // determine if this cell is part of any found path and pass its type
              (() => {
                for (const fp of foundPaths) {
                  if ((fp.path || []).some(p => p.row === rowIndex && p.col === colIndex)) return fp.type;
                }
                return foundPositions && foundPositions.has(`${rowIndex}-${colIndex}`) ? 'found' : null;
              })()
            }
            onMouseDown={onMouseDown}
          />
        ))
      )}
    </div>
  );
});

Grid.displayName = "Grid";
export default Grid;