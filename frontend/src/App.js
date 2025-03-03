import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])

  // 獲取歷史記錄
  const fetchHistory = async () => {
    try {
      console.log('正在獲取歷史記錄...');  // 添加日誌
      const response = await fetch('http://localhost:8000/history')
      console.log('歷史記錄回應:', response);  // 添加日誌
      
      if (!response.ok) {
        throw new Error('獲取歷史記錄失敗')
      }
      
      const data = await response.json()
      console.log('歷史記錄數據:', data);  // 添加日誌
      
      if (Array.isArray(data)) {
        setHistory(data)
      } else {
        console.error('History data is not an array:', data)
        setHistory([])
      }
    } catch (error) {
      console.error('Error fetching history:', error)
      setHistory([])
    }
  }

  // 在組件加載時和每次問答後獲取歷史記錄
  useEffect(() => {
    fetchHistory()
  }, [])

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
      await fetchHistory()  // 在獲得回答後更新歷史記錄
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

      {/* 歷史記錄顯示 */}
      <div className="history-section">
        <h2>對話歷史</h2>
        {history.length > 0 ? (
          history.map((item) => (
            <div key={item.conversation_id} className="history-item">
              <div className="question">問：{item.question}</div>
              <div className="answer">答：{item.answer}</div>
              <div className="timestamp">
                {new Date(item.created_at).toLocaleString()}
              </div>
            </div>
          ))
        ) : (
          <p>暫無對話歷史</p>
        )}
      </div>
    </div>
  )
}

export default App 