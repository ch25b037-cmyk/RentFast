import { useQuery } from "@tanstack/react-query";
import { catalogApi } from "../api/catalog";

export function useCategories() { return useQuery({ queryKey: ["categories"], queryFn: catalogApi.categories, staleTime: 300_000 }); }
export function useMeetupSpots() { return useQuery({ queryKey: ["meetup-spots"], queryFn: catalogApi.spots, staleTime: 300_000 }); }
export function useMyItems() { return useQuery({ queryKey: ["items", "mine"], queryFn: catalogApi.items, staleTime: 30_000 }); }
