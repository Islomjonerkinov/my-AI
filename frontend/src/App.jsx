import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { API_ERROR_MSG, fetchStatus, fileToBase64, sendChat } from './api';

const samplePrompts = [
  'Rasmni tahlil qiling',
  'Bu kodni tushuntiring',
  'Qisqa javob bering',
];

function App() {
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [status, setStatus] = useState('Ulanish tekshirilmoqda…');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [audioFile, setAudioFile] = useState(null);
  const [recording, setRecording] = useState(false);
  const scrollRef = useRef(null);
  const imageInputRef = useRef(null);
  const audioInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    fetchStatus()
      .then((payload) => {
        setStatus(`${payload.model} · ${payload.device}`);
      })
      .catch(() => {
        setStatus('Server ulanmagan');
      });
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory, loading]);

  useEffect(() => {
    return () => {
      if (imagePreview) URL.revokeObjectURL(imagePreview);
    };
  }, [imagePreview]);

  const clearAttachments = () => {
    setImageFile(null);
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    setImagePreview('');
    setAudioFile(null);
  };

  const onImagePick = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    setImagePreview(URL.createObjectURL(file));
    setAudioFile(null);
    event.target.value = '';
  };

  const onAudioPick = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setAudioFile(file);
    setImageFile(null);
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    setImagePreview('');
    event.target.value = '';
  };

  const startRecording = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setError('Mikrofon qo‘llab-quvvatlanmaydi.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      audioChunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioFile(new File([blob], 'ovoz.webm', { type: 'audio/webm' }));
        setImageFile(null);
        if (imagePreview) URL.revokeObjectURL(imagePreview);
        setImagePreview('');
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setRecording(true);
    } catch {
      setError('Mikrofonga ruxsat bering.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);
  };

  const sendQuestion = async () => {
    const text = question.trim();
    if (!text && !imageFile && !audioFile) return;

    setLoading(true);
    setError('');

    const displayQuestion =
      text ||
      (imageFile ? '📷 Rasm yuborildi' : '') ||
      (audioFile ? '🎤 Ovoz yuborildi' : '');

    const currentQuestion = text;
    setQuestion('');
    setChatHistory((prev) => [...prev, { question: displayQuestion, answer: '', imageUrl: imagePreview }]);

    try {
      const payload = {
        question: currentQuestion || 'Faylni tahlil qiling va qisqa javob bering.',
        history: chatHistory.map((item) => [item.question, item.answer]),
      };

      if (imageFile) {
        payload.image_base64 = await fileToBase64(imageFile);
        payload.image_mime = imageFile.type || 'image/jpeg';
      }
      if (audioFile) {
        payload.audio_base64 = await fileToBase64(audioFile);
        payload.audio_mime = audioFile.type || 'audio/webm';
      }

      const data = await sendChat(payload);
      setChatHistory(data.history.map(([q, a]) => ({ question: q, answer: a, imageUrl: '' })));
      clearAttachments();
    } catch {
      setError(API_ERROR_MSG);
      setChatHistory((prev) => prev.slice(0, -1));
      setQuestion(currentQuestion);
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

  const clearChat = () => {
    setChatHistory([]);
    setError('');
    clearAttachments();
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">AI</span>
          <div>
            <h1>Yordamchi</h1>
            <p className="brand-sub">{status}</p>
          </div>
        </div>
        <button type="button" className="btn-text" onClick={clearChat}>
          Tozalash
        </button>
      </header>

      <main className="chat-shell">
        <div className="messages" ref={scrollRef}>
          {chatHistory.length === 0 ? (
            <div className="welcome">
              <h2>Salom!</h2>
              <p>Matn, rasm yoki ovoz yuboring — javob shu yerda chiqadi.</p>
              <div className="prompt-grid">
                {samplePrompts.map((sample) => (
                  <button
                    key={sample}
                    type="button"
                    className="prompt-card"
                    onClick={() => setQuestion(sample)}
                    disabled={loading}
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            chatHistory.map((item, index) => (
              <article key={index} className="thread">
                <div className="bubble user">
                  {item.imageUrl && (
                    <img src={item.imageUrl} alt="Yuborilgan rasm" className="msg-image" />
                  )}
                  <p>{item.question}</p>
                </div>
                {item.answer ? (
                  <div className="bubble bot">
                    <div className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{item.answer}</ReactMarkdown>
                    </div>
                  </div>
                ) : (
                  loading && (
                    <div className="bubble bot typing">
                      <span />
                      <span />
                      <span />
                    </div>
                  )
                )}
              </article>
            ))
          )}
        </div>

        {(imagePreview || audioFile) && (
          <div className="attach-bar">
            {imagePreview && <img src={imagePreview} alt="" className="attach-thumb" />}
            {audioFile && (
              <span className="attach-tag">🎤 {audioFile.name || 'Ovoz yozuvi'}</span>
            )}
            <button type="button" className="attach-remove" onClick={clearAttachments} aria-label="Olib tashlash">
              ×
            </button>
          </div>
        )}

        {error && <div className="alert">{error}</div>}

        <footer className="composer">
          <input
            ref={imageInputRef}
            type="file"
            accept="image/*"
            hidden
            onChange={onImagePick}
          />
          <input
            ref={audioInputRef}
            type="file"
            accept="audio/*"
            hidden
            onChange={onAudioPick}
          />

          <div className="composer-tools">
            <button
              type="button"
              className="icon-btn"
              title="Rasm yuklash"
              onClick={() => imageInputRef.current?.click()}
              disabled={loading}
            >
              📷
            </button>
            <button
              type="button"
              className="icon-btn"
              title="Ovoz fayli"
              onClick={() => audioInputRef.current?.click()}
              disabled={loading}
            >
              📎
            </button>
            <button
              type="button"
              className={`icon-btn ${recording ? 'recording' : ''}`}
              title={recording ? 'Yozuvni to‘xtatish' : 'Ovoz yozish'}
              onClick={recording ? stopRecording : startRecording}
              disabled={loading}
            >
              {recording ? '⏹' : '🎤'}
            </button>
          </div>

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Xabar yozing…"
            rows={2}
            disabled={loading}
          />

          <button
            type="button"
            className="send-btn"
            onClick={sendQuestion}
            disabled={loading || (!question.trim() && !imageFile && !audioFile)}
          >
            {loading ? '…' : 'Yuborish'}
          </button>
        </footer>
      </main>
    </div>
  );
}

export default App;
