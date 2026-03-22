import { create } from "zustand";
import type { ScribeResponse } from "@/types";

type RecordingState = "idle" | "recording" | "processing" | "done" | "error";

interface ScribeState {
  recordingState: RecordingState;
  elapsed: number;
  result: ScribeResponse | null;
  draftNote: string;
  error: string | null;

  setRecordingState: (s: RecordingState) => void;
  setElapsed: (n: number) => void;
  incrementElapsed: () => void;
  setResult: (r: ScribeResponse) => void;
  setDraftNote: (note: string) => void;
  setError: (msg: string) => void;
  reset: () => void;
}

const INITIAL: Pick<ScribeState, "recordingState" | "elapsed" | "result" | "draftNote" | "error"> = {
  recordingState: "idle",
  elapsed: 0,
  result: null,
  draftNote: "",
  error: null,
};

export const useScribeStore = create<ScribeState>((set) => ({
  ...INITIAL,
  setRecordingState: (recordingState) => set({ recordingState }),
  setElapsed: (elapsed) => set({ elapsed }),
  incrementElapsed: () => set((s) => ({ elapsed: s.elapsed + 1 })),
  setResult: (result) => set({ result, draftNote: result.draft_note }),
  setDraftNote: (draftNote) => set({ draftNote }),
  setError: (error) => set({ error, recordingState: "error" }),
  reset: () => set(INITIAL),
}));
