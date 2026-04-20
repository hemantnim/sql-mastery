"use client";

import React, { useState, useEffect } from 'react';
import Script from 'next/script';
import problemData from './problems.json';

const PROBLEMS = problemData;

export default function Home() {
  const [currentProblemIndex, setCurrentProblemIndex] = useState(0);
  const problem = PROBLEMS[currentProblemIndex];

  const [query, setQuery] = useState(problem.defaultQuery);
  const [results, setResults] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  // Update state and re-init DB when problem changes
  useEffect(() => {
    setQuery(problem.defaultQuery);
    setResults(null);
    setError(null);
    initDB();
  }, [currentProblemIndex]);

  const initDB = (retryCount = 0) => {
    const alasql = (window as any).alasql;
    if (!alasql) {
      if (retryCount < 10) {
        setTimeout(() => initDB(retryCount + 1), 500);
      } else {
        setError("SQL engine failed to load. Please refresh the page.");
      }
      return;
    }

    try {
      setIsReady(false);
      // Properly clear previous tables
      alasql.tables = {};
      alasql.options.casesensitive = false;
      
      if (problem.setupSql && problem.setupSql.trim()) {
        const statements = problem.setupSql.split(';').filter((s: string) => s.trim());
        for (const statement of statements) {
          try {
            alasql(statement);
          } catch (stmtErr: any) {
             console.warn("Setup statement failed:", statement, stmtErr);
          }
        }
      }
      setIsReady(true);
    } catch(e: any) {
      console.error("Failed to initialize DB", e);
      setError("Initialization Error: " + (e.message || "Could not setup database tables."));
      setIsReady(true);
    }
  };

  const handleRunQuery = () => {
    const alasql = (window as any).alasql;
    if (!alasql) {
      setError("SQL engine not loaded yet.");
      return;
    }

    try {
      setError(null);
      setResults(null);

      if (!query || !query.trim()) {
        setError("Please enter a query.");
        return;
      }

      let res = alasql(query);
      
      // If the query was just comments or empty, alasql might return undefined
      if (res === undefined || res === null) {
        setResults([]);
        return;
      }

      // If multiple queries were executed (separated by ';'), alasql returns an array of arrays
      if (Array.isArray(res) && res.length > 0 && Array.isArray(res[res.length - 1])) {
        res = res[res.length - 1];
      }
      
      if (Array.isArray(res)) {
        setResults(res);
      } else if (typeof res === 'object') {
        setResults([res]);
      } else {
        setResults([{ result: String(res) }]);
      }
    } catch (err: any) {
      setResults(null);
      setError(err.message || "An error occurred while executing the query.");
    }
  };

  const handleNext = () => {
    if (currentProblemIndex < PROBLEMS.length - 1) {
      setCurrentProblemIndex(currentProblemIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentProblemIndex > 0) {
      setCurrentProblemIndex(currentProblemIndex - 1);
    }
  };

  const getStarColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return '#22c55e'; // Green
      case 'Medium': return '#f59e0b'; // Orange
      case 'Hard': return '#ef4444'; // Red
      default: return 'var(--text-secondary)';
    }
  };

  return (
    <div className="app-container">
      <Script 
        src="https://cdn.jsdelivr.net/npm/alasql@4.17.2/dist/alasql.min.js" 
        strategy="afterInteractive"
        onLoad={initDB}
      />
      {/* Navbar */}
      <nav className="navbar">
        <div className="nav-brand">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
            <path d="M22 6l-10 7L2 6"></path>
          </svg>
          SQLMastery
        </div>
        <div className="nav-links">
          <a href="#" className="nav-link active">Problems</a>
          <a href="#" className="nav-link">Discuss</a>
          <a href="#" className="nav-link">Leaderboard</a>
        </div>
        <div className="nav-actions">
          <button className="btn btn-secondary">Sign In</button>
          <button className="btn btn-primary">Premium</button>
        </div>
      </nav>

      {/* Main Layout */}
      <main className="main-content">
        
        {/* Sidebar - Problem List */}
        <div className="sidebar">
          <div className="pane-header">
            <span>Problem List</span>
          </div>
          <ul className="problem-list">
            {PROBLEMS.map((p: any, idx: number) => (
              <li 
                key={p.id} 
                className={`problem-item ${idx === currentProblemIndex ? 'active' : ''}`}
                onClick={() => setCurrentProblemIndex(idx)}
                title={p.title}
                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill={getStarColor(p.difficulty)} stroke={getStarColor(p.difficulty)}>
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p.title}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Left Pane - Problem Description */}
        <div className="pane left-pane">
          <div className="pane-header">
            <span>Description</span>
            <div className="flex gap-2">
              <button className="btn btn-secondary" style={{padding: '4px 8px', fontSize: '0.8rem', opacity: currentProblemIndex === 0 ? 0.5 : 1}} disabled={currentProblemIndex === 0} onClick={handlePrev}>&lt; Prev</button>
              <button className="btn btn-secondary" style={{padding: '4px 8px', fontSize: '0.8rem', opacity: currentProblemIndex === PROBLEMS.length - 1 ? 0.5 : 1}} disabled={currentProblemIndex === PROBLEMS.length - 1} onClick={handleNext}>Next &gt;</button>
            </div>
          </div>
          <div className="pane-content">
            <h1 className="problem-title" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill={getStarColor(problem.difficulty)} stroke={getStarColor(problem.difficulty)}>
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
              {problem.title}
            </h1>
            <div className="problem-meta">
              <span className={`badge ${problem.difficulty === 'Easy' ? 'badge-easy' : problem.difficulty === 'Medium' ? 'badge-medium' : 'badge-hard'}`} style={
                problem.difficulty === 'Easy' ? {backgroundColor: 'rgba(34, 197, 94, 0.15)', color: '#22c55e'} : 
                problem.difficulty === 'Medium' ? {backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b'} :
                {backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444'}
              }>{problem.difficulty}</span>
              <span className="badge" style={{color: 'var(--text-secondary)'}}>{problem.category}</span>
            </div>
            
            <div className="problem-desc">
              <div dangerouslySetInnerHTML={{ __html: problem.description }} />
              
              {problem.tables && problem.tables.map((table: any, i: number) => (
                <div key={i}>
                  <h3 style={{color: 'var(--text-primary)', marginTop: '24px', marginBottom: '12px'}}>Table: {table.name}</h3>
                  <table className="schema-table">
                    <thead>
                      <tr>
                        <th>Column Name</th>
                        <th>Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {table.columns.map((col: any, j: number) => (
                        <tr key={j}>
                          <td>{col.name}</td>
                          <td>{col.type}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Pane - Editor and Results */}
        <div className="right-pane">
          
          {/* Top: Editor */}
          <div className="editor-pane">
            <div className="pane-header">
              <div className="flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                SQL
              </div>
              <div className="nav-actions">
                <button className="btn btn-secondary" onClick={() => setQuery(problem.defaultQuery)}>Reset</button>
                <button className="btn btn-primary" style={{backgroundColor: 'var(--success-color)', opacity: isReady ? 1 : 0.5}} disabled={!isReady} onClick={handleRunQuery}>
                  {isReady ? 'Run Query' : 'Loading Engine...'}
                </button>
              </div>
            </div>
            <textarea 
              className="editor-textarea" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              spellCheck="false"
            />
          </div>

          {/* Bottom: Results */}
          <div className="results-pane">
            <div className="pane-header">
              <span>Testcases & Results</span>
            </div>
            <div className="pane-content" style={{padding: '0', display: 'flex', flexDirection: 'column'}}>
              {!results && !error ? (
                <div className="empty-state">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                    <path d="M2 12h4l2-9 5 18 3-9h6"></path>
                  </svg>
                  <p>Run your query to see results here</p>
                </div>
              ) : error ? (
                <div style={{color: '#ef4444', padding: '16px', fontFamily: 'monospace', fontSize: '0.9rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', height: '100%'}}>
                  <strong>Error executing query:</strong><br/>
                  {error}
                </div>
              ) : results && results.length > 0 ? (
                <div style={{overflowX: 'auto', padding: '16px'}}>
                  <table className="schema-table" style={{marginTop: 0}}>
                    <thead>
                      <tr>
                        {results[0] && typeof results[0] === 'object' ? (
                          Object.keys(results[0]).map(key => (
                            <th key={key}>{key}</th>
                          ))
                        ) : (
                          <th>Result</th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((row, i) => (
                        <tr key={i}>
                          {row && typeof row === 'object' ? (
                            Object.values(row).map((val: any, j) => (
                              <td key={j}>{val === null || val === undefined ? 'null' : String(val)}</td>
                            ))
                          ) : (
                            <td>{String(row)}</td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{padding: '16px', color: 'var(--text-secondary)'}}>
                  Query executed successfully, but returned 0 rows.
                </div>
              )}
            </div>
          </div>

        </div>

      </main>
    </div>
  );
}
