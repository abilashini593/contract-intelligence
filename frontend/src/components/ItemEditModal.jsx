import React, { useState } from 'react';
import { X, Save, AlertCircle } from 'lucide-react';

export default function ItemEditModal({ isOpen, onClose, onSave, item, itemType }) {
  if (!isOpen || !item) return null;

  const [formData, setFormData] = useState({
    name: item.name || '',
    role: item.role || '',
    title: item.title || item.term_title || '',
    summary: item.summary || item.description || '',
    responsible_party: item.responsible_party || '',
    effective_date: item.effective_date || '',
    expiry_date: item.expiry_date || '',
    due_date: item.due_date || '',
    notice_period_days: item.notice_period_days !== null && item.notice_period_days !== undefined ? item.notice_period_days : '',
    certainty: item.certainty || 'CONFIRMED',
    user_correction_notes: item.user_correction_notes || '',
    user_answer: item.clarification_questions?.[0]?.user_answer || '',
  });

  const handleChange = (field, val) => {
    setFormData((prev) => ({ ...prev, [field]: val }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      ...formData,
      status: 'EDITED',
    };
    if (formData.notice_period_days !== '') {
      payload.notice_period_days = parseInt(formData.notice_period_days, 10) || null;
    }
    onSave(item.id, itemType, payload);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full border border-slate-200 overflow-hidden my-8">
        <div className="bg-slate-50 px-5 py-3.5 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-800">
            Edit Extracted {itemType.toUpperCase()}
          </h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
          {itemType === 'party' && (
            <>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Party Legal Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-sky-500"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Role / Side</label>
                  <input
                    type="text"
                    value={formData.role}
                    onChange={(e) => handleChange('role', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-sky-500"
                    required
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Effective Date (YYYY-MM-DD)</label>
                  <input
                    type="text"
                    value={formData.effective_date}
                    onChange={(e) => handleChange('effective_date', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-sky-500"
                  />
                </div>
              </div>
            </>
          )}

          {(itemType === 'clause' || itemType === 'obligation') && (
            <>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-sky-500"
                  required
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  {itemType === 'clause' ? 'Clause Summary' : 'Obligation Duty Description'}
                </label>
                <textarea
                  rows={3}
                  value={formData.summary}
                  onChange={(e) => handleChange('summary', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-sky-500"
                  required
                />
              </div>
            </>
          )}

          {itemType === 'clause' && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Expiry Date (YYYY-MM-DD)</label>
                <input
                  type="text"
                  placeholder="2028-02-29"
                  value={formData.expiry_date}
                  onChange={(e) => handleChange('expiry_date', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-sky-500"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Notice Period (Days)</label>
                <input
                  type="number"
                  placeholder="e.g. 30, 60"
                  value={formData.notice_period_days}
                  onChange={(e) => handleChange('notice_period_days', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-sky-500"
                />
              </div>
            </div>
          )}

          {itemType === 'obligation' && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Responsible Party</label>
                <input
                  type="text"
                  value={formData.responsible_party}
                  onChange={(e) => handleChange('responsible_party', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-sky-500"
                  required
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Due Date (YYYY-MM-DD)</label>
                <input
                  type="text"
                  placeholder="2026-09-30"
                  value={formData.due_date}
                  onChange={(e) => handleChange('due_date', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-sky-500"
                />
              </div>
            </div>
          )}

          {itemType === 'unclear_term' && (
            <>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Issue Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-sky-500"
                  required
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Ambiguity Description</label>
                <textarea
                  rows={2}
                  value={formData.summary}
                  onChange={(e) => handleChange('summary', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-sky-500"
                />
              </div>
              {item.clarification_questions?.length > 0 && (
                <div className="bg-sky-50 p-3 rounded-xl border border-sky-200">
                  <span className="font-semibold text-sky-900 block mb-1">
                    Clarification Question: {item.clarification_questions[0].question}
                  </span>
                  <label className="block text-slate-600 mb-1">Your Clarification Answer:</label>
                  <input
                    type="text"
                    placeholder="Enter confirmed interpretation..."
                    value={formData.user_answer}
                    onChange={(e) => handleChange('user_answer', e.target.value)}
                    className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-sky-500"
                  />
                </div>
              )}
            </>
          )}

          {/* Certainty & User Notes */}
          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-200">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Certainty Level</label>
              <select
                value={formData.certainty}
                onChange={(e) => handleChange('certainty', e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-sky-500"
              >
                <option value="CONFIRMED">CONFIRMED (Factually stated)</option>
                <option value="UNCERTAIN">UNCERTAIN (Requires review)</option>
              </select>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Correction Notes</label>
              <input
                type="text"
                placeholder="Reason for correction..."
                value={formData.user_correction_notes}
                onChange={(e) => handleChange('user_correction_notes', e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-sky-500"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-700 text-white rounded-lg shadow-sm flex items-center space-x-1.5"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Save & Update Reminders</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
