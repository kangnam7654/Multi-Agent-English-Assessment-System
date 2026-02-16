const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Mode = "synthesis" | "assessment";
export type Grade = "elem_6" | "mid_2" | "high_2";
export type Level = "beginner" | "intermediate" | "advanced" | "master";

export interface RunRequest {
  mode: Mode;
  user_prompt?: string;
  grade_for_student: Grade;
  grade_for_assessor: Grade;
  level: Level;
  essay?: string;
}

export interface CriterionResult {
  score: number;
  comment_english: string;
  comment_korean: string;
}

export interface AssessedContent {
  grade: Grade;
  overall_score: number;
  level: Level;
  per_criterion: Record<string, CriterionResult>;
  summary_feedback_english: string;
  summary_feedback_korean: string;
}

export interface RunResponse {
  grade: Grade | null;
  level: Level | null;
  essay: string | null;
  assessed_content: AssessedContent | null;
}

export async function runPipeline(
  req: RunRequest,
  signal?: AbortSignal,
): Promise<RunResponse> {
  const res = await fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    signal,
  });

  if (!res.ok) {
    let message: string;
    try {
      const body = await res.json();
      message = typeof body?.detail === "string" ? body.detail : JSON.stringify(body);
    } catch {
      message = await res.text().catch(() => "Unknown error");
    }
    throw new Error(message);
  }

  return res.json();
}

export function wordCount(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

export const GRADE_LABELS: Record<Grade, string> = {
  elem_6: "Elementary 6th",
  mid_2: "Middle 2nd",
  high_2: "High 2nd",
};

export const LEVEL_LABELS: Record<Level, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
  master: "Master",
};

export const LEVEL_COLORS: Record<Level, string> = {
  beginner: "#ef4444",
  intermediate: "#f59e0b",
  advanced: "#3b82f6",
  master: "#8b5cf6",
};
