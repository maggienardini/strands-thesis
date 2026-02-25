function Cell({ letter, row, col, selected, onMouseDown }) {
  return (
    <div
      className={`cell ${selected ? "selected" : ""}`}
      data-row={row}
      data-col={col}
      onMouseDown={() => onMouseDown(row, col)}
    >
      {letter}
    </div>
  );
}

export default Cell;