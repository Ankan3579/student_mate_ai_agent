"""
🎓 Student Mate — Streamlit UI

Run:   streamlit run app.py
"""
import html
import os
import time
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv

# Must be the first Streamlit call.
st.set_page_config(
    page_title="Student Mate · AI College Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

# =========================================================
# CONSTANTS
# =========================================================

AVATAR_USER = "🧑‍🎓"
AVATAR_BOT = "🎓"

CATEGORY_META = {
    "fees": ("💰", "Fees"),
    "academic": ("📚", "Academic"),
    "placement": ("💼", "Placement"),
    "general": ("🏫", "Campus & General"),
}

SEMESTERS = ["Not specified"] + [
    f"{n}{'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'} Semester"
    for n in range(1, 9)
]

TOPICS = {
    "Auto-detect": "",
    "💰 Fees": "fees",
    "📚 Academic": "academic",
    "💼 Placement": "placement",
    "🏫 General": "general",
}

# graph node -> pipeline step index
NODE_TO_STEP = {
    "input_guardrails_agent": 0,
    "blocked_response": 0,
    "classifier_agent": 1,
    "fees_agent": 2,
    "academic_agent": 2,
    "placement_agent": 2,
    "general_agent": 2,
    "output_guardrails_agent": 3,
}

EXAMPLES = [
    ("⏰ Minimum attendance for exams?", "What is the minimum attendance required to sit for semester exams?"),
    ("💰 Tuition fee for this semester", "What is the tuition fee for this semester and when is the last date to pay?"),
    ("💼 Average package & recruiters", "What is the average placement package and which companies recruit here?"),
    ("🎉 Events, sports & clubs", "What sports, cultural events and student clubs does the campus have?"),
]

# =========================================================
# STYLE  (dark navy + teal, cards, pills)
# =========================================================

CSS = """
:root{
  --navy:#0A1128; --navy-2:#101B3A; --navy-3:#16244D;
  --teal:#14B8A6; --teal-2:#2DD4BF; --teal-3:#5EEAD4;
  --text:#E6F1FF; --muted:#8FA3C7; --border:rgba(45,212,191,.22);
  --danger:#F87171; --amber:#FBBF24;
}
html, body, .stApp{ color:var(--text); }
.stApp{
  background:
    radial-gradient(900px 480px at 88% -8%, rgba(20,184,166,.17), transparent 60%),
    radial-gradient(800px 460px at -8% 6%, rgba(56,110,255,.13), transparent 55%),
    var(--navy);
}
header[data-testid="stHeader"]{ background:transparent; }
#MainMenu, footer{ visibility:hidden; }
.block-container{ padding-top:1.6rem; padding-bottom:6rem; max-width:1080px; }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0E1A3D 0%,#0A1128 100%);
  border-right:1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container{ padding-top:1.2rem; }
.brand{ display:flex; align-items:center; gap:.7rem; margin-bottom:1rem; }
.brand-logo{
  width:44px; height:44px; border-radius:14px; display:flex; align-items:center; justify-content:center;
  font-size:1.5rem; background:linear-gradient(135deg,var(--teal),#3B82F6);
  box-shadow:0 8px 24px rgba(20,184,166,.35);
}
.brand-name{ font-weight:800; font-size:1.25rem; line-height:1.1; }
.brand-name span{ color:var(--teal-2); }
.brand-sub{ color:var(--muted); font-size:.75rem; }
.side-label{ color:var(--muted); font-size:.72rem; letter-spacing:.1em; text-transform:uppercase; margin:.9rem 0 .2rem; }

/* ---------- hero ---------- */
.hero{
  position:relative; overflow:hidden; padding:2.2rem 2.2rem 2rem; border-radius:24px;
  border:1px solid var(--border);
  background:linear-gradient(135deg, rgba(22,36,77,.95) 0%, rgba(10,17,40,.95) 65%);
  box-shadow:0 20px 60px rgba(0,0,0,.35);
}
.hero::after{
  content:""; position:absolute; right:-80px; top:-80px; width:300px; height:300px; border-radius:50%;
  background:radial-gradient(circle, rgba(45,212,191,.35), transparent 65%);
}
.hero-badge{
  display:inline-block; padding:.28rem .8rem; border-radius:999px; font-size:.72rem; font-weight:700;
  letter-spacing:.12em; color:var(--teal-3); border:1px solid var(--border); background:rgba(20,184,166,.1);
}
.hero h1{ font-size:3rem; font-weight:800; margin:.8rem 0 .4rem; padding:0; line-height:1.05; letter-spacing:-.02em; }
.hero h1 span{ background:linear-gradient(90deg,var(--teal-2),#60A5FA); -webkit-background-clip:text; background-clip:text; color:transparent; }
.hero p{ color:#B8C7E6; font-size:1.05rem; max-width:640px; margin:0; }

/* ---------- grids / cards ---------- */
.grid4{ display:grid; grid-template-columns:repeat(4,1fr); gap:.9rem; margin:1.1rem 0; }
@media (max-width:820px){ .grid4{ grid-template-columns:repeat(2,1fr); } .hero h1{ font-size:2.2rem; } }
.card{
  background:linear-gradient(160deg, rgba(22,36,77,.75), rgba(16,27,58,.75));
  border:1px solid var(--border); border-radius:18px; padding:1.1rem 1.2rem;
  transition:transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
.card:hover{ transform:translateY(-3px); border-color:rgba(45,212,191,.55); box-shadow:0 12px 30px rgba(20,184,166,.12); }
.card .ico{ font-size:1.7rem; margin-bottom:.4rem; }
.card .ttl{ font-weight:700; margin-bottom:.15rem; }
.card .dsc{ color:var(--muted); font-size:.85rem; line-height:1.35; }
.stat{ text-align:center; padding:.95rem .6rem; }
.stat .num{
  font-size:2.1rem; font-weight:800; line-height:1.1;
  background:linear-gradient(90deg,var(--teal-2),var(--teal-3)); -webkit-background-clip:text; background-clip:text; color:transparent;
}
.stat .lbl{ color:var(--muted); font-size:.7rem; text-transform:uppercase; letter-spacing:.09em; margin-top:.15rem; }
.section-title{ font-weight:700; font-size:1.05rem; margin:1.5rem 0 .2rem; }
.section-sub{ color:var(--muted); font-size:.88rem; margin-bottom:.6rem; }

/* ---------- pills / chips ---------- */
.chips{ display:flex; flex-wrap:wrap; gap:.4rem; margin:.1rem 0 .7rem; }
.chip{
  display:inline-flex; align-items:center; gap:.35rem; padding:.22rem .7rem; border-radius:999px; font-size:.78rem;
  border:1px solid var(--border); background:rgba(45,212,191,.08); color:var(--teal-2);
}
.chip.ok{ background:rgba(45,212,191,.16); color:var(--teal-3); }
.chip.warn{ background:rgba(251,191,36,.12); border-color:rgba(251,191,36,.4); color:var(--amber); }
.chip.muted{ background:rgba(255,255,255,.04); color:var(--muted); border-color:rgba(255,255,255,.1); }

/* ---------- pipeline tracker ---------- */
.pipeline{ display:flex; flex-wrap:wrap; align-items:center; gap:.45rem; margin:.15rem 0 .8rem; }
.step{
  display:flex; align-items:center; gap:.45rem; padding:.36rem .8rem; border-radius:999px; font-size:.8rem;
  border:1px solid var(--border); background:rgba(255,255,255,.03); color:var(--muted); transition:all .3s ease;
}
.step.done{ color:#052E2A; background:linear-gradient(90deg,var(--teal),var(--teal-2)); border-color:transparent; font-weight:700; }
.step.active{ color:var(--teal-2); border-color:var(--teal-2); animation:pulse 1.4s infinite; }
.step.blocked{ color:#FFD9D9; background:rgba(239,68,68,.18); border-color:rgba(239,68,68,.55); font-weight:600; }
.step.skipped{ opacity:.3; }
.arrow{ color:var(--muted); opacity:.6; }
@keyframes pulse{
  0%{ box-shadow:0 0 0 0 rgba(45,212,191,.45); }
  70%{ box-shadow:0 0 0 10px rgba(45,212,191,0); }
  100%{ box-shadow:0 0 0 0 rgba(45,212,191,0); }
}

/* ---------- notices ---------- */
.notice{ border-radius:16px; padding:1rem 1.2rem; border:1px solid var(--border); background:rgba(45,212,191,.07); }
.notice.danger{ border-color:rgba(248,113,113,.45); background:rgba(248,113,113,.08); }
.notice.warn{ border-color:rgba(251,191,36,.4); background:rgba(251,191,36,.07); }
.notice .n-title{ font-weight:700; margin-bottom:.25rem; }
.notice .n-body{ color:#C9D6EE; font-size:.93rem; }
.notice code{ background:rgba(255,255,255,.08); padding:.05rem .35rem; border-radius:6px; }

/* ---------- sources ---------- */
.src-grid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:.6rem; }
a.src{
  display:block; text-decoration:none !important; padding:.65rem .85rem; border-radius:12px;
  border:1px solid var(--border); background:rgba(255,255,255,.03); transition:all .2s ease;
}
a.src:hover{ border-color:var(--teal-2); background:rgba(45,212,191,.08); transform:translateY(-2px); }
.src-domain{ color:var(--teal-2); font-size:.72rem; font-weight:600; }
.src-title{ color:var(--text); font-size:.85rem; line-height:1.3; margin-top:.15rem; }

/* ---------- streamlit widgets ---------- */
div[data-testid="stChatMessage"]{
  background:linear-gradient(160deg, rgba(22,36,77,.55), rgba(16,27,58,.55));
  border:1px solid var(--border); border-radius:18px; padding:1rem 1.1rem;
}
div[data-testid="stChatInput"]{ border-radius:16px; }
div[data-testid="stChatInput"] textarea{ font-size:1rem; }
div[data-testid="stElementContainer"]:has(> div[data-testid="stButton"]){ width:100% !important; }
.stButton, div[data-testid="stButton"]{ width:100% !important; }
.stButton > button{
  width:100% !important; border-radius:14px; border:1px solid var(--border); background:rgba(45,212,191,.07);
  color:var(--text); padding:.65rem .9rem; text-align:left; transition:all .2s ease;
}
.stButton > button:hover{ border-color:var(--teal-2); background:rgba(45,212,191,.16); color:#fff; transform:translateY(-2px); }
.stButton > button:focus:not(:active){ border-color:var(--teal-2); color:#fff; }
div[data-testid="stExpander"]{ border:1px solid var(--border); border-radius:14px; background:rgba(255,255,255,.02); }
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# =========================================================
# SMALL HELPERS
# =========================================================

def _html(block: str) -> str:
    """Strip indentation and blank lines so Markdown never turns HTML into a code block."""
    return "\n".join(line.strip() for line in block.splitlines() if line.strip())


def show_html(block: str) -> None:
    st.markdown(_html(block), unsafe_allow_html=True)


def esc(text) -> str:
    return html.escape(str(text or ""))


def notice(kind: str, title: str, body: str) -> None:
    """kind: '' | 'danger' | 'warn'.  `title` and `body` may contain trusted HTML."""
    show_html(
        f"""
        <div class="notice {kind}">
        <div class="n-title">{title}</div>
        <div class="n-body">{body}</div>
        </div>
        """
    )


def pipeline_html(done: set, category: str = "", blocked: bool = False) -> str:
    icon, label = CATEGORY_META.get(category, ("🤖", "Specialist"))
    steps = [
        ("🛡️", "Input Guard"),
        ("🧭", "Classifier"),
        (icon, f"{label} Agent"),
        ("✅", "Output Guard"),
    ]
    active = next((i for i in range(len(steps)) if i not in done), None)

    parts = []
    for i, (ico, name) in enumerate(steps):
        if blocked:
            cls = "blocked" if i == 0 else "skipped"
            if i == 0:
                name = "Input Guard · stopped"
        elif i in done:
            cls = "done"
        elif i == active:
            cls = "active"
        else:
            cls = "pending"
        parts.append(f'<div class="step {cls}"><span>{ico}</span>{esc(name)}</div>')
        if i < len(steps) - 1:
            parts.append('<span class="arrow">›</span>')
    return _html(f'<div class="pipeline">{"".join(parts)}</div>')


def chips_html(msg: dict) -> str:
    icon, label = CATEGORY_META.get(msg.get("category", ""), ("🏫", "General"))
    chips = [f'<span class="chip">{icon} {esc(label)}</span>']
    if msg.get("verified"):
        chips.append('<span class="chip ok">✅ Verified by output guard</span>')
    else:
        chips.append('<span class="chip warn">⚠️ Unverified — double-check with your college</span>')
    chips.append(f'<span class="chip muted">⏱ {msg.get("elapsed", 0):.1f}s</span>')
    n = len(msg.get("sources", []))
    if n:
        chips.append(f'<span class="chip muted">🔗 {n} sources</span>')
    return _html(f'<div class="chips">{"".join(chips)}</div>')


def sources_html(sources: list) -> str:
    cards = []
    for s in sources:
        url = str(s.get("url", ""))
        if not url.startswith(("http://", "https://")):
            continue
        domain = urlparse(url).netloc.removeprefix("www.")
        title = (s.get("title") or url)[:90]
        cards.append(
            f'<a class="src" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
            f'<div class="src-domain">{esc(domain)}</div><div class="src-title">{esc(title)}</div></a>'
        )
    return _html(f'<div class="src-grid">{"".join(cards)}</div>')


# =========================================================
# SETUP CHECKS (API keys, graph import)
# =========================================================

REQUIRED_KEYS = ("OPENROUTER_API_KEY", "TAVILY_API_KEY")
missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]

if missing:
    show_html(
        """
        <div class="hero">
        <span class="hero-badge">ALMOST THERE</span>
        <h1>Student<span> Mate</span></h1>
        <p>Add your API keys once and the assistant is ready.</p>
        </div>
        """
    )
    st.write("")
    notice(
        "warn",
        "🔑 Missing API keys",
        "Create a file named <code>.env</code> next to <code>app.py</code> with:<br><br>"
        + "<br>".join(f"<code>{k}=your_key_here</code>" for k in REQUIRED_KEYS)
        + "<br><br>Missing right now: "
        + ", ".join(f"<code>{k}</code>" for k in missing)
        + ".<br>Then restart with <code>streamlit run app.py</code>.",
    )
    st.stop()


@st.cache_resource(show_spinner="Warming up the agents…")
def load_graph():
    from graph.graph import graph  # imported lazily so the key check above runs first

    return graph


# =========================================================
# SESSION STATE
# =========================================================

ss = st.session_state
ss.setdefault("messages", [])
ss.setdefault("stats", {"asked": 0, "verified": 0, "blocked": 0})
ss.setdefault("college", "")
ss.setdefault("semester_choice", SEMESTERS[0])
ss.setdefault("topic_choice", "Auto-detect")


# =========================================================
# SIDEBAR — inputs
# =========================================================

with st.sidebar:
    show_html(
        """
        <div class="brand">
        <div class="brand-logo">🎓</div>
        <div><div class="brand-name">Student<span> Mate</span></div>
        <div class="brand-sub">AI college assistant</div></div>
        </div>
        """
    )
    show_html('<div class="side-label">🏫 Your college</div>')
    st.text_input(
        "College / University",
        key="college",
        placeholder="e.g. JIS College of Engineering",
        label_visibility="collapsed",
    )
    show_html('<div class="side-label">📅 Semester</div>')
    st.selectbox(
        "Semester",
        SEMESTERS,
        key="semester_choice",
        help="Needed for semester-wise fee questions.",
        label_visibility="collapsed",
    )
    show_html('<div class="side-label">🎯 Topic</div>')
    st.selectbox(
        "Topic",
        list(TOPICS),
        key="topic_choice",
        help="Leave on Auto-detect and the classifier agent will pick the right specialist.",
        label_visibility="collapsed",
    )


# =========================================================
# PIPELINE RUNNER
# =========================================================

def run_pipeline(graph, inputs: dict, tracker) -> tuple[dict, float]:
    """Stream the LangGraph run and update the live tracker after every node."""
    state = dict(inputs)
    done: set = set()
    started = time.perf_counter()

    tracker.markdown(pipeline_html(done), unsafe_allow_html=True)

    for update in graph.stream(inputs, stream_mode="updates"):
        for node, delta in update.items():
            if delta:
                state.update(delta)
            step = NODE_TO_STEP.get(node)
            if step is not None:
                done.add(step)

        blocked = state.get("input_guardrails_result") is False
        tracker.markdown(
            pipeline_html(done, state.get("user_query_type", ""), blocked),
            unsafe_allow_html=True,
        )

    return state, time.perf_counter() - started


def build_message(state: dict, elapsed: float) -> dict:
    if state.get("input_guardrails_result") is False:
        return {
            "role": "assistant",
            "kind": "blocked",
            "reason": state.get("guardrail_reason", ""),
            "elapsed": elapsed,
        }
    return {
        "role": "assistant",
        "kind": "answer",
        "content": state.get("final_response") or "Sorry, I couldn't find an answer.",
        "category": state.get("user_query_type", "general"),
        "verified": bool(state.get("output_guardrails_result")),
        "sources": state.get("sources", []),
        "elapsed": elapsed,
    }


# =========================================================
# RENDERING
# =========================================================

def render_assistant(msg: dict, with_pipeline: bool = True) -> None:
    kind = msg.get("kind")

    if kind == "needs_college":
        notice(
            "warn",
            "🏫 Which college?",
            "Add your college name in the sidebar first, then ask again — "
            "every answer is searched for <b>your</b> college.",
        )
        return

    if kind == "error":
        notice(
            "danger",
            "😕 Something went wrong",
            "The request couldn't be completed. Check your API keys and internet connection, then try again.",
        )
        with st.expander("Technical details"):
            st.code(msg.get("error", "unknown error"))
        return

    if kind == "blocked":
        if with_pipeline:
            st.markdown(pipeline_html({0}, blocked=True), unsafe_allow_html=True)
        notice(
            "danger",
            "🛡️ I can't process this yet",
            esc(msg.get("reason") or "The request didn't pass the safety check.")
            + "<br><br>Tip: check your college name, semester and question, then try again.",
        )
        return

    # normal answer
    if with_pipeline:
        st.markdown(pipeline_html({0, 1, 2, 3}, msg.get("category", "")), unsafe_allow_html=True)
    st.markdown(chips_html(msg), unsafe_allow_html=True)
    st.markdown(msg["content"].replace("$", "\\$"))  # escape $ so prices never turn into LaTeX
    sources = msg.get("sources", [])
    if sources:
        with st.expander(f"🔗 Sources ({len(sources)})"):
            st.markdown(sources_html(sources), unsafe_allow_html=True)


def render_welcome() -> None:
    show_html(
        """
        <div class="hero">
        <span class="hero-badge">🎓 AI MULTI-AGENT ASSISTANT</span>
        <h1>Student<span> Mate</span></h1>
        <p>Ask anything about your college — fees, academics, placements and campus life.
        Specialist agents search the live web and two guardrails keep every answer safe and grounded.</p>
        </div>
        """
    )
    show_html(
        """
        <div class="grid4">
        <div class="card stat"><div class="num">4</div><div class="lbl">Specialist agents</div></div>
        <div class="card stat"><div class="num">2</div><div class="lbl">Guardrail checks</div></div>
        <div class="card stat"><div class="num">5</div><div class="lbl">Web sources / answer</div></div>
        <div class="card stat"><div class="num">Live</div><div class="lbl">Search &amp; scraping</div></div>
        </div>
        """
    )
    show_html(
        """
        <div class="section-title">✨ What can I help with?</div>
        <div class="grid4">
        <div class="card"><div class="ico">💰</div><div class="ttl">Fees</div><div class="dsc">Tuition, hostel, refunds and late charges</div></div>
        <div class="card"><div class="ico">📚</div><div class="ttl">Academic</div><div class="dsc">Attendance, exams, credits, SGPA / CGPA, syllabus</div></div>
        <div class="card"><div class="ico">💼</div><div class="ttl">Placements</div><div class="dsc">Packages, recruiters and placement stats</div></div>
        <div class="card"><div class="ico">🏫</div><div class="ttl">Campus life</div><div class="dsc">Events, sports, clubs and infrastructure</div></div>
        </div>
        <div class="section-title">💡 Try asking</div>
        <div class="section-sub">Set your college in the sidebar, then tap a question or type your own.</div>
        """
    )
    cols = st.columns(2)
    for i, (label, question) in enumerate(EXAMPLES):
        if cols[i % 2].button(label, key=f"example_{i}"):
            ss.pending_query = question
            st.rerun()


def render_context_bar() -> None:
    college = ss.college.strip()
    chips = [
        f'<span class="chip">🏫 {esc(college) if college else "No college set"}</span>',
        f'<span class="chip muted">📅 {esc(ss.semester_choice)}</span>',
        f'<span class="chip muted">🎯 {esc(ss.topic_choice)}</span>',
    ]
    show_html(
        f"""
        <div class="chips" style="margin-bottom:.9rem">
        <span class="chip ok">🎓 Student Mate</span>{"".join(chips)}
        </div>
        """
    )


# =========================================================
# MAIN FLOW
# =========================================================

# chat_input is pinned to the bottom of the page wherever it is called.
prompt = st.chat_input("Ask about fees, syllabus, attendance, placements…")
if not prompt:
    prompt = ss.pop("pending_query", None)

if prompt:
    ss.messages.append({"role": "user", "content": prompt})

if ss.messages:
    render_context_bar()
    for m in ss.messages:
        if m["role"] == "user":
            with st.chat_message("user", avatar=AVATAR_USER):
                st.markdown(m["content"].replace("$", "\\$"))
        else:
            with st.chat_message("assistant", avatar=AVATAR_BOT):
                render_assistant(m)
else:
    render_welcome()

if prompt:
    college = ss.college.strip()

    if not college:
        reply = {"role": "assistant", "kind": "needs_college"}
        with st.chat_message("assistant", avatar=AVATAR_BOT):
            render_assistant(reply)
    else:
        inputs = {
            "user_query": prompt,
            "college_name": college,
            "semester": "" if ss.semester_choice == SEMESTERS[0] else ss.semester_choice,
            "user_query_type": TOPICS[ss.topic_choice],
        }
        with st.chat_message("assistant", avatar=AVATAR_BOT):
            tracker = st.empty()
            try:
                final_state, elapsed = run_pipeline(load_graph(), inputs, tracker)
                reply = build_message(final_state, elapsed)
            except Exception as exc:  # show a friendly card instead of a stack trace
                reply = {"role": "assistant", "kind": "error", "error": f"{type(exc).__name__}: {exc}"}

            if reply["kind"] == "error":
                tracker.empty()  # no pipeline strip for failed runs
            # for answers and blocked requests the live tracker already shows the pipeline
            render_assistant(reply, with_pipeline=False)

        ss.stats["asked"] += 1
        if reply["kind"] == "blocked":
            ss.stats["blocked"] += 1
        if reply.get("verified"):
            ss.stats["verified"] += 1

    ss.messages.append(reply)


# =========================================================
# SIDEBAR — stats & actions (rendered last so the numbers are current)
# =========================================================

with st.sidebar:
    show_html('<div class="side-label">📊 This session</div>')
    show_html(
        f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem">
        <div class="card stat" style="padding:.7rem .4rem"><div class="num" style="font-size:1.6rem">{ss.stats["asked"]}</div><div class="lbl">Questions</div></div>
        <div class="card stat" style="padding:.7rem .4rem"><div class="num" style="font-size:1.6rem">{ss.stats["verified"]}</div><div class="lbl">Verified</div></div>
        </div>
        """
    )
    st.write("")
    if st.button("🗑️ Clear conversation", key="clear_chat"):
        ss.messages = []
        ss.stats = {"asked": 0, "verified": 0, "blocked": 0}
        st.rerun()

    with st.expander("⚙️ How it works"):
        st.markdown(
            "1. 🛡️ **Input guard** checks the request is safe and complete\n"
            "2. 🧭 **Classifier** picks fees / academic / placement / general\n"
            "3. 🤖 **Specialist agent** searches the web and reads the top pages\n"
            "4. ✅ **Output guard** removes made-up facts before you see the answer"
        )
    st.caption("Answers come from live web sources — confirm important details with your college.")
