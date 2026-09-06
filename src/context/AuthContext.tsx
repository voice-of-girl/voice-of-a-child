import React, { createContext, useContext, useState } from 'react';
import { User, UserRole, Organisation } from '../types';

interface AuthContextType {
  user: User | null;
  organisation: Organisation | null;
  role: UserRole;
  switchRole: (newRole: UserRole) => void;
  login: (email: string) => boolean;
  logout: () => void;
  notificationsCount: number;
}

const DEFAULT_USERS: Record<UserRole, User> = {
  ORGANISATION_ADMIN: {
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
  BENEFICIARY: {
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
  FIELD_OFFICER: {
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
  PLATFORM_ADMIN: {
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
};

const DEFAULT_ORG: Organisation = {
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
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRole] = useState<UserRole>('ORGANISATION_ADMIN');
  const [user, setUser] = useState<User | null>(DEFAULT_USERS.ORGANISATION_ADMIN);
  const [organisation, setOrganisation] = useState<Organisation | null>(DEFAULT_ORG);
  const [notificationsCount, setNotificationsCount] = useState<number>(3);

  const switchRole = (newRole: UserRole) => {
    setRole(newRole);
    setUser(DEFAULT_USERS[newRole]);
    if (newRole === 'ORGANISATION_ADMIN' || newRole === 'FIELD_OFFICER') {
      setOrganisation(DEFAULT_ORG);
    } else {
      setOrganisation(null);
    }
  };

  const login = (email: string) => {
    const found = Object.values(DEFAULT_USERS).find(u => u.email.toLowerCase() === email.toLowerCase());
    if (found) {
      switchRole(found.role);
      return true;
    } else {
      return false;
    }
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        organisation,
        role,
        switchRole,
        login,
        logout,
        notificationsCount
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
