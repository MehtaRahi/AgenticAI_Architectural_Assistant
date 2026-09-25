import React, { useState, useEffect, MouseEvent } from 'react';

interface LayoutElement {
  id?: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  type: string;
}

export default function SvgRenderer({ elements }: { elements: LayoutElement[] }) {
  const [localElements, setLocalElements] = useState<LayoutElement[]>([]);
  const [draggingIdx, setDraggingIdx] = useState<number | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  useEffect(() => {
    // Add unique IDs to incoming elements if they don't have them
    if (elements) {
      setLocalElements(elements.map((el, i) => ({ ...el, id: el.id || `el-${i}` })));
    }
  }, [elements]);

  if (!localElements || localElements.length === 0) return null;

  const SCALE = 30;

  // Calculate bounds based on rooms
  const rooms = localElements.filter(el => el.type === 'room');
  const maxX = Math.max(...(rooms.length > 0 ? rooms : localElements).map(el => (el.x || 0) + (el.width || 0)), 12);
  const maxY = Math.max(...(rooms.length > 0 ? rooms : localElements).map(el => (el.y || 0) + (el.height || 0)), 12);

  const w = maxX * SCALE + 40;
  const h = maxY * SCALE + 40;

  // Sort elements: rooms first, so they are drawn at the bottom
  const sortedIndices = localElements.map((el, i) => ({ el, i })).sort((a, b) => {
    if (a.el.type === 'room' && b.el.type !== 'room') return -1;
    if (a.el.type !== 'room' && b.el.type === 'room') return 1;
    return 0;
  });

  const handleMouseDown = (e: MouseEvent, index: number, el: LayoutElement) => {
    if (el.type === 'room') return; // Don't drag the room itself
    
    // Calculate the offset between the mouse and the top-left of the element
    const svgRect = (e.currentTarget as Element).closest('svg')?.getBoundingClientRect();
    if (!svgRect) return;

    const mouseX = e.clientX - svgRect.left;
    const mouseY = e.clientY - svgRect.top;

    const elScreenX = (el.x || 0) * SCALE + 20;
    const elScreenY = (el.y || 0) * SCALE + 20;

    setDragOffset({
      x: mouseX - elScreenX,
      y: mouseY - elScreenY
    });
    setDraggingIdx(index);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (draggingIdx === null) return;
    
    const svgRect = (e.currentTarget as Element).closest('svg')?.getBoundingClientRect();
    if (!svgRect) return;

    const mouseX = e.clientX - svgRect.left;
    const mouseY = e.clientY - svgRect.top;

    const newX = (mouseX - dragOffset.x - 20) / SCALE;
    const newY = (mouseY - dragOffset.y - 20) / SCALE;

    setLocalElements(prev => {
      const updated = [...prev];
      // Snap to a 0.5ft grid
      updated[draggingIdx] = {
        ...updated[draggingIdx],
        x: Math.round(newX * 2) / 2,
        y: Math.round(newY * 2) / 2
      };
      return updated;
    });
  };

  const handleMouseUp = () => {
    setDraggingIdx(null);
  };

  return (
    <div className="relative group">
      <div className="absolute top-2 right-2 bg-slate-900/80 text-[10px] text-white px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
        Drag furniture to reposition
      </div>
      <svg 
        width={w} 
        height={h} 
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #ccc',
          margin: '0',
          fontFamily: 'monospace',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
        }}
      >
        {/* Grid Background */}
        <defs>
          <pattern id="grid" width={SCALE} height={SCALE} patternUnits="userSpaceOnUse">
            <path d={`M ${SCALE} 0 L 0 0 0 ${SCALE}`} fill="none" stroke="#e5e7eb" strokeWidth="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        {sortedIndices.map(({ el, i }) => {
          const ex = (el.x || 0) * SCALE + 20;
          const ey = (el.y || 0) * SCALE + 20;
          const ew = (el.width || 0) * SCALE;
          const eh = (el.height || 0) * SCALE;
          const etype = el.type || 'furniture';
          
          const label = (el.label || (etype === 'room' ? 'ROOM' : '')).toUpperCase();
          const wFt = el.width || 0;
          const hFt = el.height || 0;
          
          const isDragging = draggingIdx === i;
          
          if (etype === 'room') {
            return (
              <g key={el.id}>
                <rect x={ex} y={ey} width={ew} height={eh} fill="#f8fafc" stroke="#334155" strokeWidth="4" />
                <text x={ex + ew / 2} y={ey + 20} fill="#334155" fontSize="12" fontWeight="bold" textAnchor="middle">{label}</text>
                <text x={ex + ew / 2} y={ey + 35} fill="#64748b" fontSize="10" textAnchor="middle">{`${wFt}' x ${hFt}'`}</text>
              </g>
            );
          } else if (etype === 'door') {
            return (
              <g 
                key={el.id} 
                onMouseDown={(e) => handleMouseDown(e, i, el)}
                style={{ cursor: 'grab' }}
              >
                <rect x={ex} y={ey} width={ew} height={eh} fill="#ffffff" stroke="#ef4444" strokeWidth="2" strokeDasharray="4,4" />
                <text x={ex + ew / 2} y={ey + eh / 2 + 3} fill="#ef4444" fontSize="9" fontWeight="bold" textAnchor="middle">DOOR</text>
              </g>
            );
          } else {
            return (
              <g 
                key={el.id} 
                onMouseDown={(e) => handleMouseDown(e, i, el)}
                style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
                className={isDragging ? 'opacity-80' : 'opacity-100 hover:opacity-90'}
              >
                <rect 
                  x={ex} y={ey} 
                  width={ew} height={eh} 
                  fill={isDragging ? '#e0f2fe' : '#ffffff'} 
                  stroke={isDragging ? '#0284c7' : '#0ea5e9'} 
                  strokeWidth="2" 
                  rx="4"
                  filter={isDragging ? 'drop-shadow(0 4px 3px rgb(0 0 0 / 0.15))' : 'none'}
                />
                <text x={ex + ew / 2} y={ey + eh / 2 - 2} fill="#0f172a" fontSize="10" fontWeight="bold" textAnchor="middle">{label}</text>
                <text x={ex + ew / 2} y={ey + eh / 2 + 10} fill="#64748b" fontSize="8" textAnchor="middle">{`${wFt}' x ${hFt}'`}</text>
              </g>
            );
          }
        })}
      </svg>
    </div>
  );
}
