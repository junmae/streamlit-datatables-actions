import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, {
  useEffect,
  useMemo,
  useState,
  useRef,
  ReactElement,
} from "react"

import DataTable, { type DataTableRef } from "datatables.net-react"
import DT from "datatables.net-dt"
import "datatables.net-select-dt"
import "datatables.net-buttons/js/buttons.colVis.mjs"
import "datatables.net-buttons/js/buttons.html5.mjs"

import "./MyComponent.css"

DataTable.use(DT)

type ActionButton = {
  id: string
  className?: string
  title?: string
  svg?: string
  text?: string
}
type ActionsConfig = {
  buttons: ActionButton[]
  insertIndex?: number
  hideWhenSelectSingle?: boolean
  btndirection?: "horizontal" | "vertical"
}

type Args = {
  columns: string[]
  data: any[]
  pageLength?: number
  lengthMenu?: number[]
  orderable?: string[]
  hidden?: string[]
  searchable?: string[]
  select?: "single" | "multi" | false
  scrollX?: boolean | string
  scrollY?: boolean | string
  deferRender?: boolean
  layout?: any
  actions?: ActionsConfig | null
  reset_nonce?: number
}

function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const {
    columns = [],
    data = [],
    pageLength = 50,
    lengthMenu = [10, 25, 50, 100],
    orderable = [],
    hidden = [],
    searchable = [],
    select = "single",
    scrollX = false,
    scrollY = false,
    deferRender = true,
    layout = null,
    actions = null,
    reset_nonce = 0,
  } = (args || {}) as Args

  const dtColumns: any[] = [
    ...columns.map((c) => ({
      title: c,
      data: c,
      orderable: orderable.includes(c),
      visible: !hidden.includes(c),
      searchable: searchable.includes(c),
    })),
  ]
  const escapeHtml = (s: string) =>
    s.replace(
      /[&<>"']/g,
      (m) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        }[m] as string)
    )

  if (actions !== null) {
    const rawIndex = (actions as ActionsConfig).insertIndex ?? 0
    const insertIndex = Math.min(Math.max(rawIndex, 0), dtColumns.length)
    const btndirection = (actions as ActionsConfig).btndirection ?? "horizontal"

    const btns = (actions as ActionsConfig).buttons
    const btnHtml = btns
      .map((b) => {
        const hasSvg = !!b.svg
        const hasText = typeof b.text === "string" && b.text.trim().length > 0
        if (!hasSvg && !hasText) return ""

        const kindClass =
          hasSvg && hasText
            ? "icon-label-btn"
            : hasSvg
            ? "icon-btn"
            : "text-btn"
        const cls = `row-action-btn ${kindClass} ${b.className ?? ""}`.trim()
        const titleAttr = b.title ? ` title="${escapeHtml(b.title)}"` : ""
        const labelSpan = hasText
          ? `<span class="btn-label">${escapeHtml(b.text!)}</span>`
          : ""
        const content = hasSvg
          ? `${b.svg}${labelSpan}`
          : labelSpan || escapeHtml(b.id)
        const ariaLabel = escapeHtml(b.title || b.text || b.id)

        return `<button class="${cls}" data-action="${b.id}" aria-label="${ariaLabel}"${titleAttr}>${content}</button>`
      })
      .filter(Boolean)
      .join("\n")

    const renderHtml = `<div class="actions-wrap ${btndirection}">${btnHtml}</div>`

    const actionsColumn = {
      title: "Actions",
      data: null,
      orderable: false,
      className: "actions-cell",
      render: () => renderHtml,
    }
    dtColumns.splice(insertIndex, 0, actionsColumn)
  }

  const tableRef = useRef<DataTableRef>(null)

  const [isFocused, setIsFocused] = useState(false)

  const style: React.CSSProperties = useMemo(() => {
    if (!theme) return {}
    const borderStyling = `1px solid ${isFocused ? theme.primaryColor : "gray"}`
    return { border: borderStyling, outline: borderStyling }
  }, [theme, isFocused])

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [style, theme])

  useEffect(() => {
    const api = tableRef.current?.dt()
    if (!api) return

    const publishSelection = () => {
      const selected = api.rows({ selected: true })
      const rows = selected.data().toArray()
      const indexes = selected.indexes().toArray()

      Streamlit.setComponentValue({
        rows,
        indexes,
        count: rows.length,
      })
    }

    const onSelect = (e: any, dt: any, type: string, _indexes: number[]) => {
      if (type !== "row") return
      publishSelection()
    }

    const onDeselect = (e: any, dt: any, type: string, _indexes: number[]) => {
      if (type !== "row") return
      publishSelection()
    }

    api.on("select", onSelect)
    api.on("deselect", onDeselect)

    publishSelection()

    return () => {
      api.off("select", onSelect)
      api.off("deselect", onDeselect)
    }
  }, [])

  useEffect(() => {
    const api = tableRef.current?.dt()
    if (!api) return
    api.rows().deselect()
    const selected = api.rows({ selected: true })
    const rows = selected.data().toArray()
    const indexes = selected.indexes().toArray()
    Streamlit.setComponentValue({ rows, indexes, count: rows.length })
  }, [reset_nonce])

  useEffect(() => {
    Streamlit.setFrameHeight()

    const api = tableRef.current?.dt()
    if (!api) return

    const tableNode = api.table().node() as HTMLElement

    const handleClick = (e: MouseEvent) => {
      const btn = (e.target as HTMLElement).closest<HTMLButtonElement>(
        ".row-action-btn"
      )
      if (!btn) return

      e.stopPropagation()

      const action = btn.dataset.action || btn.getAttribute("data-action") || ""

      const tr = btn.closest("tr")
      if (!tr) return

      const row = api.row(tr)
      const rowData = row.data()

      Streamlit.setComponentValue({
        ...rowData,
        action,
        _rowIndex: row.index(),
      })
    }

    tableNode.addEventListener("click", handleClick)
    return () => {
      tableNode.removeEventListener("click", handleClick)
    }
  }, [])

  useEffect(() => {
    const api = tableRef.current?.dt()
    if (!api) return

    const adjustHeight = () =>
      requestAnimationFrame(() => Streamlit.setFrameHeight())

    api.on("draw", adjustHeight)
    api.on("page.dt", adjustHeight)
    api.on("order.dt", adjustHeight)
    api.on("search.dt", adjustHeight)
    api.on("length.dt", () => setTimeout(adjustHeight, 0))

    adjustHeight()

    return () => {
      api.off("draw", adjustHeight)
      api.off("page.dt", adjustHeight)
      api.off("order.dt", adjustHeight)
      api.off("search.dt", adjustHeight)
      api.off("length.dt", adjustHeight as any)
    }
  }, [])

  return (
    <div style={{ width: "100%" }}>
      <DataTable
        ref={tableRef}
        data={data}
        columns={dtColumns as any}
        className="display"
        options={{
          select: select,
          pageLength: pageLength,
          lengthMenu: lengthMenu,
          scrollX: scrollX as any,
          scrollY: scrollY as any,
          deferRender: deferRender,
          ...(layout ? { layout } : {}),
        }}
      ></DataTable>
    </div>
  )
}

export default withStreamlitConnection(MyComponent)
