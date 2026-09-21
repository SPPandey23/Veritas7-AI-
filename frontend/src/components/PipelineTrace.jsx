import { useState } from 'react'
import './PipelineTrace.css'

const STAGES = [
  { key: 'planner', number: 1, title: 'Planner', subtitle: 'Sub-Questions', icon: '🧠' },
  { key: 'rewriter', number: 2, title: 'Query Rewriter', subtitle: 'Search Keywords', icon: '✏️' },
  { key: 'researcher', number: 3, title: 'Researcher', subtitle: 'Gathered Context', icon: '🔍' },
  { key: 'summarizer', number: 4, title: 'Summarizer', subtitle: 'Context Brief', icon: '📝' },
  { key: 'generator', number: 5, title: 'Generator', subtitle: 'First Draft', icon: '⚡' },
  { key: 'critic', number: 6, title: 'Critic', subtitle: 'Evaluation', icon: '🎯' },
  { key: 'refiner', number: 7, title: 'Refiner', subtitle: 'Corrections', icon: '🔧' },
]

function PipelineTrace({ result }) {
  const [isOpen, setIsOpen] = useState(false)
  const [openStage, setOpenStage] = useState(null)

  const toggleStage = (key) => {
    setOpenStage(openStage === key ? null : key)
  }

  const renderStageContent = (stage) => {
    switch (stage.key) {
      case 'planner': {
        const questions = result.sub_questions || []
        return questions.length > 0 ? (
          <ul className="trace-list">
            {questions.map((q, i) => <li key={i}>{q}</li>)}
          </ul>
        ) : <p className="trace-empty">No sub-questions generated.</p>
      }

      case 'rewriter': {
        const queries = result.rewritten_queries || []
        return queries.length > 0 ? (
          <ul className="trace-list">
            {queries.map((q, i) => <li key={i}><code>{q}</code></li>)}
          </ul>
        ) : <p className="trace-empty">No queries rewritten.</p>
      }

      case 'researcher': {
        const docs = result.raw_documents || []
        return (
          <div>
            <p className="trace-metric">
              <strong>{docs.length}</strong> unique context chunks gathered
            </p>
            {docs.length > 0 && (
              <div className="trace-sources">
                {docs.slice(0, 5).map((doc, i) => (
                  <div key={i} className="source-chip">
                    <span className="source-score">
                      {(doc.relevance_score * 100).toFixed(0)}%
                    </span>
                    <span className="source-url" title={doc.source}>
                      {doc.source.length > 50 ? doc.source.substring(0, 50) + '...' : doc.source}
                    </span>
                  </div>
                ))}
                {docs.length > 5 && (
                  <p className="trace-more">+ {docs.length - 5} more sources</p>
                )}
              </div>
            )}
          </div>
        )
      }

      case 'summarizer':
        return (
          <div className="trace-text-block">
            {result.context_summary || 'No summary generated.'}
          </div>
        )

      case 'generator':
        return (
          <div className="trace-text-block">
            {result.draft_answer || 'No draft generated.'}
          </div>
        )

      case 'critic': {
        const critic = result.critic_result
        if (!critic) return <p className="trace-empty">No critic evaluation available.</p>
        return (
          <div className="critic-detail">
            <div className="critic-header">
              <span className={`critic-verdict ${critic.verdict === 'good' ? 'verdict-good' : 'verdict-improve'}`}>
                {critic.verdict === 'good' ? '✅ Good' : '🔄 Needs Improvement'}
              </span>
              <span className="critic-score">
                Score: <strong>{critic.overall_score}</strong>/10
              </span>
            </div>
            {critic.issues && critic.issues.length > 0 && (
              <div className="critic-section">
                <h5>Issues</h5>
                <ul>{critic.issues.map((issue, i) => <li key={i}>{issue}</li>)}</ul>
              </div>
            )}
            {critic.missing_topics && critic.missing_topics.length > 0 && (
              <div className="critic-section">
                <h5>Missing Topics</h5>
                <ul>{critic.missing_topics.map((topic, i) => <li key={i}>{topic}</li>)}</ul>
              </div>
            )}
            {critic.improvement_instruction && (
              <div className="critic-section">
                <h5>Improvement Instruction</h5>
                <p>{critic.improvement_instruction}</p>
              </div>
            )}
          </div>
        )
      }

      case 'refiner': {
        const iterations = result.iteration_count || 0
        return iterations > 0 ? (
          <div className="refiner-success">
            <span className="refiner-icon">✅</span>
            <p>Refiner successfully corrected the draft <strong>{iterations}</strong> time{iterations !== 1 ? 's' : ''} based on Critic feedback!</p>
          </div>
        ) : (
          <div className="refiner-skip">
            <span className="refiner-icon">💤</span>
            <p>Draft was deemed good enough initially; Refiner was bypassed.</p>
          </div>
        )
      }

      default:
        return null
    }
  }

  return (
    <section className="trace-section">
      <button
        id="toggle-trace-btn"
        className={`trace-toggle ${isOpen ? 'trace-open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="trace-toggle-icon">🛠️</span>
        <span className="trace-toggle-text">View Internal Pipeline Trace &amp; Working Data</span>
        <svg
          className={`trace-chevron ${isOpen ? 'chevron-open' : ''}`}
          viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          width="18" height="18"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {isOpen && (
        <div className="trace-body">
          <div className="trace-timeline">
            {STAGES.map((stage) => (
              <div key={stage.key} className="trace-stage">
                <button
                  className={`stage-header ${openStage === stage.key ? 'stage-active' : ''}`}
                  onClick={() => toggleStage(stage.key)}
                >
                  <span className="stage-number">{stage.number}</span>
                  <span className="stage-icon">{stage.icon}</span>
                  <div className="stage-info">
                    <span className="stage-title">{stage.title}</span>
                    <span className="stage-subtitle">{stage.subtitle}</span>
                  </div>
                  <svg
                    className={`stage-chevron ${openStage === stage.key ? 'chevron-open' : ''}`}
                    viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                    width="16" height="16"
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </button>

                {openStage === stage.key && (
                  <div className="stage-content">
                    {renderStageContent(stage)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

export default PipelineTrace
