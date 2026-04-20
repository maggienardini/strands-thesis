function Cell({ letter, row, col, selected, onMouseDown, type, hintIndex, hintStage, hintLength }) {
  const cls = ['cell'];
  if (selected) cls.push('selected');
  if (type === 'hint') {
    cls.push('hint');
    if (hintStage === 'bounce') cls.push('hint-bounce');
  }
  else if (type === 'spangram') cls.push('spangram');
  else if (type === 'found' || type) cls.push('found');

  return (
    <div
      className={cls.join(' ')}
      data-row={row}
      data-col={col}
      data-hint-index={hintIndex}
      data-hint-length={hintLength}
      onMouseDown={(e) => onMouseDown(row, col, e)}
    >
      {letter}
    </div>
  );
}

export default Cell;