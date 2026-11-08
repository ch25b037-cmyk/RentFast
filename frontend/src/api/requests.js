import { z } from "zod";
import { api } from "./client";

const requestSchema = z.object({ id: z.string(), title: z.string(), description: z.string(), needed_from: z.string(), needed_until: z.string(), status: z.string(), requester_id: z.string(), category_id: z.string(), preferred_spot_id: z.string().nullable(), offers_count: z.number(), loan_id: z.string().nullable() });
const pageSchema = z.object({ items: z.array(requestSchema), total: z.number(), limit: z.number(), offset: z.number() });

export const requestsApi = {
  list: async (params = "") => pageSchema.parse(await api.get(`/requests${params ? `?${params}` : ""}`)),
  get: async (id) => requestSchema.parse(await api.get(`/requests/${id}`)),
  create: async (body) => requestSchema.parse(await api.post("/requests", body)),
  cancel: async (id) => requestSchema.parse(await api.post(`/requests/${id}/cancel`)),
};
