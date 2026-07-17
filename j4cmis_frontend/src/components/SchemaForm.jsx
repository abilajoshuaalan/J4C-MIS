import { useState } from "react";
import {
  Box, Button, Checkbox, FormControlLabel, MenuItem, Stack, TextField,
  Typography, Alert, CircularProgress,
} from "@mui/material";
import { useList, uploadDocument } from "../api/hooks";
import { cleanPayload } from "../lib/schemas";

function caseLabel(c) {
  return `${c.case_number || "(unsubmitted)"} — ${c.child_name || ""}`.trim();
}

// A document upload field. Uploads to /documents/ against the resolved
// case id and stores the returned document id in the field value.
function DocumentField({ field, caseId, value, onChange }) {
  const [busy, setBusy] = useState(false);
  const [name, setName] = useState("");
  const [err, setErr] = useState("");
  const handle = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!caseId) { setErr("Select a case first, then upload."); return; }
    setErr(""); setBusy(true);
    try {
      const doc = await uploadDocument(caseId, file, field.label);
      onChange(doc.id);
      setName(file.name);
    } catch {
      setErr("Upload failed. Check the file and try again.");
    } finally {
      setBusy(false);
    }
  };
  return (
    <Box>
      <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>{field.label}</Typography>
      <Stack direction="row" spacing={1.5} alignItems="center">
        <Button component="label" variant="outlined" size="small" disabled={busy || !caseId}>
          {busy ? <CircularProgress size={16} /> : "Choose file"}
          <input type="file" hidden onChange={handle} />
        </Button>
        <Typography variant="body2" color={value ? "success.main" : "text.secondary"}>
          {value ? `Uploaded: ${name || "document #" + value}` : (caseId ? "No file selected" : "Select a case first")}
        </Typography>
      </Stack>
      {err && <Typography variant="caption" color="error">{err}</Typography>}
    </Box>
  );
}

export default function SchemaForm({ fields, initial, hiddenValues, submitLabel = "Save", onSubmit, submitting, error }) {
  const [values, setValues] = useState(() => ({ ...(initial || {}) }));
  const [touchedErr, setTouchedErr] = useState("");
  const casesQ = useList("cases");
  const cases = casesQ.data?.results || [];
  const caseId = hiddenValues?.case ?? values.case;

  const set = (name, v) => setValues((s) => ({ ...s, [name]: v }));

  const submit = (e) => {
    e.preventDefault();
    for (const f of fields) {
      const isHidden = hiddenValues && f.name in hiddenValues;
      if (f.required && !isHidden && !values[f.name]) {
        setTouchedErr(`${f.label} is required.`);
        return;
      }
    }
    setTouchedErr("");
    onSubmit({ ...cleanPayload(values), ...(hiddenValues || {}) });
  };

  const visible = fields.filter((f) => !(hiddenValues && f.name in hiddenValues));

  return (
    <Box component="form" onSubmit={submit}>
      {(touchedErr || error) && <Alert severity="error" sx={{ mb: 2 }}>{touchedErr || error}</Alert>}
      <Stack spacing={2}>
        {visible.map((f) => {
          const v = values[f.name] ?? "";
          if (f.type === "select") {
            return (
              <TextField key={f.name} select fullWidth label={f.label} value={v}
                required={f.required} onChange={(e) => set(f.name, e.target.value)}>
                <MenuItem value=""><em>—</em></MenuItem>
                {f.options.map(([val, lab]) => <MenuItem key={val} value={val}>{lab}</MenuItem>)}
              </TextField>
            );
          }
          if (f.type === "case") {
            return (
              <TextField key={f.name} select fullWidth label={f.label} value={v}
                required={f.required} onChange={(e) => set(f.name, e.target.value)}
                helperText={casesQ.isLoading ? "Loading cases…" : "Pick the case this record belongs to"}>
                <MenuItem value=""><em>—</em></MenuItem>
                {cases.map((c) => <MenuItem key={c.id} value={c.id}>{caseLabel(c)}</MenuItem>)}
              </TextField>
            );
          }
          if (f.type === "document") {
            return <DocumentField key={f.name} field={f} caseId={caseId} value={values[f.name]} onChange={(id) => set(f.name, id)} />;
          }
          if (f.type === "checkbox") {
            return (
              <FormControlLabel key={f.name}
                control={<Checkbox checked={!!values[f.name]} onChange={(e) => set(f.name, e.target.checked)} />}
                label={f.label} />
            );
          }
          const typeMap = { text: "text", textarea: "text", number: "number", date: "date", time: "time", datetime: "datetime-local" };
          return (
            <TextField key={f.name} fullWidth label={f.label} type={typeMap[f.type] || "text"}
              value={v} required={f.required} multiline={f.type === "textarea"} minRows={f.type === "textarea" ? 2 : undefined}
              onChange={(e) => set(f.name, e.target.value)}
              InputLabelProps={["date", "time", "datetime"].includes(f.type) ? { shrink: true } : undefined} />
          );
        })}
        <Box>
          <Button type="submit" variant="contained" disabled={submitting}>
            {submitting ? "Saving…" : submitLabel}
          </Button>
        </Box>
      </Stack>
    </Box>
  );
}
