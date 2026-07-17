import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import {
  Box, Paper, Stack, Typography, Chip, Tabs, Tab, Grid, Button, Divider,
  MenuItem, TextField, Alert, CircularProgress,
} from "@mui/material";
import { useOne, useCreate, useUpdate } from "../api/hooks";
import SchemaForm from "../components/SchemaForm";
import RecordTable from "../components/RecordTable";
import { RESOURCES } from "../lib/schemas";
import { CASE_STATUS, CASE_CATEGORY, labelOf } from "../config/enums";

function Info({ label, value }) {
  return (
    <Grid item xs={12} sm={6} md={4}>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Typography variant="body2" fontWeight={600}>{value || "—"}</Typography>
    </Grid>
  );
}

// Add-record form for a case sub-resource; refetches the case on success.
function AddRecord({ resource, caseId, onDone }) {
  const create = useCreate(resource);
  const [err, setErr] = useState("");
  const fields = RESOURCES[resource].fields;
  return (
    <SchemaForm
      fields={fields}
      hiddenValues={{ case: caseId }}
      submitLabel={`Add ${RESOURCES[resource].singular}`}
      submitting={create.isPending}
      error={err}
      onSubmit={(body) => {
        setErr("");
        create.mutate(body, {
          onSuccess: onDone,
          onError: (e) => setErr(e.response?.data ? JSON.stringify(e.response.data) : "Save failed."),
        });
      }}
    />
  );
}

function OneToOneTab({ record, resource, caseId, onDone }) {
  if (record) {
    const entries = Object.entries(record).filter(([k]) => !["id", "case", "created_at", "updated_at", "incomplete_data_flag", "missing_fields"].includes(k));
    return (
      <Grid container spacing={2}>
        {entries.map(([k, v]) => <Info key={k} label={k.replaceAll("_", " ")} value={typeof v === "object" ? JSON.stringify(v) : String(v ?? "")} />)}
      </Grid>
    );
  }
  return <AddRecord resource={resource} caseId={caseId} onDone={onDone} />;
}

export default function CaseDetailPage() {
  const { id } = useParams();
  const qc = useQueryClient();
  const { data: c, isLoading, refetch } = useOne("cases", id);
  const updateCase = useUpdate("cases");
  const [tab, setTab] = useState(0);
  const refresh = () => { qc.invalidateQueries({ queryKey: ["cases"] }); refetch(); };

  if (isLoading) return <Stack alignItems="center" sx={{ py: 8 }}><CircularProgress /></Stack>;
  if (!c) return <Alert severity="error">Case not found.</Alert>;

  const child = c.child || {};
  const counsellings = c.counselling_sessions || [];
  const civils = c.civil_cases || [];

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={800}>{c.case_number}</Typography>
          <Typography color="text.secondary">{child.first_name} {child.last_name} · {labelOf(CASE_CATEGORY, c.case_category)}</Typography>
        </Box>
        <Button component={Link} to="/cases" variant="outlined">Back to Cases</Button>
      </Stack>

      <Paper variant="outlined" sx={{ borderRadius: 3 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ borderBottom: "1px solid #ECE7F3", px: 2 }} variant="scrollable">
          <Tab label="Overview" />
          <Tab label="Arrest (UC-03)" />
          <Tab label="Classification (UC-04)" />
          <Tab label={`Counselling (${counsellings.length})`} />
          <Tab label={`Civil Case (${civils.length})`} />
        </Tabs>
        <Box sx={{ p: 3 }}>
          {tab === 0 && (
            <Box>
              <Typography fontWeight={700} sx={{ mb: 1 }}>Child</Typography>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Info label="Name" value={`${child.first_name || ""} ${child.last_name || ""}`} />
                <Info label="Date of birth" value={child.dob} />
                <Info label="Gender" value={child.gender} />
                <Info label="Nationality" value={child.nationality} />
              </Grid>
              <Divider sx={{ my: 2 }} />
              <Typography fontWeight={700} sx={{ mb: 1 }}>Case</Typography>
              <Grid container spacing={2} alignItems="center">
                <Info label="Source" value={c.case_source} />
                <Info label="Region" value={c.region} />
                <Info label="District" value={c.district} />
                <Grid item xs={12} sm={6} md={4}>
                  <TextField select size="small" fullWidth label="Status" value={c.status}
                    onChange={(e) => updateCase.mutate({ id, body: { status: e.target.value } }, { onSuccess: refresh })}>
                    {CASE_STATUS.map(([v, l]) => <MenuItem key={v} value={v}>{l}</MenuItem>)}
                  </TextField>
                </Grid>
              </Grid>
              {c.description && <Typography variant="body2" sx={{ mt: 2 }}>{c.description}</Typography>}
            </Box>
          )}
          {tab === 1 && <OneToOneTab record={c.arrest} resource="arrests" caseId={id} onDone={refresh} />}
          {tab === 2 && <OneToOneTab record={c.classification} resource="classifications" caseId={id} onDone={refresh} />}
          {tab === 3 && (
            <Stack spacing={3}>
              <RecordTable columns={RESOURCES["counselling-sessions"].columns.filter((x) => x.kind !== "caseref")} rows={counsellings} empty="No counselling sessions yet." />
              <Divider textAlign="left"><Typography variant="caption">Add session</Typography></Divider>
              <AddRecord resource="counselling-sessions" caseId={id} onDone={refresh} />
            </Stack>
          )}
          {tab === 4 && (
            <Stack spacing={3}>
              <RecordTable columns={RESOURCES["civil-cases"].columns.filter((x) => x.kind !== "caseref")} rows={civils} empty="No civil cases yet." />
              <Divider textAlign="left"><Typography variant="caption">Add civil case</Typography></Divider>
              <AddRecord resource="civil-cases" caseId={id} onDone={refresh} />
            </Stack>
          )}
        </Box>
      </Paper>
    </Box>
  );
}
