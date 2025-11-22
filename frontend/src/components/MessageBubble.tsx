import { Citation } from '@/types';

interface MessageBubbleProps {
  role: 'user' | 'ai';
  content: string;
  citations?: Citation[];
}

export default function MessageBubble({ role, content, citations }: MessageBubbleProps) {
  const isUser = role === 'user';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div 
        className={`
          max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm
          ${isUser 
            ? 'bg-indigo-600 text-white rounded-br-none' 
            : 'bg-white border border-gray-100 text-gray-800 rounded-bl-none'}
        `}
      >
        <p className="whitespace-pre-wrap">{content}</p>
        
        {/* Render Citations if available (only for AI) */}
        {citations && citations.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100/50">
            <p className="text-xs font-semibold opacity-70 mb-2">Sources:</p>
            <div className="flex flex-wrap gap-2">
              {citations.map((c, i) => (
                <div key={i} className="bg-gray-50 text-gray-500 text-xs px-2 py-1 rounded border border-gray-100">
                   Page {c.page}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}