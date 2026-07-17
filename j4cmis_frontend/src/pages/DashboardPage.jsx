/**
 * Dashboard (ui/appx_dashboard.png). Live data via React Query from the
 * real endpoints already verified against the backend: /api/cases/ for
 * counts and recent activity, /api/cases/{id}/timeline/ pattern reused
 * per-row is avoided — this list is intentionally flat (list serializer),
 * matching "Recent Case Activity" in the mockup which shows summary
 * columns only, not full case detail.
 */
import { useQuery } from "@tanstack/react-query";
import {
  Box, Card, Chip, Grid, Paper, Stack, Table, TableBody, TableCell,
  TableHead, TableRow, Typography, Button,
} from "@mui/material";
import { Link } from "react-router-dom";
import { apiClient } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { CasesIcon, PlusIcon, ReportingIcon, UserIcon } from "../icons";

const STATUS_COLORS = {
  open: "default",
  at_pswo: "warning",
  at_dpp: "warning",
  at_court: "info",
  on_remand: "error",
  in_rehabilitation: "info",
  resettled: "success",
  closed: "default",
};

function StatCard({ label, value, delta }) {
  return (
    <Card variant="outlined" sx={{ p: 2.5, borderRadius: 3, flex: 1 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Typography variant="caption" color="text.secondary">{delta}</Typography>
      </Stack>
      <Typography color="text.secondary" sx={{ mt: 1 }}>{label}</Typography>
      <Typography variant="h4" fontWeight={800}>{value}</Typography>
    </Card>
  );
}

export default function DashboardPage() {
  const { user, profile } = useAuth();
  const displayName = user?.first_name || user?.username;

  const { data: cases } = useQuery({
    queryKey: ["cases", "dashboard"],
    queryFn: async () => (await apiClient.get("/cases/", { params: { page_size: 200 } })).data,
  });

  const results = cases?.results || [];
  const total = cases?.count ?? results.length;
  const open = results.filter((c) => c.status !== "closed").length;
  const atPswo = results.filter((c) => c.status === "at_pswo").length;
  const atCourt = results.filter((c) => c.status === "at_court").length;
  const recent = [...results].sort((a, b) => (b.reg_datetime || "").localeCompare(a.reg_datetime || "")).slice(0, 8);

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={800}>System Overview</Typography>
          <Typography color="text.secondary">
            Welcome back{displayName ? `, ${displayName}` : ""}. Here is what&apos;s happening today.
          </Typography>
        </Box>
        <Button component={Link} to="/cases/new" variant="contained" startIcon={<PlusIcon />}>
          New Case
        </Button>
      </Stack>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Total Active Cases" value={total} delta="" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Open Cases" value={open} delta="" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Awaiting PSWO" value={atPswo} delta="" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="At Court" value={atCourt} delta="" />
        </Grid>
      </Grid>

      {profile?.role === "regional_coordinator" && profile?.region && (
        <Chip
          icon={<UserIcon sx={{ fontSize: 16 }} />}
          label={`Showing cases for ${profile.region} region only`}
          size="small"
          sx={{ mb: 2 }}
        />
      )}

      <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 3, mb: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
          <Box>
            <Typography variant="h6" fontWeight={700}>Recent Case Activity</Typography>
            <Typography variant="body2" color="text.secondary">Tracking real-time updates across the MIS</Typography>
          </Box>
          <Button component={Link} to="/cases" size="small">View All Activity</Button>
        </Stack>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Case Number</TableCell>
              <TableCell>Child</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Region</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recent.map((c) => (
              <TableRow key={c.id} hover component={Link} to={`/cases/${c.id}`} sx={{ textDecoration: "none" }}>
                <TableCell sx={{ fontWeight: 700 }}>{c.case_number}</TableCell>
                <TableCell>{c.child_name}</TableCell>
                <TableCell sx={{ textTransform: "capitalize" }}>{c.case_category?.replaceAll("_", " ")}</TableCell>
                <TableCell>
                  <Chip
                    label={c.status?.replaceAll("_", " ")}
                    size="small"
                    color={STATUS_COLORS[c.status] || "default"}
                    sx={{ textTransform: "capitalize" }}
                  />
                </TableCell>
                <TableCell>{c.region}</TableCell>
              </TableRow>
            ))}
            {recent.length === 0 && (
              <TableRow>
                <TableCell colSpan={5}>
                  <Stack alignItems="center" spacing={1} sx={{ py: 4 }}>
                    <CasesIcon sx={{ fontSize: 32, color: "text.disabled" }} />
                    <Typography color="text.secondary">No cases yet. Register the first case to get started.</Typography>
                  </Stack>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Paper>

      <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 3 }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
          <ReportingIcon color="primary" />
          <Typography variant="h6" fontWeight={700}>Quick Actions</Typography>
        </Stack>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <Button component={Link} to="/cases/new" variant="outlined" sx={{ flex: 1, justifyContent: "flex-start", py: 1.5 }}>
            Register a new child case
          </Button>
          <Button component={Link} to="/reporting" variant="outlined" sx={{ flex: 1, justifyContent: "flex-start", py: 1.5 }}>
            Generate a report
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
