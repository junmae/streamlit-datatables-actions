import os

import streamlit as st
import streamlit.components.v1 as components

_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "st_datatables",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_datatables", path=build_dir)


def st_datatables(
    df = None,
    id_col="ID",
    pageLength=25, 
    lengthMenu = [10, 25, 50, 100], 
    orderable_cols=[],
    hidden_cols = [],
    searchable_cols=[],
    select="single",
    scrollX=False, 
    scrollY=False,
    deferRender=True,
    layout=None,
    actions=None,
    key=None
    ):
    
    
    """
    Create a new instance of the `st_datatables` Streamlit component.

    This component wraps DataTables v2 with support for selection, custom
    action buttons, scrolling, and the modern `layout` API (e.g. colvis/csv
    buttons). It accepts a pandas DataFrame or explicit column/data arguments.

    Parameters
    ----------
    df : pandas.DataFrame
    pageLength : int, default 25
        Number of rows per page initially.
    lengthMenu : list[int], default [10, 25, 50, 100]
        Available options for rows per page.
    orderable_cols : list[str], default []
        Column names that can be sorted.
    hidden_cols : list[str], default []
        Column names to hide.
    searchable_cols : list[str], default []
        Column names that should be included in search.
    select : {"single", "multi", False}, default "single"
        Row selection mode: single row, multiple rows, or disabled.
    scrollX : bool or str, default False
        Enable horizontal scrolling, or specify a CSS width.
    scrollY : bool or str, default False
        Enable vertical scrolling, or specify a CSS height (e.g. "480px").
    deferRender : bool, default True
        Only render rows as they are displayed (improves performance with
        images/SVGs and larger datasets).
    layout : dict, optional
        DataTables v2 layout configuration, passed through directly.
        Example:
            {
              "top1End": { "buttons": ["colvis"] },
              "top2End": { "buttons": ["csv"] }
            }
    actions : dict, optional
        Configuration for a custom actions column. Example:
            {
              "insertIndex": 0,
              "btndirection": "horizontal",
              "buttons": [
                 {"id": "view", "title": "View", "text": "View"},
                 {"id": "delete", "title": "Delete", "svg": "<svg .../>"}
              ]
            }
        If used, the component will return row data with an `action` field
        when a button is clicked.
        "insertIndex": column number that actions column to be inserted,
        "btndirection": Direction of action buttons. "horizontal" or "vertical",

    key : str, optional
        Streamlit widget key.

    Returns
    -------
    dict or None
        - On row selection:
            {"rows": [...], "indexes": [...], "count": int}
        - On action button click:
            {<row data...>, "action": str, "_rowIndex": int}
        - None if no interaction.

    """
    columns = df.columns.tolist()
    data = df.to_dict(orient="records")

    reset_nonce = None
    if key:
        reset_nonce = st.session_state.get(f"{key}__reset_nonce", 0)
    
    component_value = _component_func(
        columns=columns,
        data=data,
        id_col=id_col,
        pageLength=pageLength,
        lengthMenu=lengthMenu,
        orderable=orderable_cols,
        hidden=hidden_cols,
        searchable=searchable_cols,
        select=select,
        scrollX=scrollX,
        scrollY=scrollY,
        deferRender=deferRender,
        layout=layout,
        actions=actions,
        key=key,
        default={'rows': [], 'indexes': [], 'count': 0},
        reset_nonce=reset_nonce,
        )

    return component_value


def reset_selection(key: str, *, rerun: bool = True) -> None:
    """
    Signal the front-end table with given key to clear its selection.
    This increments a nonce in session_state and (optionally) reruns immediately.
    """
    nonce_key = f"{key}__reset_nonce"
    st.session_state[nonce_key] = st.session_state.get(nonce_key, 0) + 1
    if rerun:
        st.rerun()