import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  User,
  Mail,
  Phone,
  Camera,
  Shield,
  Car,
  Star,
  MapPin,
  Calendar,
  CheckCircle2,
  ChevronRight,
  Cigarette,
  Dog,
  Briefcase,
  Edit3,
  Save,
  X,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Button, Card, Drawer, Input } from '@/components/common';
import { authService } from '@/services/auth';
import { driverService } from '@/services/driver';
import { UpdateProfileData } from '@/types';

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const Profile: React.FC = () => {
  const { t } = useTranslation();
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isDriverActionLoading, setIsDriverActionLoading] = useState(false);
  const [isDriverDrawerOpen, setIsDriverDrawerOpen] = useState(false);
  const [driverFormLoading, setDriverFormLoading] = useState(false);
  const [driverError, setDriverError] = useState('');
  const [formData, setFormData] = useState<UpdateProfileData>({
    full_name: user?.full_name || '',
    phone_number: user?.phone_number || '',
  });

  const isDriver = !!user?.driver_profile;
  const driverProfile = user?.driver_profile;

  type DriverFormState = {
    license_number: string;
    license_expiry: string;
    bio: string;
    accepts_smoking: boolean;
    accepts_pets: boolean;
    accepts_luggage: boolean;
    is_active: boolean;
  };

  const [driverForm, setDriverForm] = useState<DriverFormState>({
    license_number: driverProfile?.license_number || '',
    license_expiry: driverProfile?.license_expiry || '',
    bio: driverProfile?.bio || '',
    accepts_smoking: driverProfile?.accepts_smoking ?? false,
    accepts_pets: driverProfile?.accepts_pets ?? false,
    accepts_luggage: driverProfile?.accepts_luggage ?? true,
    is_active: driverProfile?.is_active ?? false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      const updatedUser = await authService.updateProfile(formData);
      updateUser(updatedUser);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      full_name: user?.full_name || '',
      phone_number: user?.phone_number || '',
    });
    setIsEditing(false);
  };

  const handleToggleDriverActive = async () => {
    if (!driverProfile) return;
    setIsDriverActionLoading(true);
    try {
      const updatedDriver = await driverService.updateDriverProfile({
        is_active: !driverProfile.is_active,
      });

      if (user) {
        updateUser({
          ...user,
          driver_profile: {
            ...driverProfile,
            ...updatedDriver,
          },
        });
      }
    } catch (error) {
      console.error('Failed to update driver status:', error);
    } finally {
      setIsDriverActionLoading(false);
    }
  };

  const openDriverDrawer = () => {
    if (driverProfile) {
      setDriverForm({
        license_number: driverProfile.license_number || '',
        license_expiry: driverProfile.license_expiry || '',
        bio: driverProfile.bio || '',
        accepts_smoking: driverProfile.accepts_smoking,
        accepts_pets: driverProfile.accepts_pets,
        accepts_luggage: driverProfile.accepts_luggage,
        is_active: driverProfile.is_active,
      });
    }
    setDriverError('');
    setIsDriverDrawerOpen(true);
  };

  useEffect(() => {
    if (driverProfile && !isDriverDrawerOpen) {
      setDriverForm((prev) => ({
        ...prev,
        license_number: driverProfile.license_number || '',
        license_expiry: driverProfile.license_expiry || '',
        bio: driverProfile.bio || '',
        accepts_smoking: driverProfile.accepts_smoking,
        accepts_pets: driverProfile.accepts_pets,
        accepts_luggage: driverProfile.accepts_luggage,
        is_active: driverProfile.is_active,
      }));
    }
  }, [driverProfile, isDriverDrawerOpen]);

  const handleDriverInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setDriverForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const toggleDriverPreference = (key: keyof DriverFormState) => {
    setDriverForm((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleDriverSubmit = async () => {
    if (!driverProfile) return;
    setDriverFormLoading(true);
    setDriverError('');
    try {
      const payload = {
        license_number: driverForm.license_number,
        license_expiry: driverForm.license_expiry || null,
        bio: driverForm.bio,
        accepts_smoking: driverForm.accepts_smoking,
        accepts_pets: driverForm.accepts_pets,
        accepts_luggage: driverForm.accepts_luggage,
        is_active: driverProfile.is_verified ? driverForm.is_active : undefined,
      };
      const updatedDriver = await driverService.updateDriverProfile(payload);
      if (user) {
        updateUser({
          ...user,
          driver_profile: {
            ...driverProfile,
            ...updatedDriver,
          },
        });
      }
      setIsDriverDrawerOpen(false);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      setDriverError(err.response?.data?.detail || t('profile.driver.manage.updateError'));
    } finally {
      setDriverFormLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Profile Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <Card className="relative overflow-hidden">
            {/* Background Gradient */}
            <div className="absolute inset-0 h-32 bg-gradient-to-br from-primary-500 to-primary-600" />
            
            <div className="relative pt-16 pb-6">
              {/* Profile Picture */}
              <div className="flex justify-center">
                <div className="relative">
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="h-24 w-24 rounded-full border-4 border-white bg-white shadow-lg overflow-hidden"
                  >
                    {user?.profile_photo_url ? (
                      <img
                        src={user.profile_photo_url}
                        alt={user.full_name}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary-100 to-primary-200">
                        <User className="h-12 w-12 text-primary-600" />
                      </div>
                    )}
                  </motion.div>
                  <button className="absolute bottom-0 right-0 flex h-8 w-8 items-center justify-center rounded-full bg-primary-500 text-white shadow-lg transition-colors hover:bg-primary-600">
                    <Camera className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Name and Status */}
              <div className="mt-4 text-center">
                <h1 className="text-2xl font-bold text-secondary-900">
                  {user?.full_name || 'User'}
                </h1>
                <div className="mt-2 flex items-center justify-center gap-2">
                  {user?.is_verified && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
                      <CheckCircle2 className="h-4 w-4" />
                      {t('profile.verified')}
                    </span>
                  )}
                  {isDriver && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
                      <Car className="h-4 w-4" />
                      {t('profile.driver.label')}
                    </span>
                  )}
                </div>
              </div>

              {/* Stats Row */}
              {isDriver && driverProfile && (
                <div className="mt-6 grid grid-cols-3 gap-4 border-t border-secondary-200 pt-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-secondary-900">{driverProfile.total_trips}</p>
                    <p className="text-sm text-secondary-500">{t('profile.stats.trips')}</p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1">
                      <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                      <span className="text-2xl font-bold text-secondary-900">
                        {driverProfile.rating.toFixed(1)}
                      </span>
                    </div>
                    <p className="text-sm text-secondary-500">{t('profile.stats.rating')}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-secondary-900">{driverProfile.total_reviews}</p>
                    <p className="text-sm text-secondary-500">{t('profile.stats.reviews')}</p>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="space-y-6"
        >
          {/* Personal Information */}
          <motion.div variants={fadeInUp}>
            <Card>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-secondary-900">
                  {t('profile.personalInfo.title')}
                </h2>
                {!isEditing ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                    leftIcon={<Edit3 className="h-4 w-4" />}
                  >
                    {t('common.edit')}
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleCancel}
                      leftIcon={<X className="h-4 w-4" />}
                    >
                      {t('common.cancel')}
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleSave}
                      isLoading={isLoading}
                      leftIcon={<Save className="h-4 w-4" />}
                    >
                      {t('common.save')}
                    </Button>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                {isEditing ? (
                  <>
                    <Input
                      label={t('profile.personalInfo.fullName')}
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                      leftIcon={<User className="h-5 w-5" />}
                    />
                    <Input
                      label={t('profile.personalInfo.phone')}
                      name="phone_number"
                      value={formData.phone_number || ''}
                      onChange={handleChange}
                      leftIcon={<Phone className="h-5 w-5" />}
                      placeholder="+36 XX XXX XXXX"
                    />
                  </>
                ) : (
                  <>
                    <div className="flex items-center gap-4 p-4 rounded-xl bg-secondary-50">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-200">
                        <User className="h-5 w-5 text-secondary-600" />
                      </div>
                      <div>
                        <p className="text-sm text-secondary-500">{t('profile.personalInfo.fullName')}</p>
                        <p className="font-medium text-secondary-900">{user?.full_name || '-'}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 rounded-xl bg-secondary-50">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-200">
                        <Mail className="h-5 w-5 text-secondary-600" />
                      </div>
                      <div>
                        <p className="text-sm text-secondary-500">{t('profile.personalInfo.email')}</p>
                        <p className="font-medium text-secondary-900">{user?.email || '-'}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 rounded-xl bg-secondary-50">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-200">
                        <Phone className="h-5 w-5 text-secondary-600" />
                      </div>
                      <div>
                        <p className="text-sm text-secondary-500">{t('profile.personalInfo.phone')}</p>
                        <p className="font-medium text-secondary-900">{user?.phone_number || '-'}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 rounded-xl bg-secondary-50">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-200">
                        <Calendar className="h-5 w-5 text-secondary-600" />
                      </div>
                      <div>
                        <p className="text-sm text-secondary-500">{t('profile.personalInfo.memberSince')}</p>
                        <p className="font-medium text-secondary-900">
                          {user?.created_at
                            ? new Date(user.created_at).toLocaleDateString()
                            : '-'}
                        </p>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </Card>
          </motion.div>

          {/* Driver Section */}
          <motion.div variants={fadeInUp}>
            <Card>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-100">
                    <Car className="h-5 w-5 text-primary-600" />
                  </div>
                  <h2 className="text-xl font-semibold text-secondary-900">
                    {t('profile.driver.title')}
                  </h2>
                </div>
                {isDriver && driverProfile && driverProfile.is_verified &&(
                  <Button variant="secondary" size="sm" onClick={openDriverDrawer}>
                    {t('profile.driver.manage.button')}
                  </Button>
                )}
              </div>

              {isDriver && driverProfile ? (
                driverProfile.is_verified ? (
                  <div className="space-y-4">
                    {/* Driver Status */}
                    <div className={`flex items-center justify-between p-4 rounded-xl border ${driverProfile.is_active ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className={`h-6 w-6 ${driverProfile.is_active ? 'text-green-600' : 'text-yellow-600'}`} />
                        <div>
                          <p className={`font-medium ${driverProfile.is_active ? 'text-green-900' : 'text-yellow-900'}`}>
                            {driverProfile.is_active ? t('profile.driver.active') : t('profile.driver.inactive')}
                          </p>
                          <p className={`text-sm ${driverProfile.is_active ? 'text-green-700' : 'text-yellow-700'}`}>
                            {driverProfile.is_active ? t('profile.driver.activeDesc') : t('profile.driver.inactiveDesc')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
                          <Shield className="h-4 w-4" />
                          {t('profile.driver.verified')}
                        </span>
                        {/* <Button
                          variant={driverProfile.is_active ? 'secondary' : 'primary'}
                          size="sm"
                          onClick={handleToggleDriverActive}
                          isLoading={isDriverActionLoading}
                        >
                          {driverProfile.is_active ? t('profile.driver.pause') : t('profile.driver.activate')}
                        </Button> */}
                      </div>
                    </div>

                    {/* Bio */}
                    {driverProfile.bio && (
                      <div className="p-4 rounded-xl bg-secondary-50">
                        <p className="text-sm text-secondary-500 mb-1">{t('profile.driver.bio')}</p>
                        <p className="text-secondary-900">{driverProfile.bio}</p>
                      </div>
                    )}

                    {/* Preferences */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className={`flex flex-col items-center gap-2 p-4 rounded-xl ${driverProfile.accepts_smoking ? 'bg-green-50' : 'bg-secondary-50'}`}>
                        <Cigarette className={`h-6 w-6 ${driverProfile.accepts_smoking ? 'text-green-600' : 'text-secondary-400'}`} />
                        <span className="text-sm text-center text-secondary-700">{t('profile.driver.smoking')}</span>
                      </div>
                      <div className={`flex flex-col items-center gap-2 p-4 rounded-xl ${driverProfile.accepts_pets ? 'bg-green-50' : 'bg-secondary-50'}`}>
                        <Dog className={`h-6 w-6 ${driverProfile.accepts_pets ? 'text-green-600' : 'text-secondary-400'}`} />
                        <span className="text-sm text-center text-secondary-700">{t('profile.driver.pets')}</span>
                      </div>
                      <div className={`flex flex-col items-center gap-2 p-4 rounded-xl ${driverProfile.accepts_luggage ? 'bg-green-50' : 'bg-secondary-50'}`}>
                        <Briefcase className={`h-6 w-6 ${driverProfile.accepts_luggage ? 'text-green-600' : 'text-secondary-400'}`} />
                        <span className="text-sm text-center text-secondary-700">{t('profile.driver.luggage')}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-amber-100">
                      <Shield className="h-8 w-8 text-amber-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                      {t('profile.driver.underReview.title')}
                    </h3>
                    <p className="text-secondary-600 mb-4 max-w-md mx-auto">
                      {t('profile.driver.underReview.desc')}
                    </p>
                    <div className="rounded-xl bg-amber-50 border border-amber-200 p-4 inline-flex items-center gap-2">
                      <span className="inline-flex h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
                      <p className="text-sm text-amber-800">{t('profile.driver.underReview.note')}</p>
                    </div>
                  </div>
                )
              ) : (
                <div className="text-center py-8">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary-100">
                    <Car className="h-8 w-8 text-primary-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                    {t('profile.driver.becomeTitle')}
                  </h3>
                  <p className="text-secondary-600 mb-6 max-w-md mx-auto">
                    {t('profile.driver.becomeDesc')}
                  </p>
                  <Link to="/become-driver">
                    <Button variant="primary" size="lg" rightIcon={<ChevronRight className="h-5 w-5" />}>
                      {t('profile.driver.becomeButton')}
                    </Button>
                  </Link>
                </div>
              )}
            </Card>
          </motion.div>

          {/* Security Section */}
          <motion.div variants={fadeInUp}>
            <Card>
              <div className="flex items-center gap-3 mb-6">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-100">
                  <Shield className="h-5 w-5 text-red-600" />
                </div>
                <h2 className="text-xl font-semibold text-secondary-900">
                  {t('profile.security.title')}
                </h2>
              </div>

              <div className="space-y-3">
                <button className="flex w-full items-center justify-between p-4 rounded-xl bg-secondary-50 hover:bg-secondary-100 transition-colors">
                  <span className="font-medium text-secondary-900">{t('profile.security.changePassword')}</span>
                  <ChevronRight className="h-5 w-5 text-secondary-400" />
                </button>
                <button className="flex w-full items-center justify-between p-4 rounded-xl bg-secondary-50 hover:bg-secondary-100 transition-colors">
                  <span className="font-medium text-secondary-900">{t('profile.security.twoFactor')}</span>
                  <ChevronRight className="h-5 w-5 text-secondary-400" />
                </button>
              </div>
            </Card>
          </motion.div>
        </motion.div>
      </div>

      {/* Driver management drawer */}
      <Drawer
        isOpen={isDriverDrawerOpen}
        onClose={() => setIsDriverDrawerOpen(false)}
        title={t('profile.driver.manage.title')}
        widthClass="max-w-2xl"
        footer={
          <div className="flex items-center justify-end gap-3">
            <Button variant="ghost" onClick={() => setIsDriverDrawerOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button variant="primary" onClick={handleDriverSubmit} isLoading={driverFormLoading}>
              {t('common.save')}
            </Button>
          </div>
        }
      >
        {driverError && (
          <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {driverError}
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Input
            label={t('profile.driver.manage.licenseNumber')}
            name="license_number"
            value={driverForm.license_number}
            onChange={handleDriverInputChange}
            leftIcon={<Car className="h-5 w-5" />}
          />
          <Input
            label={t('profile.driver.manage.licenseExpiry')}
            name="license_expiry"
            type="date"
            value={driverForm.license_expiry || ''}
            onChange={driverProfile ? handleDriverInputChange : undefined}
            leftIcon={<Calendar className="h-5 w-5" />}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            {t('profile.driver.manage.bio')}
          </label>
          <textarea
            name="bio"
            value={driverForm.bio}
            onChange={handleDriverInputChange}
            rows={3}
            className="w-full rounded-xl border border-secondary-300 px-4 py-3 text-secondary-900 placeholder-secondary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-colors"
            placeholder={t('profile.driver.manage.bioPlaceholder')}
          />
        </div>

        <div className="space-y-3">
          <p className="text-sm font-medium text-secondary-700">
            {t('profile.driver.manage.preferences')}
          </p>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <button
              type="button"
              onClick={() => toggleDriverPreference('accepts_smoking')}
              className={`flex w-full items-center gap-3 rounded-xl border-2 p-3 transition-colors ${
                driverForm.accepts_smoking
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-secondary-200 bg-white hover:border-secondary-300'
              }`}
            >
              <Cigarette className={`h-5 w-5 ${driverForm.accepts_smoking ? 'text-primary-600' : 'text-secondary-500'}`} />
              <div className="text-left">
                <p className="font-medium text-secondary-900 text-sm">{t('profile.driver.manage.smokingTitle')}</p>
                <p className="text-xs text-secondary-500">{t('profile.driver.manage.smokingDesc')}</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => toggleDriverPreference('accepts_pets')}
              className={`flex w-full items-center gap-3 rounded-xl border-2 p-3 transition-colors ${
                driverForm.accepts_pets
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-secondary-200 bg-white hover:border-secondary-300'
              }`}
            >
              <Dog className={`h-5 w-5 ${driverForm.accepts_pets ? 'text-primary-600' : 'text-secondary-500'}`} />
              <div className="text-left">
                <p className="font-medium text-secondary-900 text-sm">{t('profile.driver.manage.petsTitle')}</p>
                <p className="text-xs text-secondary-500">{t('profile.driver.manage.petsDesc')}</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => toggleDriverPreference('accepts_luggage')}
              className={`flex w-full items-center gap-3 rounded-xl border-2 p-3 transition-colors ${
                driverForm.accepts_luggage
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-secondary-200 bg-white hover:border-secondary-300'
              }`}
            >
              <Briefcase className={`h-5 w-5 ${driverForm.accepts_luggage ? 'text-primary-600' : 'text-secondary-500'}`} />
              <div className="text-left">
                <p className="font-medium text-secondary-900 text-sm">{t('profile.driver.manage.luggageTitle')}</p>
                <p className="text-xs text-secondary-500">{t('profile.driver.manage.luggageDesc')}</p>
              </div>
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between rounded-xl border border-secondary-200 bg-secondary-50 px-4 py-3">
          <div>
            <p className="font-medium text-secondary-900">{t('profile.driver.manage.activeTitle')}</p>
            <p className="text-sm text-secondary-600">
              {t('profile.driver.manage.activeDesc')}
              {!driverProfile?.is_verified && ` (${t('profile.driver.manage.activeLocked')})`}
            </p>
          </div>
          <button
            type="button"
            onClick={() => driverProfile?.is_verified && toggleDriverPreference('is_active')}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              driverProfile?.is_verified && driverForm.is_active ? 'bg-primary-500' : 'bg-secondary-300'
            } ${!driverProfile?.is_verified ? 'opacity-60 cursor-not-allowed' : ''}`}
            aria-pressed={driverForm.is_active}
            aria-label="Toggle active status"
          >
            <span
              className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${
                driverForm.is_active ? 'translate-x-5' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {!driverProfile?.is_verified && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            Your driver profile is under review. You can update details now; activation will be available after verification.
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default Profile;

