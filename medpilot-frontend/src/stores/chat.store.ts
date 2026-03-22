import { create } from "zustand";
import type { UIChatMessage } from "@/types";

interface ChatState {
  messages: UIChatMessage[];
  isLoading: boolean;

  addMessage: (msg: UIChatMessage) => void;
  updateMessage: (id: string, patch: Partial<UIChatMessage>) => void;
  setLoading: (v: boolean) => void;
  reset: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,

  addMessage: (msg) =>
    set((s) => ({ messages: [...s.messages, msg] })),

  updateMessage: (id, patch) =>
    set((s) => ({
      messages: s.messages.map((m) => (m.id === id ? { ...m, ...patch } : m)),
    })),

  setLoading: (isLoading) => set({ isLoading }),
  reset: () => set({ messages: [], isLoading: false }),
}));
