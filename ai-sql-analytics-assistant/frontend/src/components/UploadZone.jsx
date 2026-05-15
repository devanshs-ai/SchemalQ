import { useState, useRef } from 'react'
import './UploadZone.css'

export default function UploadZone({ onUpload, loading }) {
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const inputRef = useRef(null)

  const handleFile = (file) => {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.csv')) {
      alert('Only .csv files are accepted.')
      return
    }
    onUpload(file, setProgress)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  const handleChange = (e) => {
    handleFile(e.target.files[0])
  }

  return (
    <div
      id="upload-zone"
      className={`upload-zone ${dragging ? 'dragging' : ''} ${loading ? 'loading' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !loading && inputRef.current.click()}
      role="button"
      tabIndex={0}
      aria-label="CSV upload zone"
      onKeyDown={(e) => e.key === 'Enter' && inputRef.current.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        style={{ display: 'none' }}
        onChange={handleChange}
        id="csv-file-input"
      />

      {loading ? (
        <div className="upload-loading">
          <div className="spinner" />
          <p>Ingesting data…</p>
          {progress > 0 && (
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
          )}
        </div>
      ) : (
        <div className="upload-idle">
          <div className="upload-icon">📂</div>
          <h3>Drop your CSV here</h3>
          <p>or click to browse</p>
          <span className="upload-hint">.csv only · max 500 MB</span>
        </div>
      )}
    </div>
  )
}
