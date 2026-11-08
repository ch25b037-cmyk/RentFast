import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("welcome page exposes the core trust promise", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Borrow what you need for the day." })).toBeVisible();
  await expect(page.getByText("College-only access")).toBeVisible();
  await page.screenshot({ path: "test-results/welcome.png", fullPage: true });
});

test("sign-in advances after an accepted OTP request", async ({ page }) => {
  await page.route("**/api/v1/auth/otp/request", (route) => route.fulfill({ status: 202, body: JSON.stringify({ status: "accepted" }) }));
  await page.goto("/sign-in");
  await page.getByLabel("College email").fill("student@example.edu");
  await page.getByRole("button", { name: "Send me a code" }).click();
  await expect(page.getByRole("heading", { name: "Enter your six-digit code." })).toBeVisible();
  await expect(page.getByLabel("One-time code")).toBeVisible();
});

test("protected routes redirect unauthenticated users", async ({ page }) => {
  await page.goto("/home");
  await expect(page).toHaveURL(/\/sign-in$/);
  await expect(page.getByRole("heading", { name: "Your campus, in one place." })).toBeVisible();
});

test("sign-in displays a server validation error", async ({ page }) => {
  await page.route("**/api/v1/auth/otp/request", (route) =>
    route.fulfill({ status: 400, contentType: "application/json", body: JSON.stringify({ error: { code: "EMAIL_DOMAIN_NOT_ALLOWED", message: "Use your college email." } }) }),
  );
  await page.goto("/sign-in");
  await page.getByLabel("College email").fill("outside@example.com");
  await page.getByRole("button", { name: "Send me a code" }).click();
  await expect(page.getByText("Use your college email.")).toBeVisible();
});

test("welcome page has no critical accessibility violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations.filter((violation) => violation.impact === "critical")).toEqual([]);
});

test("a lender can offer help from the request board", async ({ page }) => {
  await page.route("**/api/v1/users/me", (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "lender-1", email: "lender@example.edu", display_name: "Lender", department: null, hostel: null, avatar_url: null, role: "member", status: "active", trust_score: 50, trust_tier: "Member" }) }));
  await page.route("**/api/v1/requests**", (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ id: "request-1", requester_id: "borrower-1", category_id: "cat-1", preferred_spot_id: null, loan_id: null, title: "Scientific calculator", description: "Needed for an exam", needed_from: "2026-11-09T10:00:00Z", needed_until: "2026-11-09T12:00:00Z", status: "open", offers_count: 0 }], total: 1, limit: 20, offset: 0 }) }));
  await page.route("**/api/v1/requests/request-1/offers", (route) => route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ id: "offer-1", request_id: "request-1", owner_id: "lender-1", item_id: null, message: "I can lend mine.", status: "pending", created_at: "2026-11-08T10:00:00Z" }) }));
  await page.goto("/requests");
  await page.getByRole("button", { name: "Offer to lend" }).click();
  await expect(page.getByRole("heading", { name: "Offer to lend" })).toBeVisible();
  await page.getByLabel("Offer message").fill("I can lend mine at the library.");
  await page.getByRole("button", { name: "Send offer" }).click();
  await expect(page.getByText("Offer sent to the requester.")).toBeVisible();
});
