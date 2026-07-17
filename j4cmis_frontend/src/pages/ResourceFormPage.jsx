import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box, Paper, Stack, Typography, Button, CircularProgress } from "@mui/material";
import { useOne, useCreate, useUpdate } from "../api/hooks";
import SchemaForm from "../components/SchemaForm";
import { RESOURCES } from "../lib/schemas";

export default function ResourceFormPage({ resource }) {
  const { id } = useParams();
  const nav = useNavigate();
  const cfg = RESOURCES[resource];
  const editing = id && id !== "new";
  const { data: existing, isLoading } = useOne(resource, editing ? id : null);
  const create = useCreate(resource);
  const update = useUpdate(resource);
  const [err, setErr] = useState("");
  if (!cfg) return <Typography>Unknown module.</Typography>;
  if (editing && isLoading) return <Stack alignItems="center" sx={{ py: 8 }}><CircularProgress /></Stack>;

  const onSubmit = (body) => {
    setErr("");
    const onError = (e) => setErr(e.response?.data ? JSON.stringify(e.response.data) : "Save failed.");
    if (editing) update.mutate({ id, body }, { onSuccess: () => nav(`/${resource}`), onError });
    else create.mutate(body, { onSuccess: () => nav(`/${resource}`), onError });
  };
  return (
    <Box sx={{ maxWidth: 760, mx: "auto" }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h4" fontWeight={800}>{editing ? "Edit" : "New"} {cfg.singular}</Typography>
        <Button variant="outlined" onClick={() => nav(`/${resource}`)}>Cancel</Button>
      </Stack>
      <Paper variant="outlined" sx={{ p: 3, borderRadius: 3 }}>
        <SchemaForm fields={cfg.fields} initial={editing ? existing : undefined}
          submitLabel={editing ? "Save changes" : `Create ${cfg.singular}`}
          submitting={create.isPending || update.isPending} error={err} onSubmit={onSubmit} />
      </Paper>
    </Box>
  );
}
