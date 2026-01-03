import { isApiError } from "@/types/api";
import { useAuthStore } from "@/stores/auth.store";

export async function withRefreshRetry<T>(fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (e) {
    if (isApiError(e) && e.status === 401) {
      await useAuthStore.getState().refresh();
      return await fn();
    }
    throw e;
  }
}

export async function* sseWithRefreshRetry<T>(
  sse: () => AsyncGenerator<T>
): AsyncGenerator<T> {
  try {
    yield* sse();
  } catch (e) {
    if (isApiError(e) && e.status === 401) {
      await useAuthStore.getState().refresh();
      yield* sse();
      return;
    }
    throw e;
  }
}
