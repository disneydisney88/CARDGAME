
export default function (component) {
  const d = component.data || {};
  const root = component.parentElement.querySelector('#xqroot');
  if (!root) return;
  const P = 5, S = 10;
  const X = c => P + c * S, Y = r => P + r * S;

  let lines = '';
  for (let c = 0; c < 9; c++) {
    if (c === 0 || c === 8) {
      lines += `<line x1="${X(c)}" y1="${Y(0)}" x2="${X(c)}" y2="${Y(9)}"/>`;
    } else {
      lines += `<line x1="${X(c)}" y1="${Y(0)}" x2="${X(c)}" y2="${Y(4)}"/>`;
      lines += `<line x1="${X(c)}" y1="${Y(5)}" x2="${X(c)}" y2="${Y(9)}"/>`;
    }
  }
  for (let r = 0; r < 10; r++) {
    lines += `<line x1="${X(0)}" y1="${Y(r)}" x2="${X(8)}" y2="${Y(r)}"/>`;
  }
  for (const [x1, y1, x2, y2] of [[X(3),Y(0),X(5),Y(2)],[X(5),Y(0),X(3),Y(2)],
                                   [X(3),Y(7),X(5),Y(9)],[X(5),Y(7),X(3),Y(9)]]) {
    lines += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
  }
  const outer = `<rect x="${X(0)-1.6}" y="${Y(0)-1.6}" width="${S*8+3.2}" height="${S*9+3.2}"
    fill="none" stroke-width="0.8"/>`;

  let h = `<div class="xqboard">
    <svg viewBox="0 0 90 100" stroke="#7a4a1c" stroke-width="0.45">
      ${lines}${outer}
      <text x="25" y="51.8" font-size="4.6" fill="#8a5a24" text-anchor="middle"
        font-weight="700" stroke="none" font-family="serif" letter-spacing="1">楚 河</text>
      <text x="65" y="51.8" font-size="4.6" fill="#8a5a24" text-anchor="middle"
        font-weight="700" stroke="none" font-family="serif" letter-spacing="1">漢 界</text>
    </svg>`;
  if (d.last && d.last.length === 2) {
    for (const sq of d.last) {
      const r = Math.floor(sq / 9), c = sq % 9;
      h += `<div class="lastmv" style="left:${X(c)}%;top:${Y(r)}%;"></div>`;
    }
  }
  for (let sq = 0; sq < 90; sq++) {
    const p = d.board[sq];
    if (!p) continue;
    const r = Math.floor(sq / 9), c = sq % 9;
    const cls = (p.red ? 'red' : 'blk') + (d.sel === sq ? ' selpc' : '');
    h += `<div class="pc ${cls}" data-sq="${sq}"
      style="left:${X(c)}%;top:${Y(r)}%;">${p.t}</div>`;
  }
  for (const sq of (d.targets || [])) {
    const r = Math.floor(sq / 9), c = sq % 9;
    const isCap = !!d.board[sq];
    h += isCap
      ? `<div class="ring" data-sq="${sq}" style="left:${X(c)}%;top:${Y(r)}%;"></div>`
      : `<div class="dot" data-sq="${sq}" style="left:${X(c)}%;top:${Y(r)}%;"></div>`;
  }
  h += '</div>';
  root.innerHTML = h;
  root.querySelectorAll('[data-sq]').forEach(el => {
    el.addEventListener('click', () => component.setTriggerValue('sq', Number(el.dataset.sq)));
  });
  return {};
}
