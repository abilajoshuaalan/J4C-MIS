/**
 * Palette matches the Visily mockups: deep plum/purple primary (buttons,
 * active nav item), soft lavender accents on the login split-screen,
 * plain white content areas. See ui/uc01.png and ui/appx_dashboard.png.
 */
import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    primary: {
      main: "#5B2A86",
      dark: "#3E1C5C",
      light: "#F3EAFB",
    },
    secondary: {
      main: "#8B5CF6",
    },
    background: {
      default: "#F7F5FA",
      paper: "#FFFFFF",
    },
    success: { main: "#2E7D32" },
    warning: { main: "#B7891A" },
    error: { main: "#B03A3A" },
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: '"Inter", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 800 },
    h4: { fontWeight: 800 },
    h5: { fontWeight: 700 },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: "none", fontWeight: 600, borderRadius: 8 },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: "none" },
      },
    },
  },
});
