import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { listDatasets } from '../api/datasets'
import QueryConsole from '../components/QueryConsole'
import './QueryPage.css'

export default function QueryPage() {
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchParams] = useSearchParams()

  useEffect(() => {
    listDatasets()
      .then((res) => setDatasets(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <main className="page">
      <div className="container query-page-container">
        <div className="page-header">
          <h1>Query Console</h1>
          <p>Ask questions about your data in plain English. SchemaIQ generates and executes safe SQL for you.</p>
        </div>

        {loading && (
          <div className="query-loading">
            <span className="spinner" />
            <span>Loading datasets…</span>
          </div>
        )}

        {error && (
          <div className="banner banner-error" id="datasets-load-error">
            <span>⚠</span>
            <span>Failed to load datasets: {error}</span>
          </div>
        )}

        {!loading && <QueryConsole datasets={datasets} />}
      </div>
    </main>
  )
}
