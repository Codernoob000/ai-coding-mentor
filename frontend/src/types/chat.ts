export interface CodeExample {
  title: string;
  language: string;
  code: string;
}

export interface MentorResponse {
  concept_explanation: string;
  code_examples: CodeExample[];
  key_takeaway: string;
  mentor_question: string;
  suggested_next_topic: string;
  session_id: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string | MentorResponse;
  timestamp: string;
}
