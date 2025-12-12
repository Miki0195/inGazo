import api from './api';
import { Vehicle, CreateVehiclePayload } from '@/types';

const VEHICLE_ENDPOINT = '/vehicles/';

export const vehicleService = {
  async getMyVehicles(): Promise<Vehicle[]> {
    const response = await api.get(`${VEHICLE_ENDPOINT}?mine=true`);
    const data = response.data;
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.results)) return data.results;
    return [];
  },

  async createVehicle(data: CreateVehiclePayload): Promise<Vehicle> {
    const response = await api.post<Vehicle>(VEHICLE_ENDPOINT, data);
    return response.data;
  },

  async deleteVehicle(id: string): Promise<void> {
    await api.delete(`${VEHICLE_ENDPOINT}${id}/`);
  },
};

export default vehicleService;
