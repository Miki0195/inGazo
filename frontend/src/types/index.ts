// User types
export interface User {
  id: string;
  email: string | null;
  phone_number: string | null;
  full_name: string;
  profile_photo_url: string | null;
  is_verified: boolean;
  created_at?: string;
  last_login?: string;
  driver_profile?: Driver | null;
}

// Driver types
export interface Driver {
  id: string;
  license_number: string;
  license_expiry: string | null;
  license_photo_url: string | null;
  rating: number;
  total_trips: number;
  total_reviews: number;
  is_verified: boolean;
  is_active: boolean;
  bio: string;
  accepts_smoking: boolean;
  accepts_pets: boolean;
  accepts_luggage: boolean;
  created_at: string;
}

export interface BecomeDriverData {
  license_number: string;
  license_expiry?: string;
  bio?: string;
  accepts_smoking?: boolean;
  accepts_pets?: boolean;
  accepts_luggage?: boolean;
}

export interface UpdateProfileData {
  full_name?: string;
  phone_number?: string;
  profile_photo_url?: string;
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email?: string;
  phone_number?: string;
  full_name: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse extends AuthTokens {
  user: User;
}

export interface RegisterResponse {
  message: string;
  user: User;
}

// API Response types
export interface ApiError {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}

// Language types
export type Language = 'en' | 'hu' | 'de';

export interface LanguageOption {
  code: Language;
  name: string;
  flag: string;
}
