import { motion, AnimatePresence } from 'framer-motion';
import { useChat } from './hooks/useChat';
import { StructuredResponse } from './components/mentor/StructuredResponse';
import { MessageInput } from './components/chat/MessageInput';
import { useRef, useEffect } from 'react';
import { Terminal, BrainCircuit, AlertCircle, Command, History, Settings } from 'lucide-react';

export default function App() {
  const { messages, isLoading, error, sendMessage } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div className="flex h-screen bg-[#09090b] text-text-primary overflow-hidden font-sans selection:bg-brand/30">
      
      {/* Sidebar - Pro Design */}
      <aside className="w-[280px] bg-[#0c0c0e] border-r border-white/5 p-5 hidden lg:flex flex-col z-20">
        <div className="flex items-center space-x-3 mb-12 px-2">
          <div className="w-9 h-9 bg-brand rounded-xl flex items-center justify-center shadow-glow border border-white/10">
            <Terminal className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-black tracking-tight uppercase leading-none">Mentor <span className="text-brand">AI</span></h1>
            <div className="flex items-center mt-1 space-x-1.5">
              <div className="w-1.5 h-1.5 bg-status-success rounded-full" />
              <span className="text-[9px] text-text-muted font-bold uppercase tracking-widest">Core Engine v1</span>
            </div>
          </div>
        </div>
        
        <div className="flex-1 space-y-1">
          <div className="text-[10px] font-black text-text-muted uppercase tracking-[0.2em] mb-4 px-2">Knowledge Space</div>
          <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl bg-brand/10 border border-brand/20 text-brand text-xs font-bold transition-all">
            <Command className="w-4 h-4" />
            <span>Active Mentor Session</span>
          </button>
          <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-white/5 text-text-secondary text-xs font-medium transition-all group">
            <History className="w-4 h-4 group-hover:text-text-primary" />
            <span>Previous Context</span>
          </button>
        </div>

        <div className="mt-auto space-y-4 pt-6 border-t border-white/5">
          <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-xl hover:bg-white/5 text-text-muted text-xs transition-all">
            <Settings className="w-4 h-4" />
            <span>Project Settings</span>
          </button>
        </div>
      </aside>

      {/* Main Experience */}
      <main className="flex-1 flex flex-col relative bg-[#09090b]">
        
        {/* Decorative Background Accent */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-[500px] bg-brand/5 blur-[120px] pointer-events-none rounded-full" />

        {/* Content Stream */}
        <div 
          ref={scrollRef}
          className="flex-1 w-full max-w-4xl mx-auto overflow-y-auto px-6 py-12 md:px-12 space-y-12 scroll-smooth no-scrollbar relative z-10"
        >
          <AnimatePresence>
            {messages.length === 0 ? (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="h-full flex flex-col items-center justify-center text-center pb-20"
              >
                <div className="w-24 h-24 bg-brand/10 rounded-[2.5rem] flex items-center justify-center mb-10 border border-brand/20 shadow-glow relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-tr from-brand/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  <BrainCircuit className="w-12 h-12 text-brand relative z-10" />
                </div>
                <h2 className="text-5xl font-black mb-6 tracking-tighter bg-gradient-to-b from-white to-white/50 bg-clip-text text-transparent">
                  Build better code.
                </h2>
                <p className="text-text-secondary max-w-md mx-auto text-lg font-medium leading-relaxed mb-8">
                  Your AI Mentor for technical architecture, logic debugging, and Socratic learning.
                </p>
                <div className="flex items-center space-x-3 text-text-muted">
                  <div className="px-3 py-1.5 rounded-lg border border-white/5 bg-white/5 text-[10px] font-bold tracking-widest uppercase">Deep Context</div>
                  <div className="px-3 py-1.5 rounded-lg border border-white/5 bg-white/5 text-[10px] font-bold tracking-widest uppercase">Tool Aware</div>
                </div>
              </motion.div>
            ) : (
              messages.map((msg) => (
                <motion.div 
                  key={msg.id} 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`${
                    msg.role === 'user' 
                      ? 'max-w-[80%] bg-brand text-white p-5 rounded-2xl rounded-tr-none shadow-glow font-medium text-[15px]' 
                      : 'w-full'
                  }`}>
                    {typeof msg.content === 'string' ? (
                      <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <div className="w-full">
                        {/* Avatar/System Label for AI */}
                        <div className="flex items-center space-x-3 mb-6 opacity-60">
                           <div className="w-6 h-6 bg-brand/20 rounded-lg flex items-center justify-center">
                              <Terminal className="w-3.5 h-3.5 text-brand" />
                           </div>
                           <span className="text-[10px] font-black uppercase tracking-widest">Mentor Intelligence</span>
                        </div>
                        <StructuredResponse data={msg.content} />
                      </div>
                    )}
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>

          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center space-x-4">
              <div className="w-6 h-6 bg-brand/10 rounded-lg flex items-center justify-center animate-pulse">
                <Terminal className="w-3.5 h-3.5 text-brand" />
              </div>
              <div className="flex space-x-1.5">
                <div className="w-1.5 h-1.5 bg-brand rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-brand rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-1.5 h-1.5 bg-brand rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </motion.div>
          )}
        </div>

        {/* Global Action Bar */}
        <div className="w-full max-w-4xl mx-auto p-6 md:p-10 mt-auto">
          <div className="glass p-1.5 rounded-[2rem] shadow-2xl ring-1 ring-white/10 relative group">
             <div className="absolute inset-0 bg-brand/5 blur-xl rounded-full opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none" />
             <MessageInput onSend={sendMessage} disabled={isLoading} />
          </div>
          <p className="mt-5 text-[9px] text-center text-text-muted/40 uppercase tracking-[0.4em] font-black pointer-events-none">
            Production Environment • Secure Execution • Socratic Engine
          </p>
        </div>
      </main>
    </div>
  );
}
