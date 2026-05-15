import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import QueryPage from './pages/QueryPage'
import DatasetsPage from './pages/DatasetsPage'
import './index.css'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/query" element={<QueryPage />} />
        <Route path="/datasets" element={<DatasetsPage />} />
        <Route path="*" element={
          <main className="page">
            <div className="container page-header">
              <h1>404</h1>
              <p>Page not found.</p>
            </div>
          </main>
        } />
      </Routes>
    </BrowserRouter>
  )
}
