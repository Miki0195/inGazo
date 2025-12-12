import api from './api';
import { Driver, BecomeDriverData } from '@/types';

const DRIVER_ENDPOINTS = {
  // Dedicated "become" endpoint includes server-side guard against duplicates
  become: '/drivers/become/',
  me: '/drivers/me/',
  // Profile endpoint used for updates/toggling active state
  update: '/drivers/profile/',
};

export const driverService = {
  /**
   * Become a driver - creates driver profile for current user
   */
  async becomeDriver(data: BecomeDriverData): Promise<Driver> {
    const response = await api.post<Driver>(DRIVER_ENDPOINTS.become, data);
    return response.data;
  },

  /**
   * Get current user's driver profile
   */
  async getMyDriverProfile(): Promise<Driver> {
    const response = await api.get<Driver>(DRIVER_ENDPOINTS.me);
    return response.data;
  },

  /**
   * Update driver profile
   */
  async updateDriverProfile(
    data: Partial<BecomeDriverData> & { is_active?: boolean }
  ): Promise<Driver> {
    const response = await api.patch<Driver>(DRIVER_ENDPOINTS.update, data);
    return response.data;
  },
};

export default driverService;

