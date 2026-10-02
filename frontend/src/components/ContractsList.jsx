import React, { useState } from 'react';
import {
  FileText,
  Plus,
  Search,
  Calendar,
  AlertTriangle,
  ChevronRight,
  Clock,
  Sparkles,
  ShieldCheck,
  Trash2,
} from 'lucide-react';

export default function ContractsList({
  contracts,
  onSelectContract,
  onUploadClick,
  onDeleteContract,
  loading,
}) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredContracts = contracts.filter((c) =>
    c.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Hero Welcome & Value Header */}
      <div className="bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center space-x-1.5 bg-sky-500/20 text-sky-300 px-3 py-1 rounded-full text-xs font-semibold border border-sky-400/30">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Administrative Tracking • Not Legal Advice</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Contract Intelligence & Deadline Management
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Upload text-based contracts and organizational policy documents. Extract parties, renewal terms, and obligations with exact citations, track revisions across versions, and automate deterministic deadline calculations.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <button
              onClick={onUploadClick}
              className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-lg shadow-sky-500/25 flex items-center space-x-1.5 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>Upload Contract (PDF, DOCX, Text)</span>
            </button>
          </div>
        </div>

        {/* Decorative background glow */}
        <div className="absolute right-0 top-0 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
      </div>

      {/* Contracts Table Header & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Managed Contracts</h2>
          <p className="text-xs text-slate-500">
            {contracts.length} contract document{contracts.length === 1 ? '' : 's'} registered in PostgreSQL
          </p>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search contracts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-xl text-xs bg-white focus:ring-2 focus:ring-sky-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Loading state */}
      {loading ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-xs text-slate-500">
          Loading contracts from PostgreSQL...
        </div>
      ) : filteredContracts.length === 0 ? (
        /* Empty State */
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-lg mx-auto space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center mx-auto shadow-inner">
            <FileText className="w-7 h-7" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-slate-900">No Contracts Found</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              {searchTerm
                ? 'No contracts matched your search term.'
                : 'Upload a contract document (PDF, DOCX, or text) to begin structured intelligence extraction.'}
            </p>
          </div>
          <div>
            <button
              onClick={onUploadClick}
              className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs rounded-xl shadow-sm inline-flex items-center space-x-1.5 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>Upload New Contract</span>
            </button>
          </div>
        </div>
      ) : (
        /* Contracts Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredContracts.map((c) => (
            <div
              key={c.id}
              onClick={() => onSelectContract(c.id)}
              className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col justify-between hover:border-sky-300 group"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="text-sm font-bold text-slate-900 group-hover:text-sky-700 transition-colors line-clamp-1">
                    {c.title}
                  </h3>
                  <span className="bg-slate-100 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase flex-shrink-0">
                    v{c.latest_version}
                  </span>
                </div>

                {/* Stale Warning Badge if any */}
                {c.stale_items_count > 0 && (
                  <div className="mb-3 inline-flex items-center space-x-1 text-[11px] font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-200">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                    <span>{c.stale_items_count} Stale Item{c.stale_items_count === 1 ? '' : 's'}</span>
                  </div>
                )}

                <p className="text-xs text-slate-500 line-clamp-2 mb-4">
                  {c.description || 'Administrative contract tracking record.'}
                </p>

                {/* Metrics Pill Grid */}
                <div className="grid grid-cols-3 gap-2 bg-slate-50 p-2.5 rounded-xl border border-slate-100 text-center text-[11px] mb-4">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Clauses</span>
                    <span className="font-bold text-slate-800">{c.clauses_count}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Obligations</span>
                    <span className="font-bold text-slate-800">{c.obligations_count}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Flagged</span>
                    <span className="font-bold text-slate-800">{c.unclear_terms_count}</span>
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="flex items-center justify-between pt-3 border-t border-slate-100 text-xs text-slate-400">
                <span className="inline-flex items-center space-x-1">
                  <Calendar className="w-3 h-3" />
                  <span>{new Date(c.updated_at).toLocaleDateString()}</span>
                </span>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteContract(c.id);
                    }}
                    title="Delete contract"
                    className="p-1 hover:text-rose-600 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                  <span className="inline-flex items-center space-x-0.5 text-sky-600 font-semibold group-hover:translate-x-0.5 transition-transform">
                    <span>Inspect</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
