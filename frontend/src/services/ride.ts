import api from './api';
import { Ride, CreateRidePayload } from '@/types';

const RIDE_ENDPOINT = '/rides/';

export const rideService = {
  async createRide(data: CreateRidePayload): Promise<Ride> {
    const response = await api.post<Ride>(RIDE_ENDPOINT, data);
    return response.data;
  },
};

export default rideService;
