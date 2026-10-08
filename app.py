"""Bill Splitter — a compact, light Streamlit interface.

Run: python -m streamlit run app.py
Keep db.py and settle.py beside this file. No JavaScript is required.
"""
from html import escape
from decimal import Decimal, InvalidOperation

import streamlit as st

import db
from settle import compute_balances, settle

st.set_page_config(page_title="Bill Splitter", page_icon="🧾", layout="centered")
db.init_db()

# This design deliberately uses a light surface, even if Streamlit's menu is
# set to Dark. HTML section headers are the DOM-independent color fallback.
CSS = """
:root { color-scheme: light; }
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: #f7f8fa !important; color: #18232d !important;
}
.stApp, .stApp button, .stApp input, .stApp textarea,
.stApp [data-baseweb="select"], .bs-card, .bs-section {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarCollapsedControl"] button { color: #64717d !important; }
[data-testid="stSidebarCollapseButton"] svg, [data-testid="stSidebarCollapsedControl"] svg { fill: #64717d !important; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stNumberInput"] button { background: #edf1f4 !important; color: #64717d !important; border: 0 !important; }
[data-testid="stNumberInput"] button svg { fill: #64717d !important; }
[data-testid="stHeader"] { background: #f7f8fa !important; }
.block-container { max-width: 820px; padding-top: 4.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e6e9ed; }
[data-testid="stSidebar"] > div { background: #ffffff !important; }
/* Native text and form surfaces must remain readable under a Dark setting. */
h1, h2, h3, h4, label, [data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"], [data-testid="stMetricLabel"],
[data-testid="stMetricValue"], [data-testid="stCaptionContainer"] {
    color: #18232d !important;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: #64717d !important; }
/* Streamlit has shipped several widget DOM layouts. Style the visible
   controls themselves as well as the older BaseWeb wrappers. */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] input,
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stNumberInput"] [data-baseweb="base-input"],
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] [role="combobox"],
[data-testid="stSelectbox"] [role="combobox"] > div {
    background-color: #f8fafb !important;
    color: #18232d !important;
    -webkit-text-fill-color: #18232d !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stSelectbox"] [role="combobox"] * {
    color: #18232d !important;
    -webkit-text-fill-color: #18232d !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder {
    color: #84929d !important;
    -webkit-text-fill-color: #84929d !important;
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] summary,
[data-testid="stSidebar"] details > summary {
    background: #ffffff !important;
    color: #18232d !important;
}
[data-testid="stExpander"] summary *,
[data-testid="stExpander"] summary p,
[data-testid="stSidebar"] details > summary * { color: #18232d !important; }
[data-testid="stExpander"] summary svg { fill: #64717d !important; }
/* Sidebar group actions have separate, softly colored surfaces. */
.st-key-create_group_panel [data-testid="stExpander"] details {
    background: #f4fbf6 !important;
    border: 1px solid #b8dfc4 !important;
    border-radius: 10px !important;
}
.st-key-create_group_panel [data-testid="stExpander"] summary,
.st-key-create_group_panel [data-testid="stExpander"] details > summary {
    background: #e6f6eb !important;
    color: #166534 !important;
}
.st-key-create_group_panel [data-testid="stExpander"] summary * { color: #166534 !important; }
.st-key-create_group_panel [data-testid="stExpander"] summary svg { fill: #166534 !important; }
.st-key-manage_group_panel [data-testid="stExpander"] details {
    background: #f4f7fb !important;
    border: 1px solid #bfd1e3 !important;
    border-radius: 10px !important;
}
.st-key-manage_group_panel [data-testid="stExpander"] summary,
.st-key-manage_group_panel [data-testid="stExpander"] details > summary {
    background: #e9f0f8 !important;
    color: #123456 !important;
}
.st-key-manage_group_panel [data-testid="stExpander"] summary * { color: #123456 !important; }
.st-key-manage_group_panel [data-testid="stExpander"] summary svg { fill: #123456 !important; }
[data-baseweb="input"], [data-baseweb="base-input"],
[data-baseweb="select"] > div, [data-baseweb="textarea"] {
    background: #f8fafb !important;
    color: #18232d !important;
    border-radius: 8px;
}
/* BaseInput can be the outer field itself, or nested inside Input.
   Style either root directly; only a nested root loses its border. */
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="select"] {
    background: #f8fafb !important;
    border: 1px solid #cbd5df !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-baseweb="input"] *,
[data-baseweb="base-input"] *,
[data-baseweb="select"] * {
    border: 0 !important;
    outline: 0 !important;
    box-shadow: none !important;
}
[data-baseweb="input"] input,
[data-baseweb="base-input"] input,
[data-baseweb="input"] [data-baseweb="base-input"],
[data-baseweb="select"] > div,
[data-baseweb="select"] [role="combobox"] {
    background-color: #f8fafb !important;
    color: #18232d !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within,
[data-baseweb="select"]:focus-within {
    border-color: #16a34a !important;
    box-shadow: none !important;
}
input, textarea, [data-baseweb="select"] span {
    color: #18232d !important; -webkit-text-fill-color: #18232d !important;
}
input::placeholder, textarea::placeholder { color: #8a96a2 !important; }
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
    background: #ffffff !important; color: #18232d !important;
}
[role="option"] { color: #18232d !important; background: #ffffff !important; }
[role="option"]:hover { background: #f0f5f3 !important; }
[data-baseweb="select"] svg, [data-baseweb="input"] svg { fill: #73808c !important; }
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: #e3e8ec !important; border-radius: 12px !important;
}
[data-testid="stForm"] { background: #ffffff; border-color: #e3e8ec; border-radius: 12px; }
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
    background: #ffffff !important; color: #33414b !important;
    border: 1px solid #dce3e8 !important; border-radius: 8px;
    font-weight: 600; box-shadow: none;
}
[data-testid="stButton"] button [data-testid="stMarkdownContainer"],
[data-testid="stFormSubmitButton"] button [data-testid="stMarkdownContainer"],
[data-testid="stButton"] button p, [data-testid="stFormSubmitButton"] button p {
    color: inherit !important;
}
[data-testid="stButton"] button:hover { border-color: #16a34a !important; color: #15803d !important; }
[data-testid="stFormSubmitButton"] button {
    background: #16a34a !important; color: #ffffff !important; border-color: #16a34a !important;
}
[data-testid="stFormSubmitButton"] button:hover { background: #15803d !important; }
[data-testid="stCode"], [data-testid="stCodeBlock"] {
    background: #f8fafb !important; color: #33414b !important;
}
[data-testid="stCode"] pre, [data-testid="stCode"] code,
[data-testid="stCodeBlock"] pre, [data-testid="stCodeBlock"] code {
    background: #f8fafb !important; color: #33414b !important;
}
[data-testid="stAlert"] { color: #18232d !important; }

/* Streamlit tabs expose role="tab" in the rendered UI. */
[role="tablist"] { gap: 0.12rem !important; background: transparent; border: 0; padding: 0; }
[role="tab"] {
    position: relative;
    min-height: 44px;
    margin: 0 0.1rem 0 0 !important;
    padding: 0.65rem 1.05rem !important;
    border: 0 !important;
    border-radius: 9px !important;
    color: white !important;
    opacity: 0.60;
    box-shadow: none !important;
    background-image: none !important;
    background-color: #123456 !important;
    transition: opacity 120ms ease;
}
[role="tab"]:nth-of-type(1),
[role="tab"]:nth-child(1 of [role="tab"]) { background-color: #16a34a !important; }
[role="tab"]:nth-of-type(2),
[role="tab"]:nth-child(2 of [role="tab"]) { background-color: #dc2626 !important; }
[role="tab"]:nth-of-type(3),
[role="tab"]:nth-child(3 of [role="tab"]) { background-color: #123456 !important; }
[role="tab"] *, [role="tab"] p { color: white !important; -webkit-text-fill-color: white !important; font-weight: 600; }
[role="tab"]:hover, [role="tab"][aria-selected="true"] { opacity: 1; box-shadow: none !important; border: 0 !important; }
/* Mask Streamlit's underline, including the tiny exposed ends at the corners. */
[role="tab"][aria-selected="true"]::before {
    content: "" !important;
    display: block !important;
    position: absolute;
    left: -2px; right: -2px; bottom: -5px; height: 14px;
    background: #f7f8fa !important;
    z-index: 9998;
}
[role="tab"][aria-selected="true"]::after {
    content: "" !important;
    display: block !important;
    position: absolute;
    left: 0; right: 0; bottom: 0; height: 14px;
    background-color: inherit !important;
    border-radius: 0 0 9px 9px;
    z-index: 9999;
}
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"],
[data-testid="stTabHighlight"], [data-testid="stTabBorder"] { display: none !important; }
/* Streamlit moves BaseWeb's presentation indicator during tab switches. */
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"],
[data-testid="stTabs"] [role="tablist"] > [role="presentation"][aria-hidden="true"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    transition: none !important;
    animation: none !important;
}

/* Guaranteed colored HTML: never hide this when a panel selector fails. */
.bs-section { padding: 18px 20px; border-radius: 10px; margin-bottom: 4px; }
.bs-log { background: #f0fdf4; --section-color: #16a34a; }
.bs-settle { background: #fef2f2; --section-color: #dc2626; }
.bs-history { background: #f1f5f9; --section-color: #475569; border: 1px solid #e2e8f0; }
.bs-section-title { font-size: 1rem; font-weight: 650; color: var(--section-color); margin-bottom: 4px; }
.bs-section-note { font-size: 0.85rem; color: #64717d; line-height: 1.5; }
.bs-hero { margin: 0 0 12px; }
.bs-eyebrow { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.09em; color: #73808c; text-transform: uppercase; margin: 0 0 7px; }
.bs-hero h1 { color: #18232d !important; font-size: clamp(2.2rem, 5vw, 2.8rem); font-weight: 750; letter-spacing: -0.045em; line-height: 1.08; margin: 0 !important; padding: 0; }
.bs-hero-dot { color: #16a34a; }
.bs-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 4px; }
.bs-stat { background: #ffffff; border: 1px solid #e3e8ec; border-radius: 10px; padding: 16px 18px; }
.bs-stat-label { font-size: 0.8rem; color: #73808c; margin-bottom: 6px; }
.bs-stat-value { font-size: 1.7rem; color: #18232d; font-weight: 650; font-variant-numeric: tabular-nums; }
.bs-card { margin-bottom: 12px; background: #ffffff; border: 1px solid #e3e8ec; border-radius: 12px; padding: 18px 20px; }
.bs-card-title { color: #18232d; font-size: 0.95rem; font-weight: 650; margin-bottom: 12px; }
.bs-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 12px 0; border-bottom: 1px solid #edf0f2; }
.bs-row:last-child { border-bottom: 0; padding-bottom: 0; }
.bs-row:first-of-type { padding-top: 0; }
.bs-name { color: #26343e; font-size: 0.9rem; font-weight: 600; overflow-wrap: anywhere; }
.bs-detail { color: #73808c; font-size: 0.78rem; margin-top: 4px; overflow-wrap: anywhere; }
.bs-money { color: #33414b; font-variant-numeric: tabular-nums; white-space: nowrap; font-weight: 600; font-size: 0.95rem; }
.bs-history-entry { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.st-key-history_items {
    background: #ffffff !important; border: 1px solid #e3e8ec !important;
    border-radius: 12px !important; padding: 18px 20px !important; margin-bottom: 12px;
}
.bs-history-separator { height: 1px; background: #e7ebef; margin: 4px 0; }
.st-key-history_items [data-testid="stButton"] button {
    color: #b91c1c !important; background: #fef2f2 !important; border-color: #fecaca !important;
}
.st-key-history_items [data-testid="stButton"] button:hover {
    color: #991b1b !important; background: #fee2e2 !important; border-color: #fca5a5 !important;
}
.bs-positive { color: #16a34a; }
.bs-negative { color: #dc2626; }
.bs-empty { background: #ffffff; border: 1px solid #e3e8ec; border-radius: 12px; padding: 30px 24px; color: #73808c; font-size: 0.9rem; line-height: 1.7; }

/* Optional enhancement, NOT required for visible color. No sibling guesses:
   locate the BaseWeb panel containing our own section header. */
@supports selector(div:has(.bs-section)) {
    :is(div[data-baseweb="tab-panel"], div[role="tabpanel"]):has(.bs-section) {
        padding: 14px 0 0;
    }
}
@media (max-width: 600px) {
    .block-container { padding: 4.5rem 1rem 2rem; }
    [role="tab"] { padding: 0.65rem 0.55rem; }
    [role="tab"] p { font-size: 0.78rem; }
    .bs-card, .bs-section { padding: 16px; }
    .bs-stat { padding: 14px; }
    .bs-stat-value { font-size: 1.4rem; }
}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def html(content):
    st.markdown(content, unsafe_allow_html=True)


def markdown_safe(value):
    return "".join("\\" + char if char in "\\`*_{}[]()#+-.!|>" else char for char in str(value))


def section(theme, title, note):
    html(f'<div class="bs-section bs-{theme}"><div class="bs-section-title">{escape(title)}</div>'
         f'<div class="bs-section-note">{escape(note)}</div></div>')


def empty(message):
    html(f'<div class="bs-empty">{escape(message)}</div>')


def card(title, rows):
    html(f'<div class="bs-card"><div class="bs-card-title">{escape(title)}</div>{"".join(rows)}</div>')


def row(name, detail, amount, color=""):
    return (f'<div class="bs-row"><div><div class="bs-name">{escape(name)}</div>'
            f'<div class="bs-detail">{escape(detail)}</div></div>'
            f'<div class="bs-money {color}">{escape(amount)}</div></div>')


def get_expenses_with_ids(group_id):
    records = db.get_expenses(group_id)
    if not records or "id" in records[0]:
        return records
    # Older db.py versions leave the id out of get_expenses().
    conn = db.get_connection()
    try:
        rows = conn.execute(
            """SELECT e.id, e.description, e.amount, p.name AS payer_name
               FROM expenses e JOIN people p ON e.paid_by = p.id
               WHERE e.group_id = ? ORDER BY e.created_at, e.id""",
            (group_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_expense_record(expense_id, group_id):
    conn = db.get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM expenses WHERE id = ? AND group_id = ?",
            (expense_id, group_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


with st.sidebar:
    st.header("Your groups")
    groups = db.get_groups()
    if groups:
        group_names = dict(groups)
        group_ids = list(group_names)
        if st.session_state.get("group_id") not in group_ids:
            st.session_state["group_id"] = group_ids[0]
        gid = st.selectbox("Current group", group_ids,
                           index=group_ids.index(st.session_state["group_id"]),
                           format_func=lambda i: group_names[i])
        st.session_state["group_id"] = gid
    else:
        st.caption("Create your first group below.")

    with st.container(key="create_group_panel"):
        with st.expander("Create a group", expanded=not bool(groups)):
            with st.form("new_group_form", clear_on_submit=True, enter_to_submit=False):
                group_name = st.text_input("Group name", placeholder="Friday dinner")
                if st.form_submit_button("Create group", use_container_width=True):
                    if group_name.strip():
                        st.session_state["group_id"] = db.add_group(group_name.strip())
                        st.rerun()
                    else:
                        st.warning("Enter a group name.")

    if groups:
        people = db.get_people(st.session_state["group_id"])
        st.subheader("Members")
        if people:
            st.caption(" · ".join(name for _, name in people))
        else:
            st.caption("No members yet.")
        with st.form("new_member_form", clear_on_submit=True, enter_to_submit=False):
            person_name = st.text_input("Member name", placeholder="Enter a name")
            if st.form_submit_button("Add member", use_container_width=True):
                value = person_name.strip()
                if not value:
                    st.warning("Enter a member name.")
                elif value in [name for _, name in people]:
                    st.warning("That name is already in this group.")
                else:
                    db.add_person(st.session_state["group_id"], value)
                    st.rerun()

        with st.container(key="manage_group_panel"):
            with st.expander("Manage group and members"):
                if people:
                    member_ids = [pid for pid, _ in people]
                    member_names = dict(people)
                    remove_id = st.selectbox(
                        "Member to remove", member_ids,
                        format_func=lambda pid: member_names[pid],
                        key=f"remove_member_{gid}",
                    )
                    remove_name = member_names[remove_id]
                    paid_count = sum(
                        e["payer_name"] == remove_name
                        for e in db.get_expenses(gid)
                    )
                    st.caption(
                        f"Removing {remove_name} also deletes {paid_count} expense(s) "
                        "they paid. Other expenses will be split among the remaining members."
                    )
                    confirm_member = st.checkbox(
                        f"I understand what happens when I remove {remove_name}",
                        key=f"confirm_member_{gid}_{remove_id}",
                    )
                    if st.button("Remove member", disabled=not confirm_member,
                                 key=f"remove_member_button_{gid}", use_container_width=True):
                        db.delete_person(remove_id)
                        st.session_state["action_notice"] = f"Removed {remove_name}."
                        st.rerun()

                st.divider()
                current_group_name = dict(groups)[gid]
                group_expense_count = len(db.get_expenses(gid))
                st.caption(
                    f"Deleting {current_group_name} also deletes its {len(people)} "
                    f"member(s) and {group_expense_count} expense(s)."
                )
                confirm_group = st.checkbox(
                    f"I understand what happens when I delete {current_group_name}",
                    key=f"confirm_group_{gid}",
                )
                if st.button("Delete group", disabled=not confirm_group,
                             key=f"delete_group_button_{gid}", use_container_width=True):
                    db.delete_group(gid)
                    st.session_state["group_id"] = next(
                        (other_id for other_id in group_ids if other_id != gid), None
                    )
                    st.session_state["action_notice"] = f"Deleted {current_group_name}."
                    st.rerun()


groups = db.get_groups()
html('<div class="bs-hero"><div class="bs-eyebrow">Shared expenses, made simple</div>'
     '<h1>Bill Splitter<span class="bs-hero-dot">.</span></h1></div>')

if not groups:
    if "action_notice" in st.session_state:
        st.success(st.session_state.pop("action_notice"))
    empty("Start by creating a group in the sidebar. Then add the people sharing your expenses.")
    st.stop()

gid = st.session_state["group_id"]
people = db.get_people(gid)
names = [name for _, name in people]
expenses = get_expenses_with_ids(gid)
st.caption(f"{dict(groups)[gid]} · {len(people)} members · {len(expenses)} expenses")
if "action_notice" in st.session_state:
    st.success(st.session_state.pop("action_notice"))
if "expense_notice" in st.session_state:
    st.success(st.session_state.pop("expense_notice"))

tab_log, tab_settle, tab_hist = st.tabs(["Log expense", "Balances & Settlement", "Expense history"])

with tab_log:
    section("log", "Add an expense", "One person pays. Everyone in the group shares equally.")
    if not people:
        empty("Add a member in the sidebar to record your first expense.")
    else:
        with st.form(f"expense_form_{gid}", clear_on_submit=True, enter_to_submit=False):
            c1, c2 = st.columns(2)
            payer = c1.selectbox("Paid by", [pid for pid, _ in people], format_func=lambda pid: dict(people)[pid])
            amount_text = c2.text_input("Amount", placeholder="0.00")
            description = st.text_input("What was it for?", placeholder="Dinner, groceries, taxi…")
            st.caption(f"Equal split between {len(people)} members. Amounts use your group's currency.")
            submitted = st.form_submit_button("Add expense", use_container_width=True)
        if submitted:
            try:
                amount_value = Decimal(amount_text.strip())
            except InvalidOperation:
                amount_value = Decimal(0)
            if not amount_value.is_finite() or amount_value <= 0:
                st.error("Enter an amount greater than zero.")
            elif amount_value.as_tuple().exponent < -2:
                st.error("Enter an amount with no more than two decimal places.")
            else:
                amount = float(amount_value)
                reason = description.strip() or "Untitled expense"
                db.add_expense(gid, reason, amount, payer)
                st.session_state["expense_notice"] = (
                    f"Added **{amount:.2f}** · Paid by **{markdown_safe(dict(people)[payer])}**"
                    f" · For: **{markdown_safe(reason)}**"
                )
                st.rerun()

with tab_settle:
    section("settle", "Settle up", "See everyone's balance and who should pay whom.")
    if len(people) < 2:
        empty("Add at least two members to calculate a settlement.")
    elif not expenses:
        empty("No expenses to settle yet. Add one in Log expense.")
    else:
        total = sum(e["amount"] for e in expenses)
        share = total / len(people)
        exp_tuples = [(e["payer_name"], e["amount"]) for e in expenses]
        balances = compute_balances(names, exp_tuples)
        transfers = settle(dict(balances))
        html(f'<div class="bs-stats"><div class="bs-stat"><div class="bs-stat-label">Total spent</div>'
             f'<div class="bs-stat-value">{total:,.2f}</div></div><div class="bs-stat">'
             f'<div class="bs-stat-label">Per person</div><div class="bs-stat-value">{share:,.2f}</div></div></div>')
        paid = {name: 0.0 for name in names}
        for payer_name, value in exp_tuples:
            paid[payer_name] += value
        rows = []
        for name in names:
            balance = balances[name]
            color = "bs-positive" if balance > 0 else "bs-negative" if balance < 0 else ""
            status = "to receive" if balance > 0 else "to pay" if balance < 0 else "settled"
            rows.append(row(name, f"Paid {paid[name]:,.2f} · Share {share:,.2f} · {status}",
                            f"{balance:+,.2f}" if balance else "0.00", color))
        card("Balances", rows)
        if transfers:
            card("Suggested transfers", [row(f"{sender} → {receiver}", "Suggested payment",
                                             f"{value:,.2f}", "bs-negative")
                                         for sender, receiver, value in transfers])
        else:
            empty("Everyone is settled. No payments needed.")
        with st.expander("Copy summary for your group chat"):
            lines = [f"Bill Splitter — total {total:.2f}, per person {share:.2f}"]
            lines.extend(f"{sender} -> {receiver} {value:.2f}" for sender, receiver, value in transfers)
            if not transfers:
                lines.append("Everyone is settled.")
            st.code("\n".join(lines), language="text")

with tab_hist:
    section("history", "Expense history", "Every shared expense, with the most recent first.")
    if not expenses:
        empty("Your expenses will appear here after you record one.")
    else:
        with st.container(key="history_items"):
            html(f'<div class="bs-card-title">{len(expenses)} recorded expenses</div>')
            for index, expense in enumerate(reversed(expenses)):
                if index:
                    html('<div class="bs-history-separator" aria-hidden="true"></div>')
                description = expense["description"] or "Untitled expense"
                with st.container(key=f'history_row_{gid}_{expense["id"]}'):
                    info, action = st.columns([5, 1.15], vertical_alignment="center")
                    with info:
                        html(f'<div class="bs-history-entry"><div>'
                             f'<div class="bs-name">{escape(description)}</div>'
                             f'<div class="bs-detail">Paid by {escape(expense["payer_name"])}</div>'
                             f'</div><div class="bs-money">{expense["amount"]:,.2f}</div></div>')
                    with action:
                        if st.button("Delete", key=f'delete_expense_{gid}_{expense["id"]}',
                                     use_container_width=True):
                            if delete_expense_record(expense["id"], gid):
                                st.session_state["action_notice"] = (
                                    f'Deleted {description} ({expense["amount"]:,.2f}).'
                                )
                                st.rerun()
                            else:
                                st.error("That expense is no longer in this group.")
