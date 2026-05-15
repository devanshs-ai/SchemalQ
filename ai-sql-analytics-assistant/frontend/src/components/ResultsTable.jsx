import { useState } from 'react'
import './ResultsTable.css'

const PAGE_SIZE = 50

export default function ResultsTable({ columns, rows }) {
  const [page, setPage] = useState(0)
  const [sortCol, setSortCol] = useState(null)
  const [sortAsc, setSortAsc] = useState(true)

  if (!rows || rows.length === 0) {
    return (
      <div className="results-empty glass-card">
        <p>Query returned 0 rows.</p>
      </div>
    )
  }

  const handleSort = (col) => {
    if (sortCol === col) {
      setSortAsc(!sortAsc)
    } else {
      setSortCol(col)
      setSortAsc(true)
    }
    setPage(0)
  }

  let displayRows = [...rows]
  if (sortCol) {
    displayRows.sort((a, b) => {
      const av = a[sortCol] ?? ''
      const bv = b[sortCol] ?? ''
      if (av < bv) return sortAsc ? -1 : 1
      if (av > bv) return sortAsc ? 1 : -1
      return 0
    })
  }

  const totalPages = Math.ceil(displayRows.length / PAGE_SIZE)
  const pageRows = displayRows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  return (
    <div className="results-table-wrap glass-card">
      <div className="results-header">
        <span className="form-label">{rows.length.toLocaleString()} results</span>
        {totalPages > 1 && (
          <div className="pagination">
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setPage(page - 1)}
              disabled={page === 0}
              id="prev-page-btn"
            >
              ← Prev
            </button>
            <span className="page-info">
              {page + 1} / {totalPages}
            </span>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages - 1}
              id="next-page-btn"
            >
              Next →
            </button>
          </div>
        )}
      </div>

      <div className="table-scroll">
        <table className="results-table" id="results-data-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  onClick={() => handleSort(col)}
                  className={sortCol === col ? 'sorted' : ''}
                  title={`Sort by ${col}`}
                >
                  {col}
                  <span className="sort-icon">
                    {sortCol === col ? (sortAsc ? ' ↑' : ' ↓') : ' ⇅'}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, ri) => (
              <tr key={ri}>
                {columns.map((col) => (
                  <td key={col} title={String(row[col] ?? '')}>
                    {row[col] === null ? (
                      <span className="null-cell">NULL</span>
                    ) : (
                      String(row[col])
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
