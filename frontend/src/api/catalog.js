import { z } from "zod";
import { api } from "./client";

const categorySchema = z.object({ id: z.string(), slug: z.string(), name: z.string(), max_loan_hours: z.number() }).passthrough();
const itemSchema = z.object({ id: z.string(), category_id: z.string(), title: z.string(), description: z.string(), condition: z.string(), value_tier: z.string(), photo_urls: z.array(z.string()), is_available: z.boolean() }).passthrough();
export const catalogApi = { categories: async () => z.array(categorySchema).parse(await api.get("/categories")), spots: async () => z.array(z.object({ id: z.string(), name: z.string() }).passthrough()).parse(await api.get("/meetup-spots")), items: async () => z.object({ items: z.array(itemSchema) }).passthrough().parse(await api.get("/items")) };
