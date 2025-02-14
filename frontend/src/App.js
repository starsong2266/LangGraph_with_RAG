import { useState } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question) {
      alert('請輸入問題')
      return
    }

    setIsLoading(true)
    setAnswer('')
    setError('')

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: question })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '請求失敗')
      }

      const data = await response.json()
      setAnswer(data.response)
    } catch (error) {
      console.error('Error:', error)
      setError(error.message || '發生錯誤，請稍後再試')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>機車交通法規問答系統</h1>
      <form onSubmit={handleSubmit} className="input-group">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="請輸入您的問題（例如：駕照更換規定?）"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? '處理中...' : '送出問題'}
        </button>
      </form>
      {isLoading && <div className="loading">正在思考中...</div>}
      {error && <div className="error">{error}</div>}
      {answer && (
        <div className="answer">
          <strong>回答：</strong>
          <br />
          {answer}
        </div>
      )}
    </div>
  )
}

export default App 