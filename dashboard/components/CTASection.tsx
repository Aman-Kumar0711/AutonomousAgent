'use client';

import { motion } from 'framer-motion';
import { ArrowRight, CheckCircle2, Shield, Clock, TrendingUp } from 'lucide-react';

interface CTASectionProps {
  businessName?: string;
}

const benefits = [
  { icon: TrendingUp, text: 'Custom solution tailored to your specific needs' },
  { icon: Clock, text: 'Most fixes implemented within a few days' },
  { icon: Shield, text: 'Full website security & performance audit included' },
  { icon: CheckCircle2, text: 'No commitment — just a conversation' },
];

export default function CTASection({ businessName }: CTASectionProps) {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900" />
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDJ2LTJoMzR6bTAtMzBWMEgydjRoMzR6TTIgMTh2MmgzNHYtMkgyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />

      <div className="relative max-w-4xl mx-auto px-6 py-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Want These Issues Fixed{businessName ? `, ${businessName}` : ''}?
          </h2>
          <p className="text-lg text-primary-100 mb-10 max-w-2xl mx-auto">
            I build custom solutions based on exactly what your business needs.
            No cookie-cutter packages — just the stuff that&apos;ll actually bring you more customers.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid sm:grid-cols-2 gap-4 mb-10 max-w-xl mx-auto"
        >
          {benefits.map((benefit, i) => (
            <div key={i} className="flex items-center gap-3 text-left text-white/90">
              <benefit.icon className="w-5 h-5 text-primary-300 shrink-0" />
              <span className="text-sm">{benefit.text}</span>
            </div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <a
            href="mailto:amanchahar175@gmail.com?subject=Interested in fixing my website"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-primary-700 font-semibold rounded-xl hover:bg-primary-50 transition-colors shadow-lg shadow-primary-900/20"
          >
            Let&apos;s Talk — It&apos;s Free
            <ArrowRight className="w-5 h-5" />
          </a>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-10 text-sm text-primary-200"
        >
          Built by <span className="font-semibold text-white">Aman Kumar</span> — Web Developer & Digital Solutions
        </motion.p>
      </div>
    </section>
  );
}
