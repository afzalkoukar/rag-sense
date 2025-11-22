import { APIResponse, UploadData, StatusData, AskData, MessageData } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<APIResponse<T>> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

export const api = {
  uploadFile: async (file: File): Promise<APIResponse<UploadData>> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: "POST",
      body: formData,
    });
    return handleResponse<UploadData>(response);
  },

  checkStatus: async (uploadId: string): Promise<APIResponse<StatusData>> => {
    const response = await fetch(`${API_BASE_URL}/api/status/${uploadId}`);
    return handleResponse<StatusData>(response);
  },

  askQuestion: async (uploadId: string, query: string): Promise<APIResponse<AskData>> => {
    const response = await fetch(`${API_BASE_URL}/api/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ upload_id: uploadId, query }),
    });
    return handleResponse<AskData>(response);
  },

  clearSession: async (uploadId: string): Promise<APIResponse<MessageData>> => {
    const response = await fetch(`${API_BASE_URL}/api/clear/${uploadId}`, {
      method: "POST",
    });
    return handleResponse<MessageData>(response);
  },
};