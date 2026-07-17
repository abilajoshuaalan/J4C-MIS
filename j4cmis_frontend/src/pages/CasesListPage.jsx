import { useState } from "react";
import { Box, Button, Chip, Paper, Stack, TextField, Typography } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { useList } from "../api/hooks";
import RecordTable from "../components/RecordTable";
import { CASE_CATEGORY, CASE_STATUS } from "../config/enums";
import { PlusIcon, SearchIcon } from "../icons";

export default function CasesListPage() {
  const nav = useNavigate();
  const [q, setQ] = useState("");
  const { data, isLoading } = useList("cases");
  const rows = (data?.results || []).filter((c) => {
    const s = `${c.case_number} ${c.child_name} ${c.status}`.toLowerCase();
    return s.includes(q.toLowerCase());
  });
  const columns = [
    { key: "case_number", label: "Case Number" },
    { key: "child_name", label: "Child" },
    { key: "case_category", label: "Category", options: CASE_CATEGORY },
    { key: "status", label: "Status", options: CASE_STATUS },
    { key: "region", label: "Region" },
  ];
  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={800}>Cases</Typography>
          <Typography color="text.secondary">UC-02 Case Registration — all registered cases</Typography>
        </Box>
        <Button component={Link} to="/cases/new" variant="contained" startIcon={<PlusIcon />}>New Case</Button>
      </Stack>
      <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 3 }}>
        <TextField size="small" placeholder="Search by case number, child, or status"
          value={q} onChange={(e) => setQ(e.target.value)} sx={{ mb: 2, width: 360 }}
          InputProps={{ startAdornment: <SearchIcon fontSize="small" style={{ marginRight: 8 }} /> }} />
        <RecordTable columns={columns} rows={rows} onRowClick={(r) => nav(`/cases/${r.id}`)}
          empty={isLoading ? "Loading…" : "No cases yet. Register the first case."} />
      </Paper>
    </Box>
  );
}
