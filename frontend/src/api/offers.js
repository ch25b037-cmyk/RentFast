import { z } from "zod";
import { api } from "./client";

const offerSchema = z.object({ id: z.string(), request_id: z.string(), owner_id: z.string(), item_id: z.string().nullable(), message: z.string(), status: z.string(), created_at: z.string() }).passthrough();

export const offersApi = {
  create: async (requestId, body) => offerSchema.parse(await api.post(`/requests/${requestId}/offers`, body)),
  forRequest: async (requestId) => z.array(offerSchema).parse(await api.get(`/requests/${requestId}/offers`)),
  accept: (offerId) => api.post(`/offers/${offerId}/accept`),
  decline: async (offerId) => offerSchema.parse(await api.post(`/offers/${offerId}/decline`)),
  mine: async () => z.array(offerSchema).parse(await api.get("/offers/mine")),
};
