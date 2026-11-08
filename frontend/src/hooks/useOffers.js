import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { offersApi } from "../api/offers";

export function useRequestOffers(requestId, enabled = true) {
  return useQuery({ queryKey: ["offers", requestId], queryFn: () => offersApi.forRequest(requestId), enabled, staleTime: 10_000 });
}

export function useCreateOffer() {
  const client = useQueryClient();
  return useMutation({ mutationFn: ({ requestId, message }) => offersApi.create(requestId, { message }), onSuccess: (_, variables) => { client.invalidateQueries({ queryKey: ["requests"] }); client.invalidateQueries({ queryKey: ["offers", variables.requestId] }); } });
}

export function useAcceptOffer() {
  const client = useQueryClient();
  return useMutation({ mutationFn: offersApi.accept, onSuccess: () => { client.invalidateQueries({ queryKey: ["requests"] }); client.invalidateQueries({ queryKey: ["loans"] }); client.invalidateQueries({ queryKey: ["notifications"] }); } });
}

export function useDeclineOffer() {
  const client = useQueryClient();
  return useMutation({ mutationFn: offersApi.decline, onSuccess: (offer) => client.invalidateQueries({ queryKey: ["offers", offer.request_id] }) });
}

export function useMyOffers() { return useQuery({ queryKey: ["offers", "mine"], queryFn: offersApi.mine, staleTime: 10_000, refetchInterval: 15_000 }); }
