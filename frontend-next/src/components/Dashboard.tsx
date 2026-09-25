'use client';
import React, { useState } from 'react';
import SvgRenderer from './SvgRenderer';

interface ChatMessage {
  role: string;
  content: string;
  tools?: string[];
  layoutElements?: any[];
  layoutElements?: any[]; // Legacy fallback
  layoutVariations?: { variation_name: string; elements: any[] }[];
  plan?: string[];
  codes?: string[];
  findings?: any[];
}

export default function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [history, setHistory] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: "Welcome! I'm your **Architectural Design Assistant**.\n\nI can review floor plans, search NBC/ADA standards, or answer dimensional questions.",
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeVariationIndex, setActiveVariationIndex] = useState(0);
  const [roomConfig, setRoomConfig] = useState({
    roomType: 'Kids Room',
    width: 12,
    length: 14,
    doors: 1,
    windows: 1,
    accessibility: 'Standard',
  });

  const handleGenerateFromConfig = async () => {
    const query = `Design a ${roomConfig.width}x${roomConfig.length} ft ${roomConfig.roomType} with ${roomConfig.doors} door(s) and ${roomConfig.windows} window(s). Accessibility: ${roomConfig.accessibility}.`;
    
    setHistory(prev => [...prev, { role: 'user', content: query }]);
    setIsLoading(true);

    try {
      const historyPayload = history
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({ role: m.role, content: m.content }));

      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: query, 
          history: historyPayload,
          constraints: roomConfig 
        })
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
      setActiveVariationIndex(0); // Reset to first variation
    } catch (err) {
      setHistory(prev => [...prev, { role: 'assistant', content: `Error connecting to backend: ${err}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = input;
    setInput('');
    setHistory(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      const historyPayload = history
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({ role: m.role, content: m.content }));

      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg, history: historyPayload })
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
      setHistory(prev => [...prev, { role: 'assistant', content: `Error connecting to backend: ${err}` }]);
    } finally {
      setIsLoading(false);
    }
  };
  // Track the most recent design to display on the main canvas
  const latestDesignMsg = [...history].reverse().find(m => m.layoutVariations && m.layoutVariations.length > 0);
  const currentVariations = latestDesignMsg?.layoutVariations || [];
  const activeVariation = currentVariations[activeVariationIndex] || null;
  const currentElements = activeVariation?.elements || [];

  return (
    <div className="flex h-screen bg-slate-900 text-slate-200 overflow-hidden">
      {/* Sidebar - Design Parameters */}
      <div className="w-80 bg-slate-800 border-r border-slate-700 flex flex-col z-20 shadow-xl">
        <div className="p-4 border-b border-slate-700 bg-slate-900">
          <h2 className="font-bold text-white tracking-wide">Design Parameters</h2>
          <p className="text-xs text-slate-400 mt-1">Configure room specifications</p>
        </div>
        
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Room Type */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Room Type</label>
            <select 
              value={roomConfig.roomType}
              onChange={e => setRoomConfig({...roomConfig, roomType: e.target.value})}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg text-sm text-white px-3 py-2.5 focus:outline-none focus:border-blue-500 transition-colors"
            >
              <option value="Bedroom">Bedroom</option>
              <option value="Master Bedroom">Master Bedroom</option>
              <option value="Kids Room">Kids Room</option>
              <option value="Living Room">Living Room</option>
              <option value="Kitchen">Kitchen</option>
              <option value="Bathroom">Bathroom</option>
            </select>
          </div>

          {/* Dimensions */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Dimensions (ft)</label>
            <div className="flex items-center space-x-2">
              <div className="flex-1">
                <label className="block text-[10px] text-slate-500 mb-1">Width</label>
                <input 
                  type="number" 
                  value={roomConfig.width}
                  onChange={e => setRoomConfig({...roomConfig, width: parseInt(e.target.value) || 0})}
                  className="w-full bg-slate-900 border border-slate-600 rounded-lg text-sm text-white px-3 py-2 focus:outline-none focus:border-blue-500"
                />
              </div>
              <span className="text-slate-500 mt-4">×</span>
              <div className="flex-1">
                <label className="block text-[10px] text-slate-500 mb-1">Length</label>
                <input 
                  type="number" 
                  value={roomConfig.length}
                  onChange={e => setRoomConfig({...roomConfig, length: parseInt(e.target.value) || 0})}
                  className="w-full bg-slate-900 border border-slate-600 rounded-lg text-sm text-white px-3 py-2 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Fixtures */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1">Doors</label>
              <input 
                type="number" min="1"
                value={roomConfig.doors}
                onChange={e => setRoomConfig({...roomConfig, doors: parseInt(e.target.value) || 0})}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg text-sm text-white px-3 py-2 focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-[10px] text-slate-400 uppercase tracking-wider mb-1">Windows</label>
              <input 
                type="number" min="0"
                value={roomConfig.windows}
                onChange={e => setRoomConfig({...roomConfig, windows: parseInt(e.target.value) || 0})}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg text-sm text-white px-3 py-2 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Compliance */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Compliance Focus</label>
            <select 
              value={roomConfig.accessibility}
              onChange={e => setRoomConfig({...roomConfig, accessibility: e.target.value})}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg text-sm text-white px-3 py-2.5 focus:outline-none focus:border-blue-500"
            >
              <option value="Standard">Standard (NBC India)</option>
              <option value="Wheelchair Accessible">Wheelchair Accessible</option>
              <option value="Senior Living">Senior Living</option>
            </select>
          </div>
        </div>

        <div className="p-4 border-t border-slate-700 bg-slate-900">
          <button 
            onClick={handleGenerateFromConfig}
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
            )}
            Generate Design
          </button>
        </div>
      </div>

      {/* Main Design Canvas Area */}
      <div className="flex-1 flex flex-col bg-slate-950 relative overflow-hidden">
        <div className="p-4 border-b border-slate-700 bg-slate-900 flex justify-between items-center z-10">
          <h1 className="text-xl font-bold text-white tracking-wide">Drafting Canvas</h1>
          <div className="flex space-x-2">
            <button className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-sm rounded border border-slate-600 transition-colors">Export PDF</button>
            <button className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded transition-colors">Save Design</button>
          </div>
        </div>
        
        {currentVariations.length > 0 && (
          <div className="bg-slate-850 border-b border-slate-700 px-6 py-3 flex space-x-3 overflow-x-auto shadow-sm">
            {currentVariations.map((variation, idx) => (
              <button
                key={idx}
                onClick={() => setActiveVariationIndex(idx)}
                className={`px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-all ${
                  activeVariationIndex === idx 
                    ? 'bg-blue-600 text-white shadow-md ring-2 ring-blue-400 ring-opacity-50' 
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-600'
                }`}
              >
                {variation.variation_name || `Option ${idx + 1}`}
              </button>
            ))}
          </div>
        )}
        
        <div className="flex-1 overflow-auto p-8 flex items-center justify-center relative bg-[url('https://www.transparenttextures.com/patterns/blueprint.png')]">
          {currentElements.length > 0 ? (
            <div className="bg-white p-4 rounded-xl shadow-2xl transform transition-transform hover:scale-[1.02]">
              <SvgRenderer elements={currentElements} />
            </div>
          ) : (
            <div className="text-slate-500 flex flex-col items-center">
              <svg className="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
              <p className="text-lg">No design loaded.</p>
              <p className="text-sm">Ask the copilot to generate a floor plan.</p>
            </div>
          )}
        </div>
      </div>

      {/* Right Chat Sidebar */}
      <div className="w-[400px] bg-slate-800 border-l border-slate-700 flex flex-col shadow-2xl z-20">
        <div className="p-4 border-b border-slate-700 bg-slate-800 flex items-center justify-between">
          <h2 className="font-bold text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
            AI Assistant
          </h2>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {history.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[90%] rounded-lg p-3 text-sm ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-slate-700 border border-slate-600 rounded-bl-none text-slate-200'}`}>
                {msg.tools && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {msg.tools.map(t => (
                      <span key={t} className="px-1.5 py-0.5 bg-slate-800 text-[10px] rounded text-blue-300 border border-slate-600">{t}</span>
                    ))}
                  </div>
                )}
                
                <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                
                {msg.plan && msg.plan.length > 0 && (
                  <div className="mt-3 bg-slate-800 p-2 rounded border border-slate-600">
                    <h3 className="text-xs font-bold text-slate-300 mb-1 uppercase tracking-wider">Plan</h3>
                    <ul className="list-disc pl-4 space-y-1 text-xs text-slate-400">
                      {msg.plan.map((p, j) => <li key={j}>{p}</li>)}
                    </ul>
                  </div>
                )}
                
                {msg.codes && msg.codes.length > 0 && (
                  <div className="mt-3 bg-slate-800 p-2 rounded border border-slate-600">
                    <h3 className="text-xs font-bold text-slate-300 mb-1 uppercase tracking-wider">References</h3>
                    <div className="space-y-1">
                      {msg.codes.map((c, j) => (
                        <div key={j} className="text-xs text-slate-400 border-l-2 border-blue-500 pl-2">
                          {c}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 border border-slate-600 rounded-lg p-3 text-sm text-slate-400 flex items-center gap-2">
                <svg className="animate-spin h-4 w-4 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Thinking...
              </div>
            </div>
          )}
        </div>
        
        {/* Chat Input */}
        <div className="p-3 border-t border-slate-700 bg-slate-800">
          <div className="relative">
            <input 
              type="text" 
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask the AI to design or modify..."
              className="w-full bg-slate-900 border border-slate-600 rounded-lg pl-3 pr-12 py-3 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button 
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-1.5 bottom-1.5 bg-blue-600 hover:bg-blue-500 text-white px-3 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
