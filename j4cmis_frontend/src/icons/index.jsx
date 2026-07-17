/**
 * Hand-authored icon set (24x24 stroke-style, matching the mockups' thin
 * line icons — see ui/appx_dashboard.png sidebar). Deliberately not
 * pulling in @mui/icons-material or lucide-react: both ship 3,000+ tiny
 * files, which repeatedly corrupted during install/copy in this build
 * environment's filesystem. This set covers everything the 27 use cases'
 * sidebar + top bar need; add more paths here as new screens require them
 * rather than reintroducing a large icon package.
 */
import SvgIcon from "@mui/material/SvgIcon";

const make = (path, viewBox = "0 0 24 24") => (props) =>
  (
    <SvgIcon {...props} viewBox={viewBox}>
      {path}
    </SvgIcon>
  );

export const DashboardIcon = make(
  <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" />
);
export const CasesIcon = make(
  <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
);
export const ArrestIcon = make(
  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z" />
);
export const ClassificationIcon = make(
  <path d="M12 2l-5.5 9h11L12 2zm0 3.84L13.93 9h-3.86L12 5.84zM17.5 13c-2.49 0-4.5 2.01-4.5 4.5s2.01 4.5 4.5 4.5 4.5-2.01 4.5-4.5-2.01-4.5-4.5-4.5zM3 21.5h8v-8H3v8z" />
);
export const PswoIcon = make(
  <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" />
);
export const DppIcon = make(
  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 11.9 13 12.5 13 14h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z" />
);
export const CourtIcon = make(
  <path d="M12 3L2 8l10 5 10-5-10-5zM2 14l10 5 10-5M2 11l10 5 10-5" />
);
export const RemandIcon = make(
  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-1 14l-4-4 1.41-1.41L11 12.17l5.59-5.59L18 8l-7 7z" />
);
export const LegalRepIcon = make(
  <path d="M12 2l1.5 4.5H18l-3.5 3 1.3 4.5L12 11.5 8.2 14l1.3-4.5-3.5-3h4.5L12 2zM5 20h14v2H5z" />
);
export const MeetingsIcon = make(
  <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z" />
);
export const TrainingIcon = make(
  <path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z" />
);
export const DocumentsIcon = make(
  <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z" />
);
export const ReportingIcon = make(
  <path d="M5 9.2h3V19H5V9.2zM10.6 5h2.8v14h-2.8V5zm5.6 8H19v6h-2.8v-6z" />
);
export const RehabIcon = make(
  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
);
export const ResettlementIcon = make(
  <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
);
export const BreastfeedingIcon = make(
  <path d="M12 2a5 5 0 015 5c0 2.5-1.8 4.4-3.5 6-1 .95-2 1.85-2.5 3-.5-1.15-1.5-2.05-2.5-3C6.8 11.4 5 9.5 5 7a5 5 0 017-5zm-1 18h2v-2h-2v2z" />
);
export const FacilityInspectionIcon = make(
  <path d="M12 2L3 7v6c0 5.5 3.8 10.7 9 12 5.2-1.3 9-6.5 9-12V7l-9-5zm-1 13.5L7.5 12l1.4-1.4L11 12.7l4.1-4.1L16.5 10 11 15.5z" />
);
export const SuspectParadeIcon = make(
  <path d="M16 4c0-1.11.89-2 2-2s2 .89 2 2-.89 2-2 2-2-.89-2-2zM4 4c0-1.11.89-2 2-2s2 .89 2 2-.89 2-2 2-2-.89-2-2zm6 2c0-1.11.89-2 2-2s2 .89 2 2-.89 2-2 2-2-.89-2-2zm-6 5.5c0-1.4 2.7-2.5 6-2.5s6 1.1 6 2.5V17H4v-5.5z" />
);
export const DiversionIcon = make(
  <path d="M14.59 8L12 5.41 9.41 8H6V4h3.41L12 1.41 14.59 4H18v4h-3.41zM7 10h2v9H7v-9zm4 0h2v9h-2v-9zm4 0h2v9h-2v-9z" />
);
export const ReferralIcon = make(
  <path d="M14 12c0-1.1-.9-2-2-2s-2 .9-2 2 .9 2 2 2 2-.9 2-2zm-2-10a10 10 0 100 20 10 10 0 000-20zm0 18a8 8 0 118-8 8 8 0 01-8 8z" />
);
export const ChildCareIcon = make(
  <path d="M12 3a3 3 0 013 3c0 1.31-.84 2.42-2 2.83V10h2a4 4 0 014 4v2h-2v-2a2 2 0 00-2-2h-2v7h-2v-7H9a2 2 0 00-2 2v2H5v-2a4 4 0 014-4h2V8.83A3 3 0 019 6a3 3 0 013-3z" />
);
export const SettingsIcon = make(
  <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.5.5 0 00.12-.61l-1.92-3.32a.5.5 0 00-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.5.5 0 00-.5-.42h-3.84a.5.5 0 00-.5.42l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.5.5 0 00-.59.22L2.71 8.87a.5.5 0 00.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.5.5 0 00-.12.61l1.92 3.32c.12.22.39.3.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.25.42.5.42h3.84c.25 0 .46-.18.5-.42l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.23.09.49 0 .59-.22l1.92-3.32a.5.5 0 00-.12-.61l-2.01-1.58zM12 15.6A3.6 3.6 0 1112 8.4a3.6 3.6 0 010 7.2z" />
);
export const SignOutIcon = make(
  <path d="M17 7l-1.41 1.41L17.17 10H9v2h8.17l-1.58 1.58L17 15l4-4-4-4zM5 5h7V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h7v-2H5V5z" />
);
export const BellIcon = make(
  <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" />
);
export const WifiIcon = make(
  <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3a4.237 4.237 0 00-6 0zm-4-4l2 2a7.074 7.074 0 0110 0l2-2C15.14 9.14 8.87 9.14 5 13z" />
);
export const ChevronRightIcon = make(<path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6z" />);
export const PlusIcon = make(<path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />);
export const SearchIcon = make(
  <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
);
export const AlertIcon = make(
  <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
);
export const CheckIcon = make(<path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />);
export const UserIcon = make(
  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
);
export const EyeIcon = make(
  <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17a5 5 0 110-10 5 5 0 010 10zm0-8a3 3 0 100 6 3 3 0 000-6z" />
);
export const LockIcon = make(
  <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm3 9a2 2 0 110-4 2 2 0 010 4z" />
);
export const MailIcon = make(
  <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" />
);
export const ShieldIcon = make(
  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
);
export const InfoIcon = make(
  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
);
