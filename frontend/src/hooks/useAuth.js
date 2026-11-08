import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { authApi } from "../api/auth";

export function useCurrentUser() {
  return useQuery({ queryKey: ["me"], queryFn: authApi.me, retry: false, staleTime: 60_000 });
}

export function useRequestOtp() {
  return useMutation({ mutationFn: authApi.requestOtp });
}

export function useVerifyOtp() {
  const client = useQueryClient();
  return useMutation({ mutationFn: ({ email, code }) => authApi.verifyOtp(email, code), onSuccess: ({ user }) => client.setQueryData(["me"], user) });
}
