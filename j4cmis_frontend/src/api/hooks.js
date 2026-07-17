// Generic React Query CRUD over the DRF endpoints. DRF returns
// {count, results} for lists.
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";

export function useList(resource, params) {
  return useQuery({
    queryKey: [resource, "list", params || null],
    queryFn: async () =>
      (await apiClient.get(`/${resource}/`, { params: { page_size: 500, ...(params || {}) } })).data,
  });
}
export function useOne(resource, id) {
  return useQuery({
    enabled: !!id,
    queryKey: [resource, "one", id],
    queryFn: async () => (await apiClient.get(`/${resource}/${id}/`)).data,
  });
}
export function useCreate(resource) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body) => (await apiClient.post(`/${resource}/`, body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: [resource] }),
  });
}
export function useUpdate(resource) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, body }) => (await apiClient.patch(`/${resource}/${id}/`, body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: [resource] }),
  });
}
export async function uploadDocument(caseId, file, category) {
  const fd = new FormData();
  fd.append("file", file);
  if (caseId) fd.append("case", caseId);
  if (category) fd.append("category", category);
  const res = await apiClient.post("/documents/", fd, { headers: { "Content-Type": "multipart/form-data" } });
  return res.data;
}
