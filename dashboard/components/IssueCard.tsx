'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { Issue } from '@/lib/types';
import { getImpactColor, getCategoryColor } from '@/lib/data';

interface IssueCardProps {
  issue: Issue;
  index: number;
}

export default function IssueCard({ issue, index }: IssueCardProps) {
  const [isOpen, setIsOpen] = useState(false);

  const ImpactIcon = issue.impact === 'high' ? AlertTriangle : issue.impact === 'medium' ? AlertCircle : Info;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-30px' }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
      className="border border-slate-200 rounded-xl bg-white overflow-hidden hover:shadow-md transition-shadow"
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-4 p-5 text-left"
      >
        <div className={`p-2 rounded-lg ${issue.impact === 'high' ? 'bg-red-50' : issue.impact === 'medium' ? 'bg-yellow-50' : 'bg-slate-50'}`}>
          <ImpactIcon className={`w-5 h-5 ${issue.impact === 'high' ? 'text-red-500' : issue.impact === 'medium' ? 'text-yellow-500' : 'text-slate-400'}`} />
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 text-base">{issue.issue}</h3>
          <div className="flex items-center gap-2 mt-1.5">
            <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full border ${getImpactColor(issue.impact)}`}>
              {issue.impact.charAt(0).toUpperCase() + issue.impact.slice(1)} Impact
            </span>
            <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${getCategoryColor(issue.category)}`}>
              {issue.category.charAt(0).toUpperCase() + issue.category.slice(1)}
            </span>
          </div>
        </div>

        <ChevronDown className={`w-5 h-5 text-slate-400 shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 space-y-4">
              <div className="h-px bg-slate-100" />

              <div>
                <p className="text-sm text-slate-600 leading-relaxed">{issue.description}</p>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <p className="text-sm font-semibold text-amber-800 mb-1">Business Impact</p>
                <p className="text-sm text-amber-700">{issue.business_impact}</p>
              </div>

              <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
                <p className="text-sm font-semibold text-primary-800 mb-1">Recommendation</p>
                <p className="text-sm text-primary-700">{issue.recommendation}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
