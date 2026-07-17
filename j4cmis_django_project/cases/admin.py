from django.contrib import admin
from . import models


class IncompleteFlagListMixin:
    def get_list_display(self, request):
        base = list(super().get_list_display(request))
        if hasattr(self.model, "incomplete_data_flag") and "incomplete_data_flag" not in base:
            base.append("incomplete_data_flag")
        return base

    def get_list_filter(self, request):
        base = list(super().get_list_filter(request))
        if hasattr(self.model, "incomplete_data_flag") and "incomplete_data_flag" not in base:
            base.append("incomplete_data_flag")
        return base


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "region", "account_locked")
    list_filter = ("role", "region", "account_locked")
    search_fields = ("user__username", "user__first_name", "user__last_name")


class GuardianInline(admin.TabularInline):
    model = models.Guardian
    extra = 0


@admin.register(models.Child)
class ChildAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("first_name", "last_name", "age", "gender", "district", "age_verified", "age_out_of_range")
    list_filter = ("gender", "district", "age_verified", "age_out_of_range", "disability_type", "is_albino")
    search_fields = ("first_name", "last_name", "village", "district", "tribe")
    inlines = [GuardianInline]


class CaseStatusHistoryInline(admin.TabularInline):
    model = models.CaseStatusHistory
    extra = 0
    readonly_fields = ("previous_status", "new_status", "changed_by", "created_at")
    can_delete = False


@admin.register(models.Case)
class CaseAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case_number", "child", "case_category", "status", "region", "district", "reg_datetime")
    list_filter = ("case_category", "status", "district", "region")
    search_fields = ("case_number", "child__first_name", "child__last_name")
    date_hierarchy = "reg_datetime"
    autocomplete_fields = ["child"]
    inlines = [CaseStatusHistoryInline]
    readonly_fields = ("case_number",)


@admin.register(models.Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "district")
    list_filter = ("type", "district")
    search_fields = ("name",)


@admin.register(models.ReferralInstitution)
class ReferralInstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "district")
    search_fields = ("name",)


@admin.register(models.ChildFriendlySpace)
class ChildFriendlySpaceAdmin(admin.ModelAdmin):
    list_display = ("name", "district", "police_station_or_dpp", "num_children_served")
    search_fields = ("name",)


@admin.register(models.Arrest)
class ArrestAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "arrest_date", "police_station", "arresting_officer", "police_case_number")
    search_fields = ("case__case_number", "police_case_number")


@admin.register(models.Classification)
class ClassificationAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "offence_category", "next_action")
    list_filter = ("offence_category", "next_action")


@admin.register(models.SocialInquiryReport)
class SocialInquiryReportAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case",)


@admin.register(models.VictimImpactAssessment)
class VictimImpactAssessmentAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case",)


@admin.register(models.AgeDetermination)
class AgeDeterminationAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("child", "case", "determined_where", "estimated_age", "confirmed_age", "determined_on")
    list_filter = ("determined_where",)


class DiversionMonitoringUpdateInline(admin.TabularInline):
    model = models.DiversionMonitoringUpdate
    extra = 0


@admin.register(models.DiversionPlan)
class DiversionPlanAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "institution", "diversion_method", "status")
    list_filter = ("status", "diversion_method")
    inlines = [DiversionMonitoringUpdateInline]


@admin.register(models.ReferralInstitutionProgress)
class ReferralInstitutionProgressAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "institution", "decision")
    list_filter = ("decision",)


@admin.register(models.DPPRouting)
class DPPRoutingAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "dpp_case_number", "action", "routing_decision", "synced_from_dpp_api")
    list_filter = ("action", "routing_decision", "synced_from_dpp_api")


@admin.register(models.CourtProceeding)
class CourtProceedingAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "court_name", "hearing_date", "decision_type", "case_status")
    list_filter = ("decision_type", "release_type")
    date_hierarchy = "hearing_date"


@admin.register(models.RemandPlacement)
class RemandPlacementAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "facility", "remand_date", "status", "legal_limit_date")


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("category", "case", "uploaded_by", "upload_datetime")
    list_filter = ("category",)


class RehabilitationProgressReviewInline(admin.TabularInline):
    model = models.RehabilitationProgressReview
    extra = 0


@admin.register(models.Rehabilitation)
class RehabilitationAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "type", "provider", "completion_status")
    list_filter = ("type", "completion_status")
    inlines = [RehabilitationProgressReviewInline]


@admin.register(models.CommunityService)
class CommunityServiceAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "type", "supervising_officer", "hours_assigned", "completion_status")
    list_filter = ("completion_status",)


@admin.register(models.Counselling)
class CounsellingAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "session_datetime", "session_type", "counsellor_role")
    list_filter = ("session_type", "counsellor_role")


class CivilCaseHearingInline(admin.TabularInline):
    model = models.CivilCaseHearing
    extra = 0


@admin.register(models.CivilCase)
class CivilCaseAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "application_category", "case_file_number", "presiding_officer")
    list_filter = ("application_category",)
    inlines = [CivilCaseHearingInline]


@admin.register(models.SuspectParade)
class SuspectParadeAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "parade_datetime", "police_station", "child_category")
    list_filter = ("child_category",)


class LegalRepresentationDocumentInline(admin.TabularInline):
    model = models.LegalRepresentationDocument
    extra = 0


@admin.register(models.LegalRepresentation)
class LegalRepresentationAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("case", "representation_type", "representative_name", "case_stage", "status")
    list_filter = ("representation_type", "case_stage", "status")
    inlines = [LegalRepresentationDocumentInline]


class ChainLinkedActionPointInline(admin.TabularInline):
    model = models.ChainLinkedActionPoint
    extra = 0


@admin.register(models.ChainLinkedActivity)
class ChainLinkedActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "activity_type", "activity_datetime", "venue")
    list_filter = ("activity_type",)
    inlines = [ChainLinkedActionPointInline]


@admin.register(models.Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "train_datetime", "district", "organiser", "participant_count")


class AccompanyingChildInline(admin.TabularInline):
    model = models.AccompanyingChild
    extra = 0


@admin.register(models.BreastfeedingMother)
class BreastfeedingMotherAdmin(IncompleteFlagListMixin, admin.ModelAdmin):
    list_display = ("name", "facility", "case", "age", "district")
    inlines = [AccompanyingChildInline]


@admin.register(models.FacilityInspection)
class FacilityInspectionAdmin(admin.ModelAdmin):
    list_display = ("facility", "inspection_date", "type", "total_children")
    list_filter = ("type",)
    date_hierarchy = "inspection_date"
