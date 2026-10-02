import React from 'react';
import { AlertTriangle, CheckCheck, RefreshCw } from 'lucide-react';

export default function StaleAlertBanner({ staleItems, onReapproveAll }) {
  if (!staleItems || staleItems.length === 0) return null;

  return (
    <div className="bg-amber-500/10 border border-amber-300 rounded-2xl p-4 sm:p-5 mb-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start space-x-3">
          <div className="p-2 bg-amber-100 rounded-xl text-amber-800 flex-shrink-0 mt-0.5">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-amber-950">
                {staleItems.length} Previously Approved {staleItems.length === 1 ? 'Item Has' : 'Items Have'} Changed in This Version
              </h3>
              <span className="bg-amber-200/80 text-amber-900 text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase">
                Stale Items Detected
              </span>
            </div>
            <p className="text-xs text-amber-900/80 mt-1 max-w-2xl leading-relaxed">
              When a new version is uploaded, items you approved in prior versions that have been altered (e.g., modified deadlines, notice periods, or language) are marked as <strong>STALE</strong>. Please inspect each item below, review the differences, and re-approve or adjust.
            </p>
          </div>
        </div>

        {onReapproveAll && (
          <div className="flex-shrink-0">
            <button
              onClick={onReapproveAll}
              className="w-full sm:w-auto px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold rounded-xl shadow-sm flex items-center justify-center space-x-1.5 transition-colors"
            >
              <CheckCheck className="w-4 h-4" />
              <span>Accept & Re-Approve All</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
