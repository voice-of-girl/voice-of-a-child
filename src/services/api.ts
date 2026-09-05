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
    return res.json();
  },

  createProgramme: async (data: Partial<Programme>): Promise<Programme> => {
    const res = await fetch('/api/programmes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  updateProgramme: async (id: string, data: Partial<Programme>): Promise<Programme> => {
    const res = await fetch(`/api/programmes/${id}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  // Participants
  getParticipants: async (programmeId: string): Promise<BeneficiaryParticipation[]> => {
    const res = await fetch(`/api/programmes/${programmeId}/participants/`);
    return res.json();
  },

  enrollParticipant: async (programmeId: string, data: any): Promise<BeneficiaryParticipation> => {
    const res = await fetch(`/api/programmes/${programmeId}/participants/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  updateParticipationStatus: async (participationId: string, data: any): Promise<BeneficiaryParticipation> => {
    const res = await fetch(`/api/participation/${participationId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  // Forms
  getForms: async (programmeId: string): Promise<Form[]> => {
    const res = await fetch(`/api/programmes/${programmeId}/forms/`);
    return res.json();
  },

  getForm: async (formId: string): Promise<Form> => {
    const res = await fetch(`/api/forms/${formId}/`);
    return res.json();
  },

  createForm: async (programmeId: string, data: any): Promise<Form> => {
    const res = await fetch(`/api/programmes/${programmeId}/forms/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  updateForm: async (formId: string, data: any): Promise<Form> => {
    const res = await fetch(`/api/forms/${formId}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  publishForm: async (formId: string): Promise<Form> => {
    const res = await fetch(`/api/forms/${formId}/publish/`, {
      method: 'POST'
    });
    return res.json();
  },

  submitFormResponse: async (formId: string, data: any): Promise<FormResponse> => {
    const res = await fetch(`/api/forms/${formId}/submit/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  getFormResponses: async (formId: string): Promise<FormResponse[]> => {
    const res = await fetch(`/api/forms/${formId}/responses/`);
    return res.json();
  },

  // Challenges
  getChallenges: async (programmeId: string): Promise<Challenge[]> => {
    const res = await fetch(`/api/programmes/${programmeId}/challenges/`);
    return res.json();
  },

  reportChallenge: async (programmeId: string, data: any): Promise<Challenge> => {
    const res = await fetch(`/api/programmes/${programmeId}/challenges/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  assignChallenge: async (challengeId: string, data: any): Promise<Challenge> => {
    const res = await fetch(`/api/challenges/${challengeId}/assign/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  resolveChallenge: async (challengeId: string, resolution_notes: string): Promise<Challenge> => {
    const res = await fetch(`/api/challenges/${challengeId}/resolve/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resolution_notes })
    });
    return res.json();
  },

  // Analytics
  getAnalytics: async (programmeId: string) => {
    const res = await fetch(`/api/programmes/${programmeId}/analytics/`);
    return res.json();
  },

  getChallengeAnalytics: async (programmeId: string) => {
    const res = await fetch(`/api/programmes/${programmeId}/challenge-analytics/`);
    return res.json();
  },

  getOutcomes: async (programmeId: string) => {
    const res = await fetch(`/api/programmes/${programmeId}/outcomes/`);
    return res.json();
  },

  // Opportunities & Applications
  getOpportunities: async (): Promise<Opportunity[]> => {
    const res = await fetch('/api/opportunities/');
    return res.json();
  },

  applyForOpportunity: async (data: any): Promise<Application> => {
    const res = await fetch('/api/applications/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  getApplications: async (): Promise<Application[]> => {
    const res = await fetch('/api/applications/');
    return res.json();
  },

  // Verification
  getVerificationTasks: async (): Promise<VerificationTask[]> => {
    const res = await fetch('/api/verification/tasks/');
    return res.json();
  },

  updateVerificationTask: async (taskId: string, data: any): Promise<VerificationTask> => {
    const res = await fetch(`/api/verification/tasks/${taskId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  // Notifications
  getNotifications: async (): Promise<NotificationItem[]> => {
    const res = await fetch('/api/notifications/');
    return res.json();
  },

  // Rule-based match calculator
  calculateMatch: async (profile: any, requirements: any) => {
    const res = await fetch('/api/match/calculate/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ beneficiary_profile: profile, requirements })
    });
    return res.json();
  },

  // Organisations
  getOrganisations: async (): Promise<Organisation[]> => {
    const res = await fetch('/api/organisations/');
    return res.json();
  },

  verifyOrganisation: async (orgId: string, status: string): Promise<Organisation> => {
    const res = await fetch(`/api/organisations/${orgId}/verify/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ verification_status: status })
    });
    return res.json();
  }
};
