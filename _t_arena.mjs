
export default function (component) {
  const d = component.data || {};
  const root = component.parentElement.querySelector('#arroot');
  if (!root) return;

  const hpColor = p => p > 50 ? '#3ecf6e' : (p > 25 ? '#f5b83d' : '#e8483b');
  const card = (f, right, shake) => {
    if (!f) return '';
    const pct = Math.max(0, Math.round(100 * f.hp / Math.max(1, f.mhp)));
    let chips = '';
    if (f.status === 'burn') chips += '<span class="chip c-burn">🔥</span>';
    if (f.status === 'para') chips += '<span class="chip c-para">⚡</span>';
    if (f.buff) chips += '<span class="chip c-buff">⬆+' + f.buff + '</span>';
    if (f.shield) chips += '<span class="chip c-shield">🛡</span>';
    return '<div class="card' + (shake ? ' shake' : '') + '" style="--c1:' + f.c1 + ';--c2:' + f.c2 + '">' +
      '<div class="nm"><span>' + f.name + '</span><span class="hp">HP ' + f.hp + '</span></div>' +
      '<div class="art"><span>' + f.emoji + '</span></div>' +
      '<div class="hpw"><div class="hpf" style="width:' + pct + '%;background:' + hpColor(pct) + '"></div></div>' +
      '<div class="hplbl"><span>' + f.label + '</span><span>' + f.hp + '/' + f.mhp + '</span></div>' +
      '<div class="chips">' + chips + '</div></div>';
  };
  const benchRow = (f, clickable) => {
    if (!f) return '';
    let s = '<div class="benchrow">';
    for (const b of (f.bench || [])) {
      const pct = Math.max(0, Math.round(100 * b.hp / Math.max(1, b.mhp)));
      s += b.hp > 0
        ? '<div class="bench' + (clickable ? ' click' : '') + '"' +
          (clickable ? ' data-bench="' + b.i + '"' : '') + '>' + b.emoji + ' ' + b.name +
          '<span class="hpbar"><span class="hpfill" style="width:' + pct + '%"></span></span></div>'
        : '<div class="bench dead">' + b.emoji + ' ' + b.name + '</div>';
    }
    return s + '</div>';
  };
  const dots = d.stage_dots || null;
  let mid = '<div class="divider"><span class="logtick">' + (d.log || '') + '</span>';
  mid += '<span class="vs">VS</span>';
  mid += '<span class="turnbadge">' + (d.turn_label || '') +
         (dots ? '<span class="stagedots">' + dots.map(s => '<i class="' + s + '"></i>').join('') + '</span>' : '') +
         '</span></div>';

  let h = '<div class="arena">';
  h += '<div class="seatname" style="color:#ff9f9f;text-align:right;">🔴 ' + d.foe.label +
       (d.foe.deck_name ? ' · ' + d.foe.deck_name : '') + '</div>';
  h += '<div class="half foe"><div>' + benchRow(d.foe, false) + '</div></div>';
  h += '<div class="half foe">' + card(d.foe, true, d.hit === 'e' || d.hit === 'ep') + '</div>';
  h += mid;
  h += '<div class="half me">' + card(d.me, false, d.hit === 'p' || d.hit === 'pe') + '</div>';
  h += '<div class="half me"><div>' + benchRow(d.me, d.can_bench) + '</div></div>';

  if (d.over) {
    h += '<div class="banner ' + (d.over.win ? 'w' : 'l') + '">' + d.over.title + '</div>';
  } else if (d.pending) {
    h += '<div class="panel"><div class="ptitle">' + d.replace_title + '</div><div class="popts">';
    for (const b of (d.me.bench || [])) {
      if (b.hp > 0) {
        h += '<div class="popt" data-bench="' + b.i + '">' + b.emoji + ' ' + b.name + '</div>';
      }
    }
    h += '</div></div>';
  } else if (d.can_act) {
    h += '<div class="abar">';
    for (const m of (d.moves || [])) {
      const off = m.off ? ' off' : '';
      const cls = m.key === 'move1' ? '' : ' gold';
      h += '<div class="abtn' + cls + off + '" data-act="' + m.key + '">' + m.name +
           '<small>⚔ ' + m.power + (m.tag || '') + (m.cd ? ' · ⏳' + d.cd_txt : '') + '</small>' +
           (m.sup ? '<span class="sup">×1.5</span>' : '') + '</div>';
    }
    h += '<div class="abtn blue" data-panel="items">' + d.items_txt + '</div>';
    h += '<div class="abtn grey" data-panel="swap">' + d.swap_txt + '</div>';
    h += '<div class="abtn grey" data-act="surrender" style="font-size:.7rem;">🏳</div>';
    h += '</div>';
    if (d.panel === 'swap') {
      h += '<div class="panel"><div class="ptitle">' + d.swap_txt + '</div><div class="popts">';
      let any = false;
      for (const b of (d.me.bench || [])) {
        if (b.hp > 0 && !b.active) {
          any = true;
          h += '<div class="popt" data-bench="' + b.i + '">' + b.emoji + ' ' + b.name + '</div>';
        }
      }
      h += (any ? '' : '<span class="deads">' + d.none_txt + '</span>') + '</div></div>';
    }
    if (d.panel === 'items') {
      h += '<div class="panel"><div class="ptitle">' + d.items_txt + '</div><div class="popts">';
      if (!(d.items || []).length) h += '<span class="deads">' + d.none_txt + '</span>';
      for (const it of (d.items || [])) {
        h += '<div class="popt" data-item="' + it.id + '">' + it.emoji + ' ' + it.name + '</div>';
      }
      h += '</div></div>';
    }
  } else {
    h += '<div class="abar"><div class="abtn grey off">' + d.wait_txt + '</div></div>';
  }
  if (d.hint) h += '<div class="hint" style="color:#aeb8d8;font-size:.72rem;text-align:center;margin-top:6px;">' + d.hint + '</div>';
  h += '</div>';
  root.innerHTML = h;

  root.querySelectorAll('[data-act]').forEach(el =>
    el.addEventListener('click', () => component.setTriggerValue('act', el.dataset.act)));
  root.querySelectorAll('[data-bench]').forEach(el =>
    el.addEventListener('click', () => component.setTriggerValue('bench', Number(el.dataset.bench))));
  root.querySelectorAll('[data-item]').forEach(el =>
    el.addEventListener('click', () => component.setTriggerValue('item', el.dataset.item)));
  root.querySelectorAll('[data-panel]').forEach(el =>
    el.addEventListener('click', () => component.setTriggerValue('panel', el.dataset.panel)));
  return {};
}
