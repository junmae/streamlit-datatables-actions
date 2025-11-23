import streamlit as st
from st_datatables import st_datatables
import json
import pandas as pd
import os
import time

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import Draw as RDDraw

st.set_page_config(layout="wide")
from streamlit.components.v1 import html
import streamlit.components.v1 as components

st.session_state.setdefault("detail_open", False)
st.session_state.setdefault("detail_row", None)
st.session_state.setdefault("table1_prev", [])
st.session_state.setdefault("_restore_row_id", None)
st.session_state.setdefault("_just_closed", False)

def on_detail_dismiss():
    st.session_state["detail_open"] = False
    st.session_state["detail_row"] = None
    st.session_state["_just_closed"] = True
    st.session_state["table1_prev"] = []


@st.dialog("Detail Page",width="large", on_dismiss=on_detail_dismiss)
def show_detail_dialog(row: dict):
    name = row.get("SMILES")
    img = row.get("structure_svg")
    st.image(img, width=400)
    st.session_state["rid"] = row.get("ID")
    with st.container():
        col1, col2 = st.columns([1,8], gap="small")
        col1.write("")
        col1.write("SMILES:")
        col2.code(name)
    with st.container():
        col1, col2 = st.columns([1,8], gap="small")
        col1.write("")
        col1.write("INCHIKEY:")
        col2.code(row.get('INCHIKEY'))

if st.session_state.get("detail_open") and st.session_state.get("detail_row"):
    show_detail_dialog(st.session_state["detail_row"])
            

@st.cache_data
def load_svg():
    eyeSvg = '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#000000"><path d="M480-320q75 0 127.5-52.5T660-500q0-75-52.5-127.5T480-680q-75 0-127.5 52.5T300-500q0 75 52.5 127.5T480-320Zm0-72q-45 0-76.5-31.5T372-500q0-45 31.5-76.5T480-608q45 0 76.5 31.5T588-500q0 45-31.5 76.5T480-392Zm0 192q-146 0-266-81.5T40-500q54-137 174-218.5T480-800q146 0 266 81.5T920-500q-54 137-174 218.5T480-200Z"/></svg>'
    editSvg = '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#000000"><path d="M120-120v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm584-528 56-56-56-56-56 56 56 56Z"/></svg>'
    delsvg  ='<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#000000"><path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm80-160h80v-360h-80v360Zm160 0h80v-360h-80v360Z"/></svg>'
    return eyeSvg, editSvg, delsvg
    
eyeSvg, editSvg,delsvg = load_svg()

actions = {
    "insertIndex": 0,
    "btndirection": "vertical", 
    "buttons": [
        {"id": "detail", "title": "詳細", "text":  "Detail","className": "detail-btn", "svg":eyeSvg},
        {"id": "edit",   "title": "編集", "text":  "Edit","className": "edit-btn", "svg": editSvg},
        {"id": "run",    "title": "実行", "text":  "Run",  "className": "run-btn", "svg": delsvg},
    ],
}


def normalize(v):
    if v is None:
        return None
    return json.dumps(v, sort_keys=True, ensure_ascii=False)

def smiles_to_svg(smiles: str, w: int = 110, h: int = 80) -> str:
    if not smiles or Chem is None:
        return f"<svg width=\"{w}\" height=\"{h}\"></svg>"
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return f"<svg width=\"{w}\" height=\"{h}\"></svg>"
        AllChem.Compute2DCoords(mol)
        drawer = rdMolDraw2D.MolDraw2DSVG(w, h)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        return svg
    except Exception:
        return f"<svg width=\"{w}\" height=\"{h}\"></svg>"

@st.cache_data(show_spinner=False)
def build_df_with_assets(df: pd.DataFrame, w: int = 110, h: int = 80) -> pd.DataFrame:
    start = time.time()
    svg_list: list[str] = []
    for smi in df["SMILES"].astype(str).fillna(""):
        svg_list.append(smiles_to_svg(smi, w=w, h=h))
    out = df.copy()
    out.insert(0, "structure_svg", svg_list)
    print(time.time()-start)
    return out

state_key = "table1_prev"
if state_key not in st.session_state:
    st.session_state[state_key] = 0
    # st.session_state[state_key] = None


# st.write(os.listdir())

# selected_row = my_component("World")
df = pd.read_csv("./st_datatables/frontend/public/smiles1000.csv")

# df.drop(["PATTERN_FP","CANONICAL_SMILES"], axis=1, inplace=True)
df_with_assets = build_df_with_assets(df.iloc[:100,:], w=200, h=200)


# st.dataframe(df)
# # selected_row = my_component("World")
selected = st_datatables(
    df=df_with_assets, 
    pageLength=25, 
    lengthMenu=[10,25,100],
    orderable_cols=["MOLWT","NUM_ATOMS"],
    hidden_cols=["PATTERN_FP","CANONICAL_SMILES","INCHI"],
    searchable_cols=["SMIES","INCHI","NUM_ATOMS"],
    select="single",
    scrollX=False,
    scrollY=False,
    deferRender=True,
    layout= {
        "top1End": {"buttons": ["colvis"],},
        },
    actions=actions,
    key="table1"
    )


curr = selected["indexes"] if isinstance(selected, dict) else []
prev = st.session_state.get("table1_prev", [])
changed = (len(curr) > 0) and (set(curr) != set(prev))

if st.session_state.pop("_just_closed", False):
    st.session_state["table1_prev"] = curr
    changed = False
    
if changed and not st.session_state.get("detail_open", False):
    row = selected["rows"][0]
    st.session_state["detail_open"] = True
    st.session_state["detail_row"] = row
    st.session_state["_restore_row_id"] = row.get("ID")
    st.session_state["table1_prev"] = curr
    show_detail_dialog(row)
    
# --- scroll back to row ---
if st.session_state.get("_restore_row_id") and not st.session_state.get("detail_open"):
    rid = st.session_state["_restore_row_id"]
    components.html(
        f"""
<script>
(function(){{
  const TARGET_ID = "row-{rid}";
  function tryInDoc(doc){{
    try {{
      const el = doc.getElementById(TARGET_ID);
      if (el) {{
        el.scrollIntoView({{ behavior: "instant", block: "center" }});
        return true;
      }}
    }} catch(e){{}}
    const iframes = doc.querySelectorAll("iframe");
    for (const fr of iframes){{
      try {{
        const subDoc = fr.contentDocument;
        if (subDoc && tryInDoc(subDoc)) return true;
      }}catch(e){{}}
    }}
    return false;
  }}
  const rootDoc = (window.parent || window).document;
  let tries = 0, maxTries = 40;
  (function kick(){{
    if (tryInDoc(rootDoc) || tries >= maxTries) return;
    tries++;
    setTimeout(kick, 50);
  }})();
}})();
</script>
        """,
        height=0,
    )

