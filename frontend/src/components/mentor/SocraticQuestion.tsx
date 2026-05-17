import { HelpCircle, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export const SocraticQuestion = ({ question }: { question: string }) => {
  return (
    <motion.div 
      initial={{ scale: 0.95, opacity: 0 }}
      whileInView={{ scale: 1, opacity: 1 }}
      viewport={{ once: true }}
      className="relative overflow-hidden p-8 rounded-2xl my-10 border border-brand/20 bg-brand/5 shadow-glow group transition-all hover:bg-brand/[0.07]"
    >
      {/* Animated Background Accent */}
      <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-brand/10 blur-3xl rounded-full transition-all group-hover:bg-brand/20" />
      
      <div className="relative z-10 flex flex-col items-center text-center">
        <div className="bg-brand shadow-glow p-3 rounded-2xl mb-6">
          <HelpCircle className="w-6 h-6 text-white" />
        </div>
        
        <div className="flex items-center space-x-2 mb-3">
          <Sparkles className="w-3.5 h-3.5 text-brand animate-pulse" />
          <h4 className="text-[11px] font-black text-brand uppercase tracking-[0.3em]">Critical Thinking Challenge</h4>
          <Sparkles className="w-3.5 h-3.5 text-brand animate-pulse" />
        </div>
        
        <p className="text-text-primary font-bold text-xl md:text-2xl leading-snug tracking-tight max-w-2xl italic antialiased">
          "{question}"
        </p>
        
        <div className="mt-8 flex space-x-2">
          <div className="px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold text-text-secondary uppercase">
            Active Reflection
          </div>
        </div>
      </div>
    </motion.div>
  );
};
