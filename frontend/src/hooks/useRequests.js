import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { requestsApi } from "../api/requests";

export function useRequests(query = "") {
  return useQuery({ queryKey: ["requests", query], queryFn: () => requestsApi.list(query), staleTime: 10_000, refetchInterval: 15_000 });
}

export function useCreateRequest() {
  const client = useQueryClient();
  return useMutation({ mutationFn: requestsApi.create, onSuccess: () => client.invalidateQueries({ queryKey: ["requests"] }) });
}
