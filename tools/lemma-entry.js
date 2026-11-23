const l = require('wink-lemmatizer');
const words = require('wink-lexicon/src/wn-words.js');
const has = w => words[w] !== undefined;
// candidates: best guess first
function lemmas(w){
  w = w.toLowerCase();
  const out = [];
  const add = x => { if (x && !out.includes(x)) out.push(x); };
  const v = l.verb(w), n = l.noun(w), a = l.adjective(w);
  // fix: hoped/hoping -> hope (single consonant before -ed/-ing, with e-form existing)
  let m;
  const FIX = {does:'do', doing:'do', did:'do', done:'do', has:'have', having:'have', lives:'live', saw:'see', felt:'feel', left:'leave'};
  if (FIX[w]) add(FIX[w]);
  if ((m = w.match(/^(.*[aeiou])([^aeiouwxy])(ed|ing)$/)) && has(m[1] + m[2] + 'e')) add(m[1] + m[2] + 'e');
  if (/(ed|ing)$/.test(w)) { add(v); add(a); add(n); }
  else if (/(er|est)$/.test(w)) { add(a); add(v); add(n); }
  else if (/s$/.test(w)) { add(n); add(v); add(a); }
  else { add(v); add(n); add(a); }
  const res = out.filter(x => x !== w);
  return { base: res, known: has(w) };
}
module.exports = { lemmas };
