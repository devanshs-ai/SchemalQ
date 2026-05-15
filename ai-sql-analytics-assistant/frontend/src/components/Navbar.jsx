import { NavLink } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner container">
        <NavLink to="/" className="navbar-logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">Schema<span className="logo-accent">IQ</span></span>
        </NavLink>

        <div className="navbar-links">
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Upload
          </NavLink>
          <NavLink to="/query" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Query
          </NavLink>
          <NavLink to="/datasets" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Datasets
          </NavLink>
        </div>

        <div className="navbar-badge">
          <span className="badge badge-accent">Phase 1</span>
        </div>
      </div>
    </nav>
  )
}
