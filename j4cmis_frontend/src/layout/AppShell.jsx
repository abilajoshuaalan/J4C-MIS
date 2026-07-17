import {
  Avatar, Box, Chip, Divider, IconButton, List, ListItemButton, ListItemIcon,
  ListItemText, Stack, Typography,
} from "@mui/material";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { navSections } from "./navConfig";
import { BellIcon, SettingsIcon, SignOutIcon, WifiIcon } from "../icons";

const SIDEBAR_WIDTH = 280;

function roleLabel(role) {
  return (
    {
      system_admin: "System Administrator",
      national_coordinator: "National Coordinator",
      regional_coordinator: "Regional Coordinator",
    }[role] || role
  );
}

export default function AppShell() {
  const { user, profile, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const displayName =
    [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.username;

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      <Box
        component="nav"
        sx={{
          width: SIDEBAR_WIDTH,
          flexShrink: 0,
          bgcolor: "#fff",
          borderRight: "1px solid #ECE7F3",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Box sx={{ p: 3, pb: 2 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Box
              sx={{
                width: 36, height: 36, borderRadius: "8px", bgcolor: "primary.main",
                display: "flex", alignItems: "center", justifyContent: "center",
                color: "#fff", fontWeight: 800,
              }}
            >
              J
            </Box>
            <Box>
              <Typography variant="subtitle2" fontWeight={800} lineHeight={1.1}>
                JLOS
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Justice for All
              </Typography>
            </Box>
          </Stack>
        </Box>

        <Box sx={{ flex: 1, overflowY: "auto", px: 1.5, pb: 2 }}>
          {navSections.map((section, i) => (
            <Box key={i} sx={{ mb: 1 }}>
              {section.heading && (
                <Typography
                  variant="overline"
                  sx={{ px: 1.5, color: "text.secondary", fontWeight: 700 }}
                >
                  {section.heading}
                </Typography>
              )}
              <List dense disablePadding>
                {section.items.map((item) => {
                  const active = location.pathname === item.path;
                  const Icon = item.icon;
                  return (
                    <ListItemButton
                      key={item.path}
                      component={Link}
                      to={item.path}
                      selected={active}
                      sx={{
                        borderRadius: 2,
                        mb: 0.5,
                        color: active ? "#fff" : "text.primary",
                        bgcolor: active ? "primary.main" : "transparent",
                        "&:hover": { bgcolor: active ? "primary.dark" : "primary.light" },
                        "&.Mui-selected": { bgcolor: "primary.main" },
                        "&.Mui-selected:hover": { bgcolor: "primary.dark" },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 34, color: active ? "#fff" : "text.secondary" }}>
                        <Icon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primaryTypographyProps={{ fontSize: 14, fontWeight: active ? 700 : 500 }}
                        primary={item.label}
                      />
                    </ListItemButton>
                  );
                })}
              </List>
            </Box>
          ))}
        </Box>

        <Divider />
        <Box sx={{ p: 1.5 }}>
          <ListItemButton component={Link} to="/settings" sx={{ borderRadius: 2 }}>
            <ListItemIcon sx={{ minWidth: 34 }}>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primaryTypographyProps={{ fontSize: 14 }} primary="Settings" />
          </ListItemButton>
          <ListItemButton
            onClick={() => {
              logout();
              navigate("/login");
            }}
            sx={{ borderRadius: 2, color: "error.main" }}
          >
            <ListItemIcon sx={{ minWidth: 34, color: "error.main" }}>
              <SignOutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primaryTypographyProps={{ fontSize: 14 }} primary="Sign Out" />
          </ListItemButton>
        </Box>
      </Box>

      <Box sx={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <Box
          component="header"
          sx={{
            height: 72, px: 3, display: "flex", alignItems: "center", justifyContent: "flex-end",
            gap: 2, borderBottom: "1px solid #ECE7F3", bgcolor: "#fff",
          }}
        >
          <Chip
            icon={<WifiIcon sx={{ fontSize: 16 }} />}
            label="Online"
            size="small"
            variant="outlined"
            sx={{ borderColor: "primary.light", color: "primary.main" }}
          />
          <IconButton size="small">
            <BellIcon fontSize="small" />
          </IconButton>
          <Stack direction="row" spacing={1.2} alignItems="center">
            <Box sx={{ textAlign: "right" }}>
              <Typography variant="body2" fontWeight={700} lineHeight={1.2}>
                {displayName}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {profile ? roleLabel(profile.role) : ""}
                {profile?.region ? ` — ${profile.region}` : ""}
              </Typography>
            </Box>
            <Avatar sx={{ bgcolor: "primary.light", color: "primary.main", fontWeight: 700 }}>
              {(displayName || "?").charAt(0).toUpperCase()}
            </Avatar>
          </Stack>
        </Box>

        <Box sx={{ flex: 1, p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
