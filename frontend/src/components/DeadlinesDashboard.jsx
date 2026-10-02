import React, { useState, useEffect } from 'react';
import {
  Bell,
  Clock,
  Calendar,
  AlertCircle,
  CheckCircle,
  Filter,
  Check,
  RotateCcw,
  ShieldCheck,
  ChevronRight,
  User,
} from 'lucide-react';
import { getContractReminders, toggleDismissReminder } from '../api/client';

export default function DeadlinesDashboard({ contractId, versionId = null, onSelectContract }) {
  const [reminders, setReminders] = useState([]);
  const [urgencyCounts, setUrgencyCounts] = useState({
    overdue: 0,
    next_7_days: 0,
    next_30_days: 0,
    next_90_days: 0,
    total_active: 0,
  });
  const [selectedUrgency, setSelectedUrgency] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [includeDismissed, setIncludeDismissed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReminders = async () => {
    if (!contractId) return;
    try {
      setLoading(true);
      setError(null);
      const params = {
        include_dismissed: includeDismissed,
      };
      if (versionId) params.version_id = versionId;
      if (selectedUrgency !== 'ALL') params.urgency = selectedUrgency;
      if (selectedCategory !== 'ALL') params.category = selectedCategory;

      const data = await getContractReminders(contractId, params);
      setReminders(data.reminders || []);
      setUrgencyCounts(data.urgency_counts || {});
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to load reminders');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReminders();
  }, [contractId, versionId, selectedUrgency, selectedCategory, includeDismissed]);

  const handleToggleDismiss = async (reminderId) => {
    try {
      await toggleDismissReminder(reminderId);
      fetchReminders();
    } catch (err) {
      console.error('Error toggling reminder dismissal', err);
    }
  };

  const getUrgencyBadge = (urgency) => {
    switch (urgency) {
      case 'OVERDUE':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
            OVERDUE
          </span>
        );
      case 'HIGH':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
            HIGH (≤ 7 DAYS)
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">
            MEDIUM (≤ 30 DAYS)
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
            LOW (&gt; 30 DAYS)
          </span>
        );
    }
  };

  const getCategoryLabel = (cat) => {
    switch (cat) {
      case 'RENEWAL_NOTICE':
        return 'Renewal Notice Cutoff';
      case 'CONTRACT_EXPIRY':
        return 'Contract Expiration';
      case 'OBLIGATION_DEADLINE':
        return 'Obligation Deadline';
      case 'RECURRING_OBLIGATION':
        return 'Recurring Obligation';
      default:
        return cat;
    }
  };

  return (
    <div className="space-y-6">
      {/* Deterministic Rule Engine Callout */}
      <div className="bg-sky-50 border border-sky-200 rounded-xl p-3.5 text-xs text-sky-900 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-sky-600 flex-shrink-0" />
          <span>
            <strong>Deterministic Code Engine:</strong> All deadline milestones and advance reminder dates are computed using Python date arithmetic (zero AI calculations) to guarantee 100% mathematical accuracy.
          </span>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div
          onClick={() => setSelectedUrgency('OVERDUE')}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedUrgency === 'OVERDUE'
              ? 'bg-rose-50 border-rose-300 ring-2 ring-rose-400'
              : 'bg-white border-slate-200 hover:border-rose-200'
          }`}
        >
          <span className="text-[11px] font-semibold text-rose-700 uppercase tracking-wider block">
            Overdue
          </span>
          <span className="text-2xl font-bold text-rose-800 mt-1 block">
            {urgencyCounts.overdue || 0}
          </span>
          <span className="text-[10px] text-rose-600">Past contractual deadline</span>
        </div>

        <div
          onClick={() => setSelectedUrgency('HIGH')}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedUrgency === 'HIGH'
              ? 'bg-amber-50 border-amber-300 ring-2 ring-amber-400'
              : 'bg-white border-slate-200 hover:border-amber-200'
          }`}
        >
          <span className="text-[11px] font-semibold text-amber-700 uppercase tracking-wider block">
            Next 7 Days
          </span>
          <span className="text-2xl font-bold text-amber-800 mt-1 block">
            {urgencyCounts.next_7_days || 0}
          </span>
          <span className="text-[10px] text-amber-600">High urgency upcoming</span>
        </div>

        <div
          onClick={() => setSelectedUrgency('MEDIUM')}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedUrgency === 'MEDIUM'
              ? 'bg-sky-50 border-sky-300 ring-2 ring-sky-400'
              : 'bg-white border-slate-200 hover:border-sky-200'
          }`}
        >
          <span className="text-[11px] font-semibold text-sky-700 uppercase tracking-wider block">
            Next 30 Days
          </span>
          <span className="text-2xl font-bold text-sky-800 mt-1 block">
            {urgencyCounts.next_30_days || 0}
          </span>
          <span className="text-[10px] text-sky-600">Approaching milestones</span>
        </div>

        <div
          onClick={() => setSelectedUrgency('ALL')}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedUrgency === 'ALL'
              ? 'bg-slate-100 border-slate-300 ring-2 ring-slate-400'
              : 'bg-white border-slate-200 hover:border-slate-300'
          }`}
        >
          <span className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider block">
            Total Active
          </span>
          <span className="text-2xl font-bold text-slate-900 mt-1 block">
            {urgencyCounts.total_active || 0}
          </span>
          <span className="text-[10px] text-slate-500">Scheduled reminders</span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center space-x-1.5 text-slate-500 font-medium mr-2">
            <Filter className="w-3.5 h-3.5" />
            <span>Filter:</span>
          </div>

          <select
            value={selectedUrgency}
            onChange={(e) => setSelectedUrgency(e.target.value)}
            className="px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-sky-500"
          >
            <option value="ALL">All Urgencies</option>
            <option value="OVERDUE">Overdue Only</option>
            <option value="HIGH">High (Next 7 Days)</option>
            <option value="MEDIUM">Medium (Next 30 Days)</option>
            <option value="LOW">Low (&gt; 30 Days)</option>
          </select>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-sky-500"
          >
            <option value="ALL">All Categories</option>
            <option value="RENEWAL_NOTICE">Renewal Notice Cutoffs</option>
            <option value="CONTRACT_EXPIRY">Contract Expirations</option>
            <option value="OBLIGATION_DEADLINE">Obligation Deadlines</option>
            <option value="RECURRING_OBLIGATION">Recurring Obligations</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label className="flex items-center space-x-1.5 cursor-pointer text-slate-600">
            <input
              type="checkbox"
              checked={includeDismissed}
              onChange={(e) => setIncludeDismissed(e.target.checked)}
              className="w-3.5 h-3.5 text-sky-600 rounded border-slate-300 focus:ring-sky-500"
            />
            <span>Show Completed / Dismissed</span>
          </label>
        </div>
      </div>

      {/* Reminders List */}
      {loading ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200 text-center text-xs text-slate-500">
          Loading calculated reminders...
        </div>
      ) : error ? (
        <div className="bg-rose-50 p-4 rounded-xl border border-rose-200 text-xs text-rose-800">
          {error}
        </div>
      ) : reminders.length === 0 ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200 text-center">
          <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3">
            <Bell className="w-6 h-6" />
          </div>
          <h4 className="text-sm font-semibold text-slate-700">No Reminders Matching Filter</h4>
          <p className="text-xs text-slate-400 mt-1">
            Try adjusting your urgency or category filters above.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {reminders.map((r) => (
            <div
              key={r.id}
              className={`p-4 rounded-xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                r.is_dismissed
                  ? 'bg-slate-50 border-slate-200 opacity-60'
                  : r.urgency === 'OVERDUE'
                  ? 'bg-rose-50/50 border-rose-300'
                  : r.urgency === 'HIGH'
                  ? 'bg-amber-50/40 border-amber-300'
                  : 'bg-white border-slate-200 hover:shadow-sm'
              }`}
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold text-slate-900">{r.title}</span>
                  {getUrgencyBadge(r.urgency)}
                  <span className="bg-slate-100 text-slate-600 text-[10px] font-medium px-2 py-0.5 rounded">
                    {getCategoryLabel(r.category)}
                  </span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed">{r.description}</p>

                <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-500 pt-1">
                  <span className="inline-flex items-center space-x-1 font-mono">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>Target Date: <strong>{r.target_date}</strong></span>
                  </span>
                  <span className="inline-flex items-center space-x-1 font-mono text-sky-700 bg-sky-50 px-1.5 py-0.5 rounded">
                    <Bell className="w-3.5 h-3.5 text-sky-600" />
                    <span>Calculated Reminder Date: <strong>{r.reminder_date}</strong></span>
                  </span>
                  {r.responsible_party && (
                    <span className="inline-flex items-center space-x-1">
                      <User className="w-3.5 h-3.5 text-slate-400" />
                      <span>{r.responsible_party}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Action */}
              <div className="flex-shrink-0 self-end sm:self-center">
                <button
                  onClick={() => handleToggleDismiss(r.id)}
                  title={r.is_dismissed ? 'Restore reminder' : 'Mark as completed/dismissed'}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1.5 transition-colors ${
                    r.is_dismissed
                      ? 'bg-slate-200 text-slate-700 border-slate-300 hover:bg-slate-300'
                      : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  {r.is_dismissed ? (
                    <>
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>Restore</span>
                    </>
                  ) : (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Mark Done</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
