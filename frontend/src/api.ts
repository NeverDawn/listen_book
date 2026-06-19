import type {
  AudioAsset,
  AudioPrefetchResponse,
  BookSummary,
  Chapter,
  ReadingProgress
} from "./types";

export async function fetchBooks(): Promise<BookSummary[]> {
  const response = await fetch("/api/books");
  if (!response.ok) {
    throw new Error("Failed to load books");
  }
  return response.json();
}

export async function uploadBook(file: File): Promise<BookSummary> {
  const body = new FormData();
  body.append("file", file);

  const response = await fetch("/api/books", {
    method: "POST",
    body
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Failed to upload book");
  }
  return response.json();
}

export async function deleteBook(bookId: string): Promise<void> {
  const response = await fetch(`/api/books/${bookId}`, {
    method: "DELETE"
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Failed to delete book");
  }
}

export async function fetchChapters(bookId: string): Promise<Chapter[]> {
  const response = await fetch(`/api/books/${bookId}/chapters`);
  if (!response.ok) {
    throw new Error("Failed to load chapters");
  }
  return response.json();
}

export async function fetchBookProgress(bookId: string): Promise<ReadingProgress | null> {
  const response = await fetch(`/api/books/${bookId}/progress`);
  if (!response.ok) {
    throw new Error("Failed to load reading progress");
  }
  return response.json();
}

export async function saveBookProgress(
  bookId: string,
  sentenceId: string | null,
  audioPositionMs = 0
): Promise<ReadingProgress> {
  const response = await fetch(`/api/books/${bookId}/progress`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      sentence_id: sentenceId,
      audio_position_ms: audioPositionMs
    })
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Failed to save reading progress");
  }
  return response.json();
}

export async function generateSentenceAudio(sentenceId: string): Promise<AudioAsset> {
  const response = await fetch(`/api/audio/sentences/${sentenceId}`, {
    method: "POST"
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Failed to generate audio");
  }
  return response.json();
}

export async function prefetchSentenceAudio(
  sentenceIds: string[]
): Promise<AudioPrefetchResponse> {
  const response = await fetch("/api/audio/sentences/prefetch", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ sentence_ids: sentenceIds })
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Failed to prefetch audio");
  }
  return response.json();
}

export async function fetchSentenceAudioStatuses(sentenceIds: string[]): Promise<AudioAsset[]> {
  const response = await fetch("/api/audio/sentences/status", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ sentence_ids: sentenceIds })
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Failed to load audio statuses");
  }
  return response.json();
}
