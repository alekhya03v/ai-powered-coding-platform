import { useState, useEffect } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

function ApproachCard({ app, index }) {
  const isOldFormat = typeof app.code === 'string'
  const languages = isOldFormat ? [app.language || 'python'] : ['python', 'java', 'cpp', 'c']
  
  const [activeLang, setActiveLang] = useState(languages[0])

  const getCode = () => {
    if (isOldFormat) return app.code
    return app.code[activeLang] || `// No ${activeLang} code available`
  }

  const formatLang = (lang) => {
    if (lang === 'cpp') return 'C++'
    if (lang === 'python') return 'Python'
    if (lang === 'java') return 'Java'
    if (lang === 'c') return 'C'
    return lang.toUpperCase()
  }

  return (
    <div className="approach-card">
      <h4>{index + 1}. {app.name}</h4>
      <p><strong>Idea:</strong> {app.idea}</p>
      <div className="complexity">
        <span className="badge">Time: {app.time_complexity}</span>
        <span className="badge">Space: {app.space_complexity}</span>
      </div>
      
      {!isOldFormat && (
        <div className="lang-tabs">
          {languages.map(lang => (
            <button 
              key={lang} 
              className={`lang-tab ${activeLang === lang ? 'active' : ''}`}
              onClick={() => setActiveLang(lang)}
            >
              {formatLang(lang)}
            </button>
          ))}
        </div>
      )}
      
      <pre className={`code-block ${!isOldFormat ? 'has-tabs' : ''}`}>
        <code>{getCode()}</code>
      </pre>
    </div>
  )
}

function App() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  
  // View State
  const [selectedProblemId, setSelectedProblemId] = useState(null)
  const [viewProblem, setViewProblem] = useState(null)
  const [generatedProblem, setGeneratedProblem] = useState(null)
  
  // Edit & Notes State
  const [editTitle, setEditTitle] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [regenerating, setRegenerating] = useState(false)
  const [notes, setNotes] = useState('')
  const [savingNotes, setSavingNotes] = useState(false)

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
    if (e) e.preventDefault()
    if (!description.trim()) return

    setLoading(true)
    setGeneratedProblem(null)

    try {
      const res = await fetch(`${API_URL}/problems`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description })
      })
      const data = await res.json()
      setGeneratedProblem(data)
      fetchHistory()
    } catch (e) {
      console.error('Failed to generate problem', e)
      alert('Error generating solution. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const loadProblem = async (id) => {
    setSelectedProblemId(id)
    setViewProblem(null)
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/problems/${id}`)
      const data = await res.json()
      setViewProblem(data)
      setEditTitle(data.title || '')
      setEditDescription(data.description || '')
      setNotes(data.notes || '')
    } catch (e) {
      console.error('Failed to load problem', e)
    } finally {
      setLoading(false)
    }
  }

  const deleteProblem = async (e, id) => {
    e.stopPropagation()
    if (!window.confirm("Delete this problem?")) return
    
    try {
      await fetch(`${API_URL}/problems/${id}`, { method: 'DELETE' })
      if (selectedProblemId === id) {
        handleNewProblem()
      }
      fetchHistory()
    } catch (err) {
      console.error('Failed to delete problem', err)
    }
  }

  const handleNewProblem = () => {
    setSelectedProblemId(null)
    setTitle('')
    setDescription('')
    setGeneratedProblem(null)
  }

  const handleRegenerateSaved = async () => {
    if (!editDescription.trim()) return
    setRegenerating(true)
    try {
      const res = await fetch(`${API_URL}/problems/${selectedProblemId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: editTitle, description: editDescription })
      })
      const data = await res.json()
      setViewProblem(data)
      fetchHistory()
    } catch (e) {
      console.error('Failed to regenerate', e)
    } finally {
      setRegenerating(false)
    }
  }

  const handleSaveNotes = async () => {
    setSavingNotes(true)
    try {
      await fetch(`${API_URL}/problems/${selectedProblemId}/notes`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes })
      })
      setViewProblem(prev => ({ ...prev, notes }))
    } catch (e) {
      console.error('Failed to save notes', e)
    } finally {
      setSavingNotes(false)
    }
  }

  const displayProblem = selectedProblemId ? viewProblem : generatedProblem
  const isViewMode = selectedProblemId !== null

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
              <li 
                key={p.id} 
                onClick={() => loadProblem(p.id)} 
                className={`history-item ${selectedProblemId === p.id ? 'active' : ''}`}
              >
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
          {!isViewMode ? (
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
                <div className="form-actions">
                  <button type="submit" disabled={loading} className="generate-btn">
                    {loading ? 'Generating... (10-30s)' : 'Generate Solution'}
                  </button>
                  {generatedProblem && !loading && (
                    <button type="button" onClick={handleGenerate} className="generate-btn retry-btn-inline">
                      Regenerate
                    </button>
                  )}
                </div>
              </form>
            </section>
          ) : (
            <>
              <div className="view-header">
                <button onClick={handleNewProblem} className="back-btn">
                  ← New Problem
                </button>
              </div>
              
              {viewProblem && (
                <section className="input-section view-edit-section">
                  <div className="problem-form">
                    <input
                      type="text"
                      placeholder="Optional Title (e.g. Two Sum)"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="input-title"
                    />
                    <textarea
                      placeholder="Problem description"
                      value={editDescription}
                      onChange={(e) => setEditDescription(e.target.value)}
                      required
                      className="input-desc"
                      rows="4"
                    />
                    <button 
                      onClick={handleRegenerateSaved} 
                      disabled={regenerating} 
                      className="generate-btn regenerate-btn"
                    >
                      {regenerating ? 'Regenerating...' : 'Save & Regenerate'}
                    </button>
                  </div>
                </section>
              )}
            </>
          )}

          <section className="result-section">
            {(loading || regenerating) && (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <p>{!isViewMode ? 'AI is thinking... Grab a coffee!' : (regenerating ? 'Regenerating solution...' : 'Loading problem...')}</p>
              </div>
            )}

            {!(loading || regenerating) && displayProblem && displayProblem.generated && !displayProblem.generated.error && (
              <div className="solution-container">
                <h2>{displayProblem.title || displayProblem.generated.title || 'Solution'}</h2>
                
                {!isViewMode && displayProblem.description && (
                  <div className="card">
                    <h3>Problem Description</h3>
                    <p className="problem-description">{displayProblem.description}</p>
                  </div>
                )}

                <div className="card">
                  <h3>Explanation</h3>
                  <p className="explanation">{displayProblem.generated.explanation}</p>
                </div>

                <div className="approaches">
                  <h3>Approaches</h3>
                  {displayProblem.generated.approaches?.map((app, idx) => (
                    <ApproachCard key={idx} app={app} index={idx} />
                  ))}
                </div>

                {displayProblem.generated.follow_ups && displayProblem.generated.follow_ups.length > 0 && (
                  <div className="card follow-ups">
                    <h3>Follow-up Questions</h3>
                    <ul>
                      {displayProblem.generated.follow_ups.map((q, idx) => (
                        <li key={idx}>{q}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {isViewMode && (
                  <div className="card notes-card">
                    <h3>My Notes</h3>
                    <textarea 
                      value={notes} 
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Write your personal notes or takeaways here..."
                      className="notes-input"
                      rows="4"
                    />
                    <div className="notes-actions">
                      <button onClick={handleSaveNotes} disabled={savingNotes} className="save-notes-btn">
                        {savingNotes ? 'Saving...' : 'Save Notes'}
                      </button>
                    </div>
                  </div>
                )}

              </div>
            )}
            
            {!(loading || regenerating) && displayProblem && displayProblem.generated && displayProblem.generated.error && (
               <div className="error-card">
                 <h3>Oops! We hit a snag.</h3>
                 <p>The AI service might be busy or taking a quick nap. Feel free to try again!</p>
                 <div className="error-details">
                   <strong>{displayProblem.generated.error}</strong>
                   {displayProblem.generated.details && <div>{displayProblem.generated.details}</div>}
                 </div>
                 {!isViewMode && (
                   <button onClick={handleGenerate} className="generate-btn retry-btn">
                     Retry Generation
                   </button>
                 )}
               </div>
            )}
          </section>
        </main>
      </div>
    </div>
  )
}

export default App
