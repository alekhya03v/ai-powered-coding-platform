import { useState, useEffect } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

const ALL_PATTERNS = [
  "Arrays", "Strings", "Hashing", "Two Pointers", "Sliding Window", 
  "Stack", "Queue", "Linked List", "Trees", "Graphs", "Heap", 
  "Binary Search", "Recursion", "Backtracking", "Dynamic Programming", 
  "Greedy", "Bit Manipulation", "Math", "Tries", "Intervals"
]

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

function Dashboard({ history, onSelectProblem }) {
  const [selectedPattern, setSelectedPattern] = useState(null)

  const sortedHistory = [...history].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  const recentProblems = sortedHistory.slice(0, 5)

  const patternCounts = {}
  ALL_PATTERNS.forEach(p => patternCounts[p] = 0)
  history.forEach(p => {
    if (p.pattern && patternCounts[p.pattern] !== undefined) patternCounts[p.pattern]++
    else if (p.pattern) patternCounts[p.pattern] = (patternCounts[p.pattern] || 0) + 1
  })

  const uncoveredPatterns = Object.keys(patternCounts).filter(p => patternCounts[p] === 0 && ALL_PATTERNS.includes(p))
  const maxCount = Math.max(...Object.values(patternCounts), 1)

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Progress Dashboard</h2>
        <div className="stat-card total-solved">
          <span className="stat-value">{history.length}</span>
          <span className="stat-label">Total Problems Solved</span>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card pattern-breakdown">
          <h3>Pattern Breakdown</h3>
          <div className="bar-chart">
            {Object.entries(patternCounts)
              .sort((a, b) => b[1] - a[1])
              .filter(([p, count]) => count > 0)
              .map(([p, count]) => (
                <div key={p} className="bar-row" onClick={() => setSelectedPattern(p)}>
                  <div className="bar-label">{p}</div>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${(count / maxCount) * 100}%` }}></div>
                  </div>
                  <div className="bar-value">{count}</div>
                </div>
            ))}
          </div>
        </div>

        <div className="dashboard-side">
          <div className="dashboard-card recent-activity">
            <h3>Recent Activity</h3>
            <ul className="recent-list">
              {recentProblems.map(p => (
                <li key={p.id} onClick={() => onSelectProblem(p.id)}>
                  <span className="recent-title">{p.title || `Problem #${p.id}`}</span>
                  <span className="recent-date">{new Date(p.created_at).toLocaleDateString()}</span>
                </li>
              ))}
              {recentProblems.length === 0 && <p className="empty-text">No activity yet.</p>}
            </ul>
          </div>

          <div className="dashboard-card uncovered-patterns">
            <h3>Needs Practice (Uncovered)</h3>
            <div className="tag-cloud">
              {uncoveredPatterns.map(p => (
                <span key={p} className="uncovered-tag">{p}</span>
              ))}
              {uncoveredPatterns.length === 0 && <span className="empty-text">Wow! All patterns covered!</span>}
            </div>
          </div>
        </div>
      </div>

      {selectedPattern && (
        <div className="dashboard-card pattern-drilldown">
          <div className="drilldown-header">
            <h3>Problems for: {selectedPattern}</h3>
            <button className="close-btn" onClick={() => setSelectedPattern(null)}>✕</button>
          </div>
          <ul className="drilldown-list">
            {sortedHistory.filter(p => p.pattern === selectedPattern).map(p => (
              <li key={p.id} onClick={() => onSelectProblem(p.id)}>
                <span className="drilldown-title">{p.title || `Problem #${p.id}`}</span>
                <span className="drilldown-date">{new Date(p.created_at).toLocaleDateString()}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function SyllabusPage({ onNavigateToProblem }) {
  const [syllabusTree, setSyllabusTree] = useState({})
  const [loading, setLoading] = useState(true)
  const [suggestingFor, setSuggestingFor] = useState(null)
  
  const [customQuestionInput, setCustomQuestionInput] = useState({})

  const fetchSyllabus = async () => {
    try {
      const res = await fetch(`${API_URL}/syllabus`)
      const data = await res.json()
      setSyllabusTree(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSyllabus()
  }, [])

  const handleSuggest = async (spId) => {
    setSuggestingFor(spId)
    try {
      await fetch(`${API_URL}/syllabus/suggest/${spId}`, { method: 'POST' })
      await fetchSyllabus()
    } catch(e) {
      console.error(e)
    } finally {
      setSuggestingFor(null)
    }
  }

  const toggleComplete = async (q) => {
    try {
      await fetch(`${API_URL}/syllabus/question/${q.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !q.completed })
      })
      await fetchSyllabus()
    } catch(e) {
      console.error(e)
    }
  }
  
  const handleAddCustom = async (spId) => {
    const title = customQuestionInput[spId]
    if (!title?.trim()) return
    try {
      await fetch(`${API_URL}/syllabus/question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sub_pattern_id: spId, question_title: title })
      })
      setCustomQuestionInput({...customQuestionInput, [spId]: ''})
      await fetchSyllabus()
    } catch(e) { console.error(e) }
  }

  const handleDelete = async (qId) => {
    if (!window.confirm("Delete this question?")) return
    try {
      await fetch(`${API_URL}/syllabus/question/${qId}`, { method: 'DELETE' })
      await fetchSyllabus()
    } catch(e) { console.error(e) }
  }

  if (loading) return <div className="loading-indicator"><div className="spinner"></div><p>Loading curriculum...</p></div>

  return (
    <div className="syllabus-page">
      <div className="dashboard-header">
        <h2>Syllabus & Curriculum</h2>
      </div>
      
      {Object.entries(syllabusTree).map(([patternName, subPatterns]) => {
        let totalQ = 0
        let completedQ = 0
        subPatterns.forEach(sp => {
           totalQ += sp.questions.length
           completedQ += sp.questions.filter(q => q.completed).length
        })
        
        return (
          <div key={patternName} className="syllabus-pattern-card dashboard-card">
            <div className="pattern-header">
              <h3>{patternName}</h3>
              <span className="progress-badge">{completedQ} / {totalQ}</span>
            </div>
            
            <div className="subpatterns-list">
              {subPatterns.map(sp => {
                const spCompleted = sp.questions.filter(q => q.completed).length
                return (
                  <div key={sp.id} className="subpattern-section">
                    <div className="sp-header">
                      <h4>{sp.name}</h4>
                      <span className="sp-progress">{spCompleted} / {sp.questions.length}</span>
                    </div>
                    
                    {sp.questions.length === 0 ? (
                      <div className="sp-empty">
                        <button 
                          className="generate-btn suggest-btn" 
                          onClick={() => handleSuggest(sp.id)}
                          disabled={suggestingFor === sp.id}
                        >
                          {suggestingFor === sp.id ? 'Thinking...' : 'Suggest questions (AI)'}
                        </button>
                      </div>
                    ) : (
                      <ul className="sp-questions">
                        {sp.questions.map(q => (
                          <li key={q.id} className={`q-item ${q.completed ? 'completed' : ''}`}>
                            <div className="q-left">
                              <input 
                                type="checkbox" 
                                checked={q.completed} 
                                onChange={() => toggleComplete(q)} 
                              />
                              {q.linked_problem_id ? (
                                <a 
                                  href="#" 
                                  onClick={(e) => { e.preventDefault(); onNavigateToProblem(q.linked_problem_id) }}
                                  className="q-link"
                                >
                                  {q.question_title}
                                </a>
                              ) : (
                                <span className="q-title">{q.question_title}</span>
                              )}
                              {q.difficulty && <span className={`diff-badge diff-${q.difficulty.toLowerCase()}`}>{q.difficulty}</span>}
                            </div>
                            <button className="q-del-btn" onClick={() => handleDelete(q.id)}>✕</button>
                          </li>
                        ))}
                      </ul>
                    )}
                    
                    <div className="add-custom-q">
                      <input 
                        type="text" 
                        placeholder="Add custom question..." 
                        value={customQuestionInput[sp.id] || ''}
                        onChange={(e) => setCustomQuestionInput({...customQuestionInput, [sp.id]: e.target.value})}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddCustom(sp.id)}
                      />
                      <button onClick={() => handleAddCustom(sp.id)}>+</button>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function App() {
  const [activePage, setActivePage] = useState('generate') // 'generate' | 'dashboard' | 'syllabus'
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
  const [regeneratingId, setRegeneratingId] = useState(null)
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

  const handleDashboardProblemClick = (id) => {
    setActivePage('generate')
    loadProblem(id)
  }

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

  const handleRegenerateSaved = async (targetId, titleToSave, descToSave) => {
    if (!descToSave.trim()) return
    setRegeneratingId(targetId)
    try {
      const res = await fetch(`${API_URL}/problems/${targetId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: titleToSave, description: descToSave })
      })
      const data = await res.json()
      
      setViewProblem(prev => (prev && prev.id === targetId) ? data : prev)
      fetchHistory()
    } catch (e) {
      console.error('Failed to regenerate', e)
    } finally {
      setRegeneratingId(prev => prev === targetId ? null : prev)
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
      <header className="header app-header">
        <h1>DSA Prep Assistant</h1>
        <nav className="nav-bar">
          <button 
            className={`nav-btn ${activePage === 'generate' ? 'active' : ''}`}
            onClick={() => setActivePage('generate')}
          >
            Solve & Review
          </button>
          <button 
            className={`nav-btn ${activePage === 'syllabus' ? 'active' : ''}`}
            onClick={() => setActivePage('syllabus')}
          >
            Syllabus
          </button>
          <button 
            className={`nav-btn ${activePage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActivePage('dashboard')}
          >
            Dashboard
          </button>
        </nav>
      </header>

      {activePage === 'dashboard' ? (
        <div className="dashboard-container">
          <Dashboard history={history} onSelectProblem={handleDashboardProblemClick} />
        </div>
      ) : activePage === 'syllabus' ? (
        <div className="dashboard-container">
          <SyllabusPage onNavigateToProblem={handleDashboardProblemClick} />
        </div>
      ) : (
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
                  <div className="history-date">
                    {p.pattern && <span className="pattern-sidebar-badge">{p.pattern}</span>}
                    {new Date(p.created_at).toLocaleDateString()}
                  </div>
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
                        onClick={() => handleRegenerateSaved(selectedProblemId, editTitle, editDescription)} 
                        disabled={regeneratingId === selectedProblemId} 
                        className="generate-btn regenerate-btn"
                      >
                        {regeneratingId === selectedProblemId ? 'Regenerating...' : 'Save & Regenerate'}
                      </button>
                    </div>
                  </section>
                )}
              </>
            )}

            <section className="result-section">
              {(loading || (selectedProblemId !== null && regeneratingId === selectedProblemId)) && (
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <p>{!isViewMode ? 'AI is thinking... Grab a coffee!' : ((selectedProblemId !== null && regeneratingId === selectedProblemId) ? 'Regenerating solution...' : 'Loading problem...')}</p>
                </div>
              )}

              {!(loading || (selectedProblemId !== null && regeneratingId === selectedProblemId)) && displayProblem && displayProblem.generated && !displayProblem.generated.error && (
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
              
              {!(loading || (selectedProblemId !== null && regeneratingId === selectedProblemId)) && displayProblem && displayProblem.generated && displayProblem.generated.error && (
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
      )}
    </div>
  )
}

export default App
