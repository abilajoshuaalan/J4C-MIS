"""
DRF serializers — one ModelSerializer per model, per the "one ViewSet +
serializer per model" decision. Nested read-only representations are added
on Case (the hub entity) so the React Case Profile screen (UC-12) can fetch
a case plus every related record in a single request, while writes still go
through each model's own endpoint (keeps the API predictable and matches
how the admin/models are already shaped).
"""
from django.contrib.auth.models import User
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.UserProfile
        fields = "__all__"


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Guardian
        fields = "__all__"


class ChildSerializer(serializers.ModelSerializer):
    guardians = GuardianSerializer(many=True, read_only=True)

    class Meta:
        model = models.Child
        fields = "__all__"
        read_only_fields = ["age_out_of_range"]


class ChildListSerializer(serializers.ModelSerializer):
    """Lighter shape for list/search screens (UC-13 child search) — avoids
    shipping nested guardians for every row in a list."""
    class Meta:
        model = models.Child
        fields = ["id", "first_name", "last_name", "age", "gender", "district", "age_verified", "incomplete_data_flag"]


class CaseStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = models.CaseStatusHistory
        fields = "__all__"


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Facility
        fields = "__all__"


class ReferralInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReferralInstitution
        fields = "__all__"


class ChildFriendlySpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChildFriendlySpace
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = models.Document
        fields = "__all__"


class ArrestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Arrest
        fields = "__all__"


class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Classification
        fields = "__all__"


class SocialInquiryReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SocialInquiryReport
        fields = "__all__"


class VictimImpactAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VictimImpactAssessment
        fields = "__all__"


class DiversionMonitoringUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DiversionMonitoringUpdate
        fields = "__all__"


class DiversionPlanSerializer(serializers.ModelSerializer):
    monitoring_updates = DiversionMonitoringUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = models.DiversionPlan
        fields = "__all__"


class ReferralInstitutionProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReferralInstitutionProgress
        fields = "__all__"


class DPPRoutingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DPPRouting
        fields = "__all__"


class CourtProceedingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourtProceeding
        fields = "__all__"


class RemandPlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RemandPlacement
        fields = "__all__"


class AgeDeterminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AgeDetermination
        fields = "__all__"


class ChainLinkedActionPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChainLinkedActionPoint
        fields = "__all__"


class ChainLinkedActivitySerializer(serializers.ModelSerializer):
    action_points = ChainLinkedActionPointSerializer(many=True, read_only=True)

    class Meta:
        model = models.ChainLinkedActivity
        fields = "__all__"


class RehabilitationProgressReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RehabilitationProgressReview
        fields = "__all__"


class RehabilitationSerializer(serializers.ModelSerializer):
    progress_reviews = RehabilitationProgressReviewSerializer(many=True, read_only=True)

    class Meta:
        model = models.Rehabilitation
        fields = "__all__"


class CounsellingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Counselling
        fields = "__all__"


class CivilCaseHearingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CivilCaseHearing
        fields = "__all__"


class CivilCaseSerializer(serializers.ModelSerializer):
    hearings = CivilCaseHearingSerializer(many=True, read_only=True)

    class Meta:
        model = models.CivilCase
        fields = "__all__"


class CommunityServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CommunityService
        fields = "__all__"


class LegalRepresentationDocumentSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)

    class Meta:
        model = models.LegalRepresentationDocument
        fields = "__all__"


class LegalRepresentationSerializer(serializers.ModelSerializer):
    documents = LegalRepresentationDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = models.LegalRepresentation
        fields = "__all__"


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Training
        fields = "__all__"


class AccompanyingChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccompanyingChild
        fields = "__all__"


class BreastfeedingMotherSerializer(serializers.ModelSerializer):
    accompanying_children = AccompanyingChildSerializer(many=True, read_only=True)

    class Meta:
        model = models.BreastfeedingMother
        fields = "__all__"


class SuspectParadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SuspectParade
        fields = "__all__"


class FacilityInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FacilityInspection
        fields = "__all__"


class CaseSerializer(serializers.ModelSerializer):
    """List/write serializer — flat, fast. See CaseDetailSerializer for the
    nested Case Profile (UC-12) read shape."""
    child_name = serializers.CharField(source="child.__str__", read_only=True)

    class Meta:
        model = models.Case
        fields = "__all__"
        read_only_fields = ["case_number"]


class CaseDetailSerializer(serializers.ModelSerializer):
    """UC-12 Case Profile: the case plus every related record, nested and
    read-only, in one response — avoids 15+ round trips from the React
    case-profile screen. Writes to related records still go through their
    own endpoints (e.g. POST /api/arrests/), not through this serializer."""
    child = ChildSerializer(read_only=True)
    coordinator = UserSerializer(read_only=True)
    status_history = CaseStatusHistorySerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    arrest = ArrestSerializer(read_only=True)
    classification = ClassificationSerializer(read_only=True)
    social_inquiry_report = SocialInquiryReportSerializer(read_only=True)
    victim_impact_assessment = VictimImpactAssessmentSerializer(read_only=True)
    diversion_plan = DiversionPlanSerializer(read_only=True)
    referral_progress_records = ReferralInstitutionProgressSerializer(many=True, read_only=True)
    dpp_routing = DPPRoutingSerializer(read_only=True)
    court_proceedings = CourtProceedingSerializer(many=True, read_only=True)
    remand_placements = RemandPlacementSerializer(many=True, read_only=True)
    age_determinations = AgeDeterminationSerializer(many=True, read_only=True)
    rehabilitations = RehabilitationSerializer(many=True, read_only=True)
    counselling_sessions = CounsellingSerializer(many=True, read_only=True)
    civil_cases = CivilCaseSerializer(many=True, read_only=True)
    community_services = CommunityServiceSerializer(many=True, read_only=True)
    legal_representations = LegalRepresentationSerializer(many=True, read_only=True)
    suspect_parades = SuspectParadeSerializer(many=True, read_only=True)
    breastfeeding_mothers = BreastfeedingMotherSerializer(many=True, read_only=True)

    class Meta:
        model = models.Case
        fields = "__all__"
        read_only_fields = ["case_number"]
