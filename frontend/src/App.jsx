import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ContractsList from './components/ContractsList';
import ContractDetailView from './components/ContractDetailView';
import DeadlinesDashboard from './components/DeadlinesDashboard';
import UploadModal from './components/UploadModal';
import { listContracts, deleteContract } from './api/client';
import { ShieldAlert, BookOpen, ExternalLink } from 'lucide-react';

export default function App() {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContractId, setSelectedContractId] = useState(null);
  const [activeNav, setActiveNav] = useState('contracts'); // 'contracts' | 'deadlines'
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploadVersionTarget, setUploadVersionTarget] = useState(null);

  const fetchContracts = async () => {
    try {
      setLoading(true);
      const data = await listContracts();
      setContracts(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load contracts:', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContracts();
  }, []);

  const handleOpenUpload = () => {
    setUploadVersionTarget(null);
    setUploadModalOpen(true);
  };

  const handleOpenUploadVersion = (contract) => {
    setUploadVersionTarget(contract);
    setUploadModalOpen(true);
  };

  const handleUploadSuccess = (result) => {
    fetchContracts();
    if (result?.id) {
      setSelectedContractId(result.id);
      setActiveNav('contracts');
    }
  };

  const handleDelete = async (contractId) => {
    if (!window.confirm('Are you sure you want to delete this contract and all its versions?')) {
      return;
    }
    try {
      await deleteContract(contractId);
      if (selectedContractId === contractId) {
        setSelectedContractId(null);
      }
      fetchContracts();
    } catch (err) {
      alert(`Deletion failed: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Navigation & Header */}
      <Navbar
        onUploadClick={handleOpenUpload}
        onContractsClick={() => {
          setSelectedContractId(null);
          setActiveNav('contracts');
        }}
        onDeadlinesClick={() => {
          setActiveNav('deadlines');
        }}
        activeTab={activeNav}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {activeNav === 'deadlines' ? (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
            <div>
              <h1 className="text-xl font-bold text-slate-900">
                All Upcoming Deadlines & Renewal Notices
              </h1>
              <p className="text-xs text-slate-500">
                Calculated using deterministic date arithmetic for active contracts.
              </p>
            </div>
            {contracts.length > 0 ? (
              <DeadlinesDashboard
                contractId={selectedContractId || contracts[0]?.id}
                onSelectContract={(id) => setSelectedContractId(id)}
              />
            ) : (
              <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center text-xs text-slate-500">
                No contracts registered. Upload a contract to view deterministic deadlines.
              </div>
            )}
          </div>
        ) : selectedContractId ? (
          <ContractDetailView
            contractId={selectedContractId}
            onBack={() => setSelectedContractId(null)}
            onUploadNewVersion={handleOpenUploadVersion}
            onDeleteContract={handleDelete}
          />
        ) : (
          <ContractsList
            contracts={contracts}
            loading={loading}
            onSelectContract={(id) => setSelectedContractId(id)}
            onUploadClick={handleOpenUpload}
            onDeleteContract={handleDelete}
          />
        )}
      </main>

      {/* Upload & Version Modal */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => {
          setUploadModalOpen(false);
          setUploadVersionTarget(null);
        }}
        onSuccess={handleUploadSuccess}
        existingContract={uploadVersionTarget}
      />

      {/* Persistent Legal Notice & Compliance Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 px-4 sm:px-6 lg:px-8 no-print mt-12 text-slate-500 text-xs">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2 text-slate-600">
            <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <span className="text-[11px] leading-relaxed">
              <strong>Administrative Information-Management Tool:</strong> Not legal advice. Designed for obligation tracking, clause cataloging, and deterministic deadline calculation.
            </span>
          </div>
          <div className="flex items-center space-x-4 text-[11px] text-slate-400">
            <span>Powered by Gemini API & PostgreSQL</span>
            <span>•</span>
            <span>Deterministic Rule Engine</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
