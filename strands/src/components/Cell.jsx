function Cell({ letter, row, col, selected, onMouseDown, type }) {
  const cls = ['cell'];
  if (selected) cls.push('selected');
  if (type === 'spangram') cls.push('spangram');
  else if (type === 'found' || type) cls.push('found');

  return (
    <div
      className={cls.join(' ')}
      data-row={row}
      data-col={col}
      onMouseDown={() => onMouseDown(row, col)}
    >
      {letter}
    </div>
  );
}

export default Cell;