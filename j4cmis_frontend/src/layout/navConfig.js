/**
 * Sidebar structure transcribed directly from ui/appx_dashboard.png.
 * Grouped sections match the mockup exactly: Cases, Meetings & Capacity,
 * Documents, Services & Support, Diversion Management. Paths map to
 * batches from the project's build plan; routes not yet built (later
 * batches) still appear in nav but render a "coming in batch N" stub so
 * navigation is complete even before every screen exists.
 */
import {
  DashboardIcon, CasesIcon, ArrestIcon, ClassificationIcon, PswoIcon, DppIcon,
  CourtIcon, RemandIcon, LegalRepIcon, MeetingsIcon, TrainingIcon, DocumentsIcon,
  ReportingIcon, RehabIcon, ResettlementIcon, BreastfeedingIcon,
  FacilityInspectionIcon, SuspectParadeIcon, DiversionIcon, ReferralIcon, ChildCareIcon,
} from "../icons";

export const navSections = [
  {
    items: [{ label: "Dashboard", path: "/", icon: DashboardIcon }],
  },
  {
    heading: "Cases",
    items: [
      { label: "Case Registration", path: "/cases/new", icon: CasesIcon },
      { label: "Case List", path: "/cases", icon: CasesIcon },
      { label: "Arrest Details", path: "/arrests", icon: ArrestIcon },
      { label: "Classification", path: "/classifications", icon: ClassificationIcon },
      { label: "PSWO Social Inquiry", path: "/social-inquiry-reports", icon: PswoIcon },
      { label: "DPP / RSA Routing", path: "/dpp-routings", icon: DppIcon },
      { label: "Court Routing & Tracking", path: "/court-proceedings", icon: CourtIcon },
      { label: "Remand & Placement", path: "/remand-placements", icon: RemandIcon },
      { label: "Legal Representation", path: "/legal-representations", icon: LegalRepIcon },
      { label: "Civil Case Management", path: "/civil-cases", icon: CourtIcon },
    ],
  },
  {
    heading: "Meetings & Capacity",
    items: [
      { label: "Meetings Management", path: "/chain-linked-activities", icon: MeetingsIcon },
      { label: "Capacity Building & Training", path: "/trainings", icon: TrainingIcon },
    ],
  },
  {
    heading: "Documents",
    items: [
      { label: "Document Management", path: "/documents", icon: DocumentsIcon },
      { label: "Reporting & Analytics", path: "/reporting", icon: ReportingIcon },
    ],
  },
  {
    heading: "Services & Support",
    items: [
      { label: "Rehabilitation Management", path: "/rehabilitations", icon: RehabIcon },
      { label: "Breastfeeding Mothers", path: "/breastfeeding-mothers", icon: BreastfeedingIcon },
      { label: "Facility Inspection", path: "/facility-inspections", icon: FacilityInspectionIcon },
      { label: "Suspect Parade", path: "/suspect-parades", icon: SuspectParadeIcon },
      { label: "Community Service", path: "/community-services", icon: ResettlementIcon },
      { label: "Counselling Management", path: "/counselling-sessions", icon: PswoIcon },
    ],
  },
  {
    heading: "Diversion Management",
    items: [
      { label: "Plan Management", path: "/diversion-plans", icon: DiversionIcon },
      { label: "Referral Institutions", path: "/referral-institutions", icon: ReferralIcon },
      { label: "Child-Friendly Spaces", path: "/child-friendly-spaces", icon: ChildCareIcon },
    ],
  },
];
