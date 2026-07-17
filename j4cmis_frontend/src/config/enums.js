// Options mirror cases/models.py TextChoices verbatim (values must match the API).
export const GENDER = [["M","Male"],["F","Female"],["O","Other"]];
export const DISABILITY = [["none","None"],["mental","Mental"],["physical","Physical"],["both","Both"]];
export const CASE_CATEGORY = [["child_victim_or_witness","Child Victim or Witness"],["juvenile_accused","Juvenile Accused"],["vulnerable","Vulnerable"]];
export const CASE_STATUS = [["open","Open"],["diversion","In Diversion"],["at_pswo","At PSWO"],["at_dpp","At DPP/RSA"],["at_court","At Court"],["on_remand","On Remand"],["in_rehabilitation","In Rehabilitation"],["resettled","Resettled"],["closed","Closed"]];
export const OFFENCE_CATEGORY = [["petty_minor","Petty or Minor"],["semi_capital","Semi-Capital"],["capital","Capital Offence"],["civil","Civil Case"]];
export const NEXT_ACTION = [["diversion","Diversion"],["pswo","PSWO"],["dpp_rsa","DPP/RSA"],["closed","Closed (forwarded to RSA)"]];
export const SESSION_TYPE = [["individual","Individual"],["group","Group"],["family","Family"],["psychosocial","Psychosocial Support"]];
export const COUNSELLOR_ROLE = [["j4c_coordinator","J4C Coordinator"],["external_professional","External Professional"]];
export const APPLICATION_CATEGORY = [["custody","Custody"],["maintenance","Maintenance"],["guardianship","Guardianship"],["adoption","Adoption"],["declaration_of_parentage","Declaration of Parentage"],["care_order","Care Order"],["supervision_order","Supervision Order"],["interim_order","Interim Care or Supervision Order"],["exclusion_order","Exclusion Order"],["emergency_protection_order","Emergency Protection Order"],["search_production_order","Search and Production Order"],["recovery_order","Recovery Order"],["appeal","Appeal"]];
export function labelOf(options, value) {
  const hit = (options || []).find((o) => o[0] === value);
  return hit ? hit[1] : (value ?? "");
}
