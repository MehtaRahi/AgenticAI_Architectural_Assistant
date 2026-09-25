'use client';
import React, { useState, useEffect, MouseEvent as ReactMouseEvent } from 'react';

interface LayoutElement {
  id?: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  type: string;
}

// Color palette for different element types
const TYPE_COLORS: Record<string, { fill: string; stroke: string; text: string }> = {
  room:      { fill: '#f8fafc', stroke: '#334155', text: '#1e293b' },
  furniture: { fill: '#eff6ff', stroke: '#3b82f6', text: '#1e40af' },
  door:      { fill: '#fef2f2', stroke: '#ef4444', text: '#dc2626' },
  fixture:   { fill: '#f0fdf4', stroke: '#22c55e', text: '#16a34a' },
  window:    { fill: '#ecfeff', stroke: '#06b6d4', text: '#0891b2' },
};

export default function SvgRenderer({ elements }: { elements: LayoutElement[] }) {
  const [localElements, setLocalElements] = useState<LayoutElement[]>([]);
  const [draggingIdx, setDraggingIdx] = useState<number | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  useEffect(() => {
    if (elements) {
      setLocalElements(elements.map((el, i) => ({ ...el, id: el.id || `el-${i}` })));
    }
  }, [elements]);

  if (!localElements || localElements.length === 0) return null;

  const SCALE = 32;
  const PAD = 24;

  const rooms = localElements.filter(el => el.type === 'room');
  const maxX = Math.max(...(rooms.length > 0 ? rooms : localElements).map(el => (el.x || 0) + (el.width || 0)), 12);
  const maxY = Math.max(...(rooms.length > 0 ? rooms : localElements).map(el => (el.y || 0) + (el.height || 0)), 12);

  const svgW = maxX * SCALE + PAD * 2;
  const svgH = maxY * SCALE + PAD * 2;

  const sortedIndices = localElements.map((el, i) => ({ el, i })).sort((a, b) => {
    if (a.el.type === 'room' && b.el.type !== 'room') return -1;
    if (a.el.type !== 'room' && b.el.type === 'room') return 1;
    return 0;
  });

  const handleMouseDown = (e: ReactMouseEvent, index: number, el: LayoutElement) => {
    if (el.type === 'room') return;
    const svgRect = (e.currentTarget as Element).closest('svg')?.getBoundingClientRect();
    if (!svgRect) return;

    setDragOffset({
      x: e.clientX - svgRect.left - ((el.x || 0) * SCALE + PAD),
      y: e.clientY - svgRect.top - ((el.y || 0) * SCALE + PAD),
    });
    setDraggingIdx(index);
  };

  const handleMouseMove = (e: ReactMouseEvent) => {
    if (draggingIdx === null) return;
    const svgRect = (e.currentTarget as Element).getBoundingClientRect();

    const newX = (e.clientX - svgRect.left - dragOffset.x - PAD) / SCALE;
    const newY = (e.clientY - svgRect.top - dragOffset.y - PAD) / SCALE;

    setLocalElements(prev => {
      const updated = [...prev];
      updated[draggingIdx] = {
        ...updated[draggingIdx],
        x: Math.round(newX * 2) / 2,
        y: Math.round(newY * 2) / 2,
      };
      return updated;
    });
  };

  const handleMouseUp = () => setDraggingIdx(null);

  const getColors = (type: string) => TYPE_COLORS[type] || TYPE_COLORS.furniture;

  return (
    <div className="relative group">
      {/* Tooltip */}
      <div
        className="absolute top-3 right-3 px-3 py-1.5 rounded-lg text-[10px] font-medium pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-10"
        style={{ background: 'var(--bg-primary)', color: 'var(--text-muted)', border: '1px solid var(--border-subtle)' }}
      >
        Drag furniture to reposition • Snaps to 6″ grid
      </div>

      <svg
        width={svgW}
        height={svgH}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          fontFamily: "'Inter', sans-serif",
          borderRadius: 12,
          overflow: 'hidden',
        }}
      >
        {/* Background */}
        <rect width="100%" height="100%" fill="#fafbfc" />

        {/* Grid */}
        <defs>
          <pattern id="smallGrid" width={SCALE / 2} height={SCALE / 2} patternUnits="userSpaceOnUse">
            <path d={`M ${SCALE / 2} 0 L 0 0 0 ${SCALE / 2}`} fill="none" stroke="#e2e8f0" strokeWidth="0.5" />
          </pattern>
          <pattern id="mainGrid" width={SCALE} height={SCALE} patternUnits="userSpaceOnUse">
            <rect width={SCALE} height={SCALE} fill="url(#smallGrid)" />
            <path d={`M ${SCALE} 0 L 0 0 0 ${SCALE}`} fill="none" stroke="#cbd5e1" strokeWidth="1" />
          </pattern>
          {/* Drop shadow for dragging */}
          <filter id="dragShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="#000" floodOpacity="0.2" />
          </filter>
          <filter id="hoverShadow" x="-10%" y="-10%" width="120%" height="120%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#000" floodOpacity="0.1" />
          </filter>
        </defs>
        <rect width="100%" height="100%" fill="url(#mainGrid)" />

        {/* Scale Ruler (top) */}
        {Array.from({ length: Math.ceil(maxX) + 1 }, (_, i) => (
          <g key={`ruler-x-${i}`}>
            <line x1={i * SCALE + PAD} y1={4} x2={i * SCALE + PAD} y2={14} stroke="#94a3b8" strokeWidth="1" />
            <text x={i * SCALE + PAD} y={20} fontSize="8" fill="#94a3b8" textAnchor="middle" fontFamily="'JetBrains Mono', monospace">{i}′</text>
          </g>
        ))}

        {/* Scale Ruler (left) */}
        {Array.from({ length: Math.ceil(maxY) + 1 }, (_, i) => (
          <g key={`ruler-y-${i}`}>
            <line x1={4} y1={i * SCALE + PAD} x2={14} y2={i * SCALE + PAD} stroke="#94a3b8" strokeWidth="1" />
            <text x={18} y={i * SCALE + PAD + 3} fontSize="8" fill="#94a3b8" textAnchor="end" fontFamily="'JetBrains Mono', monospace">{i}′</text>
          </g>
        ))}

        {/* Elements */}
        {sortedIndices.map(({ el, i }) => {
          const ex = (el.x || 0) * SCALE + PAD;
          const ey = (el.y || 0) * SCALE + PAD;
          const ew = (el.width || 0) * SCALE;
          const eh = (el.height || 0) * SCALE;
          const etype = el.type || 'furniture';
          const label = (el.label || '').toUpperCase();
          const wFt = el.width || 0;
          const hFt = el.height || 0;
          const isDragging = draggingIdx === i;
          const isHovered = hoveredIdx === i;
          const colors = getColors(etype);

          if (etype === 'room') {
            return (
              <g key={el.id}>
                <rect x={ex} y={ey} width={ew} height={eh} fill={colors.fill} stroke={colors.stroke} strokeWidth="3" rx="2" />
                {/* Room label */}
                <text x={ex + ew / 2} y={ey + 18} fill={colors.text} fontSize="13" fontWeight="700" textAnchor="middle" letterSpacing="0.05em">{label}</text>
                <text x={ex + ew / 2} y={ey + 32} fill="#94a3b8" fontSize="10" textAnchor="middle" fontFamily="'JetBrains Mono', monospace">
                  {`${wFt}′ × ${hFt}′  (${wFt * hFt} sq ft)`}
                </text>
              </g>
            );
          }

          if (etype === 'door') {
            return (
              <g
                key={el.id}
                onMouseDown={(e) => handleMouseDown(e, i, el)}
                onMouseEnter={() => setHoveredIdx(i)}
                onMouseLeave={() => setHoveredIdx(null)}
                style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
                filter={isDragging ? 'url(#dragShadow)' : isHovered ? 'url(#hoverShadow)' : 'none'}
              >
                <rect x={ex} y={ey} width={ew} height={eh} fill={colors.fill} stroke={colors.stroke} strokeWidth="2" strokeDasharray="6,3" rx="2" />
                {/* Door arc */}
                {ew > eh ? (
                  <path d={`M ${ex + 2} ${ey + eh / 2} A ${ew / 3} ${ew / 3} 0 0 1 ${ex + ew / 3} ${ey + 2}`} fill="none" stroke={colors.stroke} strokeWidth="1.5" />
                ) : (
                  <path d={`M ${ex + ew / 2} ${ey + 2} A ${eh / 3} ${eh / 3} 0 0 1 ${ex + ew - 2} ${ey + eh / 3}`} fill="none" stroke={colors.stroke} strokeWidth="1.5" />
                )}
                <text x={ex + ew / 2} y={ey + eh / 2 + 4} fill={colors.text} fontSize="9" fontWeight="600" textAnchor="middle">DOOR</text>
              </g>
            );
          }

          // Furniture / Fixture / Window
          return (
            <g
              key={el.id}
              onMouseDown={(e) => handleMouseDown(e, i, el)}
              onMouseEnter={() => setHoveredIdx(i)}
              onMouseLeave={() => setHoveredIdx(null)}
              style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
              filter={isDragging ? 'url(#dragShadow)' : isHovered ? 'url(#hoverShadow)' : 'none'}
              opacity={isDragging ? 0.85 : 1}
            >
              <rect
                x={ex} y={ey}
                width={ew} height={eh}
                fill={isDragging ? '#dbeafe' : colors.fill}
                stroke={isDragging ? '#2563eb' : isHovered ? colors.stroke : colors.stroke}
                strokeWidth={isDragging || isHovered ? 2.5 : 1.5}
                rx="4"
              />
              {/* Diagonal hatch for fixtures */}
              {etype === 'fixture' && (
                <>
                  <clipPath id={`clip-${el.id}`}><rect x={ex} y={ey} width={ew} height={eh} rx="4" /></clipPath>
                  <g clipPath={`url(#clip-${el.id})`}>
                    {Array.from({ length: Math.ceil((ew + eh) / 8) }, (_, k) => (
                      <line key={k} x1={ex + k * 8} y1={ey + eh} x2={ex + k * 8 + eh} y2={ey} stroke={colors.stroke} strokeWidth="0.5" opacity="0.3" />
                    ))}
                  </g>
                </>
              )}
              <text x={ex + ew / 2} y={ey + eh / 2 - 2} fill={colors.text} fontSize="10" fontWeight="700" textAnchor="middle">{label}</text>
              <text x={ex + ew / 2} y={ey + eh / 2 + 10} fill="#94a3b8" fontSize="8" textAnchor="middle" fontFamily="'JetBrains Mono', monospace">
                {`${wFt}′×${hFt}′`}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
