import { useState } from 'react'
import ResultCard from './components/ResultCard'
import PipelineTrace from './components/PipelineTrace'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim() })
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || `Server error: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🕵️</span>
            <div>
              <h1 className="logo-title">Veritas7 AI</h1>
              <p className="logo-subtitle">7-Stage Autonomous Research Pipeline</p>
            </div>
          </div>
          <div className="header-badge">
            <span className="badge-dot"></span>
            Powered by LangGraph
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        {/* Search Section */}
        <section className="search-section">
          <div className="search-glow"></div>
          <h2 className="search-title">What would you like to research?</h2>
          <p className="search-description">
            Enter a complex question and our multi-agent pipeline will plan, research, synthesize, and refine a comprehensive answer.
          </p>
          <form className="search-form" onSubmit={handleSubmit}>
            <div className="input-wrapper">
              <svg className="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
              <input
                id="research-query"
                type="text"
                className="search-input"
                placeholder="E.g., What are the latest advancements in AI agent architectures?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
              />
            </div>
            <button
              id="run-pipeline-btn"
              type="submit"
              className="search-button"
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <span className="button-loading">
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                  <span>Researching...</span>
                </span>
              ) : (
                <>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="18" height="18">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                  Run Research Pipeline
                </>
              )}
            </button>
          </form>
        </section>

        {/* Loading State */}
        {loading && (
          <section className="loading-section">
            <div className="loading-card">
              <div className="loading-spinner"></div>
              <h3 className="loading-title">Pipeline Running</h3>
              <p className="loading-text">
                Our agents are planning, searching, synthesizing, and evaluating your query. This may take a minute...
              </p>
              <div className="loading-stages">
                {['Planner', 'Rewriter', 'Researcher', 'Summarizer', 'Generator', 'Critic', 'Refiner'].map((stage, i) => (
                  <span key={stage} className="loading-stage" style={{ animationDelay: `${i * 0.15}s` }}>
                    {stage}
                  </span>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* Error State */}
        {error && (
          <section className="error-section fade-in">
            <div className="error-card">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="24" height="24">
                <circle cx="12" cy="12" r="10" />
                <path d="m15 9-6 6M9 9l6 6" />
              </svg>
              <div>
                <h3>Pipeline Error</h3>
                <p>{error}</p>
              </div>
            </div>
          </section>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="results-section fade-in-up">
            <ResultCard result={result} />
            <PipelineTrace result={result} />

            {/* Errors from pipeline */}
            {result.errors && result.errors.length > 0 && (
              <section className="pipeline-errors fade-in">
                <h3>⚠️ Pipeline Warnings</h3>
                <ul>
                  {result.errors.map((err, i) => (
                    <li key={i}>{err}</li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Veritas7 AI — Built with LangGraph, Groq &amp; FastAPI</p>
      </footer>
    </div>
  )
}

export default App
