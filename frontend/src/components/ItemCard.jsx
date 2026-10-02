import React, { useState } from 'react';
import { Check, X, Edit3, BookOpen, AlertTriangle, ShieldCheck, AlertCircle, Calendar, User, Clock } from 'lucide-react';
import SourceCitationModal from './SourceCitationModal';
import ItemEditModal from './ItemEditModal';

export default function ItemCard({
  item,
  itemType,
  onApprove,
  onReject,
  onEditSave,
}) {
  const [showCitation, setShowCitation] = useState(false);
  const [showEdit, setShowEdit] = useState(false);

  // Status Styling
  const getStatusBadge = (status, isStale) => {
    if (isStale) {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300 animate-pulse">
          <AlertTriangle className="w-3 h-3 text-amber-700" />
          <span>STALE (RE-REVIEW NEEDED)</span>
        </span>
      );
    }
    switch (status) {
      case 'APPROVED':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <Check className="w-3 h-3 text-emerald-600" />
            <span>APPROVED</span>
          </span>
        );
      case 'REJECTED':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200">
            <X className="w-3 h-3 text-rose-600" />
            <span>REJECTED</span>
          </span>
        );
      case 'EDITED':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
            <Edit3 className="w-3 h-3 text-blue-600" />
            <span>USER EDITED</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
            <Clock className="w-3 h-3 text-amber-600" />
            <span>PENDING REVIEW</span>
          </span>
        );
    }
  };

  // Certainty Badge
  const getCertaintyBadge = (certainty, confidence, rationale) => {
    if (certainty === 'CONFIRMED') {
      return (
        <div className="inline-flex items-center space-x-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Confirmed (100%)</span>
        </div>
      );
    }
    return (
      <div
        title={rationale || 'Uncertain or ambiguous interpretation'}
        className="inline-flex items-center space-x-1 text-[11px] font-medium text-amber-800 bg-amber-50 px-2 py-0.5 rounded-md border border-amber-200 cursor-help"
      >
        <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
        <span>Uncertain ({Math.round((confidence || 0.5) * 100)}%)</span>
      </div>
    );
  };

  const title = item.title || item.name || item.term_title;
  const desc = item.summary || item.description || (item.role ? `Role: ${item.role}` : '');

  return (
    <>
      <div className={`bg-white rounded-xl border p-5 shadow-sm transition-all hover:shadow-md ${
        item.is_stale
          ? 'border-amber-400 bg-amber-50/20 ring-1 ring-amber-300'
          : item.status === 'APPROVED' || item.status === 'EDITED'
          ? 'border-emerald-200/80'
          : item.status === 'REJECTED'
          ? 'border-slate-200 opacity-60 bg-slate-50'
          : 'border-slate-200'
      }`}>
        {/* Card Header */}
        <div className="flex flex-wrap items-start justify-between gap-2 mb-3">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <h4 className="text-sm font-bold text-slate-900">{title}</h4>
              {getStatusBadge(item.status, item.is_stale)}
            </div>
            <div className="flex items-center space-x-2 pt-0.5">
              {getCertaintyBadge(item.certainty, item.confidence_score, item.uncertainty_rationale)}
              
              {/* Citation button */}
              <button
                type="button"
                onClick={() => setShowCitation(true)}
                className="inline-flex items-center space-x-1 text-[11px] text-sky-700 hover:text-sky-900 bg-sky-50 hover:bg-sky-100 px-2 py-0.5 rounded-md border border-sky-200 transition-colors"
              >
                <BookOpen className="w-3 h-3 text-sky-600" />
                <span>
                  {item.source_section || (item.source_page ? `Page ${item.source_page}` : 'Cite Text')}
                </span>
              </button>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => onApprove(item.id, itemType)}
              title="Approve extracted item"
              className={`p-1.5 rounded-lg text-xs font-medium transition-colors ${
                item.status === 'APPROVED'
                  ? 'bg-emerald-600 text-white'
                  : 'text-emerald-700 hover:bg-emerald-50 bg-white border border-emerald-200'
              }`}
            >
              <Check className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onReject(item.id, itemType)}
              title="Reject extracted item"
              className={`p-1.5 rounded-lg text-xs font-medium transition-colors ${
                item.status === 'REJECTED'
                  ? 'bg-rose-600 text-white'
                  : 'text-rose-700 hover:bg-rose-50 bg-white border border-rose-200'
              }`}
            >
              <X className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setShowEdit(true)}
              title="Edit extracted item"
              className="p-1.5 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-100 bg-white border border-slate-200 transition-colors"
            >
              <Edit3 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Stale Warning Callout */}
        {item.is_stale && (
          <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="font-semibold">Re-Review Required:</strong>{' '}
              {item.stale_reason || 'This item was approved in a previous version but modified in the new upload.'}
            </div>
          </div>
        )}

        {/* Content details */}
        <p className="text-xs text-slate-700 leading-relaxed mb-3">{desc}</p>

        {/* Specific Metadata Pills */}
        <div className="flex flex-wrap gap-2 text-[11px] text-slate-600">
          {item.role && (
            <span className="inline-flex items-center space-x-1 bg-slate-100 px-2 py-0.5 rounded-md">
              <User className="w-3 h-3 text-slate-500" />
              <span>Role: <strong>{item.role}</strong></span>
            </span>
          )}
          {item.effective_date && (
            <span className="inline-flex items-center space-x-1 bg-slate-100 px-2 py-0.5 rounded-md">
              <Calendar className="w-3 h-3 text-slate-500" />
              <span>Effective: <strong>{item.effective_date}</strong></span>
            </span>
          )}
          {item.expiry_date && (
            <span className="inline-flex items-center space-x-1 bg-slate-100 px-2 py-0.5 rounded-md">
              <Calendar className="w-3 h-3 text-slate-500" />
              <span>Expires: <strong>{item.expiry_date}</strong></span>
            </span>
          )}
          {item.notice_period_days !== null && item.notice_period_days !== undefined && (
            <span className="inline-flex items-center space-x-1 bg-slate-100 px-2 py-0.5 rounded-md">
              <Clock className="w-3 h-3 text-slate-500" />
              <span>Notice: <strong>{item.notice_period_days} days</strong></span>
            </span>
          )}
          {item.due_date && (
            <span className="inline-flex items-center space-x-1 bg-sky-50 text-sky-800 border border-sky-200 px-2 py-0.5 rounded-md">
              <Calendar className="w-3 h-3 text-sky-600" />
              <span>Deadline: <strong>{item.due_date}</strong></span>
            </span>
          )}
          {item.responsible_party && (
            <span className="inline-flex items-center space-x-1 bg-slate-100 px-2 py-0.5 rounded-md">
              <User className="w-3 h-3 text-slate-500" />
              <span>Assigned: <strong>{item.responsible_party}</strong></span>
            </span>
          )}
        </div>

        {/* Clarification Questions for Unclear Terms */}
        {item.clarification_questions?.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-100 space-y-2">
            <span className="text-[11px] font-bold text-slate-700 block">
              Clarification Needed:
            </span>
            {item.clarification_questions.map((q, idx) => (
              <div key={idx} className="bg-sky-50/70 p-2.5 rounded-lg border border-sky-100 text-xs">
                <p className="text-sky-950 font-medium">{q.question}</p>
                {q.user_answer ? (
                  <p className="mt-1 text-emerald-800 font-semibold text-[11px]">
                    Answered: "{q.user_answer}"
                  </p>
                ) : (
                  <button
                    onClick={() => setShowEdit(true)}
                    className="mt-1 text-[11px] text-sky-700 hover:text-sky-900 underline font-medium"
                  >
                    Provide Clarification Answer
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        {/* User Correction Notes if any */}
        {item.user_correction_notes && (
          <div className="mt-2 text-[11px] text-slate-500 italic">
            Note: "{item.user_correction_notes}"
          </div>
        )}
      </div>

      {/* Modals */}
      <SourceCitationModal
        isOpen={showCitation}
        onClose={() => setShowCitation(false)}
        item={item}
        itemType={itemType}
      />
      <ItemEditModal
        isOpen={showEdit}
        onClose={() => setShowEdit(false)}
        onSave={onEditSave}
        item={item}
        itemType={itemType}
      />
    </>
  );
}
