import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, CssBaseline } from "@mui/material";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { theme } from "./theme/theme";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import AppShell from "./layout/AppShell";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ComingSoonPage from "./pages/ComingSoonPage";
import CasesListPage from "./pages/CasesListPage";
import CaseRegisterWizard from "./pages/CaseRegisterWizard";
import CaseDetailPage from "./pages/CaseDetailPage";
import ResourceListPage from "./pages/ResourceListPage";
import ResourceFormPage from "./pages/ResourceFormPage";
import { navSections } from "./layout/navConfig";
import { Box, CircularProgress } from "@mui/material";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <CircularProgress />
      </Box>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

// Modules with real generic list/form screens in this MVP.
const RESOURCE_PATHS = ["arrests", "classifications", "counselling-sessions", "civil-cases"];
// Paths handled explicitly below, so they must NOT fall through to the stub.
const IMPLEMENTED = new Set(["/cases", "/cases/new", ...RESOURCE_PATHS.map((r) => `/${r}`)]);

const stubPaths = navSections
  .flatMap((s) => s.items.map((i) => i.path))
  .filter((p) => p !== "/" && !IMPLEMENTED.has(p));

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="/" element={<DashboardPage />} />

        <Route path="/cases" element={<CasesListPage />} />
        <Route path="/cases/new" element={<CaseRegisterWizard />} />
        <Route path="/cases/:id" element={<CaseDetailPage />} />

        {RESOURCE_PATHS.map((r) => (
          <Route key={r}>
            <Route path={`/${r}`} element={<ResourceListPage resource={r} />} />
            <Route path={`/${r}/new`} element={<ResourceFormPage resource={r} />} />
            <Route path={`/${r}/:id`} element={<ResourceFormPage resource={r} />} />
          </Route>
        ))}

        {stubPaths.map((path) => (
          <Route key={path} path={path} element={<ComingSoonPage />} />
        ))}
        <Route path="/settings" element={<ComingSoonPage />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider>
            <AppRoutes />
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
