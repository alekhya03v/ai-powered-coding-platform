import { useState, useEffect } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentProblem, setCurrentProblem] = useState(null)
  const [history, setHistory] = useState([])

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/problems`)
      const data = await res.json()
      setHistory(data)
    } catch (e) {
      console.error('Failed to fetch history', e)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!description.trim()) return

    setLoading(true)
    setCurrentProblem(null)

    try {
      const res = await fetch(`${API_URL}/problems`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description })
      })
      const data = await res.json()
      setCurrentProblem(data)
      fetchHistory()
    } catch (e) {
      console.error('Failed to generate problem', e)
      alert('Error generating solution. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const deleteProblem = async (e, id) => {
    e.stopPropagation()
    if (!window.confirm("Delete this problem?")) return
    
    try {
      await fetch(`${API_URL}/problems/${id}`, { method: 'DELETE' })
      if (currentProblem && currentProblem.id === id) {
        setCurrentProblem(null)
      }
      fetchHistory()
    } catch (err) {
      console.error('Failed to delete problem', err)
    }
  }

  const loadProblem = async (id) => {
    setLoading(true)
    setCurrentProblem(null)
    try {
      const res = await fetch(`${API_URL}/problems/${id}`)
      const data = await res.json()
      setCurrentProblem(data)
    } catch (e) {
      console.error('Failed to load problem', e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>DSA Prep Assistant</h1>
      </header>

      <div className="layout">
        <aside className="sidebar">
          <h3>Saved Problems</h3>
          <ul className="history-list">
            {history.map((p) => (
              <li key={p.id} onClick={() => loadProblem(p.id)} className="history-item">
                <div className="history-item-header">
                  <div className="history-title">{p.title || `Problem #${p.id}`}</div>
                  <button onClick={(e) => deleteProblem(e, p.id)} className="delete-btn" title="Delete">✕</button>
                </div>
                <div className="history-date">{new Date(p.created_at).toLocaleString()}</div>
              </li>
            ))}
            {history.length === 0 && <p className="empty-text">No saved problems yet.</p>}
          </ul>
        </aside>

        <main className="main-content">
          <section className="input-section">
            <form onSubmit={handleGenerate} className="problem-form">
              <input
                type="text"
                placeholder="Optional Title (e.g. Two Sum)"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="input-title"
              />
              <textarea
                placeholder="Paste the problem description here..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                className="input-desc"
                rows="6"
              />
              <button type="submit" disabled={loading} className="generate-btn">
                {loading ? 'Generating... (this takes 10-30s)' : 'Generate Solution'}
              </button>
            </form>
          </section>

          <section className="result-section">
            {loading && (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <p>AI is thinking... Grab a coffee!</p>
              </div>
            )}

            {!loading && currentProblem && currentProblem.generated && !currentProblem.generated.error && (
              <div className="solution-container">
                <h2>{currentProblem.title || currentProblem.generated.title || 'Solution'}</h2>
                
                <div className="card">
                  <h3>Explanation</h3>
                  <p className="explanation">{currentProblem.generated.explanation}</p>
                </div>

                <div className="approaches">
                  <h3>Approaches</h3>
                  {currentProblem.generated.approaches?.map((app, idx) => (
                    <div key={idx} className="approach-card">
                      <h4>{idx + 1}. {app.name}</h4>
                      <p><strong>Idea:</strong> {app.idea}</p>
                      <div className="complexity">
                        <span className="badge">Time: {app.time_complexity}</span>
                        <span className="badge">Space: {app.space_complexity}</span>
                      </div>
                      <pre className="code-block">
                        <code>{app.code}</code>
                      </pre>
                    </div>
                  ))}
                </div>

                {currentProblem.generated.follow_ups && currentProblem.generated.follow_ups.length > 0 && (
                  <div className="card follow-ups">
                    <h3>Follow-up Questions</h3>
                    <ul>
                      {currentProblem.generated.follow_ups.map((q, idx) => (
                        <li key={idx}>{q}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            
            {!loading && currentProblem && currentProblem.generated && currentProblem.generated.error && (
               <div className="error-card">
                 <h3>Error Generating Solution</h3>
                 <p>{currentProblem.generated.error}</p>
                 {currentProblem.generated.details && <p className="error-details">{currentProblem.generated.details}</p>}
               </div>
            )}
          </section>
        </main>
      </div>
    </div>
  )
}

export default App
