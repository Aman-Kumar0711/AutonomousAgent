'use client';

import { motion } from 'framer-motion';
import { Check, X } from 'lucide-react';

interface ChecklistItemProps {
  label: string;
  passed: boolean;
  description?: string;
  index: number;
}

export default function ChecklistItem({ label, passed, description, index }: ChecklistItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.3, delay: index * 0.06 }}
      className={`flex items-center gap-4 p-4 rounded-xl border transition-colors ${
        passed
          ? 'bg-green-50/50 border-green-200'
          : 'bg-red-50/50 border-red-200'
      }`}
    >
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
          passed ? 'bg-green-500' : 'bg-red-500'
        }`}
      >
        {passed ? (
          <Check className="w-4 h-4 text-white" />
        ) : (
          <X className="w-4 h-4 text-white" />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <p className={`font-medium text-sm ${passed ? 'text-green-800' : 'text-red-800'}`}>
          {label}
        </p>
        {description && (
          <p className={`text-xs mt-0.5 ${passed ? 'text-green-600' : 'text-red-600'}`}>
            {description}
          </p>
        )}
      </div>

      <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
        passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
      }`}>
        {passed ? 'PASS' : 'FAIL'}
      </span>
    </motion.div>
  );
}
