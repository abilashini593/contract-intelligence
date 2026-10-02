import React, { useState, useEffect } from 'react';
import {
  Users,
  FileText,
  CheckSquare,
  AlertTriangle,
  Bell,
  Sparkles,
  Upload,
  ArrowLeft,
  Calendar,
  History,
  BookOpen,
  Trash2,
  CheckCheck,
} from 'lucide-react';
import ItemCard from './ItemCard';
import StaleAlertBanner from './StaleAlertBanner';
import DeadlinesDashboard from './DeadlinesDashboard';
import ContractSummaryView from './ContractSummaryView';
import {
  getContract,
  getContractVersion,
  updateParty,
  updateClause,
  updateObligation,
  updateUnclearTerm,
  batchUpdateStatus,
} from '../api/client';

export default function ContractDetailView({
  contractId,
  onBack,
  onUploadNewVersion,
  onDeleteContract,
}) {
  const [contract, setContract] = useState(null);
  const [selectedVersionId, setSelectedVersionId] = useState(null);
  const [versionData, setVersionData] = useState(null);
  const [activeTab, setActiveTab] = useState('parties'); // 'parties' | 'clauses' | 'obligations' | 'unclear' | 'deadlines' | 'summary'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadContractDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getContract(contractId);
      setContract(data);
      
      const activeVer = data.current_version || (data.versions && data.versions[data.versions.length - 1]);
      if (activeVer) {
        setSelectedVersionId(activeVer.id);
        setVersionData(activeVer);
      }
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to load contract details');
      setLoading(false);
    }
  };

  useEffect(() => {
    if (contractId) {
      loadContractDetails();
    }
  }, [contractId]);

  const handleVersionChange = async (verId) => {
    setSelectedVersionId(verId);
    try {
      const v = await getContractVersion(contractId, verId);
      setVersionData(v);
    } catch (err) {
      console.error('Error fetching version data', err);
    }
  };

  // Item Action Handlers
  const handleApprove = async (itemId, itemType) => {
    try {
      if (itemType === 'party') await updateParty(itemId, { status: 'APPROVED' });
      else if (itemType === 'clause') await updateClause(itemId, { status: 'APPROVED' });
      else if (itemType === 'obligation') await updateObligation(itemId, { status: 'APPROVED' });
      else if (itemType === 'unclear_term') await updateUnclearTerm(itemId, { status: 'APPROVED' });

      // Refresh current version
      const v = await getContractVersion(contractId, selectedVersionId);
      setVersionData(v);
    } catch (err) {
      alert(`Approval failed: ${err.message}`);
    }
  };

  const handleReject = async (itemId, itemType) => {
    const reason = prompt('Optional rejection reason / note:');
    try {
      const payload = { status: 'REJECTED', user_correction_notes: reason || null };
      if (itemType === 'party') await updateParty(itemId, payload);
      else if (itemType === 'clause') await updateClause(itemId, payload);
      else if (itemType === 'obligation') await updateObligation(itemId, payload);
      else if (itemType === 'unclear_term') await updateUnclearTerm(itemId, payload);

      const v = await getContractVersion(contractId, selectedVersionId);
      setVersionData(v);
    } catch (err) {
      alert(`Rejection failed: ${err.message}`);
    }
  };

  const handleEditSave = async (itemId, itemType, payload) => {
    try {
      if (itemType === 'party') await updateParty(itemId, payload);
      else if (itemType === 'clause') await updateClause(itemId, payload);
      else if (itemType === 'obligation') await updateObligation(itemId, payload);
      else if (itemType === 'unclear_term') await updateUnclearTerm(itemId, payload);

      const v = await getContractVersion(contractId, selectedVersionId);
      setVersionData(v);
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const handleReapproveAllStale = async () => {
    if (!versionData) return;
    try {
      const staleParties = versionData.parties.filter((p) => p.is_stale).map((p) => p.id);
      const staleClauses = versionData.clauses.filter((c) => c.is_stale).map((c) => c.id);
      const staleObs = versionData.obligations.filter((o) => o.is_stale).map((o) => o.id);

      if (staleParties.length) await batchUpdateStatus('party', staleParties, 'APPROVED');
      if (staleClauses.length) await batchUpdateStatus('clause', staleClauses, 'APPROVED');
      if (staleObs.length) await batchUpdateStatus('obligation', staleObs, 'APPROVED');

      const v = await getContractVersion(contractId, selectedVersionId);
      setVersionData(v);
    } catch (err) {
      alert(`Batch re-approval failed: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-xs text-slate-500">
        Loading contract intelligence details...
      </div>
    );
  }

  if (error || !contract || !versionData) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <button onClick={onBack} className="flex items-center space-x-1 text-xs text-sky-600 mb-4">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Contracts</span>
        </button>
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl text-xs">
          {error || 'Contract not found.'}
        </div>
      </div>
    );
  }

  // Calculate stale items in current version
  const staleItems = [
    ...(versionData.parties?.filter((p) => p.is_stale) || []),
    ...(versionData.clauses?.filter((c) => c.is_stale) || []),
    ...(versionData.obligations?.filter((o) => o.is_stale) || []),
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to All Contracts</span>
      </button>

      {/* Contract Top Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900">{contract.title}</h1>
            <span className="bg-sky-100 text-sky-800 text-xs font-bold px-2.5 py-0.5 rounded-full">
              v{versionData.version_number}
            </span>
            {contract.policy_documents?.length > 0 && (
              <span className="bg-indigo-100 text-indigo-800 text-[11px] font-semibold px-2 py-0.5 rounded-full flex items-center space-x-1">
                <BookOpen className="w-3 h-3" />
                <span>Policy Cross-Referenced</span>
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500">
            Source File: <strong className="font-mono text-slate-700">{versionData.filename}</strong> ({versionData.file_type.toUpperCase()}) • Uploaded {new Date(versionData.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Version Switcher & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Version Switcher */}
          {contract.versions?.length > 1 && (
            <div className="flex items-center space-x-1.5 text-xs bg-slate-50 p-1 rounded-xl border border-slate-200">
              <History className="w-3.5 h-3.5 text-slate-500 ml-1.5" />
              <span className="text-slate-500 font-medium">Revision:</span>
              <select
                value={selectedVersionId}
                onChange={(e) => handleVersionChange(Number(e.target.value))}
                className="bg-white border border-slate-300 rounded-lg px-2 py-1 text-xs font-semibold text-slate-800 focus:ring-2 focus:ring-sky-500"
              >
                {contract.versions.map((v) => (
                  <option key={v.id} value={v.id}>
                    Version v{v.version_number} ({v.file_type.toUpperCase()})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Upload New Version */}
          <button
            onClick={() => onUploadNewVersion(contract)}
            className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl flex items-center space-x-1.5 transition-colors"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload v{contract.versions.length + 1}</span>
          </button>

          {/* Delete Contract */}
          <button
            onClick={() => onDeleteContract(contract.id)}
            title="Delete this contract"
            className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl border border-transparent hover:border-rose-200 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stale Items Alert Banner (Across version revisions) */}
      <StaleAlertBanner
        staleItems={staleItems}
        onReapproveAll={handleReapproveAllStale}
      />

      {/* Navigation Tabs */}
      <div className="border-b border-slate-200 flex flex-wrap gap-2 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('parties')}
          className={`pb-3 px-3 flex items-center space-x-1.5 border-b-2 transition-colors ${
            activeTab === 'parties'
              ? 'border-sky-600 text-sky-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Parties & Metadata ({versionData.parties?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('clauses')}
          className={`pb-3 px-3 flex items-center space-x-1.5 border-b-2 transition-colors ${
            activeTab === 'clauses'
              ? 'border-sky-600 text-sky-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Clauses ({versionData.clauses?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('obligations')}
          className={`pb-3 px-3 flex items-center space-x-1.5 border-b-2 transition-colors ${
            activeTab === 'obligations'
              ? 'border-sky-600 text-sky-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <CheckSquare className="w-4 h-4" />
          <span>Obligations & Deadlines ({versionData.obligations?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('unclear')}
          className={`pb-3 px-3 flex items-center space-x-1.5 border-b-2 transition-colors ${
            activeTab === 'unclear'
              ? 'border-sky-600 text-sky-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          <span>Ambiguities & Policy ({versionData.unclear_terms?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveTab('deadlines')}
          className={`pb-3 px-3 flex items-center space-x-1.5 border-b-2 transition-colors ${
            activeTab === 'deadlines'
              ? 'border-sky-600 text-sky-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Bell className="w-4 h-4" />
          <span>Deterministic Deadlines</span>
        </button>

        <button
          onClick={() => setActiveTab('summary')}
          className={`pb-3 px-3 flex items-center space-x-1.5 border-b-2 transition-colors ${
            activeTab === 'summary'
              ? 'border-sky-600 text-sky-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Sparkles className="w-4 h-4 text-sky-600" />
          <span>Reviewed Contract Summary</span>
        </button>
      </div>

      {/* Tab Panels */}
      <div>
        {/* Parties Tab */}
        {activeTab === 'parties' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Extracted legal parties, formation roles, jurisdiction, and effective dates.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {versionData.parties?.map((p) => (
                <ItemCard
                  key={p.id}
                  item={p}
                  itemType="party"
                  onApprove={handleApprove}
                  onReject={handleReject}
                  onEditSave={handleEditSave}
                />
              ))}
            </div>
          </div>
        )}

        {/* Clauses Tab */}
        {activeTab === 'clauses' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Expiry, renewal, notice periods, and termination provisions.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-4">
              {versionData.clauses?.map((c) => (
                <ItemCard
                  key={c.id}
                  item={c}
                  itemType="clause"
                  onApprove={handleApprove}
                  onReject={handleReject}
                  onEditSave={handleEditSave}
                />
              ))}
            </div>
          </div>
        )}

        {/* Obligations Tab */}
        {activeTab === 'obligations' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Actionable contractual duties, responsible parties, deadlines, and breach remedies.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {versionData.obligations?.map((o) => (
                <ItemCard
                  key={o.id}
                  item={o}
                  itemType="obligation"
                  onApprove={handleApprove}
                  onReject={handleReject}
                  onEditSave={handleEditSave}
                />
              ))}
            </div>
          </div>
        )}

        {/* Ambiguities & Policy Conflicts Tab */}
        {activeTab === 'unclear' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-500">
                Flagged ambiguous standards, undefined terms, and policy document discrepancies.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-4">
              {versionData.unclear_terms?.map((u) => (
                <ItemCard
                  key={u.id}
                  item={u}
                  itemType="unclear_term"
                  onApprove={handleApprove}
                  onReject={handleReject}
                  onEditSave={handleEditSave}
                />
              ))}
            </div>
          </div>
        )}

        {/* Deadlines & Reminders Tab */}
        {activeTab === 'deadlines' && (
          <DeadlinesDashboard
            contractId={contract.id}
            versionId={selectedVersionId}
          />
        )}

        {/* Reviewed Summary Tab */}
        {activeTab === 'summary' && (
          <ContractSummaryView
            contractId={contract.id}
            versionId={selectedVersionId}
          />
        )}
      </div>
    </div>
  );
}
