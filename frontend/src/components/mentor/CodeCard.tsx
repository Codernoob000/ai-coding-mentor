import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Check, Copy, Terminal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { CodeExample } from '../../types/chat';

export const CodeCard = ({ example }: { example: CodeExample }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(example.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col bg-[#0d1117] rounded-xl border border-white/10 overflow-hidden my-6 group transition-all hover:border-brand/40 shadow-2xl"
    >
      {/* Tab/Header Bar - IDE Style */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#161b22] border-b border-white/5">
        <div className="flex items-center space-x-3">
          <div className="flex space-x-1.5 mr-2">
            <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]/20 border border-[#ff5f56]/40" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]/20 border border-[#ffbd2e]/40" />
            <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f]/20 border border-[#27c93f]/40" />
          </div>
          <div className="flex items-center space-x-2 px-3 py-1 bg-[#0d1117] rounded-md border border-white/5 shadow-sm">
            <Terminal className="w-3.5 h-3.5 text-brand" />
            <span className="text-[11px] text-text-secondary font-bold tracking-tight">
              {example.title || 'snippet.py'}
            </span>
          </div>
          <span className="text-[10px] font-black text-text-muted uppercase tracking-[0.1em] opacity-50">
            {example.language}
          </span>
        </div>
        
        <button 
          onClick={handleCopy} 
          className="relative text-text-muted hover:text-text-primary transition-all p-2 hover:bg-white/5 rounded-lg group/btn"
        >
          <AnimatePresence mode="wait">
            {copied ? (
              <motion.div key="check" initial={{ scale: 0.5 }} animate={{ scale: 1 }} exit={{ scale: 0.5 }}>
                <Check className="w-4 h-4 text-status-success" />
              </motion.div>
            ) : (
              <motion.div key="copy" initial={{ scale: 0.5 }} animate={{ scale: 1 }} exit={{ scale: 0.5 }}>
                <Copy className="w-4 h-4" />
              </motion.div>
            )}
          </AnimatePresence>
        </button>
      </div>

      {/* Code Editor Body */}
      <div className="relative text-[13px] font-mono leading-relaxed bg-[#0d1117]">
        <SyntaxHighlighter
          language={example.language.toLowerCase()}
          style={vscDarkPlus}
          customStyle={{ 
            margin: 0, 
            padding: '1.5rem', 
            background: 'transparent',
            lineHeight: '1.7'
          }}
          showLineNumbers={true}
          lineNumberStyle={{ minWidth: '2.5em', paddingRight: '1em', color: '#484f58', textAlign: 'right' }}
        >
          {example.code}
        </SyntaxHighlighter>
      </div>
    </motion.div>
  );
};
