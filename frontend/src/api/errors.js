export class ApiError extends Error {
  constructor(code, message, details = {}, status = 0) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.details = details;
    this.status = status;
  }
}

export function friendlyError(error) {
  if (!(error instanceof ApiError)) return "Something went wrong. Try again.";
  const copy = {
    UNAUTHENTICATED: "Your session ended. Sign in again to continue.",
    RATE_LIMITED: "You are moving quickly. Wait a moment and try again.",
    INTERNAL_ERROR: "CampusLend is having trouble. Try again shortly.",
  };
  return copy[error.code] ?? error.message;
}
