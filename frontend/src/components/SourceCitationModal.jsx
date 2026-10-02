import React from 'react';
import { X, BookOpen, Quote, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function SourceCitationModal({ isOpen, onClose, item, itemType = "Item" }) {
  if (!isOpen || !item) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-xl w-full border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="bg-slate-50 px-5 py-3.5 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-4 h-4 text-sky-600" />
            <span className="text-sm font-bold text-slate-800">
              Source Citation & Document Lineage
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Extracted Element ({itemType})
            </span>
            <h3 className="text-base font-bold text-slate-900 mt-0.5">
              {item.title || item.name || item.term_title}
            </h3>
          </div>

          {/* Location metadata */}
          <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs">
            <div>
              <span className="text-slate-500 font-medium block">Document Section</span>
              <span className="text-slate-900 font-semibold font-mono">
                {item.source_section || 'General Preamble / Unlabeled'}
              </span>
            </div>
            <div>
              <span className="text-slate-500 font-medium block">Document Page</span>
              <span className="text-slate-900 font-semibold font-mono">
                {item.source_page ? `Page ${item.source_page}` : 'Pasted / Unpaginated'}
              </span>
            </div>
          </div>

          {/* Verbatim quote */}
          <div>
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-700 mb-1.5">
              <Quote className="w-3.5 h-3.5 text-sky-600" />
              <span>Verbatim Excerpt from Uploaded Document</span>
            </div>
            <div className="bg-slate-900 text-slate-100 p-4 rounded-xl text-xs font-mono leading-relaxed border border-slate-800 shadow-inner">
              {item.source_quote ? (
                `"${item.source_quote}"`
              ) : (
                <span className="text-slate-500 italic">No direct quote captured for this element.</span>
              )}
            </div>
          </div>

          {/* Certainty & Confidence */}
          <div className="p-3 rounded-xl border flex items-start space-x-3 bg-slate-50/50">
            {item.certainty === 'CONFIRMED' ? (
              <ShieldCheck className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            )}
            <div className="text-xs">
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-slate-900">
                  Certainty Status: {item.certainty}
                </span>
                <span className="bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono text-[10px]">
                  {Math.round((item.confidence_score || 1.0) * 100)}% Confidence
                </span>
              </div>
              {item.uncertainty_rationale && (
                <p className="text-slate-600 mt-1">
                  <strong>Rationale:</strong> {item.uncertainty_rationale}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-5 py-3 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
