import streamlit as st

from st_datatables import st_datatables, reset_selection
import pandas as pd

st.set_page_config(layout="wide")

@st.cache_data()
def load_data():
    print("Data loaded")
    df = pd.read_csv("./st_datatables/frontend/public/sample_data.csv")
    return df

@st.cache_data
def load_svg():
    print("SVG data loaded")
    eyeSvg = '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#000000"><path d="M480-320q75 0 127.5-52.5T660-500q0-75-52.5-127.5T480-680q-75 0-127.5 52.5T300-500q0 75 52.5 127.5T480-320Zm0-72q-45 0-76.5-31.5T372-500q0-45 31.5-76.5T480-608q45 0 76.5 31.5T588-500q0 45-31.5 76.5T480-392Zm0 192q-146 0-266-81.5T40-500q54-137 174-218.5T480-800q146 0 266 81.5T920-500q-54 137-174 218.5T480-200Z"/></svg>'
    editSvg = '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#000000"><path d="M120-120v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm584-528 56-56-56-56-56 56 56 56Z"/></svg>'
    delsvg  ='<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#000000"><path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm80-160h80v-360h-80v360Zm160 0h80v-360h-80v360Z"/></svg>'
    return eyeSvg, editSvg, delsvg

def on_detail_dismiss():
    reset_selection("table1", rerun=False)

def on_detail_dismiss2():
    print("on_detail_dismiss2 is running")
    st.session_state["detail_open"] = False
    st.session_state["detail_row"] = None
    st.session_state["edit_open"] = False
    st.session_state["edit_row"] = None

    reset_selection("buttons_table", rerun=False)
    if "buttons_table" in st.session_state:
        del st.session_state["buttons_table"]

@st.dialog("Detail Dialog",width="large", on_dismiss=on_detail_dismiss)
def show_detail_dialog(row: dict):
    st.image(row.get("structure_svg"), width=200)
    st.write(row.get("ID"))
    st.write(row.get("NAME"))
    st.write(row.get("shape"))
    st.write(row.get("person"))
    st.write(row.get("created_at"))
    del st.session_state["table1"]

@st.dialog("Detail Dialog",width="large", on_dismiss=on_detail_dismiss2)
def show_detail_dialog2(row: dict):
    st.image(row.get("structure_svg"), width=200)
    st.write(row.get("ID"))
    st.write(row.get("NAME"))
    st.write(row.get("shape"))
    st.write(row.get("person"))
    st.write(row.get("created_at"))
    
@st.dialog("Edit Dialog",width="large", on_dismiss=on_detail_dismiss2)
def show_edit_dialog(row: dict):
    with st.form("form"):
        st.text_input("ID",value=row.get("ID"))
        st.text_input("Name",value=row.get("NAME"))
        st.text_input("Shape",value=row.get("shape"))
        st.text_input("Person",value=row.get("person"))
        st.date_input("Date",value=row.get("created_at"))
        submit = st.form_submit_button("submit")
    if submit:
        print("submitted")
        # st.success("Updated")
        st.session_state["edit_open"] = False
        st.session_state["edit_row"] = None
        # return
        # st.rerun()
        st.stop()

df = load_data()
eyeSvg, editSvg,delsvg = load_svg()

TABS = ["SingleSelectTable", "MultiSelectTable", "TableWithButtons"]
active = st.segmented_control(
    "Menu",
    options=TABS,
    selection_mode="single",
    default=TABS[0],
    key="active_tab",
)
st.divider()
print("Edit Dialog:",(st.session_state.get("edit_open") and st.session_state.get("edit_row")))

if "table1" not in st.session_state:
    st.session_state.table1 = {'rows': [], 'indexes': [], 'count': 0}
if "selected" not in st.session_state:
    st.session_state.selected = {'rows': [], 'indexes': [], 'count': 0}
if st.session_state.get("detail_open") and st.session_state.get("detail_row"):
    show_detail_dialog2(st.session_state["detail_row"])
elif st.session_state.get("edit_open") and st.session_state.get("edit_row"):
    show_edit_dialog(st.session_state["edit_row"])

# --------------------------Single Row Select Table 
if active == "SingleSelectTable":
    st.subheader("Single select Table")
    selected_row = st_datatables(
        df=df, 
        pageLength=10, 
        lengthMenu=[10,25,50,100],
        orderable_cols=["ID","NAME","created_at","person"],
        searchable_cols=["ID","NAME","person"],
        select="single",
        scrollX=False,
        scrollY="500",
        deferRender=True,
        layout= {
            "top1End": {"buttons": ["colvis"],},
            },
        key="table1"
        )

    st.write(selected_row)
    if selected_row["count"] > 0:
        show_detail_dialog(selected_row["rows"][0])

# --------------------------Multi Row Select Table 
elif active == "MultiSelectTable":
    st.subheader("Multiselect Table")

    if st.button("Reset Row Selection"):
        reset_selection("multiselect_table")

    selected_row2 = st_datatables(
        df=df, 
        pageLength=10, 
        lengthMenu=[10,25,50,100],
        orderable_cols=["ID","NAME"],
        searchable_cols=["ID","NAME"],
        select="multi",
        scrollX=False,
        scrollY="500",
        deferRender=True,
        layout= {
            "top1End": {"buttons": ["colvis","copy","csv"],},
            },
        key="multiselect_table"
        )

    if selected_row2 != 0 and selected_row2["count"] > 0:
        indexes = selected_row2['indexes']
        st.write(f"Selected rows : {indexes}")

    st.write(selected_row2)

# --------------------------Table With Action Buttons
elif active == "TableWithButtons":
    st.subheader("Table with Action button")

    actions = {
        "insertIndex": 0,
        "btndirection": "vertical", 
        "buttons": [
            {"id": "detail", "title": "Detail", "text": "Detail","className": "detail-btn", "svg": eyeSvg},
            {"id": "edit", "title": "Edit", "text": "Edit","className": "edit-btn", "svg": editSvg},
            {"id": "delete", "title": "Delete", "text": "Delete", "className": "delete-btn", "svg": delsvg},
        ],
    }

    selected_row3 = st_datatables(
        df=df,
        pageLength=10,
        lengthMenu=[10,25,50,100],
        orderable_cols=["ID","NAME"],
        searchable_cols=["ID","NAME"],
        select=False,
        scrollX=False,
        scrollY="500",
        deferRender=True,
        layout= {
            "top1End": {"buttons": ["colvis"],},
            },
        actions=actions,
        key="buttons_table"
        )
    
    print("------------------------")
    print(not st.session_state.get("detail_open"))
    print(not st.session_state.get("edit_open"))
    print(selected_row3)
    print(isinstance(selected_row3, dict))
    print("action" in selected_row3)
    print("------------------------")
    
    if (not st.session_state.get("detail_open")) and (not st.session_state.get("edit_open")) \
    and selected_row3 and isinstance(selected_row3, dict) \
    and ("action" in selected_row3):
        action = selected_row3["action"]
        row_index = selected_row3.get("_rowIndex")
        st.write(f"{action} button of row {row_index} clicked!")

        if action == "detail":
            st.session_state["detail_row"] = selected_row3
            st.session_state["detail_open"] = True
            st.rerun()

        elif action == "edit":
            # show_edit_dialog(selected_row3)
            st.session_state["edit_row"] = selected_row3
            st.session_state["edit_open"] = True
            st.rerun()


    st.write(selected_row3) 

    st.divider()
    st.subheader("Horizontal Button Layout")
    actions_without_text = {
        "insertIndex": 6,
        "btndirection": "horizontal", 
        "buttons": [
            {"id": "detail", "title": "Detail","className": "detail-btn", "svg":eyeSvg},
            {"id": "edit",   "title": "Edit", "className": "edit-btn", "svg": editSvg},
            {"id": "delete",    "title": "Delete", "className": "delete-btn", "svg": delsvg},
        ],
    }
    
    selected_row4 = st_datatables(
        df=df, 
        pageLength=10, 
        lengthMenu=[10,25,50,100],
        orderable_cols=["ID","NAME"],
        searchable_cols=["ID","NAME"],
        select=False,
        scrollX=False,
        scrollY="500",
        deferRender=True,
        layout= {
            "top1End": {"buttons": ["colvis"],},
            },
        actions=actions_without_text,
        key="buttons_table_without_text"
        )

    st.write(selected_row4)