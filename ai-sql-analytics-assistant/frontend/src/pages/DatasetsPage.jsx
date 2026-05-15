import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listDatasets } from '../api/datasets'
import DatasetCard from '../components/DatasetCard'
import './DatasetsPage.css'

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const fetchDatasets = () => {
    setLoading(true)
    listDatasets()
      .then((res) => setDatasets(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchDatasets() }, [])

  const handleDeleted = (id) => {
    setDatasets((prev) => prev.filter((ds) => ds.id !== id))
  }

  return (
    <main className="page">
      <div className="container">
        <div className="page-header">
          <h1>Datasets</h1>
          <p>All your uploaded CSV files — click Query to start asking questions.</p>
        </div>

        <div className="datasets-toolbar">
          <span className="badge badge-primary">{datasets.length} dataset{datasets.length !== 1 ? 's' : ''}</span>
          <button className="btn btn-ghost btn-sm" onClick={fetchDatasets} id="refresh-datasets-btn">
            ↻ Refresh
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/')} id="upload-new-btn">
            + Upload New
          </button>
        </div>

        {loading && (
          <div className="datasets-loading">
            <span className="spinner" />
            <span>Loading datasets…</span>
          </div>
        )}

        {error && (
          <div className="banner banner-error" id="datasets-error">
            <span>⚠</span>
            <span>{error}</span>
          </div>
        )}

        {!loading && datasets.length === 0 && !error && (
          <div className="empty-state glass-card">
            <div className="empty-icon">🗂</div>
            <h3>No datasets yet</h3>
            <p>Upload a CSV file to get started.</p>
            <button className="btn btn-primary" onClick={() => navigate('/')} id="empty-upload-btn">
              Upload CSV →
            </button>
          </div>
        )}

        <div className="datasets-grid" id="datasets-grid">
          {datasets.map((ds) => (
            <DatasetCard key={ds.id} dataset={ds} onDeleted={handleDeleted} />
          ))}
        </div>
      </div>
    </main>
  )
}
