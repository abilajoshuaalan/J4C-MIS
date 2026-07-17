import { Box, Paper, Typography } from "@mui/material";
import { useLocation } from "react-router-dom";

/**
 * Stub for use cases not yet built in this batch. Nav is complete (every
 * item in navConfig.js routes somewhere) even before every screen exists,
 * so reviewers can see the full IA and click through without dead links.
 */
export default function ComingSoonPage() {
  const location = useLocation();
  return (
    <Paper variant="outlined" sx={{ p: 6, borderRadius: 3, textAlign: "center" }}>
      <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>
        Screen not built yet
      </Typography>
      <Typography color="text.secondary">
        {location.pathname} is scheduled in a later delivery batch.
      </Typography>
      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="text.secondary">
          The API endpoint behind this screen is already live — only the UI is pending.
        </Typography>
      </Box>
    </Paper>
  );
}
