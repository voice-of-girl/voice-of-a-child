import { http } from './http';
import type { User } from '../types';

export interface LoginResult {
  access: string;
  refresh?: string;
  user: User;
}

export const authService = {
  async login(email: string, password: string): Promise<LoginResult> {
    const { data } = await http.post<LoginResult>('/auth/login/', { email, password });
    return data;
  },
  async me(): Promise<{ user: User }> {
    const { data } = await http.get('/auth/me/');
    return data;
  }
};
