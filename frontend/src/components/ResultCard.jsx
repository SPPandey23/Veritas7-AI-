import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './ResultCard.css'

function ResultCard({ result }) {
  const confidence = (result.confidence_score || 0) * 100
  const iterations = result.iteration_count || 0
  const isSuccess = result.success && (!result.errors || result.errors.length === 0)

  // Determine confidence color
  const getConfidenceColor = (val) => {
    if (val >= 70) return 'var(--success)'
    if (val >= 40) return 'var(--warning)'
    return 'var(--error)'
  }

  const circumference = 2 * Math.PI * 42
  const offset = circumference - (confidence / 100) * circumference

  return (
    <section className="result-card">
      {/* Status Banner */}
      <div className={`result-status ${isSuccess ? 'status-success' : 'status-warning'}`}>
        <span className="status-icon">{isSuccess ? '✅' : '⚠️'}</span>
        <span>
          {isSuccess
            ? `Pipeline completed successfully in ${iterations} iteration${iterations !== 1 ? 's' : ''}!`
            : `Pipeline finished with ${result.errors?.length || 0} warning(s).`}
        </span>
      </div>

      <div className="result-body">
        {/* Main Answer */}
        <div className="answer-section">
          <h2 className="answer-heading">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="22" height="22">
              <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
            </svg>
            Final Synthesized Answer
          </h2>
          <div className="answer-content">
            {result.final_answer ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result.final_answer}
              </ReactMarkdown>
            ) : (
              <p>No final answer generated.</p>
            )}
          </div>
        </div>

        {/* Confidence Gauge */}
        <div className="confidence-section">
          <div className="confidence-gauge">
            <svg viewBox="0 0 100 100" className="confidence-ring">
              <circle
                cx="50" cy="50" r="42"
                fill="none"
                stroke="rgba(255,255,255,0.05)"
                strokeWidth="6"
              />
              <circle
                cx="50" cy="50" r="42"
                fill="none"
                stroke={getConfidenceColor(confidence)}
                strokeWidth="6"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                transform="rotate(-90 50 50)"
                className="confidence-progress"
              />
            </svg>
            <div className="confidence-value">
              <span className="confidence-number" style={{ color: getConfidenceColor(confidence) }}>
                {confidence.toFixed(0)}
              </span>
              <span className="confidence-percent">%</span>
            </div>
          </div>
          <p className="confidence-label">Confidence</p>
          <p className="confidence-iterations">
            {iterations > 0
              ? `Refined ${iterations} time${iterations !== 1 ? 's' : ''}`
              : 'No refinement needed'}
          </p>
        </div>
      </div>
    </section>
  )
}

export default ResultCard