import { z } from "zod";
import { api } from "./client";

const eventSchema = z.object({ id: z.string(), type: z.string(), created_at: z.string() }).passthrough();
const loanSchema = z.object({ id: z.string(), status: z.string(), lender_id: z.string(), borrower_id: z.string(), due_at: z.string(), events: z.array(eventSchema) }).passthrough();

export const loansApi = {
  list: async () => z.object({ items: z.array(loanSchema) }).passthrough().parse(await api.get("/loans")),
  get: async (id) => loanSchema.parse(await api.get(`/loans/${id}`)),
  agree: async (id) => loanSchema.parse(await api.post(`/loans/${id}/agree`, { agreement_version: 1 })),
  setSpot: async (id, spotId, scheduledStart) => loanSchema.parse(await api.post(`/loans/${id}/spot`, { spot_id: spotId, scheduled_start: scheduledStart })),
  showCode: async (id, purpose) => z.object({ code: z.string().length(6), purpose: z.string(), expires_at: z.string() }).parse(await api.post(`/loans/${id}/codes/${purpose}`)),
  confirmCode: async (id, purpose, code) => loanSchema.parse(await api.post(`/loans/${id}/confirm-${purpose}`, { code })),
};
