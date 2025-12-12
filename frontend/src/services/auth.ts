import api from './api';
import {
  LoginCredentials,
  LoginResponse,
  RegisterData,
  RegisterResponse,
  User,
} from '@/types';

const AUTH_ENDPOINTS = {
  login: '/users/auth/login/',
  register: '/users/auth/register/',
  profile: '/users/profile/',
  refreshToken: '/auth/token/refresh/',
};

export const authService = {
  /**
   * Login user with email and password
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(AUTH_ENDPOINTS.login, credentials);
    return response.data;
  },

  /**
   * Register a new user
   */
  async register(data: RegisterData): Promise<RegisterResponse> {
    const response = await api.post<RegisterResponse>(AUTH_ENDPOINTS.register, data);
    return response.data;
  },

  /**
   * Get current user profile
   */
  async getProfile(): Promise<User> {
    const response = await api.get<User>(AUTH_ENDPOINTS.profile);
    return response.data;
  },

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.patch<User>(AUTH_ENDPOINTS.profile, data);
    return response.data;
  },

  /**
   * Check if email is already registered
   */
  async checkEmail(email: string): Promise<boolean> {
    const response = await api.get<{ exists: boolean }>(`/users/check/email/${email}/`);
    return response.data.exists;
  },

  /**
   * Check if phone number is already registered
   */
  async checkPhone(phoneNumber: string): Promise<boolean> {
    const response = await api.get<{ exists: boolean }>(`/users/check/phone/${phoneNumber}/`);
    return response.data.exists;
  },
};

export default authService;
