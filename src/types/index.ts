export type UserRole = 'BENEFICIARY' | 'ORGANISATION_ADMIN' | 'FIELD_OFFICER' | 'PLATFORM_ADMIN';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  organisation_id?: string;
  created_at: string;
}

export interface Organisation {
  id: string;
  name: string;
  description: string;
  organisation_type: 'NGO' | 'FOUNDATION' | 'TRAINING_INSTITUTE' | 'EMPLOYER' | 'GOVERNMENT' | 'COMMUNITY_BASED';
  email: string;
  phone_number: string;
  website: string;
  address: string;
  district: string;
  country: string;
  verification_status: 'PENDING' | 'VERIFIED' | 'REJECTED';
  created_at: string;
}

export interface BeneficiaryProfile {
  user_id: string;
  date_of_birth?: string;
  gender: string;
  district: string;
  region: string;
  country: string;
  education_level: string;
  school_or_institution: string;
  employment_status: string;
  career_goals: string;
  bio: string;
  skills: string[];
  interests: string[];
  profile_completed: boolean;
}

export type ProgrammeType = 'NEW_PROGRAMME' | 'EXISTING_PROGRAMME';
export type ProgrammeStatus = 'DRAFT' | 'ACTIVE' | 'PAUSED' | 'COMPLETED' | 'CLOSED';

export interface Programme {
  id: string;
  organisation_id: string;
  title: string;
  name?: string;
  description: string;
  category: string;
  programme_type: ProgrammeType;
  location: string;
  locations?: string[];
  start_date: string;
  end_date: string;
  status: ProgrammeStatus;
  target_beneficiaries: number;
  target_participants?: number;
  current_beneficiaries?: number;
  completion_rate?: number;
  attendance_rate?: number;
  dropout_rate?: number;
  criteria_education?: string[];
  criteria_skills?: string[];
  criteria_locations?: string[];
  criteria_min_age?: number;
  criteria_max_age?: number;
  eligibility_criteria?: any;
  outcomes_aimed?: string[];
}

export type ParticipationStatus = 'REGISTERED' | 'SELECTED' | 'ACTIVE' | 'COMPLETED' | 'DROPPED_OUT';

export interface BeneficiaryParticipation {
  id: string;
  beneficiary_id: string;
  programme_id: string;
  participation_status: ParticipationStatus;
  status?: ParticipationStatus;
  attendance_rate: number;
  joined_at: string;
  completed_at?: string;
  outcome_notes?: string;
  // enriched fields for UI
  beneficiary_name?: string;
  beneficiary_email?: string;
  beneficiary?: any;
  completed_surveys_count?: number;
  match_score?: number;
  match_reasons?: string[];
  matching_reasons?: string[];
  missing_requirements?: string[];
}

export type OpportunityType = 'SCHOLARSHIP' | 'JOB' | 'INTERNSHIP' | 'TRAINING' | 'MENTORSHIP' | 'FELLOWSHIP' | 'ENTREPRENEURSHIP' | 'GRANT';

export interface Opportunity {
  id: string;
  programme_id: string;
  title: string;
  description: string;
  opportunity_type: OpportunityType;
  benefits: string;
  requirements: string;
  application_deadline: string;
  available_slots: number;
  status: 'OPEN' | 'CLOSED' | 'FILLED';
  organisation_name?: string;
  location?: string;
  match_score?: number;
  match_reasons?: string[];
}

export type ApplicationStatus = 'SUBMITTED' | 'UNDER_REVIEW' | 'SHORTLISTED' | 'ACCEPTED' | 'REJECTED' | 'WITHDRAWN';

export interface Application {
  id: string;
  beneficiary_id: string;
  opportunity_id: string;
  status: ApplicationStatus;
  application_date: string;
  statement_of_purpose?: string;
  notes?: string;
  reviewed_by?: string;
  opportunity_title?: string;
  organisation_name?: string;
}

export type FormType = 'BASELINE' | 'MONITORING' | 'ENDLINE' | 'FOLLOW_UP' | 'CUSTOM';
export type FormStatus = 'DRAFT' | 'PUBLISHED' | 'CLOSED';
export type QuestionType = 
  | 'SHORT_TEXT' 
  | 'LONG_TEXT' 
  | 'NUMBER' 
  | 'MULTIPLE_CHOICE' 
  | 'CHECKBOX' 
  | 'DROPDOWN' 
  | 'YES_NO' 
  | 'RATING_SCALE' 
  | 'DATE' 
  | 'FILE_UPLOAD';

export interface FormQuestion {
  id: string;
  form_id: string;
  question_text: string;
  help_text?: string;
  question_type: QuestionType;
  required: boolean;
  options: string[];
  order: number;
}

export interface Form {
  id: string;
  organisation_id: string;
  programme_id: string;
  title: string;
  description: string;
  form_type: FormType;
  status: FormStatus;
  response_deadline?: string;
  follow_up_interval_months?: number;
  created_at: string;
  questions?: FormQuestion[];
  responses_count?: number;
}

export interface FormResponse {
  id: string;
  form_id: string;
  beneficiary_id: string;
  submitted_at?: string;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'SUBMITTED';
  submitted_via: string;
  answers?: Record<string, any>; // question_id -> value
  beneficiary_name?: string;
}

export type ChallengeCategory = 'TRANSPORT' | 'FINANCIAL' | 'HEALTH' | 'ATTENDANCE' | 'SAFETY' | 'MATERIALS' | 'FAMILY_CARE' | 'OTHER';
export type ChallengeSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ChallengeStatus = 'OPEN' | 'IN_PROGRESS' | 'RESOLVED';

export interface Challenge {
  id: string;
  programme_id: string;
  programme_title?: string;
  beneficiary_id: string;
  beneficiary_name?: string;
  category: ChallengeCategory;
  description: string;
  severity: ChallengeSeverity;
  status: ChallengeStatus;
  assigned_to?: string;
  assigned_to_name?: string;
  reported_at: string;
  resolved_at?: string;
  resolution_notes?: string;
  audit_history?: Array<{
    timestamp: string;
    actor: string;
    action: string;
    note?: string;
  }>;
}

export interface KPI {
  id: string;
  programme_id: string;
  name: string;
  description?: string;
  category: 'INPUT' | 'ACTIVITY' | 'OUTPUT' | 'OUTCOME' | 'IMPACT';
  target_value: number;
  current_value: number;
  unit: string;
  measurement_frequency: string;
}

export interface OutcomeRecord {
  metric_name: string;
  baseline: number | string;
  endline: number | string;
  follow_up_6m: number | string;
  unit?: string;
  percentage_change: number;
  category: 'EMPLOYMENT' | 'SKILLS' | 'INCOME' | 'EDUCATION' | 'WELLBEING';
}

export interface VerificationTask {
  id: string;
  assigned_officer_id: string;
  beneficiary_id: string;
  beneficiary_name: string;
  beneficiary_phone: string;
  beneficiary_location: string;
  programme_id: string;
  programme_title: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'VERIFIED' | 'FLAGGED' | 'REJECTED';
  home_visit_conducted: boolean;
  id_documents_checked: boolean;
  guardian_contacted: boolean;
  field_notes?: string;
  gps_coords?: string;
  scheduled_for: string;
}

export interface NotificationItem {
  id: string;
  recipient_id: string;
  title: string;
  message: string;
  type: 'OPPORTUNITY' | 'FORM_ASSIGNED' | 'FORM_DEADLINE' | 'APPLICATION_STATUS' | 'CHALLENGE_UPDATE' | 'FOLLOW_UP_SURVEY' | 'SYSTEM';
  is_read: boolean;
  created_at: string;
}
