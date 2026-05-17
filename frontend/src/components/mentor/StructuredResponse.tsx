import { MentorResponse } from '../../types/chat';
import { CodeCard } from './CodeCard';
import { SocraticQuestion } from './SocraticQuestion';
import { TakeawayBanner } from './TakeawayBanner';

export const StructuredResponse = ({ data }: { data: MentorResponse }) => {
  return (
    <div className="flex flex-col w-full text-gray-100">
      <div className="max-w-none text-base leading-relaxed">
        {data.concept_explanation.split('\n\n').map((para, i) => (
          <p key={i} className="mb-4 last:mb-0">{para}</p>
        ))}
      </div>

      {data.code_examples?.map((ex, i) => (
        <CodeCard key={i} example={ex} />
      ))}

      {data.key_takeaway && <TakeawayBanner text={data.key_takeaway} />}
      {data.mentor_question && <SocraticQuestion question={data.mentor_question} />}
      
      {data.suggested_next_topic && (
        <div className="mt-4 pt-4 border-t border-gray-700/50 text-xs text-gray-500">
          Suggested next topic: <span className="text-gray-400 font-medium">{data.suggested_next_topic}</span>
        </div>
      )}
    </div>
  );
};
