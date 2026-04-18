'use client';

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import styles from './page.module.css';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function Home() {
  const [query, setQuery] = useState('');
  const [language, setLanguage] = useState('en');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [showFilters, setShowFilters] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { type: 'user', text: query, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const payload = {
        query,
        language,
        ...filters,
      };

      const response = await axios.post(`${API_URL}/query`, payload, {
        timeout: 120000,
      });

      const data = response.data;
      const botMessage = {
        type: 'assistant',
        text: data.answer || 'No response',
        metadata: {
          sources: data.sources || [],
          latency: data.latency_ms,
          language: data.language || language,
        },
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'error',
        text: error.response?.data?.error || 'Error: Unable to fetch response',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logo}>
            <h1>GrowMF Chatbot</h1>
            <p>Intelligent Mutual Fund Assistant</p>
          </div>
          <div className={styles.controls}>
            <button
              className={`${styles.langBtn} ${language === 'en' ? styles.active : ''}`}
              onClick={() => setLanguage('en')}
            >
              🇬🇧 English
            </button>
            <button
              className={`${styles.langBtn} ${language === 'hi' ? styles.active : ''}`}
              onClick={() => setLanguage('hi')}
            >
              🇮🇳 हिंदी
            </button>
            <button
              className={styles.filterBtn}
              onClick={() => setShowFilters(!showFilters)}
            >
              ⚙️ Filters
            </button>
          </div>
        </div>
      </header>

      {/* Filter Panel */}
      {showFilters && (
        <div className={styles.filterPanel}>
          <div className={styles.filterGrid}>
            <div className={styles.filterGroup}>
              <label>Risk Level</label>
              <select
                value={filters.max_risk_level || ''}
                onChange={(e) =>
                  setFilters({ ...filters, max_risk_level: e.target.value || undefined })
                }
              >
                <option value="">Any</option>
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className={styles.filterGroup}>
              <label>Category</label>
              <select
                value={filters.categories?.[0] || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    categories: e.target.value ? [e.target.value] : undefined,
                  })
                }
              >
                <option value="">Any</option>
                <option value="equity">Equity</option>
                <option value="debt">Debt</option>
                <option value="hybrid">Hybrid</option>
                <option value="liquid">Liquid</option>
              </select>
            </div>

            <div className={styles.filterGroup}>
              <label>Max Expense Ratio (%)</label>
              <input
                type="number"
                step="0.01"
                value={filters.max_expense_ratio || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    max_expense_ratio: e.target.value ? parseFloat(e.target.value) : undefined,
                  })
                }
              />
            </div>
          </div>
          <button className={styles.clearBtn} onClick={handleClearFilters}>
            Clear Filters
          </button>
        </div>
      )}

      {/* Messages */}
      <div className={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div className={styles.welcome}>
            <h2>Welcome to GrowMF Chatbot</h2>
            <p>Ask me anything about mutual funds, investment strategies, or fund comparisons.</p>
            <div className={styles.examples}>
              <p>Example questions:</p>
              <ul>
                <li>"What is ELSS?"</li>
                <li>"Compare equity and debt funds"</li>
                <li>"What funds have low expense ratio?"</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`${styles.message} ${styles[msg.type]}`}>
              <div className={styles.messageContent}>
                <p>{msg.text}</p>
                {msg.metadata && (
                  <div className={styles.metadata}>
                    {msg.metadata.latency && (
                      <span>⏱️ {msg.metadata.latency}ms</span>
                    )}
                    {msg.metadata.sources?.length > 0 && (
                      <span>📚 {msg.metadata.sources.length} sources</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className={`${styles.message} ${styles.loading}`}>
            <div className={styles.spinner}></div>
            <p>Thinking...</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form className={styles.form} onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder={language === 'en' ? 'Ask a question...' : 'एक सवाल पूछें...'}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
          className={styles.input}
        />
        <button type="submit" disabled={loading || !query.trim()} className={styles.submitBtn}>
          {loading ? '⏳' : '→'}
        </button>
      </form>
    </div>
  );
}
