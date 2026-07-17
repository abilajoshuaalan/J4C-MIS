import { Table, TableBody, TableCell, TableHead, TableRow, Chip, Stack, Typography, Box } from "@mui/material";
import { labelOf } from "../config/enums";

// columns: [{key,label,options?,kind?}]. casesById maps case id -> case obj.
export default function RecordTable({ columns, rows, casesById, onRowClick, empty }) {
  if (!rows || rows.length === 0) {
    return (
      <Box sx={{ py: 5, textAlign: "center" }}>
        <Typography color="text.secondary">{empty || "No records yet."}</Typography>
      </Box>
    );
  }
  const render = (row, col) => {
    const val = row[col.key];
    if (col.kind === "caseref") {
      const c = casesById?.[val];
      return c ? `${c.case_number} — ${c.child_name || ""}` : (val ?? "");
    }
    if (col.options) return <Chip size="small" label={labelOf(col.options, val)} />;
    if (typeof val === "string" && val.includes("T")) return val.replace("T", " ").slice(0, 16);
    return val ?? "";
  };
  return (
    <Table size="small">
      <TableHead>
        <TableRow>{columns.map((c) => <TableCell key={c.key}>{c.label}</TableCell>)}</TableRow>
      </TableHead>
      <TableBody>
        {rows.map((row) => (
          <TableRow key={row.id} hover onClick={() => onRowClick?.(row)} sx={{ cursor: onRowClick ? "pointer" : "default" }}>
            {columns.map((c) => <TableCell key={c.key}>{render(row, c)}</TableCell>)}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
