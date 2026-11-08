import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "../api/notifications";

export function useNotifications() { return useQuery({ queryKey: ["notifications"], queryFn: notificationsApi.list, refetchInterval: 30_000 }); }
export function useReadNotification() { const client = useQueryClient(); return useMutation({ mutationFn: notificationsApi.read, onSuccess: () => client.invalidateQueries({ queryKey: ["notifications"] }) }); }
