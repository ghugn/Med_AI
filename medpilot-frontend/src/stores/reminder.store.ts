import { create } from "zustand";
import type { ReminderResponse } from "@/types";

interface ReminderState {
  loading: boolean;
  result: ReminderResponse | null;
  error: string | null;

  setLoading: (v: boolean) => void;
  setResult: (r: ReminderResponse) => void;
  setError: (msg: string) => void;
  reset: () => void;
}

export const useReminderStore = create<ReminderState>((set) => ({
  loading: false,
  result: null,
  error: null,

  setLoading: (loading) => set({ loading }),
  setResult: (result) => set({ result, loading: false, error: null }),
  setError: (error) => set({ error, loading: false }),
  reset: () => set({ loading: false, result: null, error: null }),
}));
