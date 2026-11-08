import { z } from "zod";
import { api, setAccessToken, clearAccessToken } from "./client";

const userSchema = z.object({ id: z.string(), email: z.string().email(), display_name: z.string(), trust_tier: z.string(), trust_score: z.number() }).passthrough();
const tokenSchema = z.object({ access_token: z.string(), user: userSchema });

export const authApi = {
  requestOtp: (email) => api.post("/auth/otp/request", { email }),
  verifyOtp: async (email, code) => {
    const result = tokenSchema.parse(await api.post("/auth/otp/verify", { email, code }));
    setAccessToken(result.access_token);
    return result;
  },
  refresh: async () => {
    const result = z.object({ access_token: z.string() }).parse(await api.post("/auth/refresh"));
    setAccessToken(result.access_token);
    return result;
  },
  logout: async () => { await api.post("/auth/logout"); clearAccessToken(); },
  me: async () => userSchema.parse(await api.get("/users/me")),
};
