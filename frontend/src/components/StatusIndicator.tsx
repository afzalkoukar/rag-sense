import React from 'react';

interface StatusIndicatorProps {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'failed';
}

export default function StatusIndicator({ status }: StatusIndicatorProps) {
  const config = {
    idle: { color: 'bg-gray-100 text-gray-500', text: 'Waiting for file' },
    uploading: { color: 'bg-blue-100 text-blue-600', text: 'Uploading...' },
    processing: { color: 'bg-yellow-100 text-yellow-700', text: 'Reading PDF...' },
    completed: { color: 'bg-green-100 text-green-700', text: 'Ready to Chat' },
    failed: { color: 'bg-red-100 text-red-700', text: 'Error' },
  };

  const current = config[status];

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${current.color}`}>
      {status === 'processing' || status === 'uploading' ? (
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-current"></span>
        </span>
      ) : (
        <div className="h-2 w-2 rounded-full bg-current" />
      )}
      {current.text}
    </div>
  );
}