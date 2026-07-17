"""
DRF ViewSets — one ModelViewSet per model. Case gets a custom retrieve
action returning the nested CaseDetailSerializer for the Case Profile
screen (UC-12); list/create/update on Case stay flat via CaseSerializer.

Region scoping (NFR-06): Regional Coordinators only see cases in their own
region (and everything hanging off those cases); National Coordinators and
System Admins see everything. Enforced per-viewset via get_queryset(), not
globally, because not every model has a direct region field — most scope
through their parent Case.
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers


class IsAuthenticatedAndProfiled(permissions.IsAuthenticated):
    """Placeholder hook for role-based permission classes per viewset,
    layered on top of DRF's session/JWT authentication. Extend per-model
    where write access should be role-restricted beyond Django's
    add/change/delete permissions already wired up in bootstrap_roles."""
    pass


def _user_region(request):
    profile = getattr(request.user, "profile", None)
    if profile and profile.role == models.UserProfile.Role.REGIONAL_COORDINATOR:
        return profile.region
    return None


class RegionScopedCaseMixin:
    """Mixin for viewsets whose queryset should be filtered to the
    requesting Regional Coordinator's region, via a `region_lookup` path
    (Django ORM double-underscore lookup) pointing at Case.region."""
    region_lookup = "region"

    def get_queryset(self):
        qs = super().get_queryset()
        region = _user_region(self.request)
        if region:
            qs = qs.filter(**{self.region_lookup: region})
        return qs


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.select_related("user").all()
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChildViewSet(RegionScopedCaseMixin, viewsets.ModelViewSet):
    queryset = models.Child.objects.prefetch_related("guardians").all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["district", "gender", "age_verified", "incomplete_data_flag"]
    search_fields = ["first_name", "last_name", "village", "district", "tribe"]
    region_lookup = "region"

    def get_serializer_class(self):
        return serializers.ChildListSerializer if self.action == "list" else serializers.ChildSerializer


class GuardianViewSet(viewsets.ModelViewSet):
    queryset = models.Guardian.objects.all()
    serializer_class = serializers.GuardianSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["child"]


class CaseViewSet(RegionScopedCaseMixin, viewsets.ModelViewSet):
    queryset = models.Case.objects.select_related("child", "coordinator").all()
    serializer_class = serializers.CaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["case_category", "status", "district", "region", "incomplete_data_flag"]
    search_fields = ["case_number", "child__first_name", "child__last_name"]
    region_lookup = "region"

    def get_serializer_class(self):
        # Nested Case Profile (UC-12) on retrieve; flat list/write otherwise.
        if self.action == "retrieve":
            return serializers.CaseDetailSerializer
        return serializers.CaseSerializer

    def perform_create(self, serializer):
        serializer.save(coordinator=self.request.user)

    @action(detail=True, methods=["get"])
    def profile(self, request, pk=None):
        """UC-12 Case Profile: full nested case detail in one call."""
        case = self.get_object()
        return Response(serializers.CaseDetailSerializer(case).data)

    @action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        """FR-57: case timeline assembled from status history."""
        case = self.get_object()
        history = case.status_history.select_related("changed_by").all()
        return Response(serializers.CaseStatusHistorySerializer(history, many=True).data)

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        """Append a CaseStatusHistory row and update Case.status in one
        call — closes the gap flagged in README (history only auto-fired
        on creation until this endpoint existed)."""
        case = self.get_object()
        new_status = request.data.get("status")
        note = request.data.get("note", "")
        if not new_status:
            return Response({"detail": "status is required"}, status=400)
        previous = case.status
        case.status = new_status
        case.save(update_fields=["status", "updated_at"])
        models.CaseStatusHistory.objects.create(
            case=case, previous_status=previous, new_status=new_status, changed_by=request.user, note=note
        )
        return Response(serializers.CaseSerializer(case).data)


class CaseChildViewSetMixin(RegionScopedCaseMixin):
    """Shared base for the many viewsets whose model FKs to Case directly
    (not through another model) — scopes by case__region."""
    region_lookup = "case__region"


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = models.Facility.objects.all()
    serializer_class = serializers.FacilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["type", "district"]


class ReferralInstitutionViewSet(viewsets.ModelViewSet):
    queryset = models.ReferralInstitution.objects.all()
    serializer_class = serializers.ReferralInstitutionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChildFriendlySpaceViewSet(viewsets.ModelViewSet):
    queryset = models.ChildFriendlySpace.objects.all()
    serializer_class = serializers.ChildFriendlySpaceSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = models.Document.objects.select_related("case", "uploaded_by").all()
    serializer_class = serializers.DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "category"]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ArrestViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Arrest.objects.select_related("case", "facility").all()
    serializer_class = serializers.ArrestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case"]


class ClassificationViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Classification.objects.select_related("case").all()
    serializer_class = serializers.ClassificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "offence_category"]


class SocialInquiryReportViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.SocialInquiryReport.objects.select_related("case").all()
    serializer_class = serializers.SocialInquiryReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case"]


class VictimImpactAssessmentViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.VictimImpactAssessment.objects.select_related("case").all()
    serializer_class = serializers.VictimImpactAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case"]


class DiversionPlanViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.DiversionPlan.objects.select_related("case", "institution").prefetch_related("monitoring_updates").all()
    serializer_class = serializers.DiversionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "status"]


class DiversionMonitoringUpdateViewSet(viewsets.ModelViewSet):
    queryset = models.DiversionMonitoringUpdate.objects.all()
    serializer_class = serializers.DiversionMonitoringUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["diversion_plan"]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class ReferralInstitutionProgressViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.ReferralInstitutionProgress.objects.select_related("case", "institution").all()
    serializer_class = serializers.ReferralInstitutionProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "institution", "decision"]


class DPPRoutingViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.DPPRouting.objects.select_related("case").all()
    serializer_class = serializers.DPPRoutingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "action", "routing_decision"]


class CourtProceedingViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.CourtProceeding.objects.select_related("case", "remand_facility").all()
    serializer_class = serializers.CourtProceedingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "decision_type"]


class RemandPlacementViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.RemandPlacement.objects.select_related("case", "facility").all()
    serializer_class = serializers.RemandPlacementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "facility"]


class AgeDeterminationViewSet(viewsets.ModelViewSet):
    queryset = models.AgeDetermination.objects.select_related("case", "child").all()
    serializer_class = serializers.AgeDeterminationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "child"]


class ChainLinkedActivityViewSet(viewsets.ModelViewSet):
    queryset = models.ChainLinkedActivity.objects.prefetch_related("action_points").all()
    serializer_class = serializers.ChainLinkedActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["activity_type"]


class ChainLinkedActionPointViewSet(viewsets.ModelViewSet):
    queryset = models.ChainLinkedActionPoint.objects.all()
    serializer_class = serializers.ChainLinkedActionPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["activity"]


class RehabilitationViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Rehabilitation.objects.select_related("case").prefetch_related("progress_reviews").all()
    serializer_class = serializers.RehabilitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "type", "completion_status"]


class RehabilitationProgressReviewViewSet(viewsets.ModelViewSet):
    queryset = models.RehabilitationProgressReview.objects.all()
    serializer_class = serializers.RehabilitationProgressReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["rehabilitation"]

    def perform_create(self, serializer):
        serializer.save(reviewed_by=self.request.user)


class CounsellingViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Counselling.objects.select_related("case").all()
    serializer_class = serializers.CounsellingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "session_type", "counsellor_role"]


class CivilCaseViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.CivilCase.objects.select_related("case").prefetch_related("hearings").all()
    serializer_class = serializers.CivilCaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "application_category"]


class CivilCaseHearingViewSet(viewsets.ModelViewSet):
    queryset = models.CivilCaseHearing.objects.all()
    serializer_class = serializers.CivilCaseHearingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["civil_case"]


class CommunityServiceViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.CommunityService.objects.select_related("case").all()
    serializer_class = serializers.CommunityServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "completion_status"]


class LegalRepresentationViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.LegalRepresentation.objects.select_related("case").prefetch_related("documents").all()
    serializer_class = serializers.LegalRepresentationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "representation_type", "case_stage", "status"]


class TrainingViewSet(viewsets.ModelViewSet):
    queryset = models.Training.objects.all()
    serializer_class = serializers.TrainingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["type", "district"]


class BreastfeedingMotherViewSet(viewsets.ModelViewSet):
    queryset = models.BreastfeedingMother.objects.select_related("facility", "case").prefetch_related("accompanying_children").all()
    serializer_class = serializers.BreastfeedingMotherSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["facility", "district"]


class AccompanyingChildViewSet(viewsets.ModelViewSet):
    queryset = models.AccompanyingChild.objects.all()
    serializer_class = serializers.AccompanyingChildSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["mother"]


class SuspectParadeViewSet(CaseChildViewSetMixin, viewsets.ModelViewSet):
    queryset = models.SuspectParade.objects.select_related("case").all()
    serializer_class = serializers.SuspectParadeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["case", "child_category"]


class FacilityInspectionViewSet(viewsets.ModelViewSet):
    queryset = models.FacilityInspection.objects.select_related("facility").all()
    serializer_class = serializers.FacilityInspectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["facility", "type"]
