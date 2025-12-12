import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, LoginCredentials, RegisterData, LoginResponse } from '@/types';
import { authService } from '@/services/auth';
import {
  getTokens,
  setTokens,
  getStoredUser,
  setStoredUser,
  clearAuthData,
} from '@/utils/storage';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from storage
  useEffect(() => {
    const initAuth = async () => {
      const tokens = getTokens();
      const storedUser = getStoredUser();

      if (tokens?.access && storedUser) {
        setUser(storedUser);
        
        // Optionally verify token by fetching profile
        try {
          const profile = await authService.getProfile();
          setUser(profile);
          setStoredUser(profile);
        } catch {
          // Token might be invalid, clear auth
          clearAuthData();
          setUser(null);
        }
      }

      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const response: LoginResponse = await authService.login(credentials);
    
    // Store tokens and user
    setTokens({
      access: response.access,
      refresh: response.refresh,
    });
    setStoredUser(response.user);
    setUser(response.user);
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    await authService.register(data);
    // After registration, user needs to login
  }, []);

  const logout = useCallback(() => {
    clearAuthData();
    setUser(null);
  }, []);

  const updateUser = useCallback((updatedUser: User) => {
    setUser(updatedUser);
    setStoredUser(updatedUser);
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
