from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from . import api_views, serializers

router = DefaultRouter()
router.register("users", api_views.UserProfileViewSet, basename="userprofile")
router.register("children", api_views.ChildViewSet, basename="child")
router.register("guardians", api_views.GuardianViewSet, basename="guardian")
router.register("cases", api_views.CaseViewSet, basename="case")
router.register("facilities", api_views.FacilityViewSet, basename="facility")
router.register("referral-institutions", api_views.ReferralInstitutionViewSet, basename="referralinstitution")
router.register("child-friendly-spaces", api_views.ChildFriendlySpaceViewSet, basename="childfriendlyspace")
router.register("documents", api_views.DocumentViewSet, basename="document")
router.register("arrests", api_views.ArrestViewSet, basename="arrest")
router.register("classifications", api_views.ClassificationViewSet, basename="classification")
router.register("social-inquiry-reports", api_views.SocialInquiryReportViewSet, basename="socialinquiryreport")
router.register("victim-impact-assessments", api_views.VictimImpactAssessmentViewSet, basename="victimimpactassessment")
router.register("diversion-plans", api_views.DiversionPlanViewSet, basename="diversionplan")
router.register("diversion-monitoring-updates", api_views.DiversionMonitoringUpdateViewSet, basename="diversionmonitoringupdate")
router.register("referral-progress", api_views.ReferralInstitutionProgressViewSet, basename="referralinstitutionprogress")
router.register("dpp-routings", api_views.DPPRoutingViewSet, basename="dpprouting")
router.register("court-proceedings", api_views.CourtProceedingViewSet, basename="courtproceeding")
router.register("remand-placements", api_views.RemandPlacementViewSet, basename="remandplacement")
router.register("age-determinations", api_views.AgeDeterminationViewSet, basename="agedetermination")
router.register("chain-linked-activities", api_views.ChainLinkedActivityViewSet, basename="chainlinkedactivity")
router.register("chain-linked-action-points", api_views.ChainLinkedActionPointViewSet, basename="chainlinkedactionpoint")
router.register("rehabilitations", api_views.RehabilitationViewSet, basename="rehabilitation")
router.register("rehabilitation-progress-reviews", api_views.RehabilitationProgressReviewViewSet, basename="rehabilitationprogressreview")
router.register("community-services", api_views.CommunityServiceViewSet, basename="communityservice")
router.register("counselling-sessions", api_views.CounsellingViewSet, basename="counselling")
router.register("civil-cases", api_views.CivilCaseViewSet, basename="civilcase")
router.register("civil-case-hearings", api_views.CivilCaseHearingViewSet, basename="civilcasehearing")
router.register("legal-representations", api_views.LegalRepresentationViewSet, basename="legalrepresentation")
router.register("trainings", api_views.TrainingViewSet, basename="training")
router.register("breastfeeding-mothers", api_views.BreastfeedingMotherViewSet, basename="breastfeedingmother")
router.register("accompanying-children", api_views.AccompanyingChildViewSet, basename="accompanyingchild")
router.register("suspect-parades", api_views.SuspectParadeViewSet, basename="suspectparade")
router.register("facility-inspections", api_views.FacilityInspectionViewSet, basename="facilityinspection")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Returns the logged-in user + their role/region profile, so the React
    app can render the role-aware, region-aware dashboard/nav (FR-03)
    immediately after login without a second round of guessing."""
    profile, _ = request.user.profile, None
    return Response({
        "user": serializers.UserSerializer(request.user).data,
        "profile": serializers.UserProfileSerializer(profile).data if hasattr(request.user, "profile") else None,
    })


urlpatterns = [
    path("me/", me, name="api-me"),
    path("", include(router.urls)),
]
