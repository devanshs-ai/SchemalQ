import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { deleteDataset } from '../api/datasets'
import './DatasetCard.css'

export default function DatasetCard({ dataset, onDeleted }) {
  const navigate = useNavigate()
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async (e) => {
    e.stopPropagation()
    if (!confirm(`Delete dataset "${dataset.name}"? This cannot be undone.`)) return
    setDeleting(true)
    try {
      await deleteDataset(dataset.id)
      onDeleted(dataset.id)
    } catch (err) {
      alert(`Delete failed: ${err.message}`)
    } finally {
      setDeleting(false)
    }
  }

  const created = new Date(dataset.created_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })

  return (
    <div className="dataset-card glass-card" id={`dataset-card-${dataset.id}`}>
      <div className="card-top">
        <div className="card-icon">🗂</div>
        <div className="card-meta">
          <h3 className="card-title">{dataset.name}</h3>
          <p className="card-filename">{dataset.original_filename}</p>
        </div>
      </div>

      <div className="card-stats">
        <div className="stat">
          <span className="stat-value">{dataset.row_count.toLocaleString()}</span>
          <span className="stat-label">Rows</span>
        </div>
        <div className="stat">
          <span className="stat-value">{dataset.column_count}</span>
          <span className="stat-label">Columns</span>
        </div>
        {dataset.file_size_bytes && (
          <div className="stat">
            <span className="stat-value">{(dataset.file_size_bytes / 1024).toFixed(0)} KB</span>
            <span className="stat-label">Size</span>
          </div>
        )}
      </div>

      <div className="card-table-name">
        <code>{dataset.table_name}</code>
      </div>

      <div className="card-footer">
        <span className="card-date">{created}</span>
        <div className="card-actions">
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => navigate(`/query?dataset=${dataset.id}`)}
            id={`query-dataset-${dataset.id}`}
          >
            ⚡ Query
          </button>
          <button
            className="btn btn-danger btn-sm"
            onClick={handleDelete}
            disabled={deleting}
            id={`delete-dataset-${dataset.id}`}
          >
            {deleting ? <span className="spinner" /> : '🗑'}
          </button>
        </div>
      </div>
    </div>
  )
}
