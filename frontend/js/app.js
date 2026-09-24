"use strict";
const content = document.getElementById('content');
const statusModule = document.getElementById('status-module');
const xpChip = document.getElementById('xp-chip');
const levelChip = document.getElementById('level-chip');
const streakStatus = document.getElementById('streak-status');
let currentView = 'dashboard';
let dashboard = null;
let activeQuestion = null;
let activeDifficulty = 'easy';
let hintsUsed = 0;
let questionStarted = 0;
let personalBest = Number(localStorage.getItem('afl-personal-best') || 0);
let submitted = false;
async function api(url, options) {
    const res = await fetch(url, { headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) }, ...options });
    const data = await res.json();
    if (!res.ok)
        throw new Error(data.error || 'Request failed');
    return data;
}
function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[c]));
}
function toast(message, kind = 'ok') {
    const old = document.querySelector('.toast');
    old?.remove();
    const el = document.createElement('div');
    el.className = `toast ${kind}`;
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 2500);
}
function setNav() {
    document.querySelectorAll('.nav-item[data-view]').forEach((b) => b.classList.toggle('active', b.dataset.view === currentView));
    statusModule.textContent = currentView;
}
async function refreshDashboard() {
    dashboard = await api('/api/dashboard');
    const xp = dashboard.stats.total_xp || 0;
    xpChip.textContent = `XP ${xp}`;
    levelChip.textContent = `LEVEL ${Math.max(1, Math.floor(xp / 100) + 1)}`;
    streakStatus.textContent = `streak: ${dashboard.stats.current_streak || 0}`;
}
function progressPct(lesson) {
    const p = dashboard?.progress.find((x) => x.lesson === lesson);
    return p ? Math.min(100, Math.round((p.xp / 250) * 100)) : 0;
}
function renderDashboard() {
    const stats = dashboard.stats;
    const progress = [
        ['parameters', 'Parameter Mathematics'], ['binary', 'Binary'], ['logic', 'Logic'], ['algebra', 'Algebra'], ['functions', 'Functions'],
        ['vectors', 'Vectors'], ['matrices', 'Matrices'], ['probability', 'Probability'], ['ai_parameters', 'AI Parameters'], ['neural_networks', 'Neural Networks']
    ];
    content.innerHTML = `
    <section class="page-head"><div><div class="page-kicker">workspace / dashboard</div><h1>Train your brain before training AI.</h1><p class="page-copy">A developer-style lab for building the maths, representation, and reasoning foundations behind AI systems.</p></div></section>
    <div class="grid grid-4">
      <div class="card stat-card"><div class="stat-label">Total XP</div><div class="stat-value">${stats.total_xp}</div><div class="stat-sub">earned in this local lab</div></div>
      <div class="card stat-card"><div class="stat-label">Problems Solved</div><div class="stat-value">${stats.problems_solved}</div><div class="stat-sub">correct + wrong attempts</div></div>
      <div class="card stat-card"><div class="stat-label">Accuracy</div><div class="stat-value">${stats.accuracy}%</div><div class="stat-sub">correct answers</div></div>
      <div class="card stat-card"><div class="stat-label">Best Streak</div><div class="stat-value">🔥 ${stats.best_streak}</div><div class="stat-sub">personal record</div></div>
    </div>
    <div class="grid grid-3" style="margin-top:14px">
      <div class="card" style="padding:16px; grid-column:span 2"><h3>Learning Progress</h3><div style="margin-top:12px">${progress.map(([id, name]) => `<div class="progress-row"><div class="progress-name">${name}</div><div class="progress-bar"><div class="progress-fill" style="width:${progressPct(id)}%"></div></div><div class="progress-pct">${progressPct(id)}%</div></div>`).join('')}</div></div>
      <div class="card activity"><h3>Learning Activity</h3><div class="activity-grid">${Array.from({ length: 56 }, (_, i) => `<div class="activity-cell ${i > 41 ? 'on' : ''} ${i > 51 ? 'hot' : ''}"></div>`).join('')}</div><p class="page-copy" style="font-size:12px">Green cells represent recent solved activity in this local demo view.</p><div class="action-row"><button class="btn btn-primary" data-action="parameters">Continue Parameters</button><button class="btn btn-blue" data-action="binary">Open Binary</button></div></div>
    </div>
    <div class="grid grid-3" style="margin-top:14px">
      <div class="card" style="padding:16px; grid-column:span 2"><h3>Achievement Log</h3><div class="lesson-list" style="margin-top:12px">${(dashboard.achievements.length ? dashboard.achievements : [{ name: 'First Parameter', description: 'Solve your first parameter challenge to unlock this.' }, { name: 'Binary Beginner', description: 'Solve your first binary challenge to unlock this.' }]).map(a => `<div class="lesson-card" style="cursor:default"><div class="lesson-top"><div class="lesson-title">🏆 ${esc(a.name)}</div><div class="lesson-meta">unlocked</div></div><div class="stat-sub">${esc(a.description)}</div></div>`).join('')}</div></div>
      <div class="card" style="padding:16px"><h3>System Status</h3><div class="lesson-list" style="margin-top:12px"><div class="lesson-card" style="cursor:default"><div class="lesson-title">SQLite</div><div class="lesson-meta">LOCAL · READY</div></div><div class="lesson-card" style="cursor:default"><div class="lesson-title">Question Engine</div><div class="lesson-meta">DYNAMIC · READY</div></div><div class="lesson-card" style="cursor:default"><div class="lesson-title">Adaptive Difficulty</div><div class="lesson-meta">AUTO · ENABLED</div></div></div></div>
    </div>`;
}
function renderLessonIntro(kind) {
    const title = kind === 'parameters' ? 'Parameter Mathematics' : 'Binary Teaching';
    const copy = kind === 'parameters' ? 'Follow the path from y = ax to weights, bias, prediction, and parameter updates.' : 'Move from bits and bytes into decimal and ASCII, then practice decoding.';
    const cards = kind === 'parameters' ? [
        ['Level 1', 'y = ax', 'Recover one parameter from a simple relationship.'], ['Level 2', 'y = ax + b', 'Introduce a bias term.'], ['Level 3', '2a + b = 11', 'Solve two unknowns.'], ['AI Foundation', 'w₁x₁ + w₂x₂ + b', 'Connect parameters to model outputs.']
    ] : [
        ['Easy', '1 10 11 100', 'Binary → decimal.'], ['Medium', '0101 1010', 'Bigger place values.'], ['Hard', '8-bit values', 'Use full bytes.'], ['Challenge', '01001000', 'Decode to ASCII.']
    ];
    content.innerHTML = `<section class="page-head"><div><div class="page-kicker">module / ${kind}</div><h1>${title}</h1><p class="page-copy">${copy}</p></div><div class="action-row"><button class="btn btn-primary" data-action="practice">Start Practice</button><button class="btn btn-blue" data-action="challenge">Challenge Mode</button></div></section><div class="learn-panel card"><h3>Learn</h3><div style="margin-top:12px">${cards.map((c, i) => `<div class="learn-card card"><div class="learn-index">${i + 1} · ${esc(c[0])}</div><div style="font-weight:700;margin-top:4px">${esc(c[1])}</div><p>${esc(c[2])}</p></div>`).join('')}</div></div>`;
}
function renderPractice(kind, challenge = false) {
    const questionText = activeQuestion?.question || 'Loading…';
    const variables = activeQuestion?.variables || [];
    const inputFields = kind === 'parameters'
        ? variables.map(v => `<div class="field"><label>${esc(v)}</label><input id="ans-${esc(v)}" autocomplete="off" inputmode="decimal"></div>`).join('')
        : `<div class="field"><label>Your answer</label><input id="ans-answer" autocomplete="off" inputmode="text"></div>`;
    content.innerHTML = `<section class="page-head"><div><div class="page-kicker">game / ${kind === 'parameters' ? 'parameter battle' : 'binary decoder'}</div><h1>${challenge ? 'Challenge Mode' : (kind === 'parameters' ? 'Parameter Battle' : 'Binary Decoder')}</h1><p class="page-copy">${challenge ? 'No hints. Timer on. Beat your personal best.' : 'Solve first, inspect the explanation after submission.'}</p></div><div><div class="chip">${activeDifficulty.toUpperCase()}</div></div></section>
    <div class="level-tabs">${['easy', 'medium', 'hard', 'ai'].map(d => `<button class="level-tab ${activeDifficulty === d ? 'active' : ''}" data-diff="${d}">${d}</button>`).join('')}</div>
    <div class="lab-layout"><div class="card code-card"><div class="code-head"><span>question/${activeQuestion?.id || 'loading'}</span><span id="timer">00:00</span></div><div class="problem">${esc(questionText)}</div><div class="form-grid">${inputFields}</div><div class="action-row" style="margin-top:16px"><button class="btn btn-primary" id="submit-btn">Submit Answer</button>${challenge ? '' : '<button class="btn btn-ghost" id="hint-btn">Hint</button>'}<button class="btn btn-ghost" id="next-btn" disabled>Next</button></div><div id="result-area"></div></div><div class="card hint-panel"><h3>Hint Stack</h3><p class="stat-sub">Progressive hints cost no XP, but remove the no-hint bonus.</p><div id="hints">${challenge ? '<div class="hint-item">Hints disabled in Challenge Mode.</div>' : '<div class="hint-item">Click Hint after thinking about the problem yourself.</div>'}</div></div></div>`;
    wirePractice(kind, challenge);
}
function startTimer() {
    clearTimer();
    questionStarted = Date.now();
    window.__timer = window.setInterval(() => {
        const t = Math.floor((Date.now() - questionStarted) / 1000);
        const mm = String(Math.floor(t / 60)).padStart(2, '0');
        const ss = String(t % 60).padStart(2, '0');
        const el = document.getElementById('timer');
        if (el)
            el.textContent = `${mm}:${ss}`;
    }, 250);
}
function clearTimer() { if (window.__timer) {
    clearInterval(window.__timer);
    window.__timer = null;
} }
async function loadQuestion(kind) {
    activeQuestion = await api(`/api/question/${kind}/${activeDifficulty}`);
    hintsUsed = 0;
    submitted = false;
    renderPractice(kind, false);
    startTimer();
}
function wirePractice(kind, challenge) {
    document.querySelectorAll('[data-diff]').forEach(btn => btn.addEventListener('click', async () => {
        activeDifficulty = btn.dataset.diff;
        await loadQuestion(kind);
    }));
    document.getElementById('submit-btn')?.addEventListener('click', async () => {
        if (!activeQuestion || submitted)
            return;
        const answers = {};
        if (kind === 'parameters') {
            (activeQuestion.variables || []).forEach(v => { const el = document.getElementById(`ans-${v}`); answers[v] = el?.value || ''; });
        }
        else {
            const el = document.getElementById('ans-answer');
            answers.answer = el?.value || '';
        }
        clearTimer();
        const timeTaken = (Date.now() - questionStarted) / 1000;
        const expected = kind === 'parameters' ? { ...(activeQuestion.answer || {}), explanation: activeQuestion.explanation } : { answer_text: activeQuestion.answer_text, explanation: activeQuestion.explanation };
        try {
            const result = await api('/api/answer', { method: 'POST', body: JSON.stringify({ lesson: kind, difficulty: activeDifficulty, question_type: activeQuestion.type, expected, answers, time_taken: timeTaken, hints_used: hintsUsed }) });
            submitted = true;
            const area = document.getElementById('result-area');
            area.innerHTML = `<div class="solution ${result.correct ? '' : 'bad'}"><strong>${result.correct ? '✅ Correct' : '❌ Not quite'}</strong><div style="margin-top:7px">${esc(result.explanation)}</div><div class="stat-sub" style="margin-top:7px">XP +${result.xp_gained} ${result.no_hint_bonus ? '· no-hint bonus' : ''} ${result.fast_bonus ? '· fast-solve bonus' : ''}</div></div>`;
            const submit = document.getElementById('submit-btn');
            submit.disabled = true;
            const next = document.getElementById('next-btn');
            next.disabled = false;
            next.focus();
            await refreshDashboard();
            if (result.correct)
                toast(`+${result.xp_gained} XP · nice work`, 'ok');
            else
                toast('Keep going — the explanation is there to help.', 'bad');
        }
        catch (err) {
            toast(String(err), 'bad');
        }
    });
    document.getElementById('hint-btn')?.addEventListener('click', () => {
        if (!activeQuestion)
            return;
        if (hintsUsed >= activeQuestion.hints.length) {
            toast('All hints used. Try the explanation after submitting.', 'bad');
            return;
        }
        const hints = document.getElementById('hints');
        const div = document.createElement('div');
        div.className = 'hint-item';
        div.textContent = `Hint ${hintsUsed + 1}: ${activeQuestion.hints[hintsUsed]}`;
        hints.appendChild(div);
        hintsUsed += 1;
    });
    document.getElementById('next-btn')?.addEventListener('click', async () => loadQuestion(kind));
}
function renderTranslator() {
    content.innerHTML = `<section class="page-head"><div><div class="page-kicker">tool / translator</div><h1>Binary Code Translator</h1><p class="page-copy">Translate text ↔ binary, see ASCII values, and verify each byte visually.</p></div></section><div class="translator-grid"><div class="card text-block"><h3>TEXT → BINARY</h3><textarea id="text-input" rows="7" placeholder="HELLO"></textarea><div class="action-row" style="margin-top:12px"><button class="btn btn-primary" id="encode-btn">Encode</button><button class="btn btn-ghost" id="clear-btn">Clear</button></div><div style="margin-top:12px" id="encode-output" class="translate-output">Ready.</div></div><div class="card text-block"><h3>BINARY → TEXT</h3><textarea id="binary-input" rows="7" placeholder="01001000 01101001"></textarea><div class="action-row" style="margin-top:12px"><button class="btn btn-blue" id="decode-btn">Decode</button></div><div style="margin-top:12px" id="decode-output" class="translate-output">Ready.</div></div></div>`;
    document.getElementById('encode-btn')?.addEventListener('click', () => {
        const raw = document.getElementById('text-input').value;
        const lines = [...raw].map(ch => `<div class="byte-line"><span>${esc(ch === ' ' ? '␠' : ch)} → ${ch.charCodeAt(0)}</span><span class="byte-ascii">${ch.charCodeAt(0).toString(2).padStart(8, '0')}</span></div>`).join('');
        document.getElementById('encode-output').innerHTML = lines || 'Enter some text.';
    });
    document.getElementById('decode-btn')?.addEventListener('click', () => {
        const raw = document.getElementById('binary-input').value.trim();
        const groups = raw.split(/\s+/).filter(Boolean);
        const decoded = [];
        for (const g of groups) {
            if (!/^[01]{8}$/.test(g)) {
                decoded.push(`[invalid: ${g}]`);
                continue;
            }
            const n = parseInt(g, 2);
            decoded.push(String.fromCharCode(n));
        }
        document.getElementById('decode-output').textContent = decoded.join('') || 'Enter 8-bit binary values.';
    });
    document.getElementById('clear-btn')?.addEventListener('click', () => { document.getElementById('text-input').value = ''; document.getElementById('encode-output').textContent = 'Ready.'; });
}
async function openView(view) {
    clearTimer();
    currentView = view;
    setNav();
    await refreshDashboard();
    if (view === 'dashboard')
        renderDashboard();
    else if (view === 'translator')
        renderTranslator();
    else
        renderLessonIntro(view);
}
document.querySelectorAll('.nav-item[data-view]').forEach(btn => btn.addEventListener('click', () => openView(btn.dataset.view)));
document.getElementById('theme-btn')?.addEventListener('click', () => { document.body.classList.toggle('light'); localStorage.setItem('afl-theme', document.body.classList.contains('light') ? 'light' : 'dark'); });
if (localStorage.getItem('afl-theme') === 'light')
    document.body.classList.add('light');
document.addEventListener('click', async (e) => {
    const target = e.target;
    const action = target.closest('[data-action]')?.dataset.action;
    if (!action)
        return;
    if (action === 'parameters')
        return openView('parameters');
    if (action === 'binary')
        return openView('binary');
    if (action === 'practice') {
        const view = currentView === 'binary' ? 'binary' : 'parameters';
        activeDifficulty = view === 'parameters' ? 'easy' : 'easy';
        activeQuestion = await api(`/api/question/${view}/auto`);
        hintsUsed = 0;
        submitted = false;
        renderPractice(view, false);
        startTimer();
    }
    if (action === 'challenge') {
        const view = currentView === 'binary' ? 'binary' : 'parameters';
        activeDifficulty = view === 'parameters' ? 'hard' : 'hard';
        activeQuestion = await api(`/api/question/${view}/${activeDifficulty}`);
        hintsUsed = 0;
        submitted = false;
        renderPractice(view, true);
        startTimer();
    }
});
refreshDashboard().then(renderDashboard).catch(err => { content.innerHTML = `<div class="card" style="padding:18px">Could not load the lab: ${esc(err)}</div>`; });
