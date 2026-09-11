
export default function (component) {
  const d = component.data || {};
  const root = component.parentElement.querySelector('#mjroot');
  if (!root) return;
  const inn = d.tile_inners || [];
  const T = (tid, cls, attrs) =>
    '<div class="tile ' + cls + '"' + (attrs || '') + '>' + (inn[tid] || '') + '</div>';

  let h = '<div class="tbl">';
  h += '<div class="topline">';
  h += '<span class="pill">🀄 牌牆剩 ' + d.wall + '</span>';
  h += '<span class="pill">' + d.names.map((n, i) => n + ' ' + d.scores[i]).join('　·　') + '</span>';
  h += '</div>';

  if (d.over) {
    if (d.over.winner < 0) {
      h += '<div class="banner">' + d.over.labels.join('、') + '</div>';
    } else {
      h += '<div class="banner">🎉 ' + d.names[d.over.winner] + '　' +
           d.over.fan + ' 番　（' + d.over.labels.join('、') + '）</div>';
    }
  }

  // side/top opponents: p3 (top), p1 (left-down), p2 (right-down) simplified:
  // top row = p3, middle row = p1 melds/backs + center + p2
  const seat = (vi, pi) => {
    const pl = d.players[vi];
    let s = '<div class="seat"><span class="pname">' + d.names[pi] + ' ' + pl.score + '</span>';
    s += '<span class="backs">';
    for (let i = 0; i < pl.count; i++) s += '<span class="back"></span>';
    s += '</span><span class="melds">';
    for (const m of pl.melds) {
      if (m[0] === 'chi') {
        for (let x = m[1]; x < m[1] + 3; x++) s += T(x, 't-meld');
      } else {
        s += T(m[1], 't-meld') + T(m[1], 't-meld');
      }
    }
    s += '</span><span class="melds">';
    for (const r of pl.river) s += T(r, 't-river');
    s += '</span></div>';
    return s;
  };
  h += seat(0, 3);
  h += seat(1, 1);
  h += seat(2, 2);
  h += '<div class="center"><div class="riverrow"><span class="rname">🀄 檯面</span><span class="river">';
  h += '</span></div>';

  // my melds + river
  h += '<div class="seat"><span class="pname me">' + d.names[0] + ' ' + d.scores[0] + '</span><span class="melds">';
  for (const m of d.my_melds) {
    if (m[0] === 'chi') {
      for (let x = m[1]; x < m[1] + 3; x++) h += T(x, 't-meld');
    } else {
      h += T(m[1], 't-meld') + T(m[1], 't-meld');
    }
  }
  h += '</span><span class="melds">';
  for (const r of d.my_river) h += T(r, 't-river');
  h += '</span></div>';

  // hand
  h += '<div style="text-align:center;margin-top:4px;">';
  d.hand.forEach((tid, i) => {
    if (d.drawn_pos >= 0 && i === d.drawn_pos) h += '<span class="gap"></span>';
    const sel = i === d.sel ? ' sel' : '';
    const drw = i === d.drawn_pos ? ' drawn' : '';
    h += T(tid, 't-hand' + sel + drw, ' data-idx="' + i + '" style="cursor:pointer;"');
  });
  h += '</div>';

  // actions
  h += '<div class="acts">';
  if (d.over) {
    // nothing
  } else if (d.claim) {
    const c = d.claim;
    if (c.win) h += '<div class="act hu" data-act="win">胡</div>';
    if (c.kong) h += '<div class="act kong" data-act="kong">槓</div>';
    if (c.pong) h += '<div class="act pong" data-act="pong">碰</div>';
    if (c.chi && c.chi.length === 1) {
      h += '<div class="act up" data-act="chi:' + c.chi[0] + '">上</div>';
    }
    if (c.chi && c.chi.length > 1) {
      for (const lo of c.chi) {
        h += '<div class="act up" data-act="chi:' + lo + '" style="font-size:16px;">上' +
             d.tile_inners[lo] + '</div>';
      }
    }
    h += '<div class="act skip" data-act="skip">✕</div>';
  } else if (d.await_discard) {
    if (d.zimo) h += '<div class="act zimo" data-act="zimo">自摸</div>';
    if (d.sel >= 0) h += '<div class="act confirm" data-act="confirm">打出</div>';
  }
  h += '</div>';
  if (d.hint) h += '<div class="hint">' + d.hint + '</div>';
  h += '</div>';

  root.innerHTML = h;

  root.querySelectorAll('[data-idx]').forEach(el => {
    el.addEventListener('click', () => component.setTriggerValue('tile_click', Number(el.dataset.idx)));
  });
  root.querySelectorAll('[data-act]').forEach(el => {
    el.addEventListener('click', () => component.setTriggerValue('action', el.dataset.act));
  });
  return {};
}
