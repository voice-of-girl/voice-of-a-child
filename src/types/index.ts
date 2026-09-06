/**
 * Voice of a Girl — frontend type definitions.
 * Mirrors the Django REST API contracts exactly so the compiler guards the
 * integration.
 */

export type Role =
  | "PLATFORM_ADMIN" | "ORGANISATION_ADMIN"
  | "PROGRAMME_MANAGER" | "MONITORING_OFFICER" | "STAFF";

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Organisation {
  id: string;
  name: string;
  description?: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  district?: string;
  country?: string;
  verification_status?: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  phone_number?: string;
  role: Role;
  organisation?: Organisation;
  organisation_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginResult {
  access: string;
  refresh: string;
  user: User;
}

export type ProgrammeStatus = "PLANNED" | "ACTIVE" | "COMPLETED" | "ARCHIVED";

export interface Programme {
  id: string;
  organisation: string;
  organisation_name?: string;
  title: string;
  name: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  status: ProgrammeStatus;
  target_participants?: number;
    participant_count?: number;
  created_at: string;
  updated_at: string;
}


export type QuestionType =
  | "SHORT_TEXT" | "LONG_TEXT" | "NUMBER" | "EMAIL" | "DATE"
  | "YES_NO" | "MULTIPLE_CHOICE" | "CHECKBOX"
  | "DROPDOWN" | "RATING_SCALE";

export interface SurveyQuestion {
  id: string;
  question: string;
  help_text?: string;
  question_type: QuestionType;
  options?: string[];
  required: boolean;
  order: number;
  validation_rules?: Record<string, unknown>;
}

export type SurveyStage = "BASELINE" | "MIDLINE" | "ENDLINE" | "CUSTOM";
export type SurveyStatus = "DRAFT" | "PUBLISHED" | "CLOSED";

export interface Survey {
  id: string;
  organisation: string;
  organisation_name?: string;
  programme?: string | null;
  programme_name?: string | null;
  impact_project?: string | null;
  project_name?: string | null;
  title: string;
  description?: string;
  stage: SurveyStage;
  status: SurveyStatus;
  public_token: string;
  public_url?: string;
  start_date?: string;
  end_date?: string;
  allow_multiple_responses?: boolean;
  thank_you_message?: string;
  responses_count?: number;
  created_by?: string;
  created_at: string;
  updated_at: string;
  questions?: SurveyQuestion[];
}

export type ResponseStatus = "SUBMITTED" | "DRAFT";

export interface AnswerRead {
  id: string;
  question: string;
  question_type: QuestionType;
  order: number;
  value: unknown;
}

export interface SurveyResponse {
  id: string;
  survey: string;
  survey_title?: string;
  programme?: string | null;
  programme_name?: string | null;
  participant?: string | null;
  participant_name?: string | null;
  respondent_name?: string;
  respondent_email?: string;
  status: ResponseStatus;
  submitted_at?: string;
  metadata?: Record<string, unknown>;
  answers?: AnswerRead[];
}

export type ParticipantStatus = "ACTIVE" | "COMPLETED" | "DROPPED_OUT" | "INACTIVE";

export interface Participant {
  id: string;
  organisation: string;
  organisation_name?: string;
  programme?: string | null;
  programme_name?: string | null;
  name?: string;
  email?: string;
  phone?: string;
  external_reference?: string;
  gender?: string;
  date_of_birth?: string;
  age?: number;
  location?: string;
  district?: string;
  status: ParticipantStatus;
    enrolled_date?: string;
  created_at: string;
  updated_at: string;
}

export type ChallengePriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type ChallengeStatus = "OPEN" | "IN_PROGRESS" | "RESOLVED";

export interface Challenge {
  id: string;
  organisation: string;
  programme?: string | null;
  participant?: string | null;
  category: string;
  title: string;
  description?: string;
  status: ChallengeStatus;
  priority: ChallengePriority;
  assigned_to?: string | null;
  resolution_notes?: string;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Feedback {
  id: string;
  organisation: string;
  programme?: string | null;
  participant?: string | null;
  category: string;
  message: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface SupportRequest {
  id: string;
  organisation: string;
  programme?: string | null;
  participant?: string | null;
  category: string;
  description: string;
  status: string;
  assigned_to?: string | null;
  resolution_notes?: string;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
}

export type KpiStatus = "ON_TRACK" | "AT_RISK" | "OFF_TRACK" | "COMPLETED";

export interface KPI {
  id: string;
  organisation: string;
  programme?: string | null;
  impact_project?: string | null;
  name: string;
  description?: string;
  unit?: string;
  target?: number;
  baseline?: number;
  current_value?: number;
  endline?: number;
  status: KpiStatus;
  progress_percentage?: number;
}

export interface ImpactMeasurement {
  id: string;
  organisation: string;
  programme?: string | null;
  impact_project?: string | null;
  kpi?: string | null;
  metric: string;
  value: number;
  period: string;
  notes?: string;
  created_at: string;
}

export type ImpactProjectStatus = "PLANNED" | "ACTIVE" | "COMPLETED" | "ARCHIVED";

export interface ImpactProject {
  id: string;
  organisation: string;
  name: string;
  description?: string;
  status: ImpactProjectStatus;
  start_date?: string;
  end_date?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export type ReportType = "GENERAL" | "PROGRAMME" | "SURVEY" | "IMPACT" | "KPI" | "PROJECT";
export type ReportStatus = "GENERATING" | "READY" | "FAILED";
export type ReportFormat = "PDF" | "EXCEL" | "CSV";

export interface Report {
  id: string;
  organisation: string;
  organisation_name?: string;
  programme?: string | null;
  survey?: string | null;
  impact_project?: string | null;
  report_type: ReportType;
  title: string;
  status: ReportStatus;
    file_format: ReportFormat;
  parameters?: Record<string, unknown>;
  download_url?: string | null;
  filename?: string;
  error_message?: string;
  created_at: string;
}

export interface KPIProgress {
  id: string;
  kpi: string;
  unit?: string;
  baseline?: number;
  current?: number;
  target?: number;
  endline?: number;
  progress_percentage?: number;
  status: KpiStatus;
}

export interface BaselineEndline {
  kpi: string;
  baseline?: number;
  endline?: number;
  change?: number | null;
  unit?: string;
}

export interface DashboardResponse {
  overview: {
    participants_reached: number;
    enrolment: number;
    survey_responses: number;
    survey_response_rate: number;
    completion_rate: number;
    active_programmes: number;
    active_surveys: number;
    target_participants: number;
  };
  impact: { kpis: KPIProgress[]; baseline_endline: BaselineEndline[] };
  monitoring: {
    total_challenges: number;
    open: number;
    in_progress: number;
    resolved: number;
    resolution_rate: number;
    challenges_by_category: { category: string; count: number }[];
  };
  survey: {
    published_surveys: number;
    total_responses: number;
    responses_per_survey: { survey__title: string; count: number }[];
  };
}

export interface PublicQuestion {
  id: string;
  question: string;
  help_text?: string;
  question_type: QuestionType;
  options?: string[];
  required: boolean;
  order: number;
  validation_rules?: Record<string, unknown>;
}

export interface PublicSurvey {
  id: string;
  title: string;
  description?: string;
  stage: SurveyStage;
  questions: PublicQuestion[];
  thank_you_message?: string;
  accepting_responses: boolean;
  message?: string;
}

export interface AuthContextType {
  user: User | null;
  role: Role;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
}

