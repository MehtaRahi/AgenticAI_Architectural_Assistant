'use client';
import React, { useState, useRef, useEffect } from 'react';
import SvgRenderer from './SvgRenderer';

interface ChatMessage {
  role: string;
  content: string;
  tools?: string[];
  layoutVariations?: { variation_name: string; elements: any[] }[];
  plan?: string[];
  codes?: string[];
  findings?: any[];
}

export default function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [history, setHistory] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: "Welcome to ArchStudio AI! I can design floor plans, check building codes, or answer dimensional questions.\n\nTry selecting your room parameters on the left and clicking Generate, or just describe what you need.",
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeVariationIndex, setActiveVariationIndex] = useState(0);
  const [sidebarTab, setSidebarTab] = useState<'config' | 'history'>('config');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [roomConfig, setRoomConfig] = useState({
    roomType: 'Kids Room',
    width: 12,
    length: 14,
    doors: 1,
    windows: 1,
    accessibility: 'Standard',
  });

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, isLoading]);

  const callBackend = async (query: string, constraints?: any) => {
    setIsLoading(true);
    try {
      const historyPayload = history
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({ role: m.role, content: m.content }));

      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, history: historyPayload, constraints: constraints || {} })
      });

      const data = await res.json();

      const newMsg: ChatMessage = {
        role: 'assistant',
        content: data.generated_design || 'Analysis complete.',
        layoutVariations: data.layout_variations,
        plan: data.plan,
        codes: data.retrieved_codes,
        findings: data.findings,
        tools: ["PlannerAgent", "DesignerAgent", "ResearcherAgent", "ReviewerAgent"]
      };

      setHistory(prev => [...prev, newMsg]);
      setActiveVariationIndex(0);
    } catch (err) {
      setHistory(prev => [...prev, { role: 'assistant', content: `Connection error: ${err}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateFromConfig = () => {
    const query = `Design a ${roomConfig.width}x${roomConfig.length} ft ${roomConfig.roomType} with ${roomConfig.doors} door(s) and ${roomConfig.windows} window(s). Accessibility: ${roomConfig.accessibility}.`;
    setHistory(prev => [...prev, { role: 'user', content: query }]);
    callBackend(query, roomConfig);
  };

  const handleSend = () => {
    if (!input.trim()) return;
    const userMsg = input;
    setInput('');
    setHistory(prev => [...prev, { role: 'user', content: userMsg }]);
    callBackend(userMsg);
  };

  const latestDesignMsg = [...history].reverse().find(m => m.layoutVariations && m.layoutVariations.length > 0);
  const currentVariations = latestDesignMsg?.layoutVariations || [];
  const activeVariation = currentVariations[activeVariationIndex] || null;
  const currentElements = activeVariation?.elements || [];

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* ─── LEFT SIDEBAR ─── */}
      <div className="w-[320px] flex flex-col glass-strong" style={{ borderRight: '1px solid var(--border-subtle)' }}>
        {/* Brand Header */}
        <div className="px-5 py-4 flex items-center gap-3" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
          <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'var(--accent-gradient)', boxShadow: '0 2px 8px var(--accent-glow)' }}>
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
          </div>
          <div>
            <h1 className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>ArchStudio <span style={{ color: 'var(--accent-primary)' }}>AI</span></h1>
            <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>NBC India Edition</p>
          </div>
        </div>

        {/* Sidebar Tab Switcher */}
        <div className="flex px-4 pt-3 gap-1">
          {(['config', 'history'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setSidebarTab(tab)}
              className="flex-1 py-2 text-xs font-semibold rounded-lg transition-all uppercase tracking-wider"
              style={{
                background: sidebarTab === tab ? 'var(--bg-surface)' : 'transparent',
                color: sidebarTab === tab ? 'var(--text-primary)' : 'var(--text-muted)',
                border: sidebarTab === tab ? '1px solid var(--border-default)' : '1px solid transparent',
              }}
            >
              {tab === 'config' ? '⚙ Parameters' : '📋 History'}
            </button>
          ))}
        </div>

        {/* Config Panel */}
        {sidebarTab === 'config' && (
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5 fade-in">
            <div>
              <label className="field-label">Room Type</label>
              <select
                value={roomConfig.roomType}
                onChange={e => setRoomConfig({...roomConfig, roomType: e.target.value})}
                className="input-field"
              >
                <option value="Bedroom">Bedroom</option>
                <option value="Master Bedroom">Master Bedroom</option>
                <option value="Kids Room">Kids Room</option>
                <option value="Living Room">Living Room</option>
                <option value="Kitchen">Kitchen</option>
                <option value="Bathroom">Bathroom</option>
                <option value="Studio Apartment">Studio Apartment</option>
                <option value="1 BHK">1 BHK</option>
                <option value="2 BHK">2 BHK</option>
              </select>
            </div>

            <div>
              <label className="field-label">Dimensions (ft)</label>
              <div className="flex items-center gap-2">
                <div className="flex-1">
                  <input
                    type="number"
                    value={roomConfig.width}
                    onChange={e => setRoomConfig({...roomConfig, width: parseInt(e.target.value) || 0})}
                    className="input-field text-center"
                    min="4"
                  />
                  <span className="block text-center text-[10px] mt-1" style={{ color: 'var(--text-muted)' }}>Width</span>
                </div>
                <span className="text-lg font-light" style={{ color: 'var(--text-muted)' }}>×</span>
                <div className="flex-1">
                  <input
                    type="number"
                    value={roomConfig.length}
                    onChange={e => setRoomConfig({...roomConfig, length: parseInt(e.target.value) || 0})}
                    className="input-field text-center"
                    min="4"
                  />
                  <span className="block text-center text-[10px] mt-1" style={{ color: 'var(--text-muted)' }}>Length</span>
                </div>
              </div>
              <div className="text-center mt-2">
                <span className="text-xs font-mono" style={{ color: 'var(--text-accent)' }}>
                  {roomConfig.width * roomConfig.length} sq ft
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="field-label">Doors</label>
                <input
                  type="number" min="1" max="4"
                  value={roomConfig.doors}
                  onChange={e => setRoomConfig({...roomConfig, doors: parseInt(e.target.value) || 1})}
                  className="input-field text-center"
                />
              </div>
              <div>
                <label className="field-label">Windows</label>
                <input
                  type="number" min="0" max="6"
                  value={roomConfig.windows}
                  onChange={e => setRoomConfig({...roomConfig, windows: parseInt(e.target.value) || 0})}
                  className="input-field text-center"
                />
              </div>
            </div>

            <div>
              <label className="field-label">Compliance</label>
              <select
                value={roomConfig.accessibility}
                onChange={e => setRoomConfig({...roomConfig, accessibility: e.target.value})}
                className="input-field"
              >
                <option value="Standard">Standard (NBC India)</option>
                <option value="Wheelchair Accessible">Wheelchair Accessible</option>
                <option value="Senior Living">Senior Living</option>
              </select>
            </div>
          </div>
        )}

        {/* History Panel */}
        {sidebarTab === 'history' && (
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-2 fade-in">
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Previous design sessions will appear here.</p>
            {history.filter(m => m.role === 'user').map((msg, i) => (
              <div key={i} className="card p-3 cursor-pointer">
                <p className="text-xs truncate" style={{ color: 'var(--text-secondary)' }}>{msg.content}</p>
              </div>
            ))}
          </div>
        )}

        {/* Generate Button */}
        <div className="p-4" style={{ borderTop: '1px solid var(--border-subtle)' }}>
          <button
            onClick={handleGenerateFromConfig}
            disabled={isLoading}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            )}
            {isLoading ? 'Generating...' : 'Generate Design'}
          </button>
        </div>

        {/* User Footer */}
        <div className="px-5 py-3 flex items-center justify-between" style={{ borderTop: '1px solid var(--border-subtle)' }}>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white" style={{ background: 'var(--accent-gradient)' }}>A</div>
            <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Guest</span>
          </div>
          <button onClick={onLogout} className="text-xs hover:underline" style={{ color: 'var(--danger)' }}>Sign Out</button>
        </div>
      </div>

      {/* ─── MAIN CANVAS ─── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="glass-strong px-6 py-3 flex items-center justify-between" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
          <div className="flex items-center gap-4">
            <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>Drafting Canvas</h2>
            {activeVariation && (
              <span className="text-xs px-3 py-1 rounded-full" style={{ background: 'var(--bg-surface)', color: 'var(--text-accent)', border: '1px solid var(--border-subtle)' }}>
                {activeVariation.variation_name}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button className="btn-ghost text-xs flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
              Export
            </button>
            <button className="btn-ghost text-xs flex items-center gap-1.5" style={{ borderColor: 'var(--accent-primary)', color: 'var(--accent-primary)' }}>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" /></svg>
              Save
            </button>
          </div>
        </div>

        {/* Variation Tabs */}
        {currentVariations.length > 0 && (
          <div className="px-6 py-3 flex gap-2 overflow-x-auto" style={{ borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-secondary)' }}>
            {currentVariations.map((variation, idx) => (
              <button
                key={idx}
                onClick={() => setActiveVariationIndex(idx)}
                className={`variation-tab ${activeVariationIndex === idx ? 'active' : ''}`}
              >
                {variation.variation_name || `Option ${idx + 1}`}
              </button>
            ))}
          </div>
        )}

        {/* Blueprint Area */}
        <div className="flex-1 overflow-auto blueprint-canvas flex items-center justify-center p-8 relative">
          {currentElements.length > 0 ? (
            <div className="slide-up" style={{ background: 'white', padding: 16, borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-lg)' }}>
              <SvgRenderer elements={currentElements} />
            </div>
          ) : (
            <div className="text-center fade-in">
              <div className="w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center" style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}>
                <svg className="w-10 h-10" style={{ color: 'var(--text-muted)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>No Design Yet</h3>
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Configure parameters and click Generate, or describe a room in chat.</p>
            </div>
          )}
        </div>
      </div>

      {/* ─── RIGHT CHAT PANEL ─── */}
      <div className="w-[420px] flex flex-col glass-strong" style={{ borderLeft: '1px solid var(--border-subtle)' }}>
        {/* Chat Header */}
        <div className="px-5 py-4 flex items-center justify-between" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
          <div className="flex items-center gap-3">
            <div className="status-dot" />
            <h2 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>AI Assistant</h2>
          </div>
          <span className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>
            {history.filter(m => m.role === 'user').length} queries
          </span>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {history.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} fade-in`}>
              <div className={msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}>
                {/* Agent Tags */}
                {msg.tools && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {msg.tools.map(t => (
                      <span key={t} className="agent-tag">{t}</span>
                    ))}
                  </div>
                )}

                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Plan Section */}
                {msg.plan && msg.plan.length > 0 && (
                  <div className="mt-3 p-3 rounded-lg" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-subtle)' }}>
                    <h4 className="text-[10px] font-bold uppercase tracking-wider mb-2" style={{ color: 'var(--text-accent)' }}>
                      Execution Plan
                    </h4>
                    <ul className="space-y-1.5">
                      {msg.plan.map((p, j) => (
                        <li key={j} className="flex gap-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
                          <span style={{ color: 'var(--accent-primary)' }}>→</span>
                          {p}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* References Section */}
                {msg.codes && msg.codes.length > 0 && (
                  <div className="mt-3 p-3 rounded-lg" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-subtle)' }}>
                    <h4 className="text-[10px] font-bold uppercase tracking-wider mb-2" style={{ color: 'var(--success)' }}>
                      Code References
                    </h4>
                    <div className="space-y-1">
                      {msg.codes.map((c, j) => (
                        <div key={j} className="text-xs pl-3" style={{ color: 'var(--text-secondary)', borderLeft: '2px solid var(--accent-primary)' }}>
                          {c}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex justify-start fade-in">
              <div className="chat-bubble-ai flex items-center gap-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--accent-primary)', animationDelay: '0ms' }} />
                  <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--accent-primary)', animationDelay: '150ms' }} />
                  <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--accent-primary)', animationDelay: '300ms' }} />
                </div>
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Agents working...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Chat Input */}
        <div className="p-4" style={{ borderTop: '1px solid var(--border-subtle)' }}>
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask AI to design, review, or modify..."
              className="input-field pr-12"
              style={{ paddingTop: 14, paddingBottom: 14 }}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="absolute right-1.5 top-1.5 bottom-1.5 px-3 rounded-lg flex items-center justify-center transition-all disabled:opacity-30"
              style={{ background: 'var(--accent-gradient)', color: 'white' }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
