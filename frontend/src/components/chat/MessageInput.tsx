import { useState, useRef, useEffect } from 'react';
import { SendHorizontal, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

export const MessageInput = ({ onSend, disabled }: { onSend: (text: string) => void; disabled?: boolean }) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize logic
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [text]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative flex items-end w-full group">
      <div className="absolute left-4 bottom-4 text-brand opacity-40 group-focus-within:opacity-100 transition-opacity">
        <Zap className="w-5 h-5 fill-current" />
      </div>
      
      <textarea
        ref={textareaRef}
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Ask a question or paste your code..."
        className="w-full bg-transparent text-text-primary rounded-2xl pl-12 pr-14 py-4 focus:outline-none text-base resize-none transition-all placeholder:text-text-muted/50"
      />

      <div className="absolute right-2 bottom-2">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => handleSubmit()}
          disabled={disabled || !text.trim()}
          className="p-2.5 bg-brand text-white rounded-xl shadow-glow hover:bg-brand-hover transition-colors disabled:opacity-0 disabled:scale-90 transition-all flex items-center justify-center"
        >
          <SendHorizontal className="w-5 h-5" />
        </motion.button>
      </div>
    </div>
  );
};
