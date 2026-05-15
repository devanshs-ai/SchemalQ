import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { runQuery } from '../api/query'
import ResultsTable from './ResultsTable'
import './QueryConsole.css'

export default function QueryConsole({ datasets }) {
  const [selectedId, setSelectedId] = useState('')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedId) { setError('Please select a dataset.'); return }
    if (!prompt.trim()) { setError('Please enter a question.'); return }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await runQuery(parseInt(selectedId), prompt)
      setResult(res.data)
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.')
    } finally {
      setLoading(false)
    }
  }

  const examplePrompts = [
    'Show me the top 10 rows',
    'Count total rows',
    'What are the distinct values in the first column?',
  ]

  return (
    <div className="query-console">
      <form onSubmit={handleSubmit} className="query-form glass-card">
        {/* Dataset selector */}
        <div className="form-group">
          <label htmlFor="dataset-select" className="form-label">Dataset</label>
          {datasets.length === 0 ? (
            <div className="no-datasets">
              No datasets yet.{' '}
              <button type="button" className="btn-link" onClick={() => navigate('/')}>
                Upload one first →
              </button>
            </div>
          ) : (
            <select
              id="dataset-select"
              className="input select"
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
            >
              <option value="">Select a dataset…</option>
              {datasets.map((ds) => (
                <option key={ds.id} value={ds.id}>
                  {ds.name} — {ds.row_count.toLocaleString()} rows
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Prompt */}
        <div className="form-group">
          <label htmlFor="nl-prompt" className="form-label">Natural Language Question</label>
          <textarea
            id="nl-prompt"
            className="textarea"
            placeholder="e.g. Show me total sales by region for Q1"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
          />
          <div className="prompt-examples">
            {examplePrompts.map((ex) => (
              <button
                key={ex}
                type="button"
                className="example-chip"
                onClick={() => setPrompt(ex)}
              >
                {ex}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-lg"
          disabled={loading || datasets.length === 0}
          id="run-query-btn"
        >
          {loading ? <><span className="spinner" /> Generating…</> : '⚡ Run Query'}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="banner banner-error animate-fade-in-up" id="query-error">
          <span>⚠</span>
          <pre className="error-detail">{error}</pre>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="query-results animate-fade-in-up">
          {/* SQL display */}
          <div className="sql-block glass-card">
            <div className="sql-header">
              <span className="form-label">Generated SQL</span>
              <div className="sql-meta">
                {result.metadata.cache_hit && <span className="badge badge-accent">⚡ Cache Hit</span>}
                <span className="badge badge-primary">
                  {result.metadata.execution_time_ms}ms
                </span>
                <span className="badge badge-success">
                  {result.metadata.result_row_count} rows
                </span>
              </div>
            </div>
            <pre className="code-block">{result.metadata.generated_sql}</pre>
          </div>

          <ResultsTable columns={result.columns} rows={result.rows} />
        </div>
      )}
    </div>
  )
}
