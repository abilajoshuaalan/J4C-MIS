/**
 * UC-01 Login. Layout matches ui/uc01.png: split screen, lavender
 * branding panel on the left with two feature callouts, form on the
 * right with email/password, "Remember this device" (FR-02), and a
 * secure-access-portal notice.
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Button, Checkbox, FormControlLabel, IconButton, InputAdornment,
  Link as MuiLink, Stack, TextField, Typography, Alert, Paper,
} from "@mui/material";
import { useAuth } from "../auth/AuthContext";
import { ShieldIcon, InfoIcon, MailIcon, LockIcon, EyeIcon } from "../icons";

export default function LoginPage() {
  const { login, error } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    const ok = await login(email, password, remember);
    setSubmitting(false);
    if (ok) navigate("/");
  };

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Box
        sx={{
          flex: 1, display: { xs: "none", md: "flex" }, flexDirection: "column",
          justifyContent: "center", px: 8,
          background: "linear-gradient(135deg, #F3EAFB 0%, #FBFAFE 100%)",
        }}
      >
        <Box sx={{ mb: 4 }}>
          <Box
            sx={{
              width: 64, height: 64, borderRadius: "12px", bgcolor: "primary.main",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#fff", fontWeight: 800, fontSize: 24,
            }}
          >
            J
          </Box>
        </Box>
        <Typography variant="h3" fontWeight={800} sx={{ mb: 1 }}>
          Justice for <Box component="span" sx={{ color: "primary.main" }}>Children</Box>
        </Typography>
        <Typography variant="h3" fontWeight={800} sx={{ mb: 3 }}>
          Management System
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 5, maxWidth: 440 }}>
          Streamlining child justice workflows through secure data management,
          integrated stakeholder collaboration, and advanced reporting.
        </Typography>
        <Stack direction="row" spacing={2}>
          <Paper sx={{ p: 2.5, flex: 1, borderRadius: 3 }} elevation={0} variant="outlined">
            <ShieldIcon sx={{ color: "primary.main", mb: 1 }} />
            <Typography fontWeight={700} sx={{ mb: 0.5 }}>Secure &amp; Encrypted</Typography>
            <Typography variant="body2" color="text.secondary">
              Standard-grade encryption for sensitive case records.
            </Typography>
          </Paper>
          <Paper sx={{ p: 2.5, flex: 1, borderRadius: 3 }} elevation={0} variant="outlined">
            <InfoIcon sx={{ mb: 1 }} />
            <Typography fontWeight={700} sx={{ mb: 0.5 }}>Unified Workflow</Typography>
            <Typography variant="body2" color="text.secondary">
              Connect police, social workers, and court officers.
            </Typography>
          </Paper>
        </Stack>
      </Box>

      <Box sx={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", p: 4 }}>
        <Box sx={{ width: "100%", maxWidth: 420 }}>
          <Typography variant="h4" fontWeight={800} sx={{ mb: 0.5 }}>Welcome</Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            Enter your credentials to access the management system.
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          <Box component="form" onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
              <Box>
                <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>Email Address</Typography>
                <TextField
                  fullWidth
                  type="email"
                  placeholder="you@j4c.gov.org"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start"><MailIcon fontSize="small" color="disabled" /></InputAdornment>
                    ),
                  }}
                />
              </Box>
              <Box>
                <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>Password</Typography>
                <TextField
                  fullWidth
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start"><LockIcon fontSize="small" color="disabled" /></InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowPassword((s) => !s)} edge="end" size="small">
                          <EyeIcon fontSize="small" />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <FormControlLabel
                  control={<Checkbox checked={remember} onChange={(e) => setRemember(e.target.checked)} />}
                  label={<Typography variant="body2">Remember this device</Typography>}
                />
                <MuiLink href="#" variant="body2" underline="hover">Forgot Password?</MuiLink>
              </Stack>
              <Button type="submit" variant="contained" size="large" disabled={submitting} sx={{ py: 1.4 }}>
                {submitting ? "Signing in…" : "Sign In"}
              </Button>
            </Stack>
          </Box>

          <Typography variant="body2" align="center" sx={{ mt: 3 }} color="text.secondary">
            Don&apos;t have an account? <MuiLink href="#" underline="hover">Request access</MuiLink>
          </Typography>

          <Box sx={{ mt: 4, pt: 3, borderTop: "1px solid #ECE7F3", textAlign: "center" }}>
            <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ letterSpacing: 1 }}>
              <ShieldIcon sx={{ fontSize: 14, verticalAlign: "middle", mr: 0.5 }} />
              SECURE ACCESS PORTAL
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
              This system is restricted to authorized personnel. All access attempts are
              logged and monitored. Unauthorized entry is subject to legal action under
              local data protection laws.
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
