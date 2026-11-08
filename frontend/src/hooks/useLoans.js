import { useQuery } from "@tanstack/react-query";
import { loansApi } from "../api/loans";

export function useLoans() { return useQuery({ queryKey: ["loans"], queryFn: loansApi.list, staleTime: 15_000, refetchInterval: 30_000 }); }
export function useLoan(id) { return useQuery({ queryKey: ["loan", id], queryFn: () => loansApi.get(id), enabled: Boolean(id), refetchInterval: 15_000 }); }
