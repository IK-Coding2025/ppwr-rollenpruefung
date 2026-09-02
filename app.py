import os
import streamlit as st

st.set_page_config(page_title="PPWR-Rollenprüfung", layout="centered")

st.markdown("""
<style>
html, body, .stApp { font-family: Arial, sans-serif; }
h1.ppwrtitle { color: #0055A4; text-align: center; margin-bottom: 0; }
.subtitle { text-align: center; color: #5a6b7d; margin-top: 2px; }
/* Test-Auswahl als Pills */
div[data-testid="stRadio"] > div { padding-top: 0; }
div[data-testid="stRadio"] div[role="radiogroup"] { gap: 8px; flex-wrap: wrap; }
div[data-testid="stRadio"] div[role="radiogroup"] label {
  border: 1px solid #0055A4; border-radius: 20px; padding: 6px 16px;
  color: #0055A4; background: #fff; position: relative; margin-right: 0;
  cursor: pointer;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover { background: #eaf2fb; }
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) { background: #0055A4; color: #fff; }
/* Hover-Infokasten (keine falschen Worttrennungen: Umbruch nur an Leerzeichen) */
div[data-testid="stRadio"] div[role="radiogroup"] label::after {
  display: none; content: ""; white-space: pre-wrap; text-align: left;
  position: absolute; top: 120%; left: 0; width: 340px; max-width: 80vw;
  background: #E8F2FC; border: 1px solid #b9d4ee; border-radius: 8px;
  padding: 12px 14px; color: #1a1a1a; font-size: 10pt; line-height: 1.5;
  font-weight: normal; z-index: 9999; box-shadow: 0 2px 8px rgba(0,60,120,.15);
  word-break: normal; overflow-wrap: break-word; hyphens: none;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(1):hover::after { display: block; content: "Lieferant — Wer liefert Verpackungen oder Verpackungsmaterial an einen Erzeuger? Kontext: Informationsbereitstellung, damit der Erzeuger die Konformität der Verpackung nachweisen kann."; }
div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(2):hover::after { display: block; content: "Erzeuger — Wer bringt die Verpackung bzw. das verpackte Produkt in der EU in Verkehr und muss deren Konformität nachweisen? Kontext: Verpackungsherstellung bzw. Herstellung verpackter Produkte (Inverkehrbringen der Verpackung)."; }
div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(3):hover::after { display: block; content: "Hersteller — Wer trägt die Abfallverantwortung (erweiterte Herstellerverantwortung) in dem EU-Mitgliedstaat, in dem die Verpackung zu Abfall wird? Kontext: Abfallverantwortliche."; }
div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(4):hover::after { display: block; content: "Importeur / Vertreiber — Wann gehen die Erzeugerpflichten beim Inverkehrbringen auf Importeur oder Vertreiber über (eigener Name/eigene Marke oder konformitätsbeeinträchtigende Veränderung)? Kontext: Inverkehrbringen."; }
.result { background:#E8F2FC; border:1px solid #b9d4ee; border-radius:8px; padding:16px 18px; margin:8px 0 4px; }
.result h3 { margin:0 0 8px; color:#0055A4; font-size:12pt; }
.badge { display:inline-block; border-radius:12px; padding:3px 14px; font-weight:bold; font-size:10.5pt; }
.badge-yes { background:#0055A4; color:#fff; }
.badge-no { background:#dfe5ec; color:#5a6b7d; }
.step { color:#0055A4; font-weight:bold; margin-bottom:4px; }
.footnote { font-size:9.5pt; color:#5a6b7d; line-height:1.5; }
.rolecard { border:1px solid #d7e6f7; border-radius:8px; padding:14px 10px; text-align:center; background:#f7fbff; }
.rolecard .rname { font-weight:bold; margin-bottom:6px; }
.st-ja { color:#0055A4; font-weight:bold; font-size:13pt; }
.st-nein { color:#8a99a8; font-weight:bold; font-size:13pt; }
.st-offen { color:#b0bcc9; font-size:13pt; }
.question { font-size:11.5pt; line-height:1.55; }
</style>
""", unsafe_allow_html=True)

# ---------------- Daten (Entscheidungsbäume, Originalwortlaut) ----------------
TREES = {
    "lief": {
        "title": "Bin ich LIEFERANT im Sinne der PPWR?",
        "intro": "„Lieferant“ ist jede natürliche oder juristische Person, die Verpackungen oder Verpackungsmaterial an einen Erzeuger liefert (Art. 3 Abs. 1 Nr. 16).",
        "start": "q1",
        "nodes": {
            "q1": {"short": "Lieferung von Verpackungen/Material", "q": "Liefern Sie <strong>Verpackungen</strong> oder <strong>Verpackungsmaterial</strong>?", "yes": "q2", "no": "res_kein1"},
            "q2": {"short": "Lieferung an Erzeuger", "q": "Liefern Sie die Verpackungen oder das Verpackungsmaterial an einen <strong>Erzeuger</strong> (Art. 3 Abs. 1 Nr. 13 PPWR)?", "yes": "res_ja", "no": "q3"},
            "q3": {"short": "Andere Kunden / Drittstaaten", "q": "Liefern Sie an <strong>andere Kunden</strong>, z. B. <strong>Händler/Vertreiber</strong> (sofern diese nicht als Erzeuger handeln) oder an <strong>Abnehmer in Drittstaaten</strong>?", "yes": "res_kein2", "no": "res_pruef"},
        },
        "results": {
            "res_kein1": {"text": "Kein Lieferant im Sinne der PPWR – es werden keine Verpackungen oder Verpackungsmaterialien geliefert.", "role": "lieferant", "value": False},
            "res_ja": {"text": "Lieferant im Sinne der PPWR (Art. 3 Abs. 1 Nr. 16). Pflicht: dem Erzeuger alle Informationen und Unterlagen zur Verfügung zu stellen, die dieser benötigt, um die Konformität der Verpackungen nachzuweisen – auf Papier oder in elektronischer Form (Art. 16 Abs. 1).", "role": "lieferant", "value": True},
            "res_kein2": {"text": "Kein Lieferant im Sinne der PPWR – Lieferung an andere Kunden (z. B. Händler/Vertreiber, die nicht als Erzeuger handeln) oder an Abnehmer in Drittstaaten.", "role": "lieferant", "value": False},
            "res_pruef": {"text": "Lieferanten-Eigenschaft nicht eindeutig: Bitte prüfen, ob der Abnehmer als Erzeuger im Sinne der PPWR handelt (siehe Test „Erzeuger“).", "role": "lieferant", "value": False},
        },
        "footnotes": [
            "Hinweis: Ein Lieferant kann in bestimmten Konstellationen selbst Erzeuger sein (vgl. Art. 3 Abs. 1 Nr. 13b PPWR).",
            "Art. 16 Abs. 1: Der Lieferant hat dem Erzeuger alle Informationen und Unterlagen zur Verfügung zu stellen, die dieser zum Nachweis der Konformität der Verpackungen benötigt (Papier oder elektronische Form).",
        ],
    },
    "a2": {
        "title": "Wer ist ERZEUGER nach PPWR?",
        "intro": "„Erzeuger“ ist derjenige natürliche oder juristische Person, die eine Verpackung oder ein verpacktes Produkt herstellt (Art. 3 Abs. 1 Nr. 13). Wegen Ausnahmen gilt für die Abgrenzung zum Lieferanten folgende Prüfreihenfolge:",
        "start": "q1",
        "nodes": {
            "q1": {"short": "Markeninhaber", "q": "Lässt eine Person A (1.) eine <strong>Verpackung</strong> (nicht Verpackungsmaterial) oder ein verpacktes Produkt unter ihrem <strong>Namen</strong> oder ihrer <strong>Marke</strong> (durch eine Person B) entwickeln oder herstellen und (2.) stellt Person A diese/s erstmals in der EU bereit? (= <strong>Markeninhaber</strong>)", "yes": "q2", "no": "r1"},
            "q2": {"short": "Kleinstunternehmen", "q": "Ist der <em>Markeninhaber</em> (Person A) ein <strong>Kleinstunternehmen</strong>*?", "yes": "q3", "no": "res_mi_13a"},
            "q3": {"short": "Person B liefert Verpackungen", "q": "Liefert Person B <strong>Verpackungen</strong> (nicht Verpackungsmaterial) an den Markeninhaber (Person A)?", "yes": "q4", "no": "r2"},
            "q4": {"short": "Selber Mitgliedstaat", "q": "Sind <strong>Markeninhaber</strong> und <strong>Lieferant</strong> der Verpackung <strong>im selben EU-Mitgliedstaat</strong> ansässig?", "yes": "res_lief_13b", "no": "q5"},
            "q5": {"short": "Lieferant in EU", "q": "Ist der <strong>Lieferant der Verpackung</strong> in der <strong>EU</strong> ansässig?", "yes": "res_art15", "no": "res_mi_rueck"},
            "r1": {"short": "Leere Verkaufs-/Umverpackung", "q": "Stellt eine Person eine <strong>leere Verkaufsverpackung</strong> oder <strong>leere Umverpackung</strong> erstmals in der EU bereit?", "yes": "res_material", "no": "r2"},
            "r2": {"short": "Abfüller", "q": "Stellt eine Person eine <strong>mit einem Produkt befüllte Verkaufsverpackung</strong> oder eine <strong>mit Verkaufseinheiten befüllte Umverpackung</strong> erstmals in der EU bereit? (= Abfüller)", "yes": "res_abfueller", "no": "r3"},
            "r3": {"short": "Transportverpackung", "q": "Stellt eine Person eine <strong>Transportverpackung</strong>, inkl. Verpackungen für den elektr. Handel, <strong>Serviceverpackung</strong> oder Primärproduktionsverpackungen in ihrer <strong>endgültigen Form</strong> und <strong>unbefüllt</strong> erstmals in der EU bereit?", "yes": "res_produzent", "no": "res_keinend"},
        },
        "results": {
            "res_material": {"text": "Lieferant von Verpackungsmaterial, d.h. kein „Erzeuger“, Art. 3 Abs. 1 Nr. 5-6", "role": "erzeuger", "value": False},
            "res_abfueller": {"text": "Abfüller ist Erzeuger, Art. 3 Abs. 1 Nr. 13", "role": "erzeuger", "value": True},
            "res_produzent": {"text": "Produzent der leeren Verpackung ist Erzeuger, Rückschluss aus Art. 3 Abs. 1 Nr. 15 a/c), Erwägungsgrund 122", "role": "erzeuger", "value": True},
            "res_keinend": {"text": "Sofern nicht in endgültiger Form, handelt es sich um Verpackungsmaterial, d.h. noch kein Erzeuger. Sofern befüllt, muss der Produzent der leeren Verpackung ermittelt werden.", "role": "erzeuger", "value": False},
            "res_mi_13a": {"text": "Markeninhaber ist Erzeuger, Art. 3 Abs. 1 Nr. 13a)", "role": "erzeuger", "value": True},
            "res_lief_13b": {"text": "Lieferant der Verpackung ist Erzeuger, Art. 3 Abs. 1 Nr. 13b)", "role": "erzeuger", "value": True},
            "res_art15": {"text": "Lieferant der Verpackung ist Erzeuger nur in Bezug auf Art. 15, im Übrigen bleibt der <em>Markeninhaber</em> Erzeuger, Art. 15 Abs. 12", "role": "erzeuger", "value": True},
            "res_mi_rueck": {"text": "Markeninhaber ist Erzeuger, Rückschluss aus Art. 15 Abs. 12", "role": "erzeuger", "value": True},
        },
        "footnotes": [
            "* Kleinstunternehmen: weniger als 10 Mitarbeiter (berechnet als Jahresarbeitseinheiten) und Jahresumsatz von höchstens 2 Mio. € oder Jahresbilanzsumme von höchstens 2 Mio. €.",
            "In bestimmten Fällen gehen die Erzeugerpflichten auf den Importeur oder Vertreiber über (Art. 21).",
        ],
    },
    "a3": {
        "title": "Wer ist HERSTELLER nach PPWR?",
        "intro": "„Hersteller“ ist derjenige Erzeuger, Importeur oder Vertreiber in einem EU-Mitgliedstaat, der für die Verpackung verantwortlich ist, wenn sie dort zu Abfall wird. Dabei gilt folgende Prüfreihenfolge:",
        "start": "q1",
        "nodes": {
            "q1": {"short": "Abfall in EU", "q": "Wird die Verpackung in einem <strong>EU-Mitgliedstaat zu Abfall</strong>? (dieser Mitgliedstaat ist <em>Inland</em>)", "yes": "q2", "no": "res_kein"},
            "q2": {"short": "Transport-/Serviceverpackung", "q": "Handelt es sich um eine <strong>Transportverpackung</strong>, inkl. Verpackungen für den elektronischen Handel, <strong>Serviceverpackung</strong> oder Primärproduktionsverpackung?", "yes": "t3", "no": "v3"},
            "t3": {"short": "Inland, leer", "q": "Stellt ein <strong>im Inland ansässiger</strong> Erzeuger, Importeur oder Vertreiber diese Verpackung in ihrer <strong>endgültigen Form</strong> und <strong>unbefüllt</strong> erstmals <strong>im Inland</strong> bereit?", "yes": "res_15a", "no": "t4"},
            "t4": {"short": "Anderer Mitgliedstaat, leer", "q": "Stellt ein <strong>in der EU ansässiger</strong> Erzeuger, Importeur oder Vertreiber diese Verpackung in ihrer <strong>endgültigen Form</strong> und <strong>unbefüllt</strong> in einem <strong>anderen Mitgliedstaat direkt an Endabnehmer</strong>* erstmals bereit?", "yes": "res_15c", "no": "t5"},
            "t5": {"short": "Drittland, leer", "q": "Stellt ein <strong>in einem Drittland ansässiger</strong> Erzeuger oder Vertreiber diese Verpackung in ihrer <strong>endgültigen Form</strong> und <strong>unbefüllt</strong> in der EU <strong>direkt an Endabnehmer</strong>* erstmals bereit?", "yes": "res_15c", "no": "q6"},
            "v3": {"short": "Inland, verpacktes Produkt", "q": "Stellt ein <strong>im Inland ansässiger</strong> Erzeuger, Importeur oder Vertreiber das (in eine Verkaufsverpackung oder Umverpackung) <strong>verpackte Produkt</strong> erstmals <strong>im Inland</strong> bereit?", "yes": "res_15b", "no": "v4"},
            "v4": {"short": "Anderer Mitgliedstaat, verpacktes Produkt", "q": "Stellt ein <strong>in der EU ansässiger</strong> Erzeuger, Importeur oder Vertreiber das <strong>verpackte Produkt</strong> in einem <strong>anderen Mitgliedstaat direkt an Endabnehmer</strong>* erstmals bereit?", "yes": "res_15d", "no": "v5"},
            "v5": {"short": "Drittland, verpacktes Produkt", "q": "Stellt ein <strong>in einem Drittland ansässiger</strong> Erzeuger oder Vertreiber das <strong>verpackte Produkt</strong> in der EU <strong>direkt an Endabnehmer</strong>* erstmals bereit?", "yes": "res_15d", "no": "q6"},
            "q6": {"short": "Auspacken", "q": "<strong>Packt</strong> ein <strong>in der EU ansässiger</strong> Erzeuger, Importeur oder Vertreiber das <strong>verpackte Produkt aus</strong>, <strong>ohne Endabnehmer</strong>* zu sein?", "yes": "res_15e", "no": "res_kein"},
        },
        "results": {
            "res_kein": {"text": "Kein Hersteller nach PPWR", "role": "hersteller", "value": False},
            "res_15a": {"text": "Diese inländische Person ist Hersteller, Art. 3 Abs. 1 Nr. 15a)", "role": "hersteller", "value": True},
            "res_15b": {"text": "Diese inländische Person ist Hersteller, Art. 3 Abs. 1 Nr. 15b)", "role": "hersteller", "value": True},
            "res_15c": {"text": "Diese ausländische Person ist Hersteller, Art. 3 Abs. 1 Nr. 15c)", "role": "hersteller", "value": True},
            "res_15d": {"text": "Diese ausländische Person ist Hersteller, Art. 3 Abs. 1 Nr. 15d)", "role": "hersteller", "value": True},
            "res_15e": {"text": "Diese Person ist Hersteller, Art. 3 Abs. 1 Nr. 15e)", "role": "hersteller", "value": True},
        },
        "footnotes": [
            "* Endabnehmer: eine in der EU ansässige Person, der – von einer anderen Person – ein (verpacktes) Produkt als Verbraucher oder als beruflicher Endabnehmer bereitgestellt wird und die dieses Produkt in der an sie gelieferten Form nicht erneut auf dem Markt bereitstellt (Art. 3 Abs. 1 Nr. 23).",
        ],
    },
    "a4": {
        "title": "Wann ist ein Importeur oder Vertreiber ERZEUGER im Sinne der PPWR?",
        "intro": "Wann die Erzeugerpflichten auf den Importeur oder Vertreiber nach Art. 21 übergehen, ergibt sich aus folgender Prüfreihenfolge:",
        "start": "q1",
        "nodes": {
            "q1": {"short": "Eigener Name/Marke", "q": "Bringt ein <strong>Importeur</strong> oder <strong>Vertreiber</strong> eine Verpackung (nicht Verpackungsmaterial) unter seinem <strong>eigenen Namen</strong> oder seiner <strong>eigenen Marke</strong> in der EU in Verkehr? (= <strong>Markeninhaber</strong>)", "yes": "q2", "no": "qv"},
            "q2": {"short": "Kleinstunternehmen", "q": "Ist der Importeur oder Vertreiber ein <strong>Kleinstunternehmen</strong>*?", "yes": "q3", "no": "res_iv_erz"},
            "q3": {"short": "Lieferant in EU", "q": "Ist diejenige Person, die dem Importeur oder Vertreiber die Verpackung (nicht Verpackungsmaterial) <strong>liefert</strong>, <strong>in der EU ansässig</strong>?", "yes": "res_lief_pers", "no": "res_iv_erz"},
            "qv": {"short": "Veränderung", "q": "<strong>Verändert</strong> ein Importeur oder Vertreiber eine <strong>bereits in der EU in Verkehr gebrachte Verpackung</strong> so, dass ihre <strong>Konformität mit der PPWR beeinträchtigt</strong> werden kann?", "yes": "res_iv_erz", "no": "res_keine"},
        },
        "results": {
            "res_iv_erz": {"text": "Importeur oder Vertreiber ist Erzeuger, Art. 21 Unterabs. 1", "role": "erzeuger", "value": True},
            "res_keine": {"text": "Keine Übertragung der Erzeugerpflichten auf Importeur oder Vertreiber.", "role": "erzeuger", "value": False},
            "res_lief_pers": {"text": "Liefernde Person ist Erzeuger nur in Bezug auf Art. 15, im Übrigen ist der <em>Vertreiber</em> der Erzeuger, Art. 21 Unterabs. 2. Einen Importeur gibt es hier nicht.", "role": "erzeuger", "value": False},
        },
        "footnotes": [
            "* Kleinstunternehmen: weniger als 10 Mitarbeiter (berechnet als Jahresarbeitseinheiten) und Jahresumsatz von höchstens 2 Mio. € oder Jahresbilanzsumme von höchstens 2 Mio. €.",
            "<em>Importeur</em> ist jede in der EU ansässige natürliche oder juristische Person, die Verpackungen <em>aus einem Drittland</em> (d.h. von außerhalb der EU) erstmals in der EU bereitstellt.",
            "<em>Vertreiber</em> ist jede natürliche oder juristische Person in der Lieferkette, die Verpackungen auf dem EU-Markt bereitstellt, mit Ausnahme des Erzeugers oder des Importeurs.",
        ],
    },
}

GRUND = [
    {"key": "importeur", "label": "Importeur", "q": "Stellen Sie als <strong>in der EU ansässige</strong> Person Verpackungen <strong>aus einem Drittland</strong> (d.h. von außerhalb der EU) <strong>erstmals in der EU</strong> bereit?", "note": "Importeur ist jede in der EU ansässige natürliche oder juristische Person, die Verpackungen aus einem Drittland erstmals in der EU bereitstellt (Art. 3 Abs. 1 Nr. 17)."},
    {"key": "vertreiber", "label": "Vertreiber", "q": "Stellen Sie Verpackungen auf dem <strong>EU-Markt</strong> bereit, <strong>ohne Erzeuger oder Importeur</strong> zu sein?", "note": "Vertreiber ist jede natürliche oder juristische Person in der Lieferkette, die Verpackungen auf dem EU-Markt bereitstellt, mit Ausnahme des Erzeugers oder des Importeurs (Art. 3 Abs. 1 Nr. 18)."},
]

ROLE_LABELS = {"erzeuger": "Erzeuger", "hersteller": "Hersteller", "lieferant": "Lieferant"}

# ---------------- State ----------------
for k in ("lief", "a2", "a3", "a4"):
    if k not in st.session_state:
        st.session_state[k] = {"node": TREES[k]["start"], "hist": [], "done": None}
if "grund" not in st.session_state:
    st.session_state["grund"] = {}

# ---------------- Kopf ----------------
cl, cc, cr = st.columns([1, 2, 1])
with cc:
    st.image(os.path.join(os.path.dirname(__file__), "logo.jpg"), width=240)
st.markdown('<h1 class="ppwrtitle">PPWR-Rollenprüfung</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Interaktive Ermittlung Ihrer Rolle nach der PPWR</p>', unsafe_allow_html=True)

with st.expander("Definitionen der Rollen im Überblick"):
    st.markdown("**Lieferant** ist, wer Verpackungen oder Verpackungsmaterial an einen Erzeuger liefert. Er muss dem Erzeuger alle Informationen und Unterlagen zur Verfügung stellen, die dieser zum Nachweis der Konformität der Verpackungen benötigt (auf Papier oder in elektronischer Form).")
    st.markdown("**Erzeuger** ist, wer eine Verpackung oder ein verpacktes Produkt unter eigenem Namen oder eigener Marke entwickeln oder herstellen lässt oder selbst herstellt, um diese/s in der EU in Verkehr zu bringen. Der Erzeuger muss die Konformität der Verpackung nachweisen (u. a. Nachhaltigkeits- und Kennzeichnungsanforderungen, EU-Konformitätserklärung).")
    st.markdown("**Hersteller** ist der Erzeuger, Importeur oder Vertreiber, der in dem EU-Mitgliedstaat, in dem die Verpackung zu Abfall wird, für diese verantwortlich ist. Er registriert sich im nationalen Register, meldet jährlich die in Verkehr gebrachten Mengen und trägt die erweiterte Herstellerverantwortung – je Mitgliedstaat gibt es einen Hersteller.")
    st.markdown("**Importeur** ist jede in der EU ansässige natürliche oder juristische Person, die Verpackungen aus einem Drittland (d. h. von außerhalb der EU) erstmals in der EU bereitstellt.")
    st.markdown("**Vertreiber** ist jede natürliche oder juristische Person in der Lieferkette, die Verpackungen auf dem EU-Markt bereitstellt, mit Ausnahme des Erzeugers oder des Importeurs. Vertreiber müssen die Einhaltung der Vorgaben durch Erzeuger, Importeure und Hersteller überprüfen.")

# ---------------- Assistent ----------------
def render_tree(key):
    t = TREES[key]
    s = st.session_state[key]
    st.markdown(f"### {t['title']}")
    st.write(t["intro"])

    if s["done"]:
        r = t["results"][s["done"]]
        badge_cls = "badge-yes" if r["value"] else "badge-no"
        badge_txt = f"Rolle „{ROLE_LABELS[r['role']]}“: {'Ja' if r['value'] else 'Nein'}"
        st.markdown(
            f'<div class="result"><h3>Ergebnis</h3><p>{r["text"]}</p>'
            f'<span class="badge {badge_cls}">{badge_txt}</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("Prüfung neu starten", key=f"{key}_restart"):
            s.update(node=t["start"], hist=[], done=None)
            st.rerun()
    else:
        node = t["nodes"][s["node"]]
        if s["hist"]:
            st.caption("   ·   ".join(f"{i+1}. {h['short']}: {'Ja' if h['a'] else 'Nein'}" for i, h in enumerate(s["hist"])))
        st.markdown(f'<div class="step">Frage {len(s["hist"]) + 1}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="question">{node["q"]}</div>', unsafe_allow_html=True)
        cy, cn, cb, _ = st.columns([1, 1, 1.2, 4])
        with cy:
            ja = st.button("Ja", key=f"{key}_ja_{len(s['hist'])}", type="primary")
        with cn:
            nein = st.button("Nein", key=f"{key}_nein_{len(s['hist'])}")
        with cb:
            back = st.button("Zurück", key=f"{key}_back_{len(s['hist'])}", disabled=not s["hist"])
        if ja or nein:
            s["hist"].append({"short": node["short"], "a": ja, "nodeId": s["node"]})
            nxt = node["yes"] if ja else node["no"]
            if nxt in t["results"]:
                s["done"] = nxt
            else:
                s["node"] = nxt
            st.rerun()
        if back:
            last = s["hist"].pop()
            s["node"] = last["nodeId"]
            s["done"] = None
            st.rerun()

    for fn in t["footnotes"]:
        st.markdown(f'<span class="footnote">{fn}</span>', unsafe_allow_html=True)

def render_grund():
    st.markdown("### Grundrollen: Importeur und Vertreiber")
    st.write("Diese beiden Rollen ergeben sich direkt aus den Definitionen der PPWR (Art. 3 Abs. 1 Nr. 17–18) und sind unabhängig von den Entscheidungsbäumen zu beantworten.")
    for g in GRUND:
        v = st.session_state["grund"].get(g["key"])
        status = "offen" if v is None else ("Ja" if v else "Nein")
        badge_cls = "badge-yes" if v else "badge-no"
        st.markdown(f'<div class="question">{g["q"]}</div>', unsafe_allow_html=True)
        cy, cn, _ = st.columns([1, 1, 6])
        with cy:
            if st.button("Ja", key=f"grund_{g['key']}_ja", type="primary"):
                st.session_state["grund"][g["key"]] = True
                st.rerun()
        with cn:
            if st.button("Nein", key=f"grund_{g['key']}_nein"):
                st.session_state["grund"][g["key"]] = False
                st.rerun()
        st.markdown(f'Rolle „{g["label"]}“: <span class="badge {badge_cls}">{status}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="footnote">{g["note"]}</span>', unsafe_allow_html=True)
        st.divider()

def compute_roles():
    roles = []
    a2 = TREES["a2"]["results"][st.session_state["a2"]["done"]] if st.session_state["a2"]["done"] else None
    a4 = TREES["a4"]["results"][st.session_state["a4"]["done"]] if st.session_state["a4"]["done"] else None
    a3 = TREES["a3"]["results"][st.session_state["a3"]["done"]] if st.session_state["a3"]["done"] else None
    lief = TREES["lief"]["results"][st.session_state["lief"]["done"]] if st.session_state["lief"]["done"] else None

    erz = "Ja" if (a2 and a2["value"]) or (a4 and a4["value"]) else ("Nein" if (a2 or a4) else "offen")
    roles.append(("Erzeuger", erz))
    her = ("Ja" if a3["value"] else "Nein") if a3 else "offen"
    roles.append(("Hersteller", her))
    lf = ("Ja" if lief["value"] else "Nein") if lief else "offen"
    roles.append(("Lieferant", lf))
    for g in GRUND:
        v = st.session_state["grund"].get(g["key"])
        roles.append((g["label"], "offen" if v is None else ("Ja" if v else "Nein")))
    return roles

def render_summary():
    st.markdown("### Gesamtergebnis – Ihre Rollen nach PPWR")
    roles = compute_roles()
    cols = st.columns(len(roles))
    for col, (label, status) in zip(cols, roles):
        cls = "st-ja" if status == "Ja" else ("st-nein" if status == "Nein" else "st-offen")
        with col:
            st.markdown(f'<div class="rolecard"><div class="rname">{label}</div><div class="status {cls}">{status}</div></div>', unsafe_allow_html=True)
    st.markdown("#### Begründungen")
    for k in ("lief", "a2", "a3", "a4"):
        t = TREES[k]
        done = st.session_state[k]["done"]
        txt = t["results"][done]["text"] if done else "Noch nicht geprüft."
        st.markdown(f"**{t['title']}**")
        st.markdown(txt, unsafe_allow_html=True)
    st.markdown('<span class="footnote">Hinweis: Ein Unternehmen kann mehrere Rollen gleichzeitig einnehmen (z. B. Erzeuger und zusätzlich Hersteller in einem Mitgliedstaat).</span>', unsafe_allow_html=True)

# ---------------- Auswahl & Inhalt ----------------
sel = st.radio(
    "Rollenprüfung wählen",
    ["Lieferant", "Erzeuger", "Hersteller", "Importeur/Vertreiber als Erzeuger", "Grundrollen", "Gesamtergebnis"],
    horizontal=True,
    label_visibility="collapsed",
    key="active_test",
)
st.divider()
if sel == "Lieferant":
    render_tree("lief")
elif sel == "Erzeuger":
    render_tree("a2")
elif sel == "Hersteller":
    render_tree("a3")
elif sel == "Importeur/Vertreiber als Erzeuger":
    render_tree("a4")
elif sel == "Grundrollen":
    render_grund()
else:
    render_summary()

st.markdown("---")
st.caption("Quelle: IK-Mitteilung „Mitteilung zu den wichtigsten Rollen in der PPWR“ vom 13. März 2026. Die Angaben stehen unter dem Vorbehalt angekündigter Veröffentlichungen der EU-Kommission und der nationalen Verpackungsregister.")
