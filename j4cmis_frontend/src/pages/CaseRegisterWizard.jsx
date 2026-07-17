import { useState } from "react";
import {
  Box, Button, Step, StepLabel, Stepper, MenuItem, Paper, Stack, TextField,
  Typography, Alert, Divider, FormControlLabel, Checkbox,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../api/client";
import { GENDER, DISABILITY, CASE_CATEGORY, CASE_STATUS } from "../config/enums";

const STEPS = ["Child & Category", "Guardian", "Case Context", "Review & Submit"];

export default function CaseRegisterWizard() {
  const nav = useNavigate();
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [child, setChild] = useState({ first_name: "", last_name: "", dob: "", gender: "", nationality: "Ugandan", disability_type: "none", is_albino: false, other_details: "" });
  const [guardian, setGuardian] = useState({ name: "", relationship: "", contact: "", legal_representation: "" });
  const [cse, setCse] = useState({ case_category: "", case_source: "", reg_datetime: "", description: "", status: "open", region: "", district: "" });

  const setC = (k, v) => setChild((s) => ({ ...s, [k]: v }));
  const setG = (k, v) => setGuardian((s) => ({ ...s, [k]: v }));
  const setK = (k, v) => setCse((s) => ({ ...s, [k]: v }));

  const canNext = () => {
    if (step === 0) return child.first_name && child.last_name && cse.case_category;
    return true;
  };

  const clean = (obj) => Object.fromEntries(Object.entries(obj).filter(([, v]) => v !== "" && v !== undefined));

  const submit = async () => {
    setBusy(true); setError("");
    try {
      const childBody = { ...clean(child) };
      if (child.dob) {
        const age = Math.floor((Date.now() - new Date(child.dob)) / (365.25 * 24 * 3600 * 1000));
        if (age >= 0 && age < 130) childBody.age = age;
      }
      const childRes = await apiClient.post("/children/", childBody);
      const childId = childRes.data.id;
      if (guardian.name && guardian.relationship) {
        await apiClient.post("/guardians/", { ...clean(guardian), child: childId });
      }
      const caseBody = { ...clean(cse), child: childId };
      const caseRes = await apiClient.post("/cases/", caseBody);
      nav(`/cases/${caseRes.data.id}`);
    } catch (e) {
      const d = e.response?.data;
      setError(d ? `Could not save: ${JSON.stringify(d)}` : "Could not save. Check the form and try again.");
      setBusy(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 820, mx: "auto" }}>
      <Typography variant="h4" fontWeight={800} sx={{ mb: 0.5 }}>Register a Case</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>UC-02 Case Registration</Typography>
      <Stepper activeStep={step} sx={{ mb: 3 }}>
        {STEPS.map((s) => <Step key={s}><StepLabel>{s}</StepLabel></Step>)}
      </Stepper>
      <Paper variant="outlined" sx={{ p: 3, borderRadius: 3 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {step === 0 && (
          <Stack spacing={2}>
            <Typography fontWeight={700}>Child details</Typography>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth required label="First Name" value={child.first_name} onChange={(e) => setC("first_name", e.target.value)} />
              <TextField fullWidth required label="Last Name" value={child.last_name} onChange={(e) => setC("last_name", e.target.value)} />
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth type="date" label="Date of Birth" InputLabelProps={{ shrink: true }} value={child.dob} onChange={(e) => setC("dob", e.target.value)} />
              <TextField select fullWidth label="Gender" value={child.gender} onChange={(e) => setC("gender", e.target.value)}>
                <MenuItem value=""><em>—</em></MenuItem>
                {GENDER.map(([v, l]) => <MenuItem key={v} value={v}>{l}</MenuItem>)}
              </TextField>
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth label="Nationality" value={child.nationality} onChange={(e) => setC("nationality", e.target.value)} />
              <TextField select fullWidth label="Disability" value={child.disability_type} onChange={(e) => setC("disability_type", e.target.value)}>
                {DISABILITY.map(([v, l]) => <MenuItem key={v} value={v}>{l}</MenuItem>)}
              </TextField>
            </Stack>
            <FormControlLabel control={<Checkbox checked={child.is_albino} onChange={(e) => setC("is_albino", e.target.checked)} />} label="Child is albino" />
            <Divider />
            <Typography fontWeight={700}>Case category</Typography>
            <TextField select fullWidth required label="Case Category" value={cse.case_category} onChange={(e) => setK("case_category", e.target.value)}>
              <MenuItem value=""><em>—</em></MenuItem>
              {CASE_CATEGORY.map(([v, l]) => <MenuItem key={v} value={v}>{l}</MenuItem>)}
            </TextField>
          </Stack>
        )}

        {step === 1 && (
          <Stack spacing={2}>
            <Typography fontWeight={700}>Guardian details (optional)</Typography>
            <Typography variant="body2" color="text.secondary">Leave blank if no guardian is being recorded now.</Typography>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth label="Guardian Name" value={guardian.name} onChange={(e) => setG("name", e.target.value)} />
              <TextField fullWidth label="Relationship" value={guardian.relationship} onChange={(e) => setG("relationship", e.target.value)} />
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth label="Contact" value={guardian.contact} onChange={(e) => setG("contact", e.target.value)} />
              <TextField fullWidth label="Legal Representation" value={guardian.legal_representation} onChange={(e) => setG("legal_representation", e.target.value)} />
            </Stack>
          </Stack>
        )}

        {step === 2 && (
          <Stack spacing={2}>
            <Typography fontWeight={700}>Case context and source</Typography>
            <TextField fullWidth label="Case Source" placeholder="Police (CID/CFPU), ODPP, court, remand home…" value={cse.case_source} onChange={(e) => setK("case_source", e.target.value)} />
            <TextField fullWidth type="datetime-local" label="Registration Date & Time" InputLabelProps={{ shrink: true }} value={cse.reg_datetime} onChange={(e) => setK("reg_datetime", e.target.value)} />
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField fullWidth label="Region" value={cse.region} onChange={(e) => setK("region", e.target.value)} />
              <TextField fullWidth label="District" value={cse.district} onChange={(e) => setK("district", e.target.value)} />
            </Stack>
            <TextField select fullWidth label="Status" value={cse.status} onChange={(e) => setK("status", e.target.value)}>
              {CASE_STATUS.map(([v, l]) => <MenuItem key={v} value={v}>{l}</MenuItem>)}
            </TextField>
            <TextField fullWidth multiline minRows={3} label="Description" value={cse.description} onChange={(e) => setK("description", e.target.value)} />
          </Stack>
        )}

        {step === 3 && (
          <Stack spacing={1.5}>
            <Typography fontWeight={700}>Review</Typography>
            <Typography variant="body2"><b>Child:</b> {child.first_name} {child.last_name} {child.dob ? `(DOB ${child.dob})` : ""}</Typography>
            <Typography variant="body2"><b>Category:</b> {CASE_CATEGORY.find((c) => c[0] === cse.case_category)?.[1] || "—"}</Typography>
            <Typography variant="body2"><b>Guardian:</b> {guardian.name ? `${guardian.name} (${guardian.relationship})` : "None"}</Typography>
            <Typography variant="body2"><b>Source:</b> {cse.case_source || "—"}</Typography>
            <Typography variant="body2"><b>Region/District:</b> {cse.region || "—"} / {cse.district || "—"}</Typography>
            <Typography variant="body2" color="text.secondary">A case number is generated automatically on submit.</Typography>
          </Stack>
        )}

        <Divider sx={{ my: 3 }} />
        <Stack direction="row" justifyContent="space-between">
          <Button disabled={step === 0 || busy} onClick={() => setStep((s) => s - 1)}>Back</Button>
          {step < STEPS.length - 1 ? (
            <Button variant="contained" disabled={!canNext()} onClick={() => setStep((s) => s + 1)}>Next</Button>
          ) : (
            <Button variant="contained" disabled={busy} onClick={submit}>{busy ? "Submitting…" : "Submit Case"}</Button>
          )}
        </Stack>
      </Paper>
    </Box>
  );
}
