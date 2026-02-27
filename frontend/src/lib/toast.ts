import { toast } from "sonner"

/**
 * Toast abstraction for mogged.tv.
 *
 * Call these from anywhere — components, service functions, event handlers.
 * No hooks or React context required.
 *
 *   import { showSuccess, showError } from "@/lib/toast"
 *
 *   showSuccess("You're live")
 *   showError("Stream failed to start")
 */

export function showSuccess(message: string, description?: string) {
  toast.success(message, { description })
}

export function showError(message: string, description?: string) {
  toast.error(message, { description })
}

export function showInfo(message: string, description?: string) {
  toast.info(message, { description })
}

export function showWarning(message: string, description?: string) {
  toast.warning(message, { description })
}
