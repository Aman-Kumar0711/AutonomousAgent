'use client';

import { useEffect, useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  icon: LucideIcon;
  label: string;
  value: number;
  suffix?: string;
  prefix?: string;
  decimals?: number;
  trend?: number;
  color?: string;
  delay?: number;
}

export default function StatsCard({
  icon: Icon,
  label,
  value,
  suffix = '',
  prefix = '',
  decimals = 0,
  trend,
  color = 'primary',
  delay = 0,
}: StatsCardProps) {
  const [displayValue, setDisplayValue] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });

  const colorMap: Record<string, { bg: string; icon: string; text: string }> = {
    primary: { bg: 'bg-primary-50', icon: 'text-primary-600', text: 'text-primary-600' },
    green: { bg: 'bg-green-50', icon: 'text-green-600', text: 'text-green-600' },
    yellow: { bg: 'bg-yellow-50', icon: 'text-yellow-600', text: 'text-yellow-600' },
    red: { bg: 'bg-red-50', icon: 'text-red-600', text: 'text-red-600' },
    purple: { bg: 'bg-purple-50', icon: 'text-purple-600', text: 'text-purple-600' },
  };

  const colors = colorMap[color] || colorMap.primary;

  useEffect(() => {
    if (!isInView) return;
    const duration = 1200;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(Number((eased * value).toFixed(decimals)));
      if (progress < 1) requestAnimationFrame(animate);
    };

    const timer = setTimeout(() => requestAnimationFrame(animate), delay * 100);
    return () => clearTimeout(timer);
  }, [isInView, value, decimals, delay]);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: delay * 0.1 }}
      className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg transition-all duration-300"
    >
      <div className="flex items-start justify-between">
        <div className={`p-3 rounded-xl ${colors.bg}`}>
          <Icon className={`w-6 h-6 ${colors.icon}`} />
        </div>
        {trend !== undefined && (
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${
            trend >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {trend >= 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>

      <div className="mt-4">
        <p className="text-3xl font-bold text-slate-900">
          {prefix}{displayValue.toLocaleString()}{suffix}
        </p>
        <p className="text-sm text-slate-500 mt-1">{label}</p>
      </div>
    </motion.div>
  );
}
