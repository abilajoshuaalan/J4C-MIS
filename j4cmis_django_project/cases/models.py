"""
J4CMIS domain models — rebuilt against Use Case Specification v4 / SRS v2.2
(J4C-MIS-SRS.md), which is the project's confirmed source of truth.

Supersedes the earlier build against erd.drawio, which was the older
"change-log applied" version (civil cases removed, 2-way case_type, 8
invented roles). Key v4 differences reflected here:
  - Case category is {Child Victim or Witness, Juvenile Accused, Vulnerable}
    (FR-07), not {victim, juvenile_accused}.
  - Civil cases ARE in scope (offence category includes Civil, FR-15).
  - Child age range is 0-17 (FR-12) — no age gate at intake, flagged as an
    exception if outside range, never blocks submission.
  - Roles are exactly System Admin, National Coordinator, Regional
    Coordinator (FR-06); Regional Coordinators are restricted to their
    region (NFR-06).
  - Victim Impact Assessment (UC-06) is a distinct entity from the Social
    Inquiry Report (UC-05), for child-victim cases.
  - Legal Representation Management (UC-25) is a distinct tracked entity.
  - Counselling Management (UC-26) and Civil Case Management (UC-27) are
    distinct tracked entities per SRS v1.4.
  - Chain-Linked Initiative (UC-19) meetings, Rehabilitation (UC-20),
    Capacity Building & Training (UC-21), Breastfeeding Mothers (UC-22),
    Suspect Parade (UC-23), Facility Inspection (UC-24), and Community
    Service (UC-28) match the richer v4 field lists. Resettlement was
    removed in SRS v1.4.
  - Status history / audit trail (FR-54, FR-57) is modeled explicitly via
    CaseStatusHistory, powering the case timeline (UC-12).

Some v4 fields are described as multi-select lists in prose (e.g. UC-18
"participants and organisations", UC-26 "support provided") and are
modeled here as TextField/CharField-with-choices rather than separate
many-to-many tables, to keep v1 shippable. Flagged in README as an open
item to revisit if reporting needs per-value filtering later.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# ---------------------------------------------------------------------------
# Shared mixins
# ---------------------------------------------------------------------------

class IncompleteDataMixin(models.Model):
    """Mandatory fields are still enforced per-form, but nothing here blocks
    a save outright for optional/attachment-style gaps (e.g. SIR present but
    unsigned, PF24 not yet uploaded) — coordinators in low-connectivity
    areas need to save partial progress. Use sparingly: only on entities
    where SRS explicitly allows saving with something outstanding
    (e.g. UC-05 'report incomplete', UC-19 'missing progress information')."""
    incomplete_data_flag = models.BooleanField(default=False)
    missing_fields = models.TextField(blank=True)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# UC-01 Login / users — FR-01 to FR-06
# ---------------------------------------------------------------------------

class UserProfile(TimeStampedModel):
    """Extends auth.User with the role/region SRS requires (FR-06, NFR-05,
    NFR-06). Only three roles exist in v4 — do not add more without a spec
    change."""

    class Role(models.TextChoices):
        SYSTEM_ADMIN = "system_admin", "System Administrator"
        NATIONAL_COORDINATOR = "national_coordinator", "National Coordinator"
        REGIONAL_COORDINATOR = "regional_coordinator", "Regional Coordinator"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.REGIONAL_COORDINATOR)
    region = models.CharField(
        max_length=120, blank=True,
        help_text="Required for Regional Coordinators (NFR-06); ignored for National/Admin.",
    )
    remember_device = models.BooleanField(default=False, help_text="UC-01 'Remember Device' preference.")
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    account_locked = models.BooleanField(default=False, help_text="FR-04: lock after repeated failures.")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


# ---------------------------------------------------------------------------
# Ugandan administrative geography (NFR-19) — reused across entities
# ---------------------------------------------------------------------------

class LocationMixin(models.Model):
    village = models.CharField(max_length=120, blank=True)
    parish = models.CharField(max_length=120, blank=True)
    sub_county = models.CharField(max_length=120, blank=True)
    district = models.CharField(max_length=120, blank=True)
    city_or_municipality = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, blank=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# UC-14 Child Profile / Guardian — FR-08, FR-34
# ---------------------------------------------------------------------------

class Child(LocationMixin, IncompleteDataMixin, TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    class DisabilityType(models.TextChoices):
        NONE = "none", "None"
        MENTAL = "mental", "Mental"
        PHYSICAL = "physical", "Physical"
        BOTH = "both", "Both"

    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    dob = models.DateField(null=True, blank=True)
    age = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(120)],
        help_text="FR-12: valid range is 0-17; values outside this are flagged, not rejected.",
    )
    age_out_of_range = models.BooleanField(default=False, help_text="Set automatically when age is outside 0-17.")
    age_verified = models.BooleanField(default=False, help_text="Set via UC-17 Age Determination.")
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    nationality = models.CharField(max_length=80, blank=True, default="Ugandan")
    tribe = models.CharField(max_length=120, blank=True)
    is_albino = models.BooleanField(default=False)
    disability_type = models.CharField(max_length=10, choices=DisabilityType.choices, default=DisabilityType.NONE)
    physical_condition = models.TextField(blank=True)
    other_details = models.TextField(blank=True, help_text="UC-02 'others' catch-all field.")

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.age is not None:
            self.age_out_of_range = not (0 <= self.age <= 17)
        super().save(*args, **kwargs)


class Guardian(IncompleteDataMixin, TimeStampedModel):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="guardians")
    name = models.CharField(max_length=160)
    relationship = models.CharField(max_length=80)
    contact = models.CharField(max_length=120, blank=True)
    legal_representation = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.name} ({self.relationship} of {self.child})"


# ---------------------------------------------------------------------------
# UC-02 Case Registration — FR-07 to FR-12 (hub entity)
# ---------------------------------------------------------------------------

class Case(LocationMixin, IncompleteDataMixin, TimeStampedModel):
    class CaseCategory(models.TextChoices):
        CHILD_VICTIM_OR_WITNESS = "child_victim_or_witness", "Child Victim or Witness"
        JUVENILE_ACCUSED = "juvenile_accused", "Juvenile Accused"
        VULNERABLE = "vulnerable", "Vulnerable"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        DIVERSION = "diversion", "In Diversion"
        AT_PSWO = "at_pswo", "At PSWO"
        AT_DPP = "at_dpp", "At DPP/RSA"
        AT_COURT = "at_court", "At Court"
        ON_REMAND = "on_remand", "On Remand"
        IN_REHABILITATION = "in_rehabilitation", "In Rehabilitation"
        RESETTLED = "resettled", "Resettled"
        CLOSED = "closed", "Closed"

    case_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Auto-generated on submit (FR-11).")
    child = models.ForeignKey(Child, on_delete=models.PROTECT, related_name="cases")
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="coordinated_cases"
    )
    case_category = models.CharField(max_length=30, choices=CaseCategory.choices)
    case_source = models.CharField(
        max_length=160, blank=True,
        help_text="Police (CID/CFPU), ODPP, courts, remand homes, Prisons, probation, Human Rights Commission, etc.",
    )
    reg_datetime = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.OPEN)

    class Meta:
        ordering = ["-reg_datetime"]

    def __str__(self):
        return self.case_number or f"Case (unsubmitted) — {self.child}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if not self.case_number:
            self.case_number = f"J4C-{self.created_at.year}-{self.pk:06d}"
            super().save(update_fields=["case_number"])
        if is_new:
            CaseStatusHistory.objects.create(case=self, previous_status="", new_status=self.status, changed_by=self.coordinator)


class CaseStatusHistory(TimeStampedModel):
    """Powers the case timeline (UC-12, FR-57) and the audit trail (FR-54,
    NFR-09): who changed what status, and when."""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="status_history")
    previous_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name_plural = "Case status history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.case}: {self.previous_status or '—'} -> {self.new_status}"


# ---------------------------------------------------------------------------
# Reference / lookup entities
# ---------------------------------------------------------------------------

class Facility(models.Model):
    """Police station, prison, remand home, child care institution,
    rehabilitation centre, or court holding facility (UC-24)."""
    class FacilityType(models.TextChoices):
        POLICE_STATION = "police_station", "Police Station"
        PRISON = "prison", "Prison"
        REMAND_HOME = "remand_home", "Remand Home"
        CHILD_CARE_INSTITUTION = "child_care_institution", "Child Care Institution"
        REHABILITATION_CENTRE = "rehabilitation_centre", "Rehabilitation Centre"
        COURT_HOLDING_FACILITY = "court_holding_facility", "Court Holding Facility"

    name = models.CharField(max_length=160)
    type = models.CharField(max_length=30, choices=FacilityType.choices, blank=True)
    district = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.name


class ReferralInstitution(models.Model):
    """Diversion referral institution (UC-07): LC, probation, religious
    institution, or other referral body."""
    name = models.CharField(max_length=160)
    type = models.CharField(max_length=80, blank=True)
    district = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.name


class ChildFriendlySpace(models.Model):
    """UC-08: child care centres, juvenile cells, reception centres, court
    cells, and child-friendly spaces at police, ODPP, and court. Populated
    partly via the DPP API (FR-52) and partly by the Coordinator."""
    name = models.CharField(max_length=160)
    location = models.CharField(max_length=160, blank=True)
    district = models.CharField(max_length=120, blank=True)
    police_station_or_dpp = models.CharField(max_length=160, blank=True)
    num_children_served = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Child-Friendly Space"
        verbose_name_plural = "Child-Friendly Spaces"

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# UC-03 Arrest Details — FR-13, FR-14
# ---------------------------------------------------------------------------

class Arrest(IncompleteDataMixin, TimeStampedModel):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="arrest")
    facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name="arrests",
        help_text="Child's holding facility.",
    )
    arrest_date = models.DateField(null=True, blank=True)
    police_station = models.CharField(max_length=160, blank=True)
    police_case_number = models.CharField(max_length=80, blank=True, help_text="CRB, SD, or MCB number.")
    arrest_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    arresting_officer = models.CharField(max_length=160, blank=True)

    def __str__(self):
        return f"Arrest for {self.case}"


# ---------------------------------------------------------------------------
# UC-04 Case Classification — FR-15 to FR-18
# ---------------------------------------------------------------------------

class Classification(IncompleteDataMixin, TimeStampedModel):
    class OffenceCategory(models.TextChoices):
        PETTY_MINOR = "petty_minor", "Petty or Minor"
        SEMI_CAPITAL = "semi_capital", "Semi-Capital"
        CAPITAL = "capital", "Capital Offence"
        CIVIL = "civil", "Civil Case"

    class NextAction(models.TextChoices):
        DIVERSION = "diversion", "Diversion"
        PSWO = "pswo", "PSWO"
        DPP_RSA = "dpp_rsa", "DPP/RSA"
        CLOSED = "closed", "Closed (forwarded to RSA)"

    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="classification")
    offence_category = models.CharField(max_length=15, choices=OffenceCategory.choices, blank=True)
    offence_datetime = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    cfpu_cid_details = models.TextField(blank=True, help_text="Child and Family Protection Unit / CID officer details.")
    pf24_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="pf24_classifications",
        help_text="Police Form 24 — age and medical.",
    )
    pf48_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="pf48_classifications",
        help_text="Police Form 48 — post-mortem, where applicable.",
    )
    next_action = models.CharField(max_length=10, choices=NextAction.choices, blank=True)

    def __str__(self):
        return f"Classification for {self.case}"


# ---------------------------------------------------------------------------
# UC-05 PSWO Social Inquiry Report — FR-19, FR-20
# ---------------------------------------------------------------------------

class SocialInquiryReport(IncompleteDataMixin, TimeStampedModel):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="social_inquiry_report")
    family_visit_notes = models.TextField(blank=True)
    family_background = models.TextField(blank=True)
    education_history = models.TextField(blank=True)
    assessment = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)
    sir_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="sir_reports"
    )

    class Meta:
        verbose_name = "Social Inquiry Report"

    def __str__(self):
        return f"SIR for {self.case}"


# ---------------------------------------------------------------------------
# UC-06 Victim Impact Assessment — FR-21, FR-22 (child-victim cases only)
# ---------------------------------------------------------------------------

class VictimImpactAssessment(IncompleteDataMixin, TimeStampedModel):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="victim_impact_assessment")
    interview_details = models.TextField(blank=True)
    physical_condition = models.TextField(blank=True)
    psychological_emotional_impact = models.TextField(blank=True)
    educational_impact = models.TextField(blank=True)
    family_social_impact = models.TextField(blank=True)
    medical_findings = models.TextField(blank=True)
    protection_concerns = models.TextField(blank=True)
    services_provided = models.TextField(blank=True)
    services_required = models.TextField(blank=True)
    pswo_findings = models.TextField(blank=True)
    recommendations = models.TextField(
        blank=True,
        help_text="Counselling, medical treatment, family reunification, safe shelter, legal representation, "
                   "compensation/restitution, continued case management, others.",
    )
    via_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="victim_impact_assessments"
    )

    class Meta:
        verbose_name = "Victim Impact Assessment"

    def __str__(self):
        return f"VIA for {self.case}"


# ---------------------------------------------------------------------------
# UC-07 / UC-08 Diversion — FR-23, FR-24, FR-25
# ---------------------------------------------------------------------------

class DiversionPlan(IncompleteDataMixin, TimeStampedModel):
    class DiversionMethod(models.TextChoices):
        CAUTION_AND_RELEASE = "caution_and_release", "Caution and Release"
        COMPENSATION = "compensation", "Compensation"
        RECONCILIATION = "reconciliation", "Reconciliation"
        FAMILY_CONFERENCE = "family_conference", "Family Conference"
        APOLOGY = "apology", "Apology"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        ESCALATED = "escalated", "Escalated"

    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="diversion_plan")
    managing_party = models.CharField(
        max_length=160, blank=True,
        help_text="Referral, guardian/parent, LC, probation, or religious institution.",
    )
    institution = models.ForeignKey(
        ReferralInstitution, on_delete=models.SET_NULL, null=True, blank=True, related_name="diversion_plans"
    )
    diversion_method = models.CharField(max_length=25, choices=DiversionMethod.choices, blank=True)
    investigating_officer = models.CharField(max_length=160, blank=True)
    register_details = models.TextField(blank=True)
    agreement_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="diversion_agreements"
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ONGOING)

    def __str__(self):
        return f"Diversion plan for {self.case}"


class DiversionMonitoringUpdate(TimeStampedModel):
    """Diversion monitoring feedback (FR-24) — a plan can have several
    updates over time, unlike the 1:1 plan itself."""
    diversion_plan = models.ForeignKey(DiversionPlan, on_delete=models.CASCADE, related_name="monitoring_updates")
    feedback = models.TextField()
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Update on {self.diversion_plan} at {self.created_at:%Y-%m-%d}"


class ReferralInstitutionProgress(IncompleteDataMixin, TimeStampedModel):
    """UC-07: institution-side progress tracking, distinct from the
    Coordinator's own DiversionPlan record."""
    class Decision(models.TextChoices):
        RECOMMEND = "recommend", "Recommend"
        DEFER = "defer", "Defer"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="referral_progress_records")
    institution = models.ForeignKey(ReferralInstitution, on_delete=models.SET_NULL, null=True, blank=True)
    progress_notes = models.TextField(blank=True)
    supporting_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="referral_progress_docs"
    )
    decision = models.CharField(max_length=10, choices=Decision.choices, blank=True)

    class Meta:
        verbose_name = "Referral Institution Progress"
        verbose_name_plural = "Referral Institution Progress Records"

    def __str__(self):
        return f"Referral progress for {self.case}"


# ---------------------------------------------------------------------------
# UC-10 DPP/RSA Routing — FR-27, FR-28
# ---------------------------------------------------------------------------

class DPPRouting(IncompleteDataMixin, TimeStampedModel):
    class Action(models.TextChoices):
        SANCTIONED = "sanctioned", "Sanctioned"
        SENT_BACK_POLICE = "sent_back_police", "Sent Back to Police for Further Inquiries"
        COMMITTED_HIGH_COURT = "committed_high_court", "Committed to High Court"

    class RoutingDecision(models.TextChoices):
        PERUSAL = "perusal", "Perusal"
        SANCTIONED = "sanctioned", "Sanctioned"
        REFERRED_FOR_INQUIRY = "referred_for_inquiry", "Referred for Further Inquiry"
        DIVERTED = "diverted", "Diverted"
        TAKEN_TO_COURT = "taken_to_court", "Taken to Court"
        RELEASED_ON_BOND = "released_on_bond", "Released on Bond"
        CLOSED = "closed", "Closed and Put Away"
        CAUTION = "caution", "Caution"
        OTHER = "other", "Other"

    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="dpp_routing")
    dpp_case_number = models.CharField(max_length=80, blank=True)
    action = models.CharField(max_length=25, choices=Action.choices, blank=True)
    current_status = models.CharField(max_length=120, blank=True)
    used_child_friendly_space = models.ForeignKey(
        ChildFriendlySpace, on_delete=models.SET_NULL, null=True, blank=True, related_name="dpp_routings"
    )
    comments = models.TextField(blank=True)
    supporting_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="dpp_routing_docs"
    )
    routing_decision = models.CharField(max_length=25, choices=RoutingDecision.choices, blank=True)
    synced_from_dpp_api = models.BooleanField(default=False, help_text="True if this record arrived via the ODPP API (FR-52).")

    class Meta:
        verbose_name = "DPP Routing"
        verbose_name_plural = "DPP Routings"

    def __str__(self):
        return f"DPP routing for {self.case}"


# ---------------------------------------------------------------------------
# UC-11 Court Routing and Tracking — FR-29 to FR-31
# ---------------------------------------------------------------------------

class CourtProceeding(IncompleteDataMixin, TimeStampedModel):
    class DecisionType(models.TextChoices):
        ORDER = "order", "Order"
        REMAND = "remand", "Remand"
        RELEASE = "release", "Release"

    class RemandLocation(models.TextChoices):
        POLICE = "police", "Police"
        REMAND_HOME = "remand_home", "Remand Home"

    class ReleaseType(models.TextChoices):
        BOND = "bond", "Bond"
        BAIL = "bail", "Bail"
        DISMISSAL = "dismissal", "Dismissal"
        CAUTION = "caution", "Caution"
        DISCHARGE = "discharge", "Discharge"
        PROBATION = "probation", "Probation Orders"
        OTHER = "other", "Other"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="court_proceedings")
    court_name = models.CharField(max_length=160, blank=True)
    hearing_date = models.DateField(null=True, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    used_court_child_cells = models.BooleanField(default=False)
    decision_type = models.CharField(max_length=10, choices=DecisionType.choices, blank=True)
    order_duration = models.CharField(max_length=80, blank=True, help_text="Months or years, free text.")
    remand_location = models.CharField(max_length=15, choices=RemandLocation.choices, blank=True)
    remand_facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name="court_remand_orders"
    )
    remand_duration = models.CharField(max_length=80, blank=True)
    release_type = models.CharField(max_length=15, choices=ReleaseType.choices, blank=True)
    case_status = models.CharField(max_length=120, blank=True)
    coordinator_comments = models.TextField(blank=True)

    class Meta:
        verbose_name = "Court Proceeding"
        ordering = ["-hearing_date"]

    def __str__(self):
        return f"Court proceeding for {self.case} on {self.hearing_date}"


# ---------------------------------------------------------------------------
# UC-12 Remand and Placement Management — FR-32
# ---------------------------------------------------------------------------

class RemandPlacement(IncompleteDataMixin, TimeStampedModel):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="remand_placements")
    facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name="remand_placements"
    )
    remand_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=80, blank=True)
    legal_limit_date = models.DateField(
        null=True, blank=True, help_text="Configurable legal time limit for remand (SRS Section 8, item 6).",
    )

    class Meta:
        verbose_name = "Remand Placement"

    def __str__(self):
        return f"Remand placement for {self.case}"


# ---------------------------------------------------------------------------
# UC-15 Documents Management — FR-35
# ---------------------------------------------------------------------------

class Document(TimeStampedModel):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="documents", null=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_documents"
    )
    category = models.CharField(max_length=120, blank=True)
    file = models.FileField(upload_to="documents/%Y/%m/", blank=True, null=True)
    upload_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category or 'Document'} - {self.case}"


# ---------------------------------------------------------------------------
# UC-18 Age Determination — FR-38, FR-39
# ---------------------------------------------------------------------------

class AgeDetermination(IncompleteDataMixin, TimeStampedModel):
    class DeterminedWhere(models.TextChoices):
        POLICE = "police", "Police"
        COURT = "court", "Court"
        PRISONS = "prisons", "Prisons"
        REMAND_HOME = "remand_home", "Remand Home"

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="age_determinations")
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="age_determinations")
    determined_where = models.CharField(max_length=15, choices=DeterminedWhere.choices, blank=True)
    estimated_age = models.PositiveSmallIntegerField(null=True, blank=True)
    confirmed_age = models.PositiveSmallIntegerField(null=True, blank=True)
    supporting_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="age_determination_evidence"
    )
    determined_on = models.DateField(null=True, blank=True)
    out_of_range_comment = models.TextField(
        blank=True, help_text="Required if determined age is outside 0-17; case is then closed per UC-17.",
    )

    class Meta:
        verbose_name = "Age Determination"

    def __str__(self):
        return f"Age determination for {self.child}"


# ---------------------------------------------------------------------------
# UC-19 Chain-Linked Initiative (Meetings) — FR-40, FR-41
# ---------------------------------------------------------------------------

class ChainLinkedActivity(TimeStampedModel):
    class ActivityType(models.TextChoices):
        REGIONAL_COORDINATION = "regional_coordination", "Regional Coordination Meeting"
        DISTRICT_COORDINATION = "district_coordination", "District Coordination Meeting"
        SUB_COMMITTEE = "sub_committee", "Sub-Committee Meeting"
        INSPECTION = "inspection", "Inspection"
        COURT_OPEN_DAY = "court_open_day", "Court Open Day"
        OTHER = "other", "Other"

    activity_type = models.CharField(max_length=25, choices=ActivityType.choices)
    title = models.CharField(max_length=200)
    activity_datetime = models.DateTimeField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    objectives_agenda = models.TextField(blank=True)
    participants_organisations = models.TextField(blank=True, help_text="Free text list; see models.py module docstring.")
    invitation_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="chain_linked_invitations"
    )
    discussions_key_issues = models.TextField(blank=True)
    resolutions_recommendations = models.TextField(blank=True)
    minutes_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="chain_linked_minutes"
    )

    class Meta:
        verbose_name = "Chain-Linked Activity"
        verbose_name_plural = "Chain-Linked Activities"

    def __str__(self):
        return self.title


class ChainLinkedActionPoint(TimeStampedModel):
    activity = models.ForeignKey(ChainLinkedActivity, on_delete=models.CASCADE, related_name="action_points")
    action_point = models.CharField(max_length=250)
    responsible_person = models.CharField(max_length=160, blank=True)
    timeline = models.CharField(max_length=120, blank=True)
    reminder_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=80, blank=True)

    class Meta:
        verbose_name = "Chain-Linked Action Point"

    def __str__(self):
        return self.action_point


# ---------------------------------------------------------------------------
# UC-20 Rehabilitation Management — FR-42
# ---------------------------------------------------------------------------

class Rehabilitation(IncompleteDataMixin, TimeStampedModel):
    class RehabType(models.TextChoices):
        EDUCATION = "education", "Education"
        COUNSELLING = "counselling", "Counselling"
        SPIRITUAL = "spiritual", "Spiritual Engagement"
        SKILLS = "skills", "Skills Development"
        GAMES = "games", "Games"

    class CompletionStatus(models.TextChoices):
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        WITHDRAWN = "withdrawn", "Withdrawn"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="rehabilitations")
    start_date = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=15, choices=RehabType.choices, blank=True)
    provider = models.CharField(max_length=160, blank=True)
    services_provided = models.TextField(blank=True)
    education_support = models.TextField(blank=True)
    counselling_psychosocial_support = models.TextField(blank=True)
    health_medical_support = models.TextField(blank=True)
    assessment_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="rehabilitation_assessments"
    )
    stakeholder_observations = models.TextField(blank=True)
    completion_status = models.CharField(max_length=15, choices=CompletionStatus.choices, blank=True)

    def __str__(self):
        return f"Rehabilitation for {self.case}"


class RehabilitationProgressReview(TimeStampedModel):
    rehabilitation = models.ForeignKey(Rehabilitation, on_delete=models.CASCADE, related_name="progress_reviews")
    review_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Progress review for {self.rehabilitation} on {self.review_date}"


# ---------------------------------------------------------------------------
# UC-28 Community Service Management — FR-56
# ---------------------------------------------------------------------------

class CommunityService(IncompleteDataMixin, TimeStampedModel):
    class CompletionStatus(models.TextChoices):
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        NOT_COMPLETED = "not_completed", "Not Completed"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="community_services")
    type = models.CharField(max_length=120, blank=True)
    placement_info = models.TextField(blank=True)
    location = models.CharField(max_length=160, blank=True)
    supervising_officer = models.CharField(max_length=160, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    hours_assigned = models.PositiveIntegerField(null=True, blank=True)
    attendance_participation = models.TextField(blank=True)
    progress_observations = models.TextField(blank=True)
    challenges_incidents = models.TextField(blank=True)
    completion_status = models.CharField(max_length=15, choices=CompletionStatus.choices, blank=True)
    supporting_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="community_service_docs"
    )

    class Meta:
        verbose_name = "Community Service"
        verbose_name_plural = "Community Services"

    def __str__(self):
        return f"Community service for {self.case}"


# ---------------------------------------------------------------------------
# UC-25 Legal Representation Management — FR-50, FR-51
# ---------------------------------------------------------------------------

class LegalRepresentation(IncompleteDataMixin, TimeStampedModel):
    class RepresentationType(models.TextChoices):
        LEGAL_AID = "legal_aid", "Legal Aid"
        PRIVATE_ADVOCATE = "private_advocate", "Private Advocate"
        STATE_BRIEF = "state_brief", "State Brief"
        NGO_LEGAL_SUPPORT = "ngo_legal_support", "NGO Legal Support"
        COURT_APPOINTED_COUNSEL = "court_appointed_counsel", "Court-Appointed Counsel"
        PARALEGAL_SUPPORT = "paralegal_support", "Paralegal Support"

    class CaseStage(models.TextChoices):
        POLICE = "police", "Police"
        DPP_RSA = "dpp_rsa", "DPP/RSA"
        COURT = "court", "Court"
        DIVERSION = "diversion", "Diversion"
        REMAND = "remand", "Remand"
        REHABILITATION = "rehabilitation", "Rehabilitation"

    class Status(models.TextChoices):
        PENDING_ASSIGNMENT = "pending_assignment", "Pending Assignment"
        ASSIGNED = "assigned", "Assigned"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        WITHDRAWN = "withdrawn", "Withdrawn"
        REFERRED_ELSEWHERE = "referred_elsewhere", "Referred Elsewhere"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="legal_representations")
    representation_type = models.CharField(max_length=25, choices=RepresentationType.choices, blank=True)
    representative_name = models.CharField(max_length=160, blank=True)
    representative_org = models.CharField(max_length=160, blank=True)
    representative_phone = models.CharField(max_length=40, blank=True)
    representative_email = models.EmailField(blank=True)
    representative_district_region = models.CharField(max_length=120, blank=True)
    case_stage = models.CharField(max_length=15, choices=CaseStage.choices, blank=True)
    start_date = models.DateField(null=True, blank=True)
    support_provided = models.TextField(
        blank=True,
        help_text="Advice, court appearance, bail application, diversion support, statement support, mediation, appeal support.",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_ASSIGNMENT)
    comments = models.TextField(blank=True)

    class Meta:
        verbose_name = "Legal Representation"

    def __str__(self):
        return f"Legal representation for {self.case}"


class LegalRepresentationDocument(TimeStampedModel):
    """UC-26 documents: appointment letter, legal aid referral, court
    documents, bail application, notes — kept separate from the general
    Document model so multiple can attach to one representation record."""
    legal_representation = models.ForeignKey(LegalRepresentation, on_delete=models.CASCADE, related_name="documents")
    document = models.ForeignKey(Document, on_delete=models.CASCADE)

    def __str__(self):
        return f"Document for {self.legal_representation}"


# ---------------------------------------------------------------------------
# UC-21 Capacity Building and Training — FR-44
# ---------------------------------------------------------------------------

class Training(TimeStampedModel):
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=120, blank=True)
    train_datetime = models.DateTimeField(null=True, blank=True)
    venue = models.CharField(max_length=160, blank=True)
    district = models.CharField(max_length=120, blank=True)
    facilitators = models.CharField(max_length=200, blank=True)
    organiser = models.CharField(max_length=160, blank=True)
    target_institutions = models.TextField(blank=True)
    topics = models.TextField(blank=True)
    participant_count = models.PositiveIntegerField(null=True, blank=True)
    attendance_notes = models.TextField(blank=True)
    outcomes = models.TextField(blank=True)
    supporting_document = models.ForeignKey(
        Document, on_delete=models.SET_NULL, null=True, blank=True, related_name="training_docs"
    )

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# UC-22 Breastfeeding Mothers and Accompanying Children — FR-45
# ---------------------------------------------------------------------------

class BreastfeedingMother(IncompleteDataMixin, TimeStampedModel):
    facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True, blank=True, related_name="breastfeeding_mothers"
    )
    facility_type = models.CharField(max_length=80, blank=True)
    case = models.ForeignKey(
        Case, on_delete=models.SET_NULL, null=True, blank=True, related_name="breastfeeding_mothers"
    )
    name = models.CharField(max_length=160)
    national_id = models.CharField(max_length=40, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Child.Gender.choices, blank=True)
    district = models.CharField(max_length=120, blank=True)
    legal_status = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.name


class AccompanyingChild(IncompleteDataMixin, TimeStampedModel):
    mother = models.ForeignKey(BreastfeedingMother, on_delete=models.CASCADE, related_name="accompanying_children")
    name = models.CharField(max_length=160)
    dob = models.DateField(null=True, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Child.Gender.choices, blank=True)
    birth_registration_status = models.CharField(max_length=120, blank=True)
    health_status = models.CharField(max_length=160, blank=True)
    protection_concerns = models.TextField(blank=True)
    transition_plan_after_20_months = models.TextField(
        blank=True, help_text="UC-22: where the child transitions to after 20 months.",
    )
    follow_up_scheduled = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Accompanying Child"

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# UC-23 Suspect Parade Attendance — FR-46
# ---------------------------------------------------------------------------

class SuspectParade(IncompleteDataMixin, TimeStampedModel):
    class ChildCategory(models.TextChoices):
        VICTIM = "victim", "Victim"
        WITNESS = "witness", "Witness"
        SUSPECT = "suspect", "Suspect"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="suspect_parades")
    parade_datetime = models.DateTimeField(null=True, blank=True)
    district = models.CharField(max_length=120, blank=True)
    police_station = models.CharField(max_length=160, blank=True)
    child_category = models.CharField(max_length=10, choices=ChildCategory.choices, blank=True)
    names_and_offences = models.TextField(blank=True, help_text="Names and offences of children involved.")
    support_services_provided = models.TextField(blank=True)
    observations_protection_concerns = models.TextField(blank=True)
    supporting_document = models.ForeignKey(
        Document, on_delete=models.SET_NULL, null=True, blank=True, related_name="suspect_parade_docs"
    )

    class Meta:
        verbose_name = "Suspect Parade"

    def __str__(self):
        return f"Suspect parade for {self.case}"


# ---------------------------------------------------------------------------
# UC-24 JLOS Facility Inspection — FR-47, FR-48
# ---------------------------------------------------------------------------

class FacilityInspection(TimeStampedModel):
    class InspectionType(models.TextChoices):
        ROUTINE = "routine", "Routine"
        FOLLOW_UP = "follow_up", "Follow-up"
        EMERGENCY = "emergency", "Emergency"
        SPECIAL_INVESTIGATION = "special_investigation", "Special Investigation"
        JOINT_INSPECTION = "joint_inspection", "Joint Inspection"

    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="inspections")
    inspection_date = models.DateField(null=True, blank=True)
    district = models.CharField(max_length=120, blank=True)
    type = models.CharField(max_length=25, choices=InspectionType.choices, blank=True)

    # Child population statistics (FR-48)
    total_children = models.PositiveIntegerField(null=True, blank=True)
    male_children = models.PositiveIntegerField(null=True, blank=True)
    female_children = models.PositiveIntegerField(null=True, blank=True)
    children_with_disabilities = models.PositiveIntegerField(null=True, blank=True)
    children_on_remand = models.PositiveIntegerField(null=True, blank=True)
    child_victims = models.PositiveIntegerField(null=True, blank=True)
    child_witnesses = models.PositiveIntegerField(null=True, blank=True)
    refugee_children = models.PositiveIntegerField(null=True, blank=True)
    albino_children = models.PositiveIntegerField(null=True, blank=True)

    conditions_assessment = models.TextField(blank=True)
    protection_concerns = models.TextField(blank=True)
    support_provided = models.TextField(blank=True)
    num_children_supported = models.PositiveIntegerField(null=True, blank=True)
    reports_photos = models.ForeignKey(
        Document, on_delete=models.SET_NULL, null=True, blank=True, related_name="facility_inspection_docs"
    )
    recommendations_corrective_actions = models.TextField(blank=True)

    class Meta:
        verbose_name = "Facility Inspection"
        ordering = ["-inspection_date"]

    def __str__(self):
        return f"Inspection of {self.facility} on {self.inspection_date}"



# ---------------------------------------------------------------------------
# UC-26 Counselling Management — FR-51, FR-52
# ---------------------------------------------------------------------------

class Counselling(IncompleteDataMixin, TimeStampedModel):
    """UC-26: counselling sessions provided or coordinated for child victims,
    juvenile offenders, and their families. One row per session; the
    counselling history hangs off the case."""

    class SessionType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        GROUP = "group", "Group"
        FAMILY = "family", "Family"
        PSYCHOSOCIAL = "psychosocial", "Psychosocial Support"

    class CounsellorRole(models.TextChoices):
        J4C_COORDINATOR = "j4c_coordinator", "J4C Coordinator"
        EXTERNAL_PROFESSIONAL = "external_professional", "External Professional"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="counselling_sessions")
    session_datetime = models.DateTimeField(null=True, blank=True)
    session_type = models.CharField(max_length=20, choices=SessionType.choices, blank=True)
    location = models.CharField(max_length=160, blank=True)
    duration = models.CharField(max_length=60, blank=True)
    counsellor_role = models.CharField(max_length=25, choices=CounsellorRole.choices, blank=True)
    professional_full_name = models.CharField(max_length=160, blank=True)
    reason = models.TextField(blank=True, help_text="Trauma, Abuse, Behavioural Challenges, Reintegration, Diversion, Family Conflict, Court-ordered, etc.")
    other_reason_details = models.TextField(blank=True)
    observations_assessment = models.TextField(blank=True)
    interventions_provided = models.TextField(blank=True)
    emotional_status_post = models.TextField(blank=True)
    recommendations_referrals = models.TextField(blank=True, help_text="Legal Aid, Medical Examination, Psychiatric Referral, Educational Support, etc.")
    referral_details = models.TextField(blank=True)
    next_session_datetime = models.DateTimeField(null=True, blank=True)
    supporting_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="counselling_docs"
    )

    class Meta:
        verbose_name = "Counselling Session"
        verbose_name_plural = "Counselling Sessions"

    def __str__(self):
        return f"Counselling for {self.case} on {self.session_datetime}"


# ---------------------------------------------------------------------------
# UC-27 Civil Case Management — FR-53, FR-54, FR-55
# ---------------------------------------------------------------------------

class CivilCase(IncompleteDataMixin, TimeStampedModel):
    """UC-27: civil applications involving children (custody, maintenance,
    guardianship, adoption, etc.). Registered against the child's case and
    tracked through hearings to a court decision/order."""

    class ApplicationCategory(models.TextChoices):
        CUSTODY = "custody", "Custody"
        MAINTENANCE = "maintenance", "Maintenance"
        GUARDIANSHIP = "guardianship", "Guardianship"
        ADOPTION = "adoption", "Adoption"
        DECLARATION_OF_PARENTAGE = "declaration_of_parentage", "Declaration of Parentage"
        CARE_ORDER = "care_order", "Care Order"
        SUPERVISION_ORDER = "supervision_order", "Supervision Order"
        INTERIM_ORDER = "interim_order", "Interim Care or Supervision Order"
        EXCLUSION_ORDER = "exclusion_order", "Exclusion Order"
        EMERGENCY_PROTECTION_ORDER = "emergency_protection_order", "Emergency Protection Order"
        SEARCH_PRODUCTION_ORDER = "search_production_order", "Search and Production Order"
        RECOVERY_ORDER = "recovery_order", "Recovery Order"
        APPEAL = "appeal", "Appeal"

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="civil_cases")
    court_name_location = models.CharField(max_length=200, blank=True)
    application_category = models.CharField(max_length=30, choices=ApplicationCategory.choices, blank=True)
    case_file_number = models.CharField(max_length=120, blank=True)
    presiding_officer = models.CharField(max_length=160, blank=True)
    applicant_details = models.TextField(blank=True)
    respondent_details = models.TextField(blank=True)
    background_reason = models.TextField(blank=True)
    court_decision_order = models.TextField(blank=True)
    compliance_requirements = models.TextField(blank=True)
    responsible_persons = models.CharField(max_length=200, blank=True)
    coordinator_comments = models.TextField(blank=True)
    supporting_document = models.ForeignKey(
        "Document", on_delete=models.SET_NULL, null=True, blank=True, related_name="civil_case_docs"
    )

    class Meta:
        verbose_name = "Civil Case"
        verbose_name_plural = "Civil Cases"

    def __str__(self):
        return f"Civil case ({self.get_application_category_display()}) for {self.case}"


class CivilCaseHearing(TimeStampedModel):
    """Hearing dates schedule for a civil case (UC-27.8, UC-27.9)."""
    civil_case = models.ForeignKey(CivilCase, on_delete=models.CASCADE, related_name="hearings")
    hearing_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Civil Case Hearing"

    def __str__(self):
        return f"Hearing for {self.civil_case} on {self.hearing_date}"
