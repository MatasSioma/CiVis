import { readonly, ref } from 'vue';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastMessage {
  id: number;
  message: string;
  type: ToastType;
}

const toasts = ref<ToastMessage[]>([]);
let nextToastId = 1;

export function useToasts() {
  function removeToast(id: number) {
    toasts.value = toasts.value.filter((toast) => toast.id !== id);
  }

  function showToast(message: string, type: ToastType = 'info') {
    const existingToast = toasts.value.find(
      (toast) => toast.message === message && toast.type === type,
    );

    if (existingToast) {
      return;
    }

    const toast = {
      id: nextToastId,
      message,
      type,
    };

    nextToastId += 1;
    toasts.value = [...toasts.value, toast];

    window.setTimeout(() => {
      removeToast(toast.id);
    }, 3000);
  }

  return {
    removeToast,
    showToast,
    toasts: readonly(toasts),
  };
}
