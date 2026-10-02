import React, { useState, useEffect } from 'react';
import {
  FileText,
  Printer,
  Copy,
  Download,
  Check,
  ShieldAlert,
  Calendar,
  User,
  Clock,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';
import { getReviewedSummary, getSummaryMarkdownUrl } from '../api/client';

export default function ContractSummaryView({ contractId, versionId = null }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const loadSummary = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getReviewedSummary(contractId, versionId);
        setSummary(data);
        setLoading(false);
      } catch (err) {
        setError(err.message || 'Failed to load reviewed contract summary.');
        setLoading(false);
      }
    };
    if (contractId) {
      loadSummary();
    }
  }, [contractId, versionId]);

  const handleCopyMarkdown = () => {
    if (!summary?.markdown_content) return;
    navigator.clipboard.writeText(summary.markdown_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center text-xs text-slate-500">
        Compiling reviewed contract summary...
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="bg-rose-50 p-6 rounded-2xl border border-rose-200 text-xs text-rose-800">
        {error || 'Unable to generate summary.'}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden p-6 sm:p-8 space-y-8">
      {/* Top Action Bar (hidden during print) */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-200 no-print">
        <div>
          <span className="text-xs font-bold text-sky-700 uppercase tracking-wider block">
            Executive Report
          </span>
          <h2 className="text-xl font-bold text-slate-900 mt-0.5">
            Reviewed Contract Summary: {summary.contract_title}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Version v{summary.version_number} • Generated on {new Date(summary.generated_at).toLocaleString()}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopyMarkdown}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg flex items-center space-x-1.5 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy Markdown'}</span>
          </button>

          <a
            href={getSummaryMarkdownUrl(contractId, versionId)}
            download
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg flex items-center space-x-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download .md</span>
          </a>

          <button
            onClick={handlePrint}
            className="px-4 py-1.5 bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold rounded-lg shadow-sm shadow-sky-600/30 flex items-center space-x-1.5 transition-colors"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Browser Print / Save PDF</span>
          </button>
        </div>
      </div>

      {/* Mandatory Legal & Information Management Disclaimer */}
      <div className="bg-amber-500/10 border-2 border-amber-300 rounded-xl p-4 text-xs text-amber-950 flex items-start space-x-3">
        <ShieldAlert className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h4 className="font-bold text-amber-900 uppercase tracking-wide text-[11px]">
            Administrative Information Management Disclaimer
          </h4>
          <p className="leading-relaxed text-amber-900/90">{summary.disclaimer}</p>
        </div>
      </div>

      {/* Review Metrics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl text-center">
          <span className="text-xs font-semibold text-emerald-800 uppercase block">Approved Items</span>
          <span className="text-2xl font-bold text-emerald-900 mt-1 block">
            {summary.total_approved_items}
          </span>
          <span className="text-[10px] text-emerald-700">Included in this summary</span>
        </div>

        <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl text-center">
          <span className="text-xs font-semibold text-amber-800 uppercase block">Pending Items</span>
          <span className="text-2xl font-bold text-amber-900 mt-1 block">
            {summary.total_pending_items}
          </span>
          <span className="text-[10px] text-amber-700">Awaiting user confirmation</span>
        </div>

        <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl text-center">
          <span className="text-xs font-semibold text-slate-700 uppercase block">Policy Checks</span>
          <span className="text-2xl font-bold text-slate-900 mt-1 block">
            {summary.policy_checks_count}
          </span>
          <span className="text-[10px] text-slate-500">Cross-referenced policies</span>
        </div>
      </div>

      {/* Key Dates & Parties */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
          1. Key Contract Milestone Dates & Approved Parties
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-1">
            <span className="text-slate-500 font-medium block">Effective Date</span>
            <span className="text-sm font-bold text-slate-900 font-mono">
              {summary.effective_date || 'Not formally confirmed'}
            </span>
          </div>

          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-1">
            <span className="text-slate-500 font-medium block">Contract Expiry Date</span>
            <span className="text-sm font-bold text-slate-900 font-mono">
              {summary.expiry_date || 'Indefinite / Not specified'}
            </span>
          </div>
        </div>

        {/* Parties */}
        <div>
          <span className="text-xs font-semibold text-slate-700 block mb-2">Approved Parties:</span>
          {summary.approved_parties?.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {summary.approved_parties.map((p) => (
                <div key={p.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{p.name}</span>
                    <span className="bg-sky-100 text-sky-800 text-[10px] font-semibold px-2 py-0.5 rounded">
                      {p.role}
                    </span>
                  </div>
                  {p.jurisdiction && (
                    <span className="text-slate-500 text-[11px] block mt-1">
                      Jurisdiction: {p.jurisdiction}
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No parties currently marked as approved.</p>
          )}
        </div>
      </div>

      {/* Approved Clauses */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
          2. Key Approved Clauses
        </h3>

        {summary.approved_clauses?.length > 0 ? (
          <div className="space-y-3">
            {summary.approved_clauses.map((c) => (
              <div key={c.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-bold text-slate-900">{c.title}</span>
                  <div className="flex items-center space-x-2">
                    <span className="bg-slate-200 text-slate-800 text-[10px] font-semibold px-2 py-0.5 rounded">
                      {c.clause_type}
                    </span>
                    {c.notice_period_days !== null && (
                      <span className="bg-blue-100 text-blue-800 text-[10px] font-semibold px-2 py-0.5 rounded font-mono">
                        {c.notice_period_days} Days Notice
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-slate-700 leading-relaxed">{c.summary}</p>
                {c.source_quote && (
                  <p className="text-[11px] text-slate-500 italic border-l-2 border-slate-300 pl-2">
                    "{c.source_quote}"
                  </p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No clauses currently marked as approved.</p>
        )}
      </div>

      {/* Approved Obligations */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
          3. Approved Key Obligations & Deadlines
        </h3>

        {summary.approved_obligations?.length > 0 ? (
          <div className="space-y-3">
            {summary.approved_obligations.map((o) => (
              <div key={o.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1.5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-bold text-slate-900">{o.title}</span>
                  <div className="flex items-center space-x-2">
                    <span className="bg-slate-200 text-slate-800 text-[10px] font-semibold px-2 py-0.5 rounded">
                      {o.responsible_party}
                    </span>
                    {o.due_date && (
                      <span className="bg-sky-100 text-sky-800 text-[10px] font-semibold px-2 py-0.5 rounded font-mono">
                        Due: {o.due_date}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-slate-700 leading-relaxed">{o.description}</p>
                {o.consequence_of_breach && (
                  <p className="text-[11px] text-rose-700 font-medium">
                    Breach Consequence: {o.consequence_of_breach}
                  </p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No obligations currently marked as approved.</p>
        )}
      </div>

      {/* Deterministic Reminders Schedule */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-200 pb-2">
          4. Deterministic Upcoming Reminders Schedule
        </h3>

        {summary.calculated_reminders?.length > 0 ? (
          <div className="space-y-2">
            {summary.calculated_reminders.map((r) => (
              <div
                key={r.id}
                className="p-3 bg-white rounded-xl border border-slate-200 flex flex-wrap items-center justify-between text-xs gap-2"
              >
                <div className="flex items-center space-x-3">
                  <span className="font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                    {r.reminder_date}
                  </span>
                  <span className="font-medium text-slate-800">{r.title}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-[11px] text-slate-500 font-mono">
                    Target: {r.target_date}
                  </span>
                  <span className="bg-sky-50 text-sky-700 border border-sky-200 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                    {r.days_before}d in advance
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No active scheduled reminders.</p>
        )}
      </div>

      {/* Open Clarification Questions */}
      {summary.flagged_unclear_terms?.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-slate-200">
          <h3 className="text-sm font-bold text-amber-900 uppercase tracking-wider">
            5. Flagged Ambiguities & Open Clarification Questions
          </h3>

          <div className="space-y-3">
            {summary.flagged_unclear_terms.map((u) => (
              <div key={u.id} className="p-4 bg-amber-50/50 rounded-xl border border-amber-200 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-amber-950">{u.term_title}</span>
                  <span className="bg-amber-100 text-amber-800 text-[10px] font-semibold px-2 py-0.5 rounded">
                    {u.issue_type}
                  </span>
                </div>
                <p className="text-amber-900 leading-relaxed">{u.description}</p>
                {u.clarification_questions?.length > 0 && (
                  <div className="space-y-1 pt-1 border-t border-amber-200/60">
                    {u.clarification_questions.map((q) => (
                      <p key={q.id} className="text-[11px] text-slate-700">
                        • <strong>Question:</strong> {q.question}{' '}
                        {q.user_answer ? (
                          <span className="text-emerald-700 font-semibold">[Answered: {q.user_answer}]</span>
                        ) : (
                          <span className="text-amber-700 italic">[Pending answer]</span>
                        )}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
