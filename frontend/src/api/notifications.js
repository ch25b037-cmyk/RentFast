import { z } from "zod";
import { api } from "./client";

const item = z.object({ id: z.string(), title: z.string(), body: z.string(), type: z.string(), created_at: z.string(), read_at: z.string().nullable() }).passthrough();
export const notificationsApi = { list: async () => z.object({ items: z.array(item) }).passthrough().parse(await api.get("/notifications")), read: (id) => api.post(`/notifications/${id}/read`) };
