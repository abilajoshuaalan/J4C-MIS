import { useMemo } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Box, Button, Paper, Stack, Typography } from "@mui/material";
import { useList } from "../api/hooks";
import RecordTable from "../components/RecordTable";
import { RESOURCES } from "../lib/schemas";
import { PlusIcon } from "../icons";

export default function ResourceListPage({ resource }) {
  const nav = useNavigate();
  const cfg = RESOURCES[resource];
  const { data, isLoading } = useList(resource);
  const casesQ = useList("cases");
  const casesById = useMemo(() => Object.fromEntries((casesQ.data?.results || []).map((c) => [c.id, c])), [casesQ.data]);
  if (!cfg) return <Typography>Unknown module.</Typography>;
  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={800}>{cfg.title}</Typography>
          <Typography color="text.secondary">{cfg.uc}</Typography>
        </Box>
        <Button component={Link} to={`/${resource}/new`} variant="contained" startIcon={<PlusIcon />}>New {cfg.singular}</Button>
      </Stack>
      <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 3 }}>
        <RecordTable columns={cfg.columns} rows={data?.results || []} casesById={casesById}
          onRowClick={(r) => nav(`/${resource}/${r.id}`)} empty={isLoading ? "Loading…" : `No ${cfg.singular.toLowerCase()} records yet.`} />
      </Paper>
    </Box>
  );
}
