import { ApiError } from "@/lib/api";

export const PROJECT_PERMISSION_MESSAGE = "We could not find this project or you do not have access to it.";

type ErrorContext = "auth" | "upload" | "analysis" | "permission" | "default";

export function friendlyErrorMessage(error: unknown, context: ErrorContext = "default"): string {
  if (context === "permission" || isPermissionError(error)) {
    return PROJECT_PERMISSION_MESSAGE;
  }

  if (error instanceof ApiError) {
    if (error.status === 401) {
      return context === "auth" ? "Sign in again to continue." : "Your session expired. Sign in again to continue.";
    }

    if (error.status === 413) {
      return "The file is too large. Upload a file within the allowed size limit.";
    }

    if (context === "upload") {
      return error.message || "Could not upload this file. Check the file type and try again.";
    }

    if (context === "analysis") {
      return error.message || "Could not start or update the analysis run.";
    }

    return error.message || "Request failed. Try again.";
  }

  if (error instanceof Error && error.message) {
    if (context === "auth") {
      return "Authentication failed. Try again.";
    }

    return error.message;
  }

  switch (context) {
    case "auth":
      return "Authentication failed. Try again.";
    case "upload":
      return "Could not upload or save this document.";
    case "analysis":
      return "Could not start or update the analysis run.";
    default:
      return "Something went wrong. Try again.";
  }
}

function isPermissionError(error: unknown): boolean {
  return error instanceof ApiError && (error.status === 403 || error.status === 404 || error.code === "not_found");
}
