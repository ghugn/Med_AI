import { useCallback } from "react";
import { useReminderStore } from "@/stores/reminder.store";
import { useScribeStore } from "@/stores/scribe.store";
import { runReminder } from "@/services/reminder.service";

export function useReminder() {
  const store = useReminderStore();
  const scribeResult = useScribeStore((s) => s.result);

  const trigger = useCallback(async () => {
    if (!scribeResult) return;
    store.setLoading(true);
    try {
      const result = await runReminder(scribeResult);
      store.setResult(result);
    } catch (err) {
      store.setError(err instanceof Error ? err.message : "Đã xảy ra lỗi.");
    }
  }, [store, scribeResult]);

  return { ...store, trigger, hasRecord: !!scribeResult };
}
