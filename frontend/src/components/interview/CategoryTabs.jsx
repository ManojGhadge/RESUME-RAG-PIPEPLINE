import React from 'react';

const categories = [
  { id: 'technical', label: 'Technical Skills' },
  { id: 'hr', label: 'HR & Background' },
  { id: 'project', label: 'Project Deep-Dive' },
  { id: 'behavioral', label: 'Behavioral & Soft Skills' },
];

export default function CategoryTabs({ activeCategory, onSelect }) {
  return (
    <div className="border-b border-gray-200/80 font-body">
      <nav className="flex space-x-6 -mb-px overflow-x-auto" aria-label="Tabs">
        {categories.map((cat) => {
          const isActive = cat.id === activeCategory;
          return (
            <button
              key={cat.id}
              onClick={() => onSelect(cat.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-all duration-200 ${
                isActive
                  ? 'border-primary text-primary font-bold'
                  : 'border-transparent text-muted hover:text-ink hover:border-gray-300'
              }`}
            >
              {cat.label}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
