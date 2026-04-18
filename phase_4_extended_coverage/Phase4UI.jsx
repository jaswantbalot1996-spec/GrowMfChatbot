import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Phase4UI.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Language = {
  ENGLISH: 'en',
  HINDI: 'hi'
};

const LanguageSelector = ({ language, setLanguage }) => {
  return (
    <div className="language-selector">
      <button
        className={`lang-btn ${language === Language.ENGLISH ? 'active' : ''}`}
        onClick={() => setLanguage(Language.ENGLISH)}
      >
        🇬🇧 English
      </button>
      <button
        className={`lang-btn ${language === Language.HINDI ? 'active' : ''}`}
        onClick={() => setLanguage(Language.HINDI)}
      >
        🇮🇳 हिंदी
      </button>
    </div>
  );
};

const FilterPanel = ({ language, filters, setFilters, visible, setVisible }) => {
  const handleChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const labels = {
    en: {
      title: 'Advanced Filters',
      risk: 'Risk Level',
      category: 'Category',
      expense: 'Max Expense Ratio (%)',
      aum: 'Max AUM (₹ Crore)',
      apply: 'Apply',
      clear: 'Clear'
    },
    hi: {
      title: 'उन्नत फ़िल्टर',
      risk: 'जोखिम स्तर',
      category: 'श्रेणी',
      expense: 'अधिकतम व्यय अनुपात (%)',
      aum: 'अधिकतम AUM (₹ करोड़)',
      apply: 'लागू करें',
      clear: 'साफ़ करें'
    }
  };

  const l = labels[language];

  return (
    <div className={`filter-panel ${visible ? 'visible' : ''}`}>
      <div className="filter-header">
        <h3>{l.title}</h3>
        <button
          className="close-btn"
          onClick={() => setVisible(false)}
        >
          ✕
        </button>
      </div>

      <div className="filter-group">
        <label>{l.risk}</label>
        <select
          value={filters.max_risk_level || ''}
          onChange={(e) => handleChange('max_risk_level', e.target.value || undefined)}
        >
          <option value="">Any</option>
          <option value="low">Low</option>
          <option value="low_to_moderate">Low to Moderate</option>
          <option value="moderate">Moderate</option>
          <option value="moderate_to_high">Moderate to High</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="filter-group">
        <label>{l.category}</label>
        <select
          value={filters.categories?.[0] || ''}
          onChange={(e) => handleChange('categories', e.target.value ? [e.target.value] : undefined)}
        >
          <option value="">Any</option>
          <option value="equity">Equity</option>
          <option value="debt">Debt</option>
          <option value="hybrid">Hybrid</option>
          <option value="liquid">Liquid</option>
        </select>
      </div>

      <div className="filter-group">
        <label>{l.expense}</label>
        <input
          type="number"
          min="0"
          max="5"
          step="0.1"
          value={filters.max_expense_ratio || 2}
          onChange={(e) => handleChange('max_expense_ratio', parseFloat(e.target.value))}
        />
      </div>

      <div className="filter-group">
        <label>{l.aum}</label>
        <input
          type="number"
          min="0"
          value={filters.max_aum_cr || ''}
          onChange={(e) => handleChange('max_aum_cr', e.target.value ? parseFloat(e.target.value) : undefined)}
          placeholder="Optional"
        />
      </div>

      <div className="filter-actions">
        <button
          className="clear-btn"
          onClick={() => setFilters({})}
        >
          {l.clear}
        </button>
        <button
          className="apply-btn"
          onClick={() => setVisible(false)}
        >
          {l.apply}
        </button>
      </div>
    </div>
  );
};

const ResponseDisplay = ({ response, language }) => {
  if (!response) return null;

  const labels = {
    en: {
      answer: 'Answer',
      sources: 'Sources',
      metadata: 'Metadata',
      responseTime: 'Response Time',
      found: 'Found',
      matching: 'matching documents'
    },
    hi: {
      answer: 'उत्तर',
      sources: 'स्रोत',
      metadata: 'मेटाडेटा',
      responseTime: 'प्रतिक्रिया समय',
      found: 'मिले',
      matching: 'मेल खाने वाले दस्तावेज़'
    }
  };

  const l = labels[language];
  const answer = language === Language.ENGLISH ?
    response.answer :
    response.answer_hi || response.answer;

  return (
    <div className="response-container">
      <section className="answer-section">
        <h3>📝 {l.answer}</h3>
        <p>{answer}</p>
      </section>

      {response.sources && response.sources.length > 0 && (
        <section className="sources-section">
          <h3>📚 {l.sources}</h3>
          <div className="sources-list">
            {response.sources.map((source, idx) => (
              <div key={idx} className="source-item">
                <div className="source-header">
                  <span className="source-name">{source.source}</span>
                  <span className="relevance">{Math.round(source.relevance * 100)}%</span>
                </div>
                <p className="source-content">{source.chunk}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="metadata-section">
        <h3>⏱️ {l.metadata}</h3>
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="label">{l.responseTime}</span>
            <span className="value">{response.latency_ms}ms</span>
          </div>
          <div className="metadata-item">
            <span className="label">Language</span>
            <span className="value">{response.language_detected.toUpperCase()}</span>
          </div>
          <div className="metadata-item">
            <span className="label">Filters</span>
            <span className="value">{response.filters_applied ? 'Applied' : 'None'}</span>
          </div>
        </div>
        {response.matched_chunks && (
          <p className="info-text">
            {l.found} {response.filtered_chunks} / {response.matched_chunks} {l.matching}
          </p>
        )}
      </section>
    </div>
  );
};

const Phase4UI = () => {
  const [language, setLanguage] = useState(Language.ENGLISH);
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [showFilters, setShowFilters] = useState(false);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiHealth, setApiHealth] = useState(true);

  useEffect(() => {
    // Check API health
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      const res = await axios.get(`${API_URL}/health`, { timeout: 5000 });
      setApiHealth(res.status === 200);
    } catch {
      setApiHealth(false);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        query,
        language,
        ...(Object.keys(filters).length > 0 && { filters })
      };

      const res = await axios.post(`${API_URL}/query`, payload, {
        timeout: 30000
      });

      setResponse(res.data);
    } catch (err) {
      setError(
        err.response?.data?.message ||
        'Failed to process query. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const labels = {
    en: {
      title: 'Groww Mutual Fund FAQ',
      subtitle: 'Phase 4: Multi-Language + Advanced Filtering',
      disclaimer: 'Disclaimer: Factual information only. Not investment advice.',
      placeholder: 'Ask about expense ratios, ELSS, fund categories...',
      search: 'Search',
      filters: 'Filters',
      apiError: 'API Server is unavailable. Please try again later.',
      searching: 'Searching...'
    },
    hi: {
      title: 'Groww म्यूचुअल फंड FAQ',
      subtitle: 'Phase 4: बहु-भाषा + उन्नत फ़िल्टरिंग',
      disclaimer: 'अस्वीकरण: तथ्यात्मक जानकारी केवल। निवेश सलाह नहीं।',
      placeholder: 'व्यय अनुपात, ELSS, फंड श्रेणियों के बारे में पूछें...',
      search: 'खोजें',
      filters: 'फ़िल्टर',
      apiError: 'API सर्वर उपलब्ध नहीं है। कृपया बाद में पुनः प्रयास करें।',
      searching: 'खोज रहे हैं...'
    }
  };

  const l = labels[language];

  return (
    <div className="phase4-ui">
      <header className="header">
        <div className="header-content">
          <h1>{l.title}</h1>
          <p>{l.subtitle}</p>
        </div>
        <LanguageSelector language={language} setLanguage={setLanguage} />
      </header>

      <main className="main-content">
        <div className="disclaimer">
          ℹ️ {l.disclaimer}
        </div>

        {!apiHealth && (
          <div className="error-banner">
            ⚠️ {l.apiError}
          </div>
        )}

        <div className="search-section">
          <div className="query-input-wrapper">
            <input
              type="text"
              className="query-input"
              placeholder={l.placeholder}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              disabled={!apiHealth}
            />
            <button
              className="filter-toggle"
              onClick={() => setShowFilters(!showFilters)}
              title={l.filters}
            >
              ⚙️
            </button>
            <button
              className="search-btn"
              onClick={handleSearch}
              disabled={!apiHealth || loading}
            >
              {loading ? l.searching : l.search}
            </button>
          </div>

          <FilterPanel
            language={language}
            filters={filters}
            setFilters={setFilters}
            visible={showFilters}
            setVisible={setShowFilters}
          />
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {response && (
          <ResponseDisplay response={response} language={language} />
        )}

        {!response && !error && !loading && (
          <div className="empty-state">
            <p>🔍 Ask a question to get started</p>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Phase 4: Extended Coverage (38 AMCs) • Multi-Language • Advanced Filtering</p>
      </footer>
    </div>
  );
};

export default Phase4UI;
