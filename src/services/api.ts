import { 
  Programme, 
  BeneficiaryParticipation, 
  Form, 
  FormResponse, 
  Challenge, 
  Opportunity, 
  Application, 
  VerificationTask,
  NotificationItem,
  Organisation
} from '../types';

export const api = {
  submitBeneficiaryInterest: async (data: any) => {
    const res = await fetch('/api/public/beneficiary-interest/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to submit interest form');
    return res.json();
  },

  getBeneficiaryInterests: async () => {
    const res = await fetch('/api/public/beneficiary-interest/');
    if (!res.ok) throw new Error('Unable to load beneficiary interest submissions');
    return res.json();
  },

  // Programmes
  getProgrammes: async (): Promise<Programme[]> => {
    const res = await fetch('/api/programmes/');
    if (!res.ok) throw new Error('Unable to load programmes');
    return res.json();
  },

  createProgramme: async (data: Partial<Programme>): Promise<Programme> => {
    const res = await fetch('/api/programmes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to create programme');
    return res.json();
  },

  updateProgramme: async (id: string, data: Partial<Programme>): Promise<Programme> => {
    const res = await fetch(`/api/programmes/${id}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to update programme');
    return res.json();
  },

  // Participants
  getParticipants: async (): Promise<BeneficiaryParticipation[]> => {
    const res = await fetch('/api/participants/');
    if (!res.ok) throw new Error('Unable to load participants');
    return res.json();
  },

  getParticipant: async (id: string): Promise<BeneficiaryParticipation> => {
    const res = await fetch(`/api/participants/${id}/`);
    if (!res.ok) throw new Error('Unable to load participant');
    return res.json();
  },

  enrollParticipant: async (programmeId: string, data: any): Promise<BeneficiaryParticipation> => {
    const res = await fetch(`/api/programmes/${programmeId}/enrollments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to enroll participant');
    return res.json();
  },

  updateParticipationStatus: async (participationId: string, data: any): Promise<BeneficiaryParticipation> => {
    const res = await fetch(`/api/programmes/enrollments/${participationId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to update participation');
    return res.json();
  },

  // Surveys / Forms
  getForms: async (_programmeId: string): Promise<Form[]> => {
    const res = await fetch('/api/surveys/');
    if (!res.ok) throw new Error('Unable to load forms');
    return res.json();
  },

  getForm: async (formId: string): Promise<Form> => {
    const res = await fetch(`/api/surveys/${formId}/`);
    if (!res.ok) throw new Error('Unable to load form');
    return res.json();
  },

  createForm: async (_programmeId: string, data: any): Promise<Form> => {
    const res = await fetch('/api/surveys/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to create form');
    return res.json();
  },

  updateForm: async (formId: string, data: any): Promise<Form> => {
    const res = await fetch(`/api/surveys/${formId}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to update form');
    return res.json();
  },

  publishForm: async (formId: string): Promise<Form> => {
    const res = await fetch(`/api/surveys/${formId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'PUBLISHED' })
    });
    if (!res.ok) throw new Error('Unable to publish form');
    return res.json();
  },

  submitFormResponse: async (formId: string, data: any): Promise<FormResponse> => {
    const res = await fetch(`/api/surveys/${formId}/submit/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to submit response');
    return res.json();
  },

  getFormResponses: async (formId: string): Promise<FormResponse[]> => {
    const res = await fetch(`/api/surveys/${formId}/responses/`);
    if (!res.ok) throw new Error('Unable to load responses');
    return res.json();
  },

  // Challenges
  getChallenges: async (): Promise<Challenge[]> => {
    const res = await fetch('/api/monitoring/challenges/');
    if (!res.ok) throw new Error('Unable to load challenges');
    return res.json();
  },

  reportChallenge: async (data: any): Promise<Challenge> => {
    const res = await fetch('/api/monitoring/challenges/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to report challenge');
    return res.json();
  },

  resolveChallenge: async (challengeId: string, resolution_notes: string): Promise<Challenge> => {
    const res = await fetch(`/api/monitoring/challenges/${challengeId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resolution_notes, status: 'RESOLVED' })
    });
    if (!res.ok) throw new Error('Unable to resolve challenge');
    return res.json();
  },

  assignChallenge: async (challengeId: string, data: any): Promise<Challenge> => {
    const res = await fetch(`/api/monitoring/challenges/${challengeId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to assign challenge');
    return res.json();
  },

  // Analytics
  getAnalytics: async (programmeId: string) => {
    const res = await fetch(`/api/analytics/programmes/${programmeId}/`);
    if (!res.ok) throw new Error('Unable to load analytics');
    return res.json();
  },

  getChallengeAnalytics: async () => {
    const res = await fetch('/api/analytics/challenges/');
    if (!res.ok) throw new Error('Unable to load challenge analytics');
    return res.json();
  },

  getOutcomes: async (programmeId: string) => {
    const res = await fetch(`/api/analytics/programmes/${programmeId}/outcomes/`);
    if (!res.ok) throw new Error('Unable to load outcomes');
    return res.json();
  },

  // Organisations
  getOrganisations: async (): Promise<Organisation[]> => {
    const res = await fetch('/api/organisations/');
    if (!res.ok) throw new Error('Unable to load organisations');
    return res.json();
  },

  getMyOrganisation: async (): Promise<Organisation> => {
    const res = await fetch('/api/organisations/my/');
    if (!res.ok) throw new Error('Unable to load organisation');
    return res.json();
  },

  verifyOrganisation: async (orgId: string, status: string): Promise<Organisation> => {
    const res = await fetch(`/api/organisations/${orgId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ verification_status: status })
    });
    if (!res.ok) throw new Error('Unable to update organisation');
    return res.json();
  },

  // Reports
  getProgrammeReport: async (programmeId: string) => {
    const res = await fetch(`/api/reports/programmes/${programmeId}/`);
    if (!res.ok) throw new Error('Unable to load report');
    return res.json();
  },

  getOrganisationReport: async () => {
    const res = await fetch('/api/reports/organisations/me/');
    if (!res.ok) throw new Error('Unable to load organisation report');
    return res.json();
  },

  // Verification
  getVerificationTasks: async (): Promise<VerificationTask[]> => {
    const res = await fetch('/api/verification/tasks/');
    if (!res.ok) throw new Error('Unable to load verification tasks');
    return res.json();
  },

  updateVerificationTask: async (taskId: string, data: any): Promise<VerificationTask> => {
    const res = await fetch(`/api/verification/tasks/${taskId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to update verification task');
    return res.json();
  },

  // Notifications
  getNotifications: async (): Promise<NotificationItem[]> => {
    const res = await fetch('/api/notifications/');
    if (!res.ok) throw new Error('Unable to load notifications');
    return res.json();
  },

  // Opportunities & Applications
  getOpportunities: async (): Promise<Opportunity[]> => {
    const res = await fetch('/api/opportunities/');
    if (!res.ok) throw new Error('Unable to load opportunities');
    return res.json();
  },

  applyForOpportunity: async (data: any): Promise<Application> => {
    const res = await fetch('/api/applications/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Unable to apply');
    return res.json();
  },

  getApplications: async (): Promise<Application[]> => {
    const res = await fetch('/api/applications/');
    if (!res.ok) throw new Error('Unable to load applications');
    return res.json();
  },

  // Rule-based match calculator
  calculateMatch: async (profile: any, requirements: any) => {
    const res = await fetch('/api/match/calculate/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beneficiary_profile: profile, requirements })
    });
    if (!res.ok) throw new Error('Unable to calculate match');
    return res.json();
  }
};
