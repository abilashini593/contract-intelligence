import React, { useState } from 'react';
import { X, Upload, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles, BookOpen } from 'lucide-react';
import { uploadContract, uploadContractVersion } from '../api/client';

export default function UploadModal({ isOpen, onClose, onSuccess, existingContract = null }) {
  if (!isOpen) return null;

  const isNewVersion = !!existingContract;

  // Form states
  const [contractMode, setContractMode] = useState('file'); // 'file' | 'text'
  const [contractFile, setContractFile] = useState(null);
  const [contractText, setContractText] = useState('');
  const [contractTitle, setContractTitle] = useState(existingContract ? existingContract.title : '');

  // Policy doc states (only for initial upload)
  const [hasPolicy, setHasPolicy] = useState(false);
  const [policyMode, setPolicyMode] = useState('file'); // 'file' | 'text'
  const [policyFile, setPolicyFile] = useState(null);
  const [policyText, setPolicyText] = useState('');
  const [policyTitle, setPolicyTitle] = useState('');

  // Submission & loading
  const [isLoading, setIsLoading] = useState(false);
  const [progressStage, setProgressStage] = useState('');
  const [errorMsg, setErrorMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);

    // Validation
    if (contractMode === 'file' && !contractFile) {
      setErrorMsg('Please select a contract file (.pdf, .docx, or .txt).');
      return;
    }
    if (contractMode === 'text' && !contractText.trim()) {
      setErrorMsg('Please enter or paste the contract text.');
      return;
    }

    try {
      setIsLoading(true);
      setProgressStage('Validating document format (No OCR)...');

      const formData = new FormData();

      if (contractMode === 'file') {
        formData.append('file', contractFile);
      } else {
        formData.append('pasted_text', contractText);
      }

      if (!isNewVersion) {
        if (contractTitle.trim()) {
          formData.append('title', contractTitle.trim());
        }

        // Optional policy doc
        if (hasPolicy) {
          if (policyMode === 'file' && policyFile) {
            formData.append('policy_file', policyFile);
          } else if (policyMode === 'text' && policyText.trim()) {
            formData.append('policy_pasted_text', policyText.trim());
          }
          if (policyTitle.trim()) {
            formData.append('policy_title', policyTitle.trim());
          }
        }
      }

      setProgressStage('Running structured extraction via Gemini AI...');

      let result;
      if (isNewVersion) {
        result = await uploadContractVersion(existingContract.id, formData);
      } else {
        result = await uploadContract(formData);
      }

      setProgressStage('Calculating deterministic deadline reminders...');
      setTimeout(() => {
        setIsLoading(false);
        onSuccess(result);
        onClose();
      }, 500);

    } catch (err) {
      setIsLoading(false);
      const detail = err.response?.data?.detail || err.message || 'An error occurred during upload and analysis.';
      setErrorMsg(detail);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full border border-slate-200 overflow-hidden my-8">
        {/* Header */}
        <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              {isNewVersion ? `Upload New Version for "${existingContract.title}"` : 'Upload Contract for Intelligence Extraction'}
            </h2>
            <p className="text-xs text-slate-500">
              Supports text-based PDF, DOCX, and pasted text. (Scanned image OCR not supported).
            </p>
          </div>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {errorMsg && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <strong>Analysis Failed:</strong> {errorMsg}
              </div>
            </div>
          )}

          {/* Title (Initial upload only) */}
          {!isNewVersion && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Contract Title (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Master Services Agreement (Apex & Meridian)"
                value={contractTitle}
                onChange={(e) => setContractTitle(e.target.value)}
                disabled={isLoading}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
            </div>
          )}

          {/* Contract Input Toggle */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold text-slate-700">Contract Document</label>
              <div className="flex bg-slate-100 p-0.5 rounded-lg text-xs font-medium">
                <button
                  type="button"
                  onClick={() => setContractMode('file')}
                  disabled={isLoading}
                  className={`px-3 py-1 rounded-md transition-colors ${
                    contractMode === 'file' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Upload File
                </button>
                <button
                  type="button"
                  onClick={() => setContractMode('text')}
                  disabled={isLoading}
                  className={`px-3 py-1 rounded-md transition-colors ${
                    contractMode === 'text' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Paste Text
                </button>
              </div>
            </div>

            {contractMode === 'file' ? (
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    setContractFile(e.dataTransfer.files[0]);
                  }
                }}
                className="border-2 border-dashed border-slate-300 hover:border-sky-400 rounded-xl p-6 text-center transition-colors bg-slate-50/50 cursor-pointer"
              >
                <input
                  type="file"
                  id="contract-file"
                  accept=".pdf,.docx,.txt"
                  disabled={isLoading}
                  onChange={(e) => setContractFile(e.target.files[0] || null)}
                  className="hidden"
                />
                <label htmlFor="contract-file" className="cursor-pointer block">
                  <div className="w-12 h-12 rounded-full bg-sky-100 text-sky-600 flex items-center justify-center mx-auto mb-2">
                    <Upload className="w-6 h-6" />
                  </div>
                  <span className="text-sm font-medium text-slate-700 block">
                    {contractFile ? contractFile.name : 'Click to upload or drag & drop'}
                  </span>
                  <span className="text-xs text-slate-400 block mt-1">
                    Text-based PDF, DOCX, or TXT (Max 15MB)
                  </span>
                </label>
                {contractFile && (
                  <div className="mt-3 inline-flex items-center space-x-1.5 px-2.5 py-1 bg-sky-50 text-sky-700 rounded-md text-xs font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Selected: {(contractFile.size / 1024).toFixed(1)} KB</span>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <textarea
                  rows={6}
                  placeholder="Paste the full text of your contract here..."
                  value={contractText}
                  onChange={(e) => setContractText(e.target.value)}
                  disabled={isLoading}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono focus:outline-none focus:ring-2 focus:ring-sky-500"
                />
              </div>
            )}
          </div>

          {/* Optional Policy Document (Initial upload only) */}
          {!isNewVersion && (
            <div className="pt-2 border-t border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="has-policy"
                    checked={hasPolicy}
                    onChange={(e) => setHasPolicy(e.target.checked)}
                    disabled={isLoading}
                    className="w-4 h-4 text-sky-600 rounded border-slate-300 focus:ring-sky-500"
                  />
                  <label htmlFor="has-policy" className="text-xs font-semibold text-slate-800 cursor-pointer flex items-center space-x-1">
                    <BookOpen className="w-3.5 h-3.5 text-indigo-600" />
                    <span>Cross-reference against Organizational Policy Document</span>
                    <span className="text-[10px] text-slate-400 font-normal">(Optional)</span>
                  </label>
                </div>

                {hasPolicy && (
                  <div className="flex bg-slate-100 p-0.5 rounded-lg text-xs font-medium">
                    <button
                      type="button"
                      onClick={() => setPolicyMode('file')}
                      disabled={isLoading}
                      className={`px-2 py-0.5 rounded transition-colors ${
                        policyMode === 'file' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600'
                      }`}
                    >
                      File
                    </button>
                    <button
                      type="button"
                      onClick={() => setPolicyMode('text')}
                      disabled={isLoading}
                      className={`px-2 py-0.5 rounded transition-colors ${
                        policyMode === 'text' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600'
                      }`}
                    >
                      Text
                    </button>
                  </div>
                )}
              </div>

              {hasPolicy && (
                <div className="space-y-3 bg-indigo-50/40 p-4 rounded-xl border border-indigo-100">
                  <p className="text-[11px] text-indigo-900">
                    The AI will cross-reference contract clauses against your policy directives (such as max notice periods, required SLA standards, and breach notification windows) and flag discrepancies.
                  </p>
                  <div>
                    <input
                      type="text"
                      placeholder="Policy Title (e.g. Corporate Vendor Security Standard v3.2)"
                      value={policyTitle}
                      onChange={(e) => setPolicyTitle(e.target.value)}
                      disabled={isLoading}
                      className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  {policyMode === 'file' ? (
                    <div>
                      <input
                        type="file"
                        id="policy-file"
                        accept=".pdf,.docx,.txt"
                        disabled={isLoading}
                        onChange={(e) => setPolicyFile(e.target.files[0] || null)}
                        className="w-full text-xs text-slate-500 file:mr-3 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-medium file:bg-indigo-100 file:text-indigo-700 hover:file:bg-indigo-200"
                      />
                    </div>
                  ) : (
                    <div>
                      <textarea
                        rows={3}
                        placeholder="Paste organizational policy directives or mandatory clauses..."
                        value={policyText}
                        onChange={(e) => setPolicyText(e.target.value)}
                        disabled={isLoading}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Loading Animation */}
          {isLoading && (
            <div className="bg-sky-50 border border-sky-200 rounded-xl p-4 flex items-center space-x-3">
              <Loader2 className="w-5 h-5 text-sky-600 animate-spin flex-shrink-0" />
              <div className="flex-1">
                <p className="text-xs font-semibold text-sky-900">Processing Contract Intelligence...</p>
                <p className="text-[11px] text-sky-700">{progressStage}</p>
              </div>
              <Sparkles className="w-4 h-4 text-sky-500 animate-pulse" />
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-2">
            <div className="text-[11px] text-slate-400">
              Information management tool. Not legal advice.
            </div>
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading}
                className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="px-5 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-700 text-white rounded-lg shadow-sm shadow-sky-600/30 flex items-center space-x-1.5 transition-all disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{isNewVersion ? 'Upload & Compare Revision' : 'Analyze & Extract'}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}