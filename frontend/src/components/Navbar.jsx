import React, { useState } from 'react';
import { FileText, ShieldAlert, Key, Plus, Bell, RefreshCw } from 'lucide-react';

export default function Navbar({ onUploadClick, onDeadlinesClick, onContractsClick, activeTab }) {
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState(sessionStorage.getItem('GEMINI_API_KEY') || '');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSaveKey = (e) => {
    e.preventDefault();
    if (apiKeyInput.trim()) {
      sessionStorage.setItem('GEMINI_API_KEY', apiKeyInput.trim());
    } else {
      sessionStorage.removeItem('GEMINI_API_KEY');
    }
    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      setShowKeyModal(false);
    }, 1200);
  };

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm no-print">
      {/* Prominent Legal Disclaimer Banner */}
      <div className="bg-amber-500/10 border-b border-amber-200/80 px-4 py-1.5 text-xs text-amber-900 flex items-center justify-between">
        <div className="flex items-center space-x-2 mx-auto sm:mx-0">
          <ShieldAlert className="w-4 h-4 text-amber-700 flex-shrink-0" />
          <span className="font-medium">
            <strong>ADMINISTRATIVE NOTICE:</strong> This application is strictly an information-management tool for tracking obligations and clauses. It does <u>not</u> provide legal advice, legal recommendations, or legal counsel.
          </span>
        </div>
        <span className="hidden sm:inline-block text-[11px] font-mono text-amber-700/80">
          Deterministic Rule Engine Active
        </span>
      </div>

      {/* Main Navbar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Platform Info */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={onContractsClick}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-md shadow-sky-500/20 text-white">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold tracking-tight text-slate-900">ContractIntelligence</span>
                <span className="bg-sky-100 text-sky-800 text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider">
                  Admin Tool
                </span>
              </div>
              <p className="text-xs text-slate-500">Information Management & Tracking</p>
            </div>
          </div>

          {/* Nav Actions */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onContractsClick}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                activeTab === 'contracts'
                  ? 'bg-slate-100 text-slate-900'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              Contracts
            </button>

            <button
              onClick={onDeadlinesClick}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors flex items-center space-x-1.5 ${
                activeTab === 'deadlines'
                  ? 'bg-slate-100 text-slate-900'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Bell className="w-4 h-4 text-sky-600" />
              <span>Deadlines</span>
            </button>

            <button
              onClick={() => setShowKeyModal(true)}
              title="Configure Session Gemini API Key"
              className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <Key className="w-4 h-4" />
            </button>

            <button
              onClick={onUploadClick}
              className="bg-sky-600 hover:bg-sky-700 text-white text-sm font-semibold px-4 py-2 rounded-lg shadow-sm shadow-sky-600/30 flex items-center space-x-1.5 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>Upload Contract</span>
            </button>
          </div>
        </div>
      </div>

      {/* API Key Modal */}
      {showKeyModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-sky-50 rounded-lg text-sky-600">
                <Key className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-slate-900">Gemini API Key Configuration</h3>
                <p className="text-xs text-slate-500">Stored safely in memory/sessionStorage (never committed)</p>
              </div>
            </div>

            <form onSubmit={handleSaveKey} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Google Gemini API Key
                </label>
                <input
                  type="password"
                  placeholder="AIzaSy..."
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-sky-500"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Leave blank to use the backend's configured .env key.
                </p>
              </div>

              {savedSuccess && (
                <div className="p-2 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-medium text-center">
                  Key saved successfully for this session!
                </div>
              )}

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowKeyModal(false)}
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Close
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 text-xs font-medium bg-sky-600 hover:bg-sky-700 text-white rounded-lg shadow-sm"
                >
                  Save Key
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
}
