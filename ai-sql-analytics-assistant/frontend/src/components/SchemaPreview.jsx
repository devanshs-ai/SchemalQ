import './SchemaPreview.css'

export default function SchemaPreview({ dataset }) {
  if (!dataset) return null

  return (
    <div className="schema-preview animate-fade-in-up">
      <div className="schema-header">
        <div>
          <h3>{dataset.name}</h3>
          <p className="schema-meta">
            {dataset.row_count.toLocaleString()} rows · {dataset.column_count} columns ·{' '}
            {dataset.table_name}
          </p>
        </div>
        <div className="schema-badges">
          <span className="badge badge-success">✓ Ingested</span>
          {dataset.file_size_bytes && (
            <span className="badge badge-primary">
              {(dataset.file_size_bytes / 1024).toFixed(1)} KB
            </span>
          )}
        </div>
      </div>

      <div className="schema-table-wrap">
        <table className="schema-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Column</th>
              <th>Type</th>
              <th>Nullable</th>
              <th>Samples</th>
            </tr>
          </thead>
          <tbody>
            {dataset.columns.map((col) => (
              <tr key={col.column_name}>
                <td className="col-pos">{col.ordinal_position + 1}</td>
                <td className="col-name">{col.column_name}</td>
                <td>
                  <span className="type-badge">{col.pg_type}</span>
                </td>
                <td>
                  {col.is_nullable ? (
                    <span className="null-yes">yes</span>
                  ) : (
                    <span className="null-no">no</span>
                  )}
                </td>
                <td className="col-samples">
                  {col.sample_values.slice(0, 3).map((s, i) => (
                    <code key={i}>{String(s)}</code>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
