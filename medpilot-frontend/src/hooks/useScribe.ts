import { useEffect, useRef, useCallback } from "react";
import { useScribeStore } from "@/stores/scribe.store";
import { runScribe } from "@/services/scribe.service";

export function useScribe() {
  const store = useScribeStore();
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  useEffect(() => () => clearTimer(), [clearTimer]);

  const startRecording = useCallback(() => {
    store.reset();
    store.setRecordingState("recording");
    timerRef.current = setInterval(() => store.incrementElapsed(), 1000);
  }, [store]);

  const stopRecording = useCallback(async (transcript?: string) => {
    clearTimer();
    store.setRecordingState("processing");

    try {
      const result = await runScribe({
        input_type: transcript ? "text" : "audio",
        transcript,
        patient_info: { patient_id: null, name: null, age: null, gender: null },
      });
      store.setResult(result);
      store.setRecordingState("done");
    } catch (err) {
      store.setError(err instanceof Error ? err.message : "Đã xảy ra lỗi khi xử lý.");
    }
  }, [store, clearTimer]);

  return {
    ...store,
    startRecording,
    stopRecording,
  };
}
