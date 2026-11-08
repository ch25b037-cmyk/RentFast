"""Development mailer. It returns the code to the caller without logging it."""

class ConsoleMailer:
    def send_otp(self, email: str, code: str) -> None:
        # In development, the caller/test harness can inspect the generated code through its test seam.
        _ = (email, code)
