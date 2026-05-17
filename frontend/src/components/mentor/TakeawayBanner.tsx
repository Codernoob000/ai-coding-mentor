import { Lightbulb } from 'lucide-react';

export const TakeawayBanner = ({ text }: { text: string }) => {
  return (
    <div className="flex items-start space-x-3 p-4 bg-blue-900/20 border border-blue-800/50 rounded-lg mt-6">
      <Lightbulb className="w-5 h-5 text-blue-400 flex-shrink-0" />
      <div>
        <h4 className="text-sm font-semibold text-blue-400 uppercase mb-1">Key Takeaway</h4>
        <p className="text-blue-100 text-sm">{text}</p>
      </div>
    </div>
  );
};
