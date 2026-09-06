import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // In-memory Database with rich seed data
  let organisations = [
    {
      id: "org_1",
      name: "FemmeTech Africa Foundation",
      description: "Empowering young African women through high-impact technology training, mentorship, and career placement.",
      organisation_type: "FOUNDATION",
      email: "info@femmetech.org",
      phone_number: "+256 700 123456",
      website: "https://femmetech.org",
      address: "Plot 14 Innovation Way, Bugolobi",
      district: "Kampala",
      country: "Uganda",
      verification_status: "VERIFIED",
      created_at: "2025-01-10T09:00:00Z"
    },
    {
      id: "org_2",
      name: "Young Women Agri-Entrepreneurs Hub",
      description: "Promoting climate-smart agribusiness and micro-enterprise scaling for adolescent mothers and out-of-school girls.",
      organisation_type: "NGO",
      email: "contact@agriwomen.org",
      phone_number: "+256 772 987654",
      website: "https://agriwomen.org",
      address: "Main Street 88, Northern Hub",
      district: "Gulu",
      country: "Uganda",
      verification_status: "VERIFIED",
      created_at: "2025-02-15T11:00:00Z"
    },
    {
      id: "org_3",
      name: "Equal Horizons Vocational Institute",
      description: "Technical craft, renewable solar installation, and tailoring apprenticeships for young women.",
      organisation_type: "TRAINING_INSTITUTE",
      email: "admissions@equalhorizons.org",
      phone_number: "+256 755 456789",
      website: "https://equalhorizons.org",
      address: "Block B, Industrial Park",
      district: "Jinja",
      country: "Uganda",
      verification_status: "PENDING",
      created_at: "2026-01-20T08:30:00Z"
    }
  ];

  let users = [
    {
      id: "usr_admin",
      email: "admin@femmetech.org",
      first_name: "Dr. Amina",
      last_name: "Okonjo",
      phone_number: "+256 701 112233",
      role: "ORGANISATION_ADMIN",
      is_active: true,
      is_verified: true,
      organisation_id: "org_1",
      created_at: "2025-01-10T09:00:00Z"
    },
    {
      id: "usr_beneficiary",
      email: "fatima.zara@gmail.com",
      first_name: "Fatima",
      last_name: "Zara",
      phone_number: "+256 788 334455",
      role: "BENEFICIARY",
      is_active: true,
      is_verified: true,
      created_at: "2025-03-01T10:00:00Z"
    },
    {
      id: "usr_field_officer",
      email: "sarah.k@femmetech.org",
      first_name: "Sarah",
      last_name: "Kibuuka",
      phone_number: "+256 752 667788",
      role: "FIELD_OFFICER",
      is_active: true,
      is_verified: true,
      organisation_id: "org_1",
      created_at: "2025-01-15T10:00:00Z"
    },
    {
      id: "usr_platform_admin",
      email: "director@voiceofagirl.org",
      first_name: "Elena",
      last_name: "Vance",
      phone_number: "+256 700 990011",
      role: "PLATFORM_ADMIN",
      is_active: true,
      is_verified: true,
      created_at: "2024-12-01T08:00:00Z"
    }
  ];

  let beneficiaryInterestSubmissions: any[] = [];

  let beneficiaryProfiles: Record<string, any> = {
    "usr_beneficiary": {
      user_id: "usr_beneficiary",
      date_of_birth: "2004-06-14",
      gender: "Female",
      district: "Kampala",
      region: "Central",
      country: "Uganda",
      education_level: "SECONDARY_A_LEVEL",
      school_or_institution: "Mengo Senior School",
      employment_status: "UNEMPLOYED",
      career_goals: "Aspiring Full-Stack Software Developer & AI Data Analyst. Aiming to build tech solutions for community healthcare.",
      bio: "Self-motivated learner who completed A-level with physics and math. Keen on software coding, graphic design, and leadership.",
      skills: ["Python Basics", "HTML/CSS", "Digital Literacy", "Public Speaking"],
      interests: ["Software Engineering", "Renewable Energy", "Girls Mentorship"],
      profile_completed: true
    }
  };

  let programmes = [
    {
      id: "prog_1",
      organisation_id: "org_1",
      title: "Girls in Tech & AI Leadership Cohort 2026",
      description: "A comprehensive 6-month scholarship and intensive apprenticeship empowering young women with software development, cloud computing, and workplace leadership.",
      category: "STEM & Tech",
      programme_type: "NEW_PROGRAMME",
      location: "Kampala & Remote Hybrid",
      start_date: "2026-02-01",
      end_date: "2026-08-01",
      status: "ACTIVE",
      target_beneficiaries: 150,
      current_beneficiaries: 128,
      completion_rate: 94.2,
      attendance_rate: 88.5,
      dropout_rate: 3.8,
      criteria_education: ["SECONDARY_O_LEVEL", "SECONDARY_A_LEVEL", "VOCATIONAL_CERTIFICATE", "DIPLOMA"],
      criteria_skills: ["Digital Literacy", "Computer Basics", "Problem Solving"],
      criteria_locations: ["Kampala", "Wakiso", "Mukono"],
      criteria_min_age: 18,
      criteria_max_age: 26
    },
    {
      id: "prog_2",
      organisation_id: "org_1",
      title: "Young Female Digital Micro-Entrepreneurs",
      description: "Bridging digital commerce, mobile money bookkeeping, and product branding for young female-led micro-enterprises.",
      category: "Entrepreneurship",
      programme_type: "EXISTING_PROGRAMME",
      location: "Jinja & Wakiso",
      start_date: "2025-09-01",
      end_date: "2026-04-30",
      status: "ACTIVE",
      target_beneficiaries: 100,
      current_beneficiaries: 92,
      completion_rate: 91.0,
      attendance_rate: 86.2,
      dropout_rate: 4.5,
      criteria_education: ["PRIMARY", "SECONDARY_O_LEVEL", "VOCATIONAL_CERTIFICATE"],
      criteria_skills: ["Basic Math", "Trade / Craft", "Customer Relations"],
      criteria_locations: ["Jinja", "Wakiso"],
      criteria_min_age: 18,
      criteria_max_age: 29
    }
  ];

  let participations = [
    {
      id: "part_1",
      beneficiary_id: "usr_beneficiary",
      programme_id: "prog_1",
      participation_status: "ACTIVE",
      attendance_rate: 92.5,
      joined_at: "2026-02-02T10:00:00Z",
      outcome_notes: "Strong technical progress in Python modules; submitted baseline and monitoring check-ins.",
      beneficiary_name: "Fatima Zara",
      beneficiary_email: "fatima.zara@gmail.com",
      match_score: 95,
      match_reasons: [
        "Location aligns: Kampala",
        "Age 21 falls directly within eligible bracket (18–26)",
        "Education level (SECONDARY_A_LEVEL) matches criteria",
        "Key skills matched: Digital Literacy, Python Basics"
      ],
      missing_requirements: []
    },
    {
      id: "part_2",
      beneficiary_id: "usr_b2",
      programme_id: "prog_1",
      participation_status: "ACTIVE",
      attendance_rate: 82.0,
      joined_at: "2026-02-03T11:00:00Z",
      outcome_notes: "Active participant; reported transportation difficulty on rainy days.",
      beneficiary_name: "Grace Mwangi",
      beneficiary_email: "grace.mwangi@gmail.com",
      match_score: 85,
      match_reasons: [
        "Location aligns: Wakiso",
        "Age 20 falls directly within eligible bracket",
        "Education level (SECONDARY_A_LEVEL) matches criteria"
      ],
      missing_requirements: ["Could benefit from additional typing practice"]
    },
    {
      id: "part_3",
      beneficiary_id: "usr_b3",
      programme_id: "prog_1",
      participation_status: "ACTIVE",
      attendance_rate: 94.0,
      joined_at: "2026-02-03T11:30:00Z",
      outcome_notes: "Excelling in front-end design and team peer tutoring.",
      beneficiary_name: "Beatrice Nakato",
      beneficiary_email: "beatrice.n@gmail.com",
      match_score: 90,
      match_reasons: [
        "Location aligns: Kampala",
        "Age 22 falls directly within eligible bracket",
        "Strong interest in Software Engineering"
      ],
      missing_requirements: []
    },
    {
      id: "part_4",
      beneficiary_id: "usr_b4",
      programme_id: "prog_1",
      participation_status: "SELECTED",
      attendance_rate: 0.0,
      joined_at: "2026-02-10T14:00:00Z",
      outcome_notes: "Recently selected for late-enrollment cohort.",
      beneficiary_name: "Janet Auma",
      beneficiary_email: "janet.auma@gmail.com",
      match_score: 88,
      match_reasons: [
        "Location aligns: Kampala",
        "Meets educational requirements"
      ],
      missing_requirements: []
    }
  ];

  let opportunities = [
    {
      id: "opp_1",
      programme_id: "prog_1",
      title: "Full Tech Immersion Scholarship & Laptop Grant",
      description: "Tuition-free sponsorship, brand-new learning laptop, mobile data stipend, and dedicated 1-on-1 industry mentorship.",
      opportunity_type: "SCHOLARSHIP",
      benefits: "100% tuition coverage, Dell Core i5 Laptop, monthly internet stipend (50GB), certified Google Cloud & Python exams.",
      requirements: "Young women aged 18-26 resident in Greater Kampala, O-Level or A-Level completed, demonstrated drive for tech.",
      application_deadline: "2026-04-15",
      available_slots: 35,
      status: "OPEN",
      organisation_name: "FemmeTech Africa Foundation",
      location: "Kampala"
    },
    {
      id: "opp_2",
      programme_id: "prog_1",
      title: "Junior Frontend Developer Internship (Paid)",
      description: "3-month paid internship placement with partner software houses across Kampala and remote fintech teams.",
      opportunity_type: "INTERNSHIP",
      benefits: "UGX 900,000 / month stipend, hands-on production code experience, strong chance of full-time offer.",
      requirements: "Completed HTML/CSS/JavaScript baseline training or equivalent portfolio.",
      application_deadline: "2026-05-01",
      available_slots: 20,
      status: "OPEN",
      organisation_name: "FemmeTech Africa Foundation",
      location: "Kampala & Hybrid"
    },
    {
      id: "opp_3",
      programme_id: "prog_2",
      title: "Digital Business Seed Fund Grant ($500)",
      description: "Non-repayable seed capital for women-owned micro businesses to implement digital payment systems and inventory tooling.",
      opportunity_type: "GRANT",
      benefits: "$500 direct grant, smartphone with POS app, business mentoring.",
      requirements: "Operational informal business for at least 3 months, committed to digital bookkeeping.",
      application_deadline: "2026-04-30",
      available_slots: 25,
      status: "OPEN",
      organisation_name: "Young Women Agri-Entrepreneurs Hub",
      location: "Jinja & Wakiso"
    }
  ];

  let applications: any[] = [
    {
      id: "app_1",
      beneficiary_id: "usr_beneficiary",
      opportunity_id: "opp_1",
      status: "ACCEPTED",
      application_date: "2026-01-15T09:30:00Z",
      statement_of_purpose: "Technology has the power to bridge gender inequalities. I want to build medical record systems for underserved rural clinics.",
      notes: "High potential, outstanding baseline logic test score.",
      reviewed_by: "Dr. Amina Okonjo",
      opportunity_title: "Full Tech Immersion Scholarship & Laptop Grant",
      organisation_name: "FemmeTech Africa Foundation"
    }
  ];

  // Forms Database
  let forms = [
    {
      id: "form_baseline",
      organisation_id: "org_1",
      programme_id: "prog_1",
      title: "Cohort Baseline Survey — Entry Profile & Socio-Economic Status",
      description: "Mandatory intake questionnaire to measure your situation prior to programme commencement. Used as reference for outcome tracking.",
      form_type: "BASELINE",
      status: "PUBLISHED",
      response_deadline: "2026-03-31T23:59:59Z",
      created_at: "2026-01-25T10:00:00Z",
      responses_count: 118,
      questions: [
        {
          id: "q_b1",
          form_id: "form_baseline",
          question_text: "What is your current primary employment status?",
          help_text: "Select the option that best describes your principal daily activity.",
          question_type: "MULTIPLE_CHOICE",
          required: true,
          options: ["Unemployed & Seeking Work", "Student / In Education", "Self-Employed / Informal Trader", "Part-Time Employed", "Full-Time Employed"],
          order: 1
        },
        {
          id: "q_b2",
          form_id: "form_baseline",
          question_text: "Rate your current digital and coding proficiency level (1 = None, 5 = Advanced)",
          help_text: "Be completely candid; this will calibrate instruction modules.",
          question_type: "RATING_SCALE",
          required: true,
          options: ["1 - Absolute Beginner", "2 - Basic Device User", "3 - Intermediate / Some Coding", "4 - Competent", "5 - Advanced"],
          order: 2
        },
        {
          id: "q_b3",
          form_id: "form_baseline",
          question_text: "What is your average monthly personal income or upkeep allowance (UGX / USD)?",
          help_text: "Enter your approximate net income bracket before joining.",
          question_type: "DROPDOWN",
          required: true,
          options: ["Zero / Fully Dependent on Guardians", "Under UGX 150,000 (<$40)", "UGX 150,000 - 350,000 ($40-$95)", "UGX 350,000 - 800,000 ($95-$215)", "Above UGX 800,000 (>$215)"],
          order: 3
        },
        {
          id: "q_b4",
          form_id: "form_baseline",
          question_text: "Do you own a reliable personal computer/laptop?",
          help_text: "Helps us allocate hub workstations or hardware loaners.",
          question_type: "YES_NO",
          required: true,
          options: ["Yes", "No"],
          order: 4
        },
        {
          id: "q_b5",
          form_id: "form_baseline",
          question_text: "What major challenges do you anticipate that might affect your daily attendance?",
          help_text: "Select all that currently pose a barrier.",
          question_type: "CHECKBOX",
          required: false,
          options: ["Transport / Commuter fare expenses", "Lack of electricity / device charging", "Family & child care obligations", "Internet connectivity costs", "Health or medical concerns", "Safety travelling after sunset"],
          order: 5
        },
        {
          id: "q_b6",
          form_id: "form_baseline",
          question_text: "What is your main goal and ambition for the next 12 months?",
          help_text: "Describe in your own words.",
          question_type: "LONG_TEXT",
          required: true,
          options: [],
          order: 6
        }
      ]
    },
    {
      id: "form_monitoring",
      organisation_id: "org_1",
      programme_id: "prog_1",
      title: "Bi-Weekly Progress & Early Challenge Monitoring",
      description: "Quick pulse check during programme execution to identify bottlenecks, attendance barriers, and immediate support needs.",
      form_type: "MONITORING",
      status: "PUBLISHED",
      response_deadline: "2026-04-15T23:59:59Z",
      created_at: "2026-02-15T12:00:00Z",
      responses_count: 104,
      questions: [
        {
          id: "q_m1",
          form_id: "form_monitoring",
          question_text: "How would you rate your learning pace and session comprehension so far?",
          help_text: "1 = Falling behind, 5 = Excellent progress",
          question_type: "RATING_SCALE",
          required: true,
          options: ["1", "2", "3", "4", "5"],
          order: 1
        },
        {
          id: "q_m2",
          form_id: "form_monitoring",
          question_text: "Have you faced any disruptions in attending classes over the past fortnight?",
          help_text: "Please indicate if anything hindered your participation.",
          question_type: "YES_NO",
          required: true,
          options: ["Yes", "No"],
          order: 2
        },
        {
          id: "q_m3",
          form_id: "form_monitoring",
          question_text: "What specific barrier or problem occurred?",
          help_text: "Choose the primary category.",
          question_type: "DROPDOWN",
          required: false,
          options: ["Transport / Travel Fares", "Device / Power Blackouts", "Illness / Family Emergency", "Caregiver Duties", "Course Material Complexity", "None / Going Smoothly"],
          order: 3
        },
        {
          id: "q_m4",
          form_id: "form_monitoring",
          question_text: "What assistance or adjustment from the programme team would help you most?",
          help_text: "Your feedback triggers early field response actions.",
          question_type: "LONG_TEXT",
          required: false,
          options: [],
          order: 4
        }
      ]
    },
    {
      id: "form_endline",
      organisation_id: "org_1",
      programme_id: "prog_1",
      title: "Endline Impact Evaluation — Immediate Outcomes",
      description: "Administered upon programme completion to measure acquired capabilities, certifications, and immediate transitions.",
      form_type: "ENDLINE",
      status: "PUBLISHED",
      response_deadline: "2026-08-15T23:59:59Z",
      created_at: "2026-02-28T14:00:00Z",
      responses_count: 42,
      questions: [
        {
          id: "q_e1",
          form_id: "form_endline",
          question_text: "What is your updated digital and coding competency level?",
          help_text: "Rate your skills now compared to the beginning.",
          question_type: "RATING_SCALE",
          required: true,
          options: ["1 - Beginner", "2 - Elementary", "3 - Competent", "4 - Proficient", "5 - Advanced / Production Ready"],
          order: 1
        },
        {
          id: "q_e2",
          form_id: "form_endline",
          question_text: "Have you secured employment, an internship, or freelancing clients?",
          help_text: "Select your current status.",
          question_type: "MULTIPLE_CHOICE",
          required: true,
          options: ["Employed Full-Time", "Employed Part-Time / Internship", "Started Own Tech / Freelance Enterprise", "In Advanced Degree / Further Studies", "Actively Interviewing"],
          order: 2
        },
        {
          id: "q_e3",
          form_id: "form_endline",
          question_text: "How much did your monthly personal earnings change?",
          help_text: "Current earnings level.",
          question_type: "DROPDOWN",
          required: true,
          options: ["Increased significantly (>100% gain)", "Increased moderately (25%-100% gain)", "Slight increase (<25% gain)", "Remained about the same", "Not yet generating income"],
          order: 3
        },
        {
          id: "q_e4",
          form_id: "form_endline",
          question_text: "What was the single most valuable outcome of this programme for you?",
          help_text: "E.g. technical confidence, peer network, financial independence.",
          question_type: "LONG_TEXT",
          required: true,
          options: [],
          order: 4
        }
      ]
    },
    {
      id: "form_followup",
      organisation_id: "org_1",
      programme_id: "prog_1",
      title: "6-Month Longitudinal Follow-Up Survey",
      description: "Automated longitudinal survey dispatched 6 months post-graduation to measure sustained career trajectory, resilience, and income stability.",
      form_type: "FOLLOW_UP",
      status: "PUBLISHED",
      follow_up_interval_months: 6,
      response_deadline: "2027-02-15T23:59:59Z",
      created_at: "2026-03-01T09:00:00Z",
      responses_count: 28,
      questions: [
        {
          id: "q_f1",
          form_id: "form_followup",
          question_text: "Are you currently employed or running a registered business?",
          help_text: "Long-term employment tracking.",
          question_type: "YES_NO",
          required: true,
          options: ["Yes", "No"],
          order: 1
        },
        {
          id: "q_f2",
          form_id: "form_followup",
          question_text: "What is your current monthly income bracket in USD equivalent?",
          help_text: "Tracked for longitudinal economic empowerment analysis.",
          question_type: "DROPDOWN",
          required: true,
          options: ["Under $100 / month", "$100 - $250 / month", "$250 - $500 / month", "$500 - $1,000 / month", "Over $1,000 / month"],
          order: 2
        },
        {
          id: "q_f3",
          form_id: "form_followup",
          question_text: "Are you still actively utilising the specific skills gained during the programme?",
          help_text: "Measures skill retention and market relevance.",
          question_type: "MULTIPLE_CHOICE",
          required: true,
          options: ["Daily in my primary work", "Weekly in projects / freelance", "Occasionally", "Not currently utilising"],
          order: 3
        }
      ]
    }
  ];

  let formResponses = [
    {
      id: "resp_1",
      form_id: "form_baseline",
      beneficiary_id: "usr_beneficiary",
      beneficiary_name: "Fatima Zara",
      submitted_at: "2026-02-04T14:30:00Z",
      status: "SUBMITTED",
      submitted_via: "WEB",
      answers: {
        "q_b1": "Unemployed & Seeking Work",
        "q_b2": "2 - Basic Device User",
        "q_b3": "Zero / Fully Dependent on Guardians",
        "q_b4": "No",
        "q_b5": ["Transport / Commuter fare expenses", "Internet connectivity costs"],
        "q_b6": "To master full-stack software development, gain a software developer role in health-tech, and support my younger sisters' schooling."
      }
    },
    {
      id: "resp_2",
      form_id: "form_monitoring",
      beneficiary_id: "usr_beneficiary",
      beneficiary_name: "Fatima Zara",
      submitted_at: "2026-02-25T16:00:00Z",
      status: "SUBMITTED",
      submitted_via: "WEB",
      answers: {
        "q_m1": "4",
        "q_m2": "Yes",
        "q_m3": "Transport / Travel Fares",
        "q_m4": "Taxi minibus fares in Kampala increased by 40% due to local fuel surcharges, making it hard to reach the lab every morning."
      }
    }
  ];

  // Challenges Tracking Database
  let challenges: any[] = [
    {
      id: "ch_1",
      programme_id: "prog_1",
      programme_title: "Girls in Tech & AI Leadership Cohort 2026",
      beneficiary_id: "usr_beneficiary",
      beneficiary_name: "Fatima Zara",
      category: "TRANSPORT",
      description: "Severe commuter fare inflation along Kawempe-Bugolobi route. Daily round-trip taxi fares escalated from UGX 5,000 to UGX 8,500.",
      severity: "HIGH",
      status: "IN_PROGRESS",
      assigned_to: "usr_field_officer",
      assigned_to_name: "Sarah Kibuuka",
      reported_at: "2026-02-25T16:05:00Z",
      audit_history: [
        {
          timestamp: "2026-02-25T16:05:00Z",
          actor: "fatima.zara@gmail.com",
          action: "REPORTED",
          note: "Triggered automatically from bi-weekly monitoring check-in"
        },
        {
          timestamp: "2026-02-26T09:15:00Z",
          actor: "admin@femmetech.org",
          action: "ASSIGNED",
          note: "Assigned to Field Officer Sarah Kibuuka to review localized transport subsidy."
        }
      ]
    },
    {
      id: "ch_2",
      programme_id: "prog_1",
      programme_title: "Girls in Tech & AI Leadership Cohort 2026",
      beneficiary_id: "usr_b2",
      beneficiary_name: "Grace Mwangi",
      category: "MATERIALS",
      description: "Laptop charging power adapter damaged by voltage surge during thunderstorms in Wakiso.",
      severity: "MEDIUM",
      status: "OPEN",
      assigned_to: "usr_field_officer",
      assigned_to_name: "Sarah Kibuuka",
      reported_at: "2026-02-27T11:20:00Z",
      audit_history: [
        {
          timestamp: "2026-02-27T11:20:00Z",
          actor: "grace.mwangi@gmail.com",
          action: "REPORTED",
          note: "Reported directly via participant dashboard"
        }
      ]
    },
    {
      id: "ch_3",
      programme_id: "prog_1",
      programme_title: "Girls in Tech & AI Leadership Cohort 2026",
      beneficiary_id: "usr_b3",
      beneficiary_name: "Beatrice Nakato",
      category: "HEALTH",
      description: "Severe malaria episode requiring 4 days bedrest and medication support.",
      severity: "HIGH",
      status: "RESOLVED",
      assigned_to: "usr_field_officer",
      assigned_to_name: "Sarah Kibuuka",
      reported_at: "2026-02-14T08:00:00Z",
      resolved_at: "2026-02-19T14:30:00Z",
      resolution_notes: "Dispatched partner clinic medical voucher. Health verified recovered; provided catch-up recording links.",
      audit_history: [
        {
          timestamp: "2026-02-14T08:00:00Z",
          actor: "beatrice.n@gmail.com",
          action: "REPORTED",
          note: "Reported illness"
        },
        {
          timestamp: "2026-02-19T14:30:00Z",
          actor: "sarah.k@femmetech.org",
          action: "RESOLVED",
          note: "Clinic visit completed. Medication provided and participant back in session."
        }
      ]
    },
    {
      id: "ch_4",
      programme_id: "prog_1",
      programme_title: "Girls in Tech & AI Leadership Cohort 2026",
      beneficiary_id: "usr_b5",
      beneficiary_name: "Aisha Nambi",
      category: "SAFETY",
      description: "Evening transit darkness near unlit railway crossing leaving lab past 6:30 PM.",
      severity: "CRITICAL",
      status: "RESOLVED",
      assigned_to: "usr_field_officer",
      assigned_to_name: "Sarah Kibuuka",
      reported_at: "2026-02-10T19:00:00Z",
      resolved_at: "2026-02-12T10:00:00Z",
      resolution_notes: "Adjusted in-person lab dismissal to 5:00 PM and arranged group van drop-off at main illuminated stage.",
      audit_history: [
        {
          timestamp: "2026-02-10T19:00:00Z",
          actor: "aisha.n@gmail.com",
          action: "REPORTED",
          note: "Safety concern flagged"
        },
        {
          timestamp: "2026-02-12T10:00:00Z",
          actor: "admin@femmetech.org",
          action: "RESOLVED",
          note: "Shifted lab timetable and secured shuttle arrangements."
        }
      ]
    }
  ];

  // KPIs Database
  let kpis = [
    {
      id: "kpi_1",
      programme_id: "prog_1",
      name: "Participants Completing Technical Training",
      description: "Beneficiaries achieving at least 80% attendance and passing capstone projects.",
      category: "OUTPUT",
      target_value: 150,
      current_value: 128,
      unit: "participants",
      measurement_frequency: "Bi-Weekly"
    },
    {
      id: "kpi_2",
      programme_id: "prog_1",
      name: "Graduates Securing Paid Tech Roles / Internships",
      description: "Formal contracts, apprenticeships, or verified freelance engagements within 90 days of graduation.",
      category: "OUTCOME",
      target_value: 100,
      current_value: 78,
      unit: "participants",
      measurement_frequency: "Monthly"
    },
    {
      id: "kpi_3",
      programme_id: "prog_1",
      name: "Beneficiaries Achieving >$150/mo Earnings Increase",
      description: "Measurable income transition compared against initial baseline records.",
      category: "IMPACT",
      target_value: 90,
      current_value: 65,
      unit: "participants",
      measurement_frequency: "Quarterly"
    },
    {
      id: "kpi_4",
      programme_id: "prog_1",
      name: "Laptop & Cloud Access Resource Deployment",
      description: "Hardware laptops and mobile internet packages distributed to enrolled girls.",
      category: "INPUT",
      target_value: 150,
      current_value: 145,
      unit: "laptops",
      measurement_frequency: "Milestone"
    }
  ];

  // Verification Tasks for Field Officers
  let verificationTasks = [
    {
      id: "task_1",
      assigned_officer_id: "usr_field_officer",
      beneficiary_id: "usr_beneficiary",
      beneficiary_name: "Fatima Zara",
      beneficiary_phone: "+256 788 334455",
      beneficiary_location: "Kawempe North, Kampala",
      programme_id: "prog_1",
      programme_title: "Girls in Tech & AI Leadership Cohort 2026",
      status: "VERIFIED",
      home_visit_conducted: true,
      id_documents_checked: true,
      guardian_contacted: true,
      field_notes: "Visited residence. Mother confirmed Fatima's passion and commitment. Academic certificates verified.",
      gps_coords: "0.3644° N, 32.5599° E",
      scheduled_for: "2026-02-05"
    },
    {
      id: "task_2",
      assigned_officer_id: "usr_field_officer",
      beneficiary_id: "usr_b2",
      beneficiary_name: "Grace Mwangi",
      beneficiary_phone: "+256 702 445566",
      beneficiary_location: "Nansana West, Wakiso",
      programme_id: "prog_1",
      programme_title: "Girls in Tech & AI Leadership Cohort 2026",
      status: "IN_PROGRESS",
      home_visit_conducted: true,
      id_documents_checked: true,
      guardian_contacted: false,
      field_notes: "Home visited. Follow up phone call required with guardian who was at work.",
      gps_coords: "0.3621° N, 32.5283° E",
      scheduled_for: "2026-03-08"
    },
    {
      id: "task_3",
      assigned_officer_id: "usr_field_officer",
      beneficiary_id: "usr_b4",
      beneficiary_name: "Janet Auma",
      beneficiary_phone: "+256 779 889900",
      beneficiary_location: "Bwaise II, Kampala",
      programme_id: "prog_1",
      programme_title: "Girls in Tech & AI Leadership Cohort 2026",
      status: "PENDING",
      home_visit_conducted: false,
      id_documents_checked: false,
      guardian_contacted: false,
      field_notes: "Scheduled field visit for Friday afternoon.",
      gps_coords: "0.3512° N, 32.5641° E",
      scheduled_for: "2026-03-12"
    }
  ];

  // Notifications Database
  let notifications = [
    {
      id: "notif_1",
      recipient_id: "usr_beneficiary",
      title: "Bi-Weekly Progress Survey Assigned",
      message: "Please complete your Bi-Weekly Progress & Early Challenge Monitoring form before April 15.",
      type: "FORM_ASSIGNED",
      is_read: false,
      created_at: "2026-03-01T08:00:00Z"
    },
    {
      id: "notif_2",
      recipient_id: "usr_beneficiary",
      title: "Scholarship Application Approved!",
      message: "Congratulations! You have been accepted into the Full Tech Immersion Scholarship & Laptop Grant.",
      type: "APPLICATION_STATUS",
      is_read: true,
      created_at: "2026-01-20T10:00:00Z"
    },
    {
      id: "notif_3",
      recipient_id: "usr_beneficiary",
      title: "Field Officer Visit Scheduled",
      message: "Field Officer Sarah Kibuuka has scheduled an onboarding verification visit for your area.",
      type: "SYSTEM",
      is_read: true,
      created_at: "2026-02-03T11:00:00Z"
    }
  ];

  // Helper for Rule-Based Matcher
  function runMatchingEngine(profile: any, reqs: any) {
    let score = 0;
    const reasons: string[] = [];
    const missing: string[] = [];

    // Location (25 pts)
    const allowedLocs = (reqs.allowed_locations || []).map((l: string) => l.toLowerCase());
    const bDistrict = (profile.district || "").toLowerCase();
    if (allowedLocs.length === 0 || allowedLocs.includes(bDistrict)) {
      score += 25;
      reasons.push(`Location matches: ${profile.district || "Target District"}`);
    } else {
      missing.push(`Resident in ${profile.district}; programme prioritises ${reqs.allowed_locations.join(", ")}`);
    }

    // Age (20 pts)
    let age = 21;
    if (profile.date_of_birth) {
      const birthYear = parseInt(profile.date_of_birth.split("-")[0], 10);
      age = new Date().getFullYear() - birthYear;
    }
    const minAge = reqs.min_age || 18;
    const maxAge = reqs.max_age || 28;
    if (age >= minAge && age <= maxAge) {
      score += 20;
      reasons.push(`Age ${age} falls directly within eligible bracket (${minAge}–${maxAge} years)`);
    } else {
      missing.push(`Age ${age} is outside preferred bracket (${minAge}–${maxAge})`);
    }

    // Education (20 pts)
    const allowedEdu = reqs.required_education || [];
    if (allowedEdu.length === 0 || allowedEdu.includes(profile.education_level)) {
      score += 20;
      reasons.push(`Education level (${profile.education_level}) matches requirement`);
    } else {
      missing.push(`Current education is ${profile.education_level}; requires ${allowedEdu.join(", ")}`);
    }

    // Skills (20 pts)
    const desiredSkills = (reqs.desired_skills || []).map((s: string) => s.toLowerCase());
    const userSkills = (profile.skills || []).map((s: string) => s.toLowerCase());
    const matchedSkills = desiredSkills.filter((d: string) => userSkills.some((u: string) => u.includes(d) || d.includes(u)));
    if (desiredSkills.length === 0) {
      score += 20;
      reasons.push("Open enrollment profile (no prior technical prerequisites mandatory)");
    } else if (matchedSkills.length > 0) {
      const ratio = Math.min(1.0, matchedSkills.length / desiredSkills.length);
      score += Math.round(ratio * 20);
      reasons.push(`Matched key skills: ${matchedSkills.slice(0, 3).join(", ")}`);
    } else {
      missing.push(`Recommended preliminary modules for: ${desiredSkills.slice(0, 2).join(", ")}`);
    }

    // Career goals & interests (15 pts)
    const userInterests = (profile.interests || []).map((i: string) => i.toLowerCase());
    const matchedInterests = (reqs.desired_interests || []).filter((i: string) => userInterests.includes(i.toLowerCase()));
    if (matchedInterests.length > 0 || (profile.career_goals && profile.career_goals.length > 10)) {
      score += 15;
      reasons.push("Demonstrated strong career goals alignment with youth development objectives");
    } else {
      score += 8;
    }

    return {
      match_score: Math.min(100, Math.max(0, score)),
      reasons,
      missing_requirements: missing
    };
  }

  // ==================== RESTful API ROUTES ====================

  // Public beneficiary intake. This records interest for staff review without creating a login.
  app.get("/api/public/beneficiary-interest/", (_req, res) => {
    res.json(beneficiaryInterestSubmissions);
  });

  app.post("/api/public/beneficiary-interest/", (req, res) => {
    const { first_name, last_name, email, phone_number, district, education_level, interest_area } = req.body;
    if (!first_name || !last_name || !email || !phone_number || !district || !education_level || !interest_area) {
      return res.status(400).json({ detail: "All intake fields are required." });
    }

    const submission = {
      id: `interest_${Date.now()}`,
      first_name,
      last_name,
      email,
      phone_number,
      district,
      education_level,
      interest_area,
      status: "NEW",
      submitted_at: new Date().toISOString()
    };
    beneficiaryInterestSubmissions.unshift(submission);
    return res.status(201).json(submission);
  });

  // Auth Endpoints
  app.post("/api/auth/login/", (req, res) => {
    const { email } = req.body;
    const user = users.find((u) => u.email.toLowerCase() === (email || "").toLowerCase()) || users[0];
    res.json({
      access: "jwt_access_token_demo_sample",
      refresh: "jwt_refresh_token_demo_sample",
      user
    });
  });

  app.post("/api/auth/register/", (req, res) => {
    const { email, first_name, last_name, phone_number, role, organisation_name } = req.body;
    let orgId = undefined;
    if (role === "ORGANISATION_ADMIN" && organisation_name) {
      const newOrg = {
        id: `org_${Date.now()}`,
        name: organisation_name,
        description: "Registered partner organisation.",
        organisation_type: "NGO" as const,
        email: email,
        phone_number: phone_number || "",
        website: "",
        address: "HQ Office",
        district: "Kampala",
        country: "Uganda",
        verification_status: "PENDING" as const,
        created_at: new Date().toISOString()
      };
      organisations.push(newOrg);
      orgId = newOrg.id;
    }

    const newUser = {
      id: `usr_${Date.now()}`,
      email,
      first_name,
      last_name,
      phone_number: phone_number || "",
      role: role || "BENEFICIARY",
      is_active: true,
      is_verified: false,
      organisation_id: orgId,
      created_at: new Date().toISOString()
    };
    users.push(newUser);

    if (newUser.role === "BENEFICIARY") {
      beneficiaryProfiles[newUser.id] = {
        user_id: newUser.id,
        date_of_birth: "2004-01-01",
        gender: "Female",
        district: "Kampala",
        region: "Central",
        country: "Uganda",
        education_level: "SECONDARY_A_LEVEL",
        school_or_institution: "",
        employment_status: "UNEMPLOYED",
        career_goals: "",
        bio: "",
        skills: ["Digital Basics"],
        interests: ["Technology"],
        profile_completed: false
      };
    }

    res.status(201).json({
      access: "jwt_access_token_sample",
      refresh: "jwt_refresh_token_sample",
      user: newUser
    });
  });

  app.get("/api/auth/me/", (req, res) => {
    const emailHeader = req.headers["x-user-email"] as string;
    const user = users.find((u) => u.email === emailHeader) || users[0];
    const profile = beneficiaryProfiles[user.id];
    res.json({
      user,
      profile,
      organisation: user.organisation_id ? organisations.find((o) => o.id === user.organisation_id) : null
    });
  });

  // Programmes Endpoints
  app.get("/api/programmes/", (req, res) => {
    res.json(programmes);
  });

  app.post("/api/programmes/", (req, res) => {
    const body = req.body;
    const newProg = {
      id: `prog_${Date.now()}`,
      organisation_id: body.organisation_id || "org_1",
      title: body.title || "New Empowerment Initiative",
      description: body.description || "",
      category: body.category || "Vocational & Life Skills",
      programme_type: body.programme_type || "NEW_PROGRAMME",
      location: body.location || "Kampala",
      start_date: body.start_date || new Date().toISOString().split("T")[0],
      end_date: body.end_date || "2026-12-31",
      status: body.status || "ACTIVE",
      target_beneficiaries: Number(body.target_beneficiaries) || 100,
      current_beneficiaries: 0,
      completion_rate: 0.0,
      attendance_rate: 100.0,
      dropout_rate: 0.0,
      criteria_education: body.criteria_education || ["SECONDARY_O_LEVEL"],
      criteria_skills: body.criteria_skills || [],
      criteria_locations: body.criteria_locations || [body.location || "Kampala"],
      criteria_min_age: body.criteria_min_age || 18,
      criteria_max_age: body.criteria_max_age || 30
    };
    programmes.unshift(newProg);
    res.status(201).json(newProg);
  });

  app.get("/api/programmes/:id/", (req, res) => {
    const prog = programmes.find((p) => p.id === req.params.id);
    if (!prog) return res.status(404).json({ detail: "Programme not found" });
    res.json(prog);
  });

  app.put("/api/programmes/:id/", (req, res) => {
    const index = programmes.findIndex((p) => p.id === req.params.id);
    if (index === -1) return res.status(404).json({ detail: "Programme not found" });
    programmes[index] = { ...programmes[index], ...req.body };
    res.json(programmes[index]);
  });

  // Participants & Matching
  app.get("/api/programmes/:id/participants/", (req, res) => {
    const parts = participations.filter((p) => p.programme_id === req.params.id);
    res.json(parts);
  });

  app.post("/api/programmes/:id/participants/", (req, res) => {
    const prog = programmes.find((p) => p.id === req.params.id);
    const { beneficiary_id, beneficiary_name, beneficiary_email } = req.body;
    
    // Transparent rule-based match calculation
    const profile = beneficiaryProfiles[beneficiary_id] || {
      district: "Kampala",
      education_level: "SECONDARY_A_LEVEL",
      skills: ["Digital Basics"],
      interests: ["Tech"],
      date_of_birth: "2004-01-01"
    };
    const match = runMatchingEngine(profile, {
      allowed_locations: prog?.criteria_locations || ["Kampala"],
      min_age: prog?.criteria_min_age || 18,
      max_age: prog?.criteria_max_age || 28,
      required_education: prog?.criteria_education || [],
      desired_skills: prog?.criteria_skills || []
    });

    const newPart = {
      id: `part_${Date.now()}`,
      beneficiary_id: beneficiary_id || `usr_b_${Date.now()}`,
      programme_id: req.params.id,
      participation_status: "SELECTED" as const,
      attendance_rate: 0.0,
      joined_at: new Date().toISOString(),
      outcome_notes: "Participant enrolled via portal.",
      beneficiary_name: beneficiary_name || "New Applicant",
      beneficiary_email: beneficiary_email || "applicant@voice.org",
      match_score: match.match_score,
      match_reasons: match.reasons,
      missing_requirements: match.missing_requirements
    };
    participations.push(newPart);
    if (prog) prog.current_beneficiaries = (prog.current_beneficiaries || 0) + 1;
    res.status(201).json(newPart);
  });

  app.patch("/api/participation/:id/", (req, res) => {
    const part = participations.find((p) => p.id === req.params.id);
    if (!part) return res.status(404).json({ detail: "Participation not found" });
    if (req.body.participation_status) part.participation_status = req.body.participation_status;
    if (req.body.attendance_rate !== undefined) part.attendance_rate = req.body.attendance_rate;
    if (req.body.outcome_notes) part.outcome_notes = req.body.outcome_notes;
    res.json(part);
  });

  // Forms Engine Endpoints
  app.get("/api/programmes/:id/forms/", (req, res) => {
    const progForms = forms.filter((f) => f.programme_id === req.params.id);
    res.json(progForms);
  });

  app.get("/api/forms/:id/", (req, res) => {
    const f = forms.find((form) => form.id === req.params.id);
    if (!f) return res.status(404).json({ detail: "Form not found" });
    res.json(f);
  });

  app.post("/api/programmes/:id/forms/", (req, res) => {
    const body = req.body;
    const newForm = {
      id: `form_${Date.now()}`,
      organisation_id: "org_1",
      programme_id: req.params.id,
      title: body.title || "Custom Participant Survey",
      description: body.description || "",
      form_type: body.form_type || "CUSTOM",
      status: body.status || "DRAFT",
      response_deadline: body.response_deadline || new Date(Date.now() + 14 * 86400000).toISOString(),
      follow_up_interval_months: body.follow_up_interval_months,
      created_at: new Date().toISOString(),
      responses_count: 0,
      questions: (body.questions || []).map((q: any, idx: number) => ({
        id: q.id || `q_${Date.now()}_${idx}`,
        form_id: `form_${Date.now()}`,
        question_text: q.question_text || "Untitled Question",
        help_text: q.help_text || "",
        question_type: q.question_type || "SHORT_TEXT",
        required: q.required !== false,
        options: q.options || [],
        order: idx + 1
      }))
    };
    forms.unshift(newForm);
    res.status(201).json(newForm);
  });

  app.put("/api/forms/:id/", (req, res) => {
    const index = forms.findIndex((f) => f.id === req.params.id);
    if (index === -1) return res.status(404).json({ detail: "Form not found" });
    forms[index] = { ...forms[index], ...req.body };
    res.json(forms[index]);
  });

  app.post("/api/forms/:id/publish/", (req, res) => {
    const f = forms.find((form) => form.id === req.params.id);
    if (!f) return res.status(404).json({ detail: "Form not found" });
    f.status = "PUBLISHED";
    // Notify enrolled participants
    notifications.push({
      id: `notif_${Date.now()}`,
      recipient_id: "usr_beneficiary",
      title: `New Survey Published: ${f.title}`,
      message: `A new ${f.form_type.toLowerCase()} questionnaire has been published for your programme. Please respond by the deadline.`,
      type: "FORM_ASSIGNED",
      is_read: false,
      created_at: new Date().toISOString()
    });
    res.json(f);
  });

  app.post("/api/forms/:id/submit/", (req, res) => {
    const f = forms.find((form) => form.id === req.params.id);
    if (!f) return res.status(404).json({ detail: "Form not found" });
    const { beneficiary_id, answers, beneficiary_name } = req.body;

    const newResponse = {
      id: `resp_${Date.now()}`,
      form_id: req.params.id,
      beneficiary_id: beneficiary_id || "usr_beneficiary",
      beneficiary_name: beneficiary_name || "Fatima Zara",
      submitted_at: new Date().toISOString(),
      status: "SUBMITTED" as const,
      submitted_via: "WEB",
      answers: answers || {}
    };
    formResponses.push(newResponse);
    f.responses_count = (f.responses_count || 0) + 1;

    // Check if monitoring form triggers challenge detection
    if (f.form_type === "MONITORING" && answers) {
      for (const [qId, val] of Object.entries(answers)) {
        if (typeof val === "string" && (val.toLowerCase().includes("fare") || val.toLowerCase().includes("transport"))) {
          challenges.unshift({
            id: `ch_${Date.now()}`,
            programme_id: f.programme_id,
            programme_title: "Girls in Tech & AI Leadership Cohort 2026",
            beneficiary_id: newResponse.beneficiary_id,
            beneficiary_name: newResponse.beneficiary_name,
            category: "TRANSPORT",
            description: `Automated issue detected from monitoring response: ${val}`,
            severity: "HIGH",
            status: "OPEN",
            reported_at: new Date().toISOString(),
            audit_history: [
              {
                timestamp: new Date().toISOString(),
                actor: "SYSTEM",
                action: "AUTO_DETECTED",
                note: "Detected recurring transport issue from monitoring survey"
              }
            ]
          });
          break;
        }
      }
    }

    res.status(201).json(newResponse);
  });

  app.get("/api/forms/:id/responses/", (req, res) => {
    const resps = formResponses.filter((r) => r.form_id === req.params.id);
    res.json(resps);
  });

  // Challenges Endpoints
  app.get("/api/programmes/:id/challenges/", (req, res) => {
    const chs = challenges.filter((c) => c.programme_id === req.params.id);
    res.json(chs);
  });

  app.post("/api/programmes/:id/challenges/", (req, res) => {
    const { category, description, severity, beneficiary_id, beneficiary_name } = req.body;
    const newChallenge = {
      id: `ch_${Date.now()}`,
      programme_id: req.params.id,
      programme_title: "Girls in Tech & AI Leadership Cohort 2026",
      beneficiary_id: beneficiary_id || "usr_beneficiary",
      beneficiary_name: beneficiary_name || "Fatima Zara",
      category: category || "OTHER",
      description: description || "Reported participant barrier.",
      severity: severity || "MEDIUM",
      status: "OPEN" as const,
      reported_at: new Date().toISOString(),
      audit_history: [
        {
          timestamp: new Date().toISOString(),
          actor: beneficiary_name || "Beneficiary",
          action: "REPORTED",
          note: "Reported directly via platform"
        }
      ]
    };
    challenges.unshift(newChallenge);
    res.status(201).json(newChallenge);
  });

  app.patch("/api/challenges/:id/", (req, res) => {
    const ch = challenges.find((c) => c.id === req.params.id);
    if (!ch) return res.status(404).json({ detail: "Challenge not found" });
    if (req.body.severity) ch.severity = req.body.severity;
    if (req.body.category) ch.category = req.body.category;
    if (req.body.description) ch.description = req.body.description;
    res.json(ch);
  });

  app.post("/api/challenges/:id/assign/", (req, res) => {
    const ch = challenges.find((c) => c.id === req.params.id);
    if (!ch) return res.status(404).json({ detail: "Challenge not found" });
    const { assigned_to, assigned_to_name, notes } = req.body;
    ch.assigned_to = assigned_to || "usr_field_officer";
    ch.assigned_to_name = assigned_to_name || "Sarah Kibuuka (Field Officer)";
    ch.status = "IN_PROGRESS";
    if (!ch.audit_history) ch.audit_history = [];
    ch.audit_history.push({
      timestamp: new Date().toISOString(),
      actor: "Organisation Admin",
      action: "ASSIGNED",
      note: notes || `Assigned to ${ch.assigned_to_name} for localized follow-up.`
    });
    res.json(ch);
  });

  app.post("/api/challenges/:id/resolve/", (req, res) => {
    const ch = challenges.find((c) => c.id === req.params.id);
    if (!ch) return res.status(404).json({ detail: "Challenge not found" });
    const { resolution_notes } = req.body;
    ch.status = "RESOLVED";
    ch.resolved_at = new Date().toISOString();
    ch.resolution_notes = resolution_notes || "Resolved following field assessment and resource allocation.";
    if (!ch.audit_history) ch.audit_history = [];
    ch.audit_history.push({
      timestamp: new Date().toISOString(),
      actor: "Response Team",
      action: "RESOLVED",
      note: ch.resolution_notes
    });
    res.json(ch);
  });

  // Analytics Endpoints
  app.get("/api/programmes/:id/analytics/", (req, res) => {
    const prog = programmes.find((p) => p.id === req.params.id) || programmes[0];
    const progChallenges = challenges.filter((c) => c.programme_id === req.params.id);
    const progKpis = kpis.filter((k) => k.programme_id === req.params.id);
    const progForms = forms.filter((f) => f.programme_id === req.params.id);

    const totalFormsSent = progForms.reduce((sum, f) => sum + (prog.current_beneficiaries || 128), 0);
    const totalResponses = progForms.reduce((sum, f) => sum + (f.responses_count || 0), 0);
    const responseRate = totalFormsSent > 0 ? Math.round((totalResponses / totalFormsSent) * 100) : 84;

    res.json({
      programme: prog,
      funnel: [
        { stage: "Registered", count: 185 },
        { stage: "Selected", count: 140 },
        { stage: "Enrolled & Active", count: prog.current_beneficiaries || 128 },
        { stage: "Completed Modules", count: 114 },
        { stage: "Followed Up (6m)", count: 88 }
      ],
      kpis: progKpis,
      open_challenges_count: progChallenges.filter((c) => c.status !== "RESOLVED").length,
      resolved_challenges_count: progChallenges.filter((c) => c.status === "RESOLVED").length,
      forms_sent: totalFormsSent,
      responses_received: totalResponses,
      response_rate: responseRate
    });
  });

  app.get("/api/programmes/:id/challenge-analytics/", (req, res) => {
    const progChallenges = challenges.filter((c) => c.programme_id === req.params.id);
    
    // Aggregated issue clusters (as specified in prompt: 35 transport, 20 materials/attendance)
    const issueClusters = [
      {
        issue: "Transport and commuter minibus fare escalation",
        participants_affected: 35,
        category: "TRANSPORT",
        status: "High Alert",
        recommended_action: "Disburse weekly transport stipend top-up (UGX 25,000) or deploy shared shuttle vans."
      },
      {
        issue: "Intermittent power outages & damaged device adapters",
        participants_affected: 18,
        category: "MATERIALS",
        status: "In Remediation",
        recommended_action: "Provide surge-protected solar power banks and replacement laptop chargers."
      },
      {
        issue: "Family care and dependent nursing during daytime hours",
        participants_affected: 12,
        category: "FAMILY_CARE",
        status: "Active Review",
        recommended_action: "Offer asynchronous lecture recordings and flexible evening lab hours."
      }
    ];

    const categoryBreakdown = [
      { name: "Transport", count: 35, fill: "#e11d48" },
      { name: "Materials / Power", count: 18, fill: "#f59e0b" },
      { name: "Family & Care", count: 12, fill: "#8b5cf6" },
      { name: "Health & Wellbeing", count: 8, fill: "#06b6d4" },
      { name: "Safety / Travel", count: 4, fill: "#10b981" }
    ];

    res.json({
      clusters: issueClusters,
      breakdown: categoryBreakdown,
      total_reported: 77,
      resolution_rate: 68
    });
  });

  app.get("/api/programmes/:id/outcomes/", (req, res) => {
    // Before vs After vs Follow-up outcome measurement data
    const outcomeData = [
      {
        metric: "Employed in Tech / Formal Enterprise",
        baseline: 8,       // 8%
        endline: 68,       // 68%
        follow_up_6m: 78,  // 78%
        unit: "% of participants",
        gain: "+70%",
        label: "Measured outcome"
      },
      {
        metric: "Digital & Coding Competency (Score / 100)",
        baseline: 24,
        endline: 82,
        follow_up_6m: 86,
        unit: "Score",
        gain: "+62 pts",
        label: "Measured change"
      },
      {
        metric: "Average Monthly Personal Income",
        baseline: 25,      // $25 USD
        endline: 185,     // $185 USD
        follow_up_6m: 290, // $290 USD
        unit: "USD / month",
        gain: "+$265/mo",
        label: "Follow-up outcome"
      },
      {
        metric: "Leadership & Self-Confidence Rating",
        baseline: 32,
        endline: 88,
        follow_up_6m: 92,
        unit: "% high confidence",
        gain: "+60%",
        label: "Reported outcome"
      },
      {
        metric: "Registered Micro-Business / Freelance Agency",
        baseline: 4,
        endline: 26,
        follow_up_6m: 38,
        unit: "% established",
        gain: "+34%",
        label: "Measured change"
      }
    ];

    res.json({
      records: outcomeData,
      methodology_notice: "Outcomes tracked longitudinally via Baseline, Endline, and 6-Month post-graduation surveys. Changes are reported outcomes and measured trends."
    });
  });

  // Verification Tasks (Field Officer)
  app.get("/api/verification/tasks/", (req, res) => {
    res.json(verificationTasks);
  });

  app.patch("/api/verification/tasks/:id/", (req, res) => {
    const task = verificationTasks.find((t) => t.id === req.params.id);
    if (!task) return res.status(404).json({ detail: "Task not found" });
    if (req.body.status) task.status = req.body.status;
    if (req.body.home_visit_conducted !== undefined) task.home_visit_conducted = req.body.home_visit_conducted;
    if (req.body.id_documents_checked !== undefined) task.id_documents_checked = req.body.id_documents_checked;
    if (req.body.guardian_contacted !== undefined) task.guardian_contacted = req.body.guardian_contacted;
    if (req.body.field_notes) task.field_notes = req.body.field_notes;
    res.json(task);
  });

  // Opportunities & Applications
  app.get("/api/opportunities/", (req, res) => {
    res.json(opportunities);
  });

  app.get("/api/applications/", (req, res) => {
    res.json(applications);
  });

  app.post("/api/applications/", (req, res) => {
    const { opportunity_id, statement_of_purpose, beneficiary_id } = req.body;
    const opp = opportunities.find((o) => o.id === opportunity_id);
    const newApp = {
      id: `app_${Date.now()}`,
      beneficiary_id: beneficiary_id || "usr_beneficiary",
      opportunity_id,
      status: "SUBMITTED" as const,
      application_date: new Date().toISOString(),
      statement_of_purpose: statement_of_purpose || "",
      notes: "Awaiting review",
      opportunity_title: opp ? opp.title : "Opportunity",
      organisation_name: opp ? opp.organisation_name : "Partner Organisation"
    };
    applications.unshift(newApp);
    res.status(201).json(newApp);
  });

  // Notifications
  app.get("/api/notifications/", (req, res) => {
    res.json(notifications);
  });

  // Organisations
  app.get("/api/organisations/", (req, res) => {
    res.json(organisations);
  });

  app.patch("/api/organisations/:id/verify/", (req, res) => {
    const org = organisations.find((o) => o.id === req.params.id);
    if (!org) return res.status(404).json({ detail: "Organisation not found" });
    org.verification_status = req.body.verification_status || "VERIFIED";
    res.json(org);
  });

  // Match calculator helper endpoint
  app.post("/api/match/calculate/", (req, res) => {
    const { beneficiary_profile, requirements } = req.body;
    const result = runMatchingEngine(beneficiary_profile || {}, requirements || {});
    res.json(result);
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Voice of a Girl SaaS server running on port ${PORT}`);
  });
}

startServer();
