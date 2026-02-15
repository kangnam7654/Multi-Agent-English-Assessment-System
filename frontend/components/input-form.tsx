"use client";

import { ModeSelector } from "./mode-selector";
import {
  type Mode,
  type Grade,
  type Level,
  GRADE_LABELS,
  LEVEL_LABELS,
  wordCount,
} from "@/lib/api";
import { Loader2, Play, Square } from "lucide-react";

interface InputFormProps {
  mode: Mode;
  gradeForStudent: Grade;
  gradeForAssessor: Grade;
  level: Level;
  userPrompt: string;
  essayInput: string;
  loading: boolean;
  onModeChange: (mode: Mode) => void;
  onGradeForStudentChange: (grade: Grade) => void;
  onGradeForAssessorChange: (grade: Grade) => void;
  onLevelChange: (level: Level) => void;
  onUserPromptChange: (value: string) => void;
  onEssayInputChange: (value: string) => void;
  onSubmit: () => void;
  onCancel: () => void;
}

export function InputForm({
  mode,
  gradeForStudent,
  gradeForAssessor,
  level,
  userPrompt,
  essayInput,
  loading,
  onModeChange,
  onGradeForStudentChange,
  onGradeForAssessorChange,
  onLevelChange,
  onUserPromptChange,
  onEssayInputChange,
  onSubmit,
  onCancel,
}: InputFormProps) {
  const canSubmit =
    mode === "synthesis"
      ? userPrompt.trim().length > 0
      : essayInput.trim().length > 0;

  const essayWords = wordCount(essayInput);

  return (
    <div className="space-y-5">
      {/* Mode selector */}
      <div>
        <label className="block text-sm font-medium text-muted-foreground mb-2">
          Mode
        </label>
        <ModeSelector value={mode} onChange={onModeChange} />
      </div>

      {/* Grade & Level selectors */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1.5">
            Grade (Assessor)
          </label>
          <select
            value={gradeForAssessor}
            onChange={(e) => onGradeForAssessorChange(e.target.value as Grade)}
            className="w-full px-3 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          >
            {Object.entries(GRADE_LABELS).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {mode === "synthesis" && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1.5">
              Grade (Student)
            </label>
            <select
              value={gradeForStudent}
              onChange={(e) => onGradeForStudentChange(e.target.value as Grade)}
              className="w-full px-3 py-2 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {Object.entries(GRADE_LABELS).map(([key, label]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
          </div>
        )}

        {mode === "synthesis" && (
          <div className="col-span-2">
            <label className="block text-sm font-medium text-muted-foreground mb-1.5">
              Target Level
            </label>
            <div className="flex gap-2">
              {(Object.entries(LEVEL_LABELS) as [Level, string][]).map(
                ([key, label]) => (
                  <button
                    key={key}
                    onClick={() => onLevelChange(key)}
                    className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium border transition-all ${
                      level === key
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-card text-muted-foreground border-border hover:border-primary/50"
                    }`}
                  >
                    {label}
                  </button>
                )
              )}
            </div>
          </div>
        )}
      </div>

      {/* Text input */}
      {mode === "synthesis" ? (
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1.5">
            Essay Topic / Prompt
          </label>
          <textarea
            value={userPrompt}
            onChange={(e) => onUserPromptChange(e.target.value)}
            rows={5}
            placeholder="Enter the essay topic or writing instructions..."
            className="w-full px-3 py-2 bg-card border border-border rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring placeholder:text-muted-foreground/50"
          />
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-sm font-medium text-muted-foreground">
              Your Essay
            </label>
            <span className="text-xs text-muted-foreground">
              {essayWords} {essayWords === 1 ? "word" : "words"}
            </span>
          </div>
          <textarea
            value={essayInput}
            onChange={(e) => onEssayInputChange(e.target.value)}
            rows={8}
            placeholder="Paste your English essay here for assessment..."
            className="w-full px-3 py-2 bg-card border border-border rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring placeholder:text-muted-foreground/50"
          />
          {essayInput.trim() && essayWords < 10 && (
            <p className="text-xs text-amber-600 mt-1">
              Essay seems very short. Consider adding more content for a better assessment.
            </p>
          )}
        </div>
      )}

      {/* Submit / Cancel button */}
      {loading ? (
        <button
          onClick={onCancel}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-500 text-white rounded-xl font-semibold text-sm hover:bg-red-600 transition-colors"
        >
          <Square size={16} />
          <span>Cancel</span>
        </button>
      ) : (
        <button
          onClick={onSubmit}
          disabled={!canSubmit}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-xl font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play size={18} />
          <span>Run Assessment</span>
        </button>
      )}
    </div>
  );
}
