import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const samplePrompts = [
  'Iltimos, men uchun Python kodini yozib bering.',
  'Bu kod nima qilayotganini soddaroq tushuntiring.',
  'Men UX dizayn haqida nima bilishim kerak?',
];

function App() {
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [status, setStatus] = useState('Model yuklanmoqda...');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const scrollRef = useRef(null);

  useEffect(() => {
    fetch('/api/status')
      .then((res) => res.json())
      .then((payload) => {
        setStatus(`Model: ${payload.model} · Qurilma: ${payload.device} · Bilimlar: ${payload.knowledge_size}`);
      })
      .catch(() => {
        setStatus('Backend ulanmayapti — iltimos, serverni ishga tushiring.');
      });
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory, loading]);

  const sendQuestion = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError('');

    const currentQuestion = question.trim();
    setQuestion('');
    
    // Add temporary user message while loading
    setChatHistory(prev => [...prev, { question: currentQuestion, answer: '' }]);

    const historyPayload = chatHistory.map((item) => [item.question, item.answer]);
    const payload = { question: currentQuestion, history: historyPayload };

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Server xatosi');
      
      setChatHistory(data.history.map(([q, a]) => ({ question: q, answer: a })));
    } catch (err) {
      setError(err.message || 'Savol yuborishda xatolik yuz berdi.');
      // Remove the temp message if failed
      setChatHistory(prev => prev.slice(0, -1));
      setQuestion(currentQuestion); // Restore question
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendQuestion();
    }
  };

  const sendExample = (example) => {
    setQuestion(example);
  };

  const clearChat = () => {
    setChatHistory([]);
    setError('');
  };

  return (
    <div className="page-shell">
      <div className="background-glow"></div>
      
      <div className="hero-panel">
        <div>
          <h1 className="gradient-text">AI Chat Assistant</h1>
          <p>React frontend va FastAPI backend bilan ishlangan intellektual yordamchi.</p>
          <div className="status-chip">
            <span className="status-dot"></span>
            {status}
          </div>
        </div>
      </div>

      <div className="layout-grid">
        <section className="chat-panel glass-panel">
          <div className="panel-header">
            <div>
              <h2>Suhbat</h2>
              <p>Soʻrovlaringiz va AI javoblari ushbu maydonda ko'rinadi.</p>
            </div>
            <button className="ghost-button" onClick={clearChat} title="Chatni tozalash">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path></svg>
            </button>
          </div>

          <div className="chat-window" ref={scrollRef}>
            {chatHistory.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">✨</div>
                <h3>Suhbatni boshlang</h3>
                <p>Istagan savolingizni pastdagi maydonga yozing.</p>
              </div>
            ) : (
              chatHistory.map((item, index) => (
                <div key={index} className="message-group">
                  <div className="message user fade-in">
                    <span className="message-label">Siz</span>
                    <p>{item.question}</p>
                  </div>
                  {item.answer ? (
                    <div className="message assistant fade-in">
                      <span className="message-label">Assistant</span>
                      <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {item.answer}
                        </ReactMarkdown>
                      </div>
                    </div>
                  ) : (
                    loading && (
                      <div className="message assistant fade-in">
                        <span className="message-label">Assistant o'ylamoqda...</span>
                        <div className="loading-dots">
                          <span></span><span></span><span></span>
                        </div>
                      </div>
                    )
                  )}
                </div>
              ))
            )}
          </div>

          <div className="query-panel">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Savolingizni bu yerga yozing... (Enter - yuborish)"
              rows={3}
              disabled={loading}
            />
            <div className="query-actions">
              <button className="primary-button" onClick={sendQuestion} disabled={loading || !question.trim()}>
                {loading ? 'Yuborilmoqda...' : 'Yuborish'}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginLeft: '8px'}}><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
              </button>
            </div>
            
            <div className="example-row">
              {samplePrompts.map((sample) => (
                <button key={sample} className="chip" onClick={() => sendExample(sample)} disabled={loading}>
                  {sample}
                </button>
              ))}
            </div>
          </div>

          {error && <div className="error-box fade-in">{error}</div>}
        </section>

        <aside className="info-panel">
          <div className="panel-card glass-panel fade-in" style={{animationDelay: '0.1s'}}>
            <h3><span className="icon">🚀</span> Zamonaviy Dizayn</h3>
            <p>
              Glassmorphism uslubidagi shaffof dizayn va premium interfeys bilan yangilandi.
            </p>
          </div>
          <div className="panel-card glass-panel fade-in" style={{animationDelay: '0.2s'}}>
            <h3><span className="icon">⚡</span> Kuchli Backend</h3>
            <ul>
              <li>FastAPI orqali ulanish</li>
              <li>Markdown yordamida chiroyli kodlar</li>
              <li>Avtomatlashtirilgan startup</li>
            </ul>
          </div>
          <div className="panel-card glass-panel fade-in" style={{animationDelay: '0.3s'}}>
            <h3><span className="icon">💡</span> Maslahat</h3>
            <p>Kod qismlari, jadvallar yoki qalin matnni kiritib ko'ring — tizim uni to'liq formatlab beradi.</p>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default App;
