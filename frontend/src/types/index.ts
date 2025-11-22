export interface MessageData {
  message: string;
}

export interface UploadData {
  upload_id: string;
  file_name: string;
  status: string;
}

export interface StatusData {
  status: string;
  file_name: string;
}

export interface Citation {
  page: number;
  snippet: string;
}

export interface AskData {
  answer: string;
  citations: Citation[];
}

// Generic API Response Envelope
export interface APIResponse<T = null> {
  status_code: number;
  timestamp: string;
  data: T | null;
  message: string | null;
}