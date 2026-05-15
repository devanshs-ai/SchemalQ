import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadCSV } from '../api/datasets'
import UploadZone from '../components/UploadZone'
import SchemaPreview from '../components/SchemaPreview'
import './Home.css'

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [dataset, setDataset] = useState(null)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleUpload = async (file, setProgress) => {
    setLoading(true)
    setError(null)
    setDataset(null)

    try {
      const res = await uploadCSV(file, setProgress)
      setDataset(res.data.dataset)
    } catch (err) {
      setError(err.message || 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <div className="container">
        <div className="page-header">
          <div className="home-eyebrow">
            <span className="badge badge-accent">Step 1</span>
          </div>
          <h1>Upload your dataset</h1>
          <p>Drop a CSV file to automatically infer its schema, create a Postgres table, and start querying with natural language.</p>
        </div>

        <div className="upload-section">
          <UploadZone onUpload={handleUpload} loading={loading} />

          {error && (
            <div className="banner banner-error animate-fade-in-up" id="upload-error">
              <span>⚠</span>
              <pre className="error-detail">{error}</pre>
            </div>
          )}

          {dataset && (
            <div className="upload-success animate-fade-in-up">
              <div className="banner banner-success">
                <span>✓</span>
                <span>
                  <strong>{dataset.original_filename}</strong> ingested successfully —{' '}
                  {dataset.row_count.toLocaleString()} rows in table <code>{dataset.table_name}</code>
                </span>
              </div>

              <SchemaPreview dataset={dataset} />

              <div className="post-upload-actions">
                <button
                  className="btn btn-primary btn-lg"
                  onClick={() => navigate(`/query?dataset=${dataset.id}`)}
                  id="go-to-query-btn"
                >
                  ⚡ Query this dataset →
                </button>
                <button
                  className="btn btn-ghost"
                  onClick={() => { setDataset(null); setError(null) }}
                  id="upload-another-btn"
                >
                  Upload another
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Feature highlights */}
        {!dataset && (
          <div className="feature-grid">
            {[
              { icon: '🧠', title: 'Auto Schema Inference', desc: 'Detects column types, nullability, and samples automatically.' },
              { icon: '🔒', title: 'SQL Safety Layer', desc: 'AST-based validation blocks any destructive query before execution.' },
              { icon: '⚡', title: 'Redis Caching', desc: 'Identical queries return cached results in milliseconds.' },
              { icon: '🤖', title: 'Groq LLM', desc: 'llama-3.3-70b-versatile generates schema-grounded SQL from plain English.' },
            ].map(({ icon, title, desc }) => (
              <div key={title} className="feature-card glass-card">
                <span className="feature-icon">{icon}</span>
                <h4>{title}</h4>
                <p>{desc}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
