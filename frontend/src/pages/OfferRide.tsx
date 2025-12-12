import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Calendar, Clock, MapPin, Car, Euro, Info, Check, Loader2, TrendingUp, Locate } from 'lucide-react';
import { Button, Card, Input } from '@/components/common';
import { useAuth } from '@/hooks/useAuth';
import { rideService, vehicleService } from '@/services';
import { CreateRidePayload, Vehicle } from '@/types';

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4 },
};

type FormState = {
  vehicle_id: string;
  departure_time: string;
  seats_total: string;
  start_city: string;
  start_address: string;
  start_lat: string;
  start_lng: string;
  end_city: string;
  end_address: string;
  end_lat: string;
  end_lng: string;
  price_per_seat: string;
  estimated_duration_minutes: string;
  estimated_distance_km: string;
  notes: string;
  allows_detours: boolean;
  instant_booking: boolean;
};

const initialForm: FormState = {
  vehicle_id: '',
  departure_time: '',
  seats_total: '1',
  start_city: '',
  start_address: '',
  start_lat: '',
  start_lng: '',
  end_city: '',
  end_address: '',
  end_lat: '',
  end_lng: '',
  price_per_seat: '',
  estimated_duration_minutes: '',
  estimated_distance_km: '',
  notes: '',
  allows_detours: false,
  instant_booking: false,
};

export const OfferRide: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(initialForm);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isVehiclesLoading, setIsVehiclesLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [geoError, setGeoError] = useState('');
  const [geoLoading, setGeoLoading] = useState<{ start?: boolean; end?: boolean }>({});

  const isDriver = !!user?.driver_profile;
  const isVerified = user?.driver_profile?.is_verified;

  useEffect(() => {
    const fetchVehicles = async () => {
      setIsVehiclesLoading(true);
      try {
        const data = await vehicleService.getMyVehicles();
        setVehicles(data);
        if (data.length > 0) {
          setForm((prev) => ({ ...prev, vehicle_id: prev.vehicle_id || data[0].id }));
        }
      } catch {
        setError(
          t('offerRide.vehiclesError', {
            defaultValue: 'Unable to load your vehicles. Please try again.',
          })
        );
      } finally {
        setIsVehiclesLoading(false);
      }
    };

    if (isDriver) {
      fetchVehicles();
    } else {
      setIsVehiclesLoading(false);
    }
  }, [isDriver, t]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type, checked } = e.target as HTMLInputElement;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const geocodeCity = async (city: string, key: 'start' | 'end') => {
    if (!city) return;
    setGeoError('');
    setGeoLoading((prev) => ({ ...prev, [key]: true }));
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(city)}`,
        {
          headers: {
            'Accept-Language': 'en',
          },
        }
      );
      const results = await response.json();
      if (Array.isArray(results) && results.length > 0) {
        const { lat, lon } = results[0];
        setForm((prev) => ({
          ...prev,
          ...(key === 'start'
            ? { start_lat: lat?.toString() || '', start_lng: lon?.toString() || '' }
            : { end_lat: lat?.toString() || '', end_lng: lon?.toString() || '' }),
        }));
      } else {
        setGeoError(
          t('offerRide.geoNotFound', {
            defaultValue: 'No coordinates found for that city.',
          })
        );
      }
    } catch (err) {
      setGeoError(
        t('offerRide.geoError', {
          defaultValue: 'Failed to fetch coordinates. Please try again.',
        })
      );
    } finally {
      setGeoLoading((prev) => ({ ...prev, [key]: false }));
    }
  };

  const parsedPayload: CreateRidePayload | null = useMemo(() => {
    try {
      if (
        !form.vehicle_id ||
        !form.departure_time ||
        !form.start_city ||
        !form.end_city ||
        !form.start_lat ||
        !form.start_lng ||
        !form.end_lat ||
        !form.end_lng ||
        !form.price_per_seat ||
        !form.seats_total
      ) {
        return null;
      }

      const departureIso = new Date(form.departure_time).toISOString();

      return {
        vehicle_id: form.vehicle_id,
        departure_time: departureIso,
        seats_total: parseInt(form.seats_total, 10),
        start_location: {
          latitude: parseFloat(form.start_lat),
          longitude: parseFloat(form.start_lng),
        },
        end_location: {
          latitude: parseFloat(form.end_lat),
          longitude: parseFloat(form.end_lng),
        },
        start_city: form.start_city,
        start_address: form.start_address,
        end_city: form.end_city,
        end_address: form.end_address,
        price_per_seat: parseFloat(form.price_per_seat),
        estimated_duration_minutes: form.estimated_duration_minutes
          ? parseInt(form.estimated_duration_minutes, 10)
          : undefined,
        estimated_distance_km: form.estimated_distance_km
          ? parseFloat(form.estimated_distance_km)
          : undefined,
        notes: form.notes || undefined,
        allows_detours: form.allows_detours,
        instant_booking: form.instant_booking,
      };
    } catch {
      return null;
    }
  }, [form]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!parsedPayload) {
      setError(
        t('offerRide.validation', {
          defaultValue: 'Please fill in all required fields with valid values.',
        })
      );
      return;
    }

    setIsLoading(true);
    try {
      await rideService.createRide(parsedPayload);
      setSuccess(
        t('offerRide.success', { defaultValue: 'Ride created successfully!' })
      );
      setForm(initialForm);
      navigate('/dashboard');
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setError(detail || t('offerRide.error', { defaultValue: 'Failed to create ride.' }));
    } finally {
      setIsLoading(false);
    }
  };

  if (!isDriver) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center px-4">
        <Card className="max-w-lg w-full text-center">
          <h2 className="text-2xl font-semibold text-secondary-900 mb-2">
            {t('offerRide.notDriverTitle', { defaultValue: 'Become a driver to offer rides' })}
          </h2>
          <p className="text-secondary-600 mb-4">
            {t('offerRide.notDriverDesc', {
              defaultValue: 'You need a driver profile to create rides.',
            })}
          </p>
          <Link to="/become-driver">
            <Button variant="primary">
              {t('offerRide.becomeDriverCta', { defaultValue: 'Become a driver' })}
            </Button>
          </Link>
        </Card>
      </div>
    );
  }

  if (!isVerified) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center px-4">
        <Card className="max-w-lg w-full text-center">
          <h2 className="text-2xl font-semibold text-secondary-900 mb-2">
            {t('offerRide.verifyTitle', { defaultValue: 'Verification required' })}
          </h2>
          <p className="text-secondary-600 mb-4">
            {t('offerRide.verifyDesc', {
              defaultValue: 'Your driver profile must be verified before offering rides.',
            })}
          </p>
          <Link to="/profile">
            <Button variant="primary">
              {t('offerRide.verifyCta', { defaultValue: 'Go to profile' })}
            </Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">
            {t('offerRide.title', { defaultValue: 'Offer a ride' })}
          </h1>
          <p className="text-secondary-600">
            {t('offerRide.subtitle', {
              defaultValue: 'Share your route, set your price, and start driving.',
            })}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <motion.div variants={fadeInUp} initial="initial" animate="animate" className="lg:col-span-2">
            <Card>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-secondary-700 flex items-center gap-2">
                      <Car className="h-4 w-4 text-primary-500" />
                      {t('offerRide.vehicle', { defaultValue: 'Vehicle' })}
                    </label>
                    {isVehiclesLoading ? (
                      <div className="flex items-center gap-2 text-secondary-500 text-sm">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {t('offerRide.loadingVehicles', { defaultValue: 'Loading vehicles...' })}
                      </div>
                    ) : vehicles.length ? (
                      <select
                        name="vehicle_id"
                        value={form.vehicle_id}
                        onChange={handleChange}
                        className="w-full rounded-xl border border-secondary-300 px-3 py-2.5 text-secondary-900 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                        required
                      >
                        {vehicles.map((v) => (
                          <option key={v.id} value={v.id}>
                            {v.make} {v.model} • {v.license_plate} • {v.seats} seats
                          </option>
                        ))}
                      </select>
                    ) : (
                      <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                        {t('offerRide.noVehicles', {
                          defaultValue: 'No active vehicles found. Add one to continue.',
                        })}
                      </div>
                    )}
                  </div>

                  <Input
                    label={t('offerRide.departure', { defaultValue: 'Departure time' })}
                    name="departure_time"
                    type="datetime-local"
                    value={form.departure_time}
                    onChange={handleChange}
                    leftIcon={<Calendar className="h-5 w-5" />}
                    required
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Input
                      label={t('offerRide.startCity', { defaultValue: 'Start city' })}
                      name="start_city"
                      value={form.start_city}
                      onChange={handleChange}
                      leftIcon={<MapPin className="h-5 w-5" />}
                      required
                    />
                    <div className="flex justify-between items-center">
                      <button
                        type="button"
                        onClick={() => geocodeCity(form.start_city, 'start')}
                        className="text-sm text-primary-600 hover:text-primary-700 inline-flex items-center gap-1"
                        disabled={geoLoading.start}
                      >
                        {geoLoading.start && <Loader2 className="h-4 w-4 animate-spin" />}
                        {!geoLoading.start && <Locate className="h-4 w-4" />}
                        {t('offerRide.autoFillCoords', { defaultValue: 'Auto-fill coordinates' })}
                      </button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Input
                      label={t('offerRide.endCity', { defaultValue: 'Destination city' })}
                      name="end_city"
                      value={form.end_city}
                      onChange={handleChange}
                      leftIcon={<MapPin className="h-5 w-5" />}
                      required
                    />
                    <div className="flex justify-between items-center">
                      <button
                        type="button"
                        onClick={() => geocodeCity(form.end_city, 'end')}
                        className="text-sm text-primary-600 hover:text-primary-700 inline-flex items-center gap-1"
                        disabled={geoLoading.end}
                      >
                        {geoLoading.end && <Loader2 className="h-4 w-4 animate-spin" />}
                        {!geoLoading.end && <Locate className="h-4 w-4" />}
                        {t('offerRide.autoFillCoords', { defaultValue: 'Auto-fill coordinates' })}
                      </button>
                    </div>
                  </div>
                  <Input
                    label={t('offerRide.startAddress', { defaultValue: 'Start address (optional)' })}
                    name="start_address"
                    value={form.start_address}
                    onChange={handleChange}
                  />
                  <Input
                    label={t('offerRide.endAddress', { defaultValue: 'Destination address (optional)' })}
                    name="end_address"
                    value={form.end_address}
                    onChange={handleChange}
                  />
                  <Input
                    label={t('offerRide.startLat', { defaultValue: 'Start latitude' })}
                    name="start_lat"
                    type="number"
                    step="any"
                    value={form.start_lat}
                    onChange={handleChange}
                    required
                  />
                  <Input
                    label={t('offerRide.startLng', { defaultValue: 'Start longitude' })}
                    name="start_lng"
                    type="number"
                    step="any"
                    value={form.start_lng}
                    onChange={handleChange}
                    required
                  />
                  <Input
                    label={t('offerRide.endLat', { defaultValue: 'Destination latitude' })}
                    name="end_lat"
                    type="number"
                    step="any"
                    value={form.end_lat}
                    onChange={handleChange}
                    required
                  />
                  <Input
                    label={t('offerRide.endLng', { defaultValue: 'Destination longitude' })}
                    name="end_lng"
                    type="number"
                    step="any"
                    value={form.end_lng}
                    onChange={handleChange}
                    required
                  />
                </div>

                {geoError && (
                  <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                    {geoError}
                  </div>
                )}

                <div className="grid gap-4 md:grid-cols-3">
                  <Input
                    label={t('offerRide.seats', { defaultValue: 'Seats available' })}
                    name="seats_total"
                    type="number"
                    min={1}
                    max={9}
                    value={form.seats_total}
                    onChange={handleChange}
                    leftIcon={<Car className="h-5 w-5" />}
                    required
                  />
                  <Input
                    label={t('offerRide.price', { defaultValue: 'Price per seat (€)' })}
                    name="price_per_seat"
                    type="number"
                    min={0}
                    step="0.01"
                    value={form.price_per_seat}
                    onChange={handleChange}
                    leftIcon={<Euro className="h-5 w-5" />}
                    required
                  />
                  <Input
                    label={t('offerRide.duration', { defaultValue: 'Est. duration (min)' })}
                    name="estimated_duration_minutes"
                    type="number"
                    min={0}
                    value={form.estimated_duration_minutes}
                    onChange={handleChange}
                    leftIcon={<Clock className="h-5 w-5" />}
                  />
                  <Input
                    label={t('offerRide.distance', { defaultValue: 'Est. distance (km)' })}
                    name="estimated_distance_km"
                    type="number"
                    min={0}
                    step="0.1"
                    value={form.estimated_distance_km}
                    onChange={handleChange}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    {t('offerRide.notes', { defaultValue: 'Notes (optional)' })}
                  </label>
                  <textarea
                    name="notes"
                    value={form.notes}
                    onChange={handleChange}
                    rows={3}
                    className="w-full rounded-xl border border-secondary-300 px-4 py-3 text-secondary-900 placeholder-secondary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-colors"
                    placeholder={t('offerRide.notesPlaceholder', {
                      defaultValue: 'Luggage size, meeting point, etc.',
                    })}
                  />
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <label className="flex items-center gap-3 rounded-xl border border-secondary-200 bg-white px-4 py-3 cursor-pointer hover:border-primary-200 transition">
                    <input
                      type="checkbox"
                      name="allows_detours"
                      checked={form.allows_detours}
                      onChange={handleChange}
                      className="h-4 w-4 text-primary-600 rounded border-secondary-300 focus:ring-primary-500"
                    />
                    <div>
                      <p className="font-medium text-secondary-900">
                        {t('offerRide.detours', { defaultValue: 'Allow small detours' })}
                      </p>
                      <p className="text-sm text-secondary-600">
                        {t('offerRide.detoursDesc', {
                          defaultValue: 'More flexible pickups along the way.',
                        })}
                      </p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 rounded-xl border border-secondary-200 bg-white px-4 py-3 cursor-pointer hover:border-primary-200 transition">
                    <input
                      type="checkbox"
                      name="instant_booking"
                      checked={form.instant_booking}
                      onChange={handleChange}
                      className="h-4 w-4 text-primary-600 rounded border-secondary-300 focus:ring-primary-500"
                    />
                    <div>
                      <p className="font-medium text-secondary-900">
                        {t('offerRide.instant', { defaultValue: 'Instant booking' })}
                      </p>
                      <p className="text-sm text-secondary-600">
                        {t('offerRide.instantDesc', {
                          defaultValue: 'Passengers can book without approval.',
                        })}
                      </p>
                    </div>
                  </label>
                </div>

                {error && (
                  <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                  </div>
                )}
                {success && (
                  <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
                    {success}
                  </div>
                )}

                <div className="flex items-center justify-end gap-3">
                  <Button variant="ghost" type="button" onClick={() => setForm(initialForm)}>
                    {t('common.cancel', { defaultValue: 'Cancel' })}
                  </Button>
                  <Button type="submit" isLoading={isLoading} disabled={isVehiclesLoading || !vehicles.length}>
                    {t('offerRide.submit', { defaultValue: 'Create ride' })}
                  </Button>
                </div>
              </form>
            </Card>
          </motion.div>

          <motion.div variants={fadeInUp} initial="initial" animate="animate" className="space-y-4">
            <Card className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-primary-100 flex items-center justify-center">
                  <Info className="h-5 w-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-semibold text-secondary-900">
                    {t('offerRide.tipsTitle', { defaultValue: 'Tips for great rides' })}
                  </p>
                  <p className="text-sm text-secondary-600">
                    {t('offerRide.tipsSubtitle', { defaultValue: 'Help passengers trust your offer.' })}
                  </p>
                </div>
              </div>
              <ul className="space-y-2 text-sm text-secondary-700">
                {[
                  t('offerRide.tip1', { defaultValue: 'Use precise pickup and drop-off locations.' }),
                  t('offerRide.tip2', { defaultValue: 'Set fair pricing per seat.' }),
                  t('offerRide.tip3', { defaultValue: 'Add notes about luggage or meeting points.' }),
                  t('offerRide.tip4', { defaultValue: 'Enable instant booking for quick matches.' }),
                ].map((tip, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary-600 mt-0.5" />
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </Card>

            <Card className="bg-gradient-to-br from-primary-500 to-primary-600 text-white">
              <div className="flex items-start gap-3">
                <div className="h-10 w-10 rounded-xl bg-white/20 flex items-center justify-center">
                  <TrendingUp className="h-5 w-5" />
                </div>
                <div className="space-y-2">
                  <p className="font-semibold">
                    {t('offerRide.highlight', { defaultValue: 'Verified drivers attract more bookings.' })}
                  </p>
                  <p className="text-primary-100 text-sm">
                    {t('offerRide.highlightDesc', {
                      defaultValue: 'Keep your profile and vehicle info up to date.',
                    })}
                  </p>
                  <Link to="/profile" className="block mt-3">
                    <Button variant="outline" size="sm" className="bg-white text-primary-600 border-white hover:bg-primary-50">
                      {t('offerRide.manageProfile', { defaultValue: 'Manage profile' })}
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default OfferRide;
