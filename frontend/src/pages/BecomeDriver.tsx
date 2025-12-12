import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  Car,
  CreditCard,
  Calendar,
  FileText,
  Cigarette,
  Dog,
  Briefcase,
  CheckCircle2,
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  Shield,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Button, Card, Input } from '@/components/common';
import { driverService } from '@/services/driver';
import { BecomeDriverData } from '@/types';

const steps = [
  { id: 1, key: 'license' },
  { id: 2, key: 'preferences' },
  { id: 3, key: 'confirm' },
];

export const BecomeDriver: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user, updateUser } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<BecomeDriverData>({
    license_number: '',
    license_expiry: '',
    bio: '',
    accepts_smoking: false,
    accepts_pets: false,
    accepts_luggage: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const togglePreference = (key: keyof BecomeDriverData) => {
    setFormData((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleNext = () => {
    if (currentStep === 1 && !formData.license_number) {
      setError(t('becomeDriver.errors.licenseRequired'));
      return;
    }
    if (currentStep === 1 && !formData.license_expiry) {
      setError(t('becomeDriver.errors.licenseExpiry'));
      return;
    }
    setError('');
    setCurrentStep((prev) => Math.min(prev + 1, 3));
  };

  const handleBack = () => {
    setError('');
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError('');

    try {
      const driverProfile = await driverService.becomeDriver(formData); 
      // Update user context with driver profile
      if (user) {
        updateUser({ ...user, driver_profile: driverProfile });
      }
      navigate('/profile', { state: { success: true } });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || t('becomeDriver.errors.failed'));
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center gap-2 mb-8">
      {steps.map((step, index) => (
        <React.Fragment key={step.id}>
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: currentStep >= step.id ? 1 : 0.8 }}
            className={`flex h-10 w-10 items-center justify-center rounded-full font-semibold transition-colors ${
              currentStep >= step.id
                ? 'bg-primary-500 text-white'
                : 'bg-secondary-200 text-secondary-500'
            }`}
          >
            {currentStep > step.id ? (
              <CheckCircle2 className="h-5 w-5" />
            ) : (
              step.id
            )}
          </motion.div>
          {index < steps.length - 1 && (
            <div
              className={`h-1 w-12 rounded transition-colors ${
                currentStep > step.id ? 'bg-primary-500' : 'bg-secondary-200'
              }`}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary-100">
          <CreditCard className="h-8 w-8 text-primary-600" />
        </div>
        <h2 className="text-xl font-semibold text-secondary-900">
          {t('becomeDriver.steps.license.title')}
        </h2>
        <p className="mt-2 text-secondary-600">
          {t('becomeDriver.steps.license.subtitle')}
        </p>
      </div>

      <Input
        label={t('becomeDriver.fields.licenseNumber')}
        name="license_number"
        value={formData.license_number}
        onChange={handleChange}
        leftIcon={<CreditCard className="h-5 w-5" />}
        placeholder="AB123456"
        required
      />

      <Input
        label={t('becomeDriver.fields.licenseExpiry')}
        name="license_expiry"
        type="date"
        value={formData.license_expiry}
        onChange={handleChange}
        leftIcon={<Calendar className="h-5 w-5" />}
      />

      <div>
        <label className="block text-sm font-medium text-secondary-700 mb-2">
          {t('becomeDriver.fields.bio')}
        </label>
        <textarea
          name="bio"
          value={formData.bio}
          onChange={handleChange}
          rows={3}
          className="w-full rounded-xl border border-secondary-300 px-4 py-3 text-secondary-900 placeholder-secondary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-colors"
          placeholder={t('becomeDriver.fields.bioPlaceholder')}
        />
      </div>
    </motion.div>
  );

  const renderStep2 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary-100">
          <Car className="h-8 w-8 text-primary-600" />
        </div>
        <h2 className="text-xl font-semibold text-secondary-900">
          {t('becomeDriver.steps.preferences.title')}
        </h2>
        <p className="mt-2 text-secondary-600">
          {t('becomeDriver.steps.preferences.subtitle')}
        </p>
      </div>

      <div className="space-y-4">
        <motion.button
          type="button"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => togglePreference('accepts_smoking')}
          className={`flex w-full items-center gap-4 rounded-xl border-2 p-4 transition-colors ${
            formData.accepts_smoking
              ? 'border-primary-500 bg-primary-50'
              : 'border-secondary-200 bg-white hover:border-secondary-300'
          }`}
        >
          <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${
            formData.accepts_smoking ? 'bg-primary-100' : 'bg-secondary-100'
          }`}>
            <Cigarette className={`h-6 w-6 ${
              formData.accepts_smoking ? 'text-primary-600' : 'text-secondary-500'
            }`} />
          </div>
          <div className="flex-1 text-left">
            <p className="font-medium text-secondary-900">{t('becomeDriver.preferences.smoking.title')}</p>
            <p className="text-sm text-secondary-500">{t('becomeDriver.preferences.smoking.desc')}</p>
          </div>
          <div className={`flex h-6 w-6 items-center justify-center rounded-full ${
            formData.accepts_smoking ? 'bg-primary-500' : 'bg-secondary-200'
          }`}>
            {formData.accepts_smoking && <CheckCircle2 className="h-4 w-4 text-white" />}
          </div>
        </motion.button>

        <motion.button
          type="button"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => togglePreference('accepts_pets')}
          className={`flex w-full items-center gap-4 rounded-xl border-2 p-4 transition-colors ${
            formData.accepts_pets
              ? 'border-primary-500 bg-primary-50'
              : 'border-secondary-200 bg-white hover:border-secondary-300'
          }`}
        >
          <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${
            formData.accepts_pets ? 'bg-primary-100' : 'bg-secondary-100'
          }`}>
            <Dog className={`h-6 w-6 ${
              formData.accepts_pets ? 'text-primary-600' : 'text-secondary-500'
            }`} />
          </div>
          <div className="flex-1 text-left">
            <p className="font-medium text-secondary-900">{t('becomeDriver.preferences.pets.title')}</p>
            <p className="text-sm text-secondary-500">{t('becomeDriver.preferences.pets.desc')}</p>
          </div>
          <div className={`flex h-6 w-6 items-center justify-center rounded-full ${
            formData.accepts_pets ? 'bg-primary-500' : 'bg-secondary-200'
          }`}>
            {formData.accepts_pets && <CheckCircle2 className="h-4 w-4 text-white" />}
          </div>
        </motion.button>

        <motion.button
          type="button"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => togglePreference('accepts_luggage')}
          className={`flex w-full items-center gap-4 rounded-xl border-2 p-4 transition-colors ${
            formData.accepts_luggage
              ? 'border-primary-500 bg-primary-50'
              : 'border-secondary-200 bg-white hover:border-secondary-300'
          }`}
        >
          <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${
            formData.accepts_luggage ? 'bg-primary-100' : 'bg-secondary-100'
          }`}>
            <Briefcase className={`h-6 w-6 ${
              formData.accepts_luggage ? 'text-primary-600' : 'text-secondary-500'
            }`} />
          </div>
          <div className="flex-1 text-left">
            <p className="font-medium text-secondary-900">{t('becomeDriver.preferences.luggage.title')}</p>
            <p className="text-sm text-secondary-500">{t('becomeDriver.preferences.luggage.desc')}</p>
          </div>
          <div className={`flex h-6 w-6 items-center justify-center rounded-full ${
            formData.accepts_luggage ? 'bg-primary-500' : 'bg-secondary-200'
          }`}>
            {formData.accepts_luggage && <CheckCircle2 className="h-4 w-4 text-white" />}
          </div>
        </motion.button>
      </div>
    </motion.div>
  );

  const renderStep3 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
          <Shield className="h-8 w-8 text-green-600" />
        </div>
        <h2 className="text-xl font-semibold text-secondary-900">
          {t('becomeDriver.steps.confirm.title')}
        </h2>
        <p className="mt-2 text-secondary-600">
          {t('becomeDriver.steps.confirm.subtitle')}
        </p>
      </div>

      {/* Summary */}
      <Card className="bg-secondary-50">
        <h3 className="font-semibold text-secondary-900 mb-4">{t('becomeDriver.summary.title')}</h3>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-secondary-200">
            <span className="text-secondary-600">{t('becomeDriver.fields.licenseNumber')}</span>
            <span className="font-medium text-secondary-900">{formData.license_number}</span>
          </div>
          
          {formData.license_expiry && (
            <div className="flex items-center justify-between py-2 border-b border-secondary-200">
              <span className="text-secondary-600">{t('becomeDriver.fields.licenseExpiry')}</span>
              <span className="font-medium text-secondary-900">
                {new Date(formData.license_expiry).toLocaleDateString()}
              </span>
            </div>
          )}
          
          <div className="flex items-center justify-between py-2">
            <span className="text-secondary-600">{t('becomeDriver.summary.preferences')}</span>
            <div className="flex gap-2">
              {formData.accepts_smoking && (
                <span className="inline-flex items-center gap-1 rounded-full bg-primary-100 px-2 py-1 text-xs text-primary-700">
                  <Cigarette className="h-3 w-3" />
                </span>
              )}
              {formData.accepts_pets && (
                <span className="inline-flex items-center gap-1 rounded-full bg-primary-100 px-2 py-1 text-xs text-primary-700">
                  <Dog className="h-3 w-3" />
                </span>
              )}
              {formData.accepts_luggage && (
                <span className="inline-flex items-center gap-1 rounded-full bg-primary-100 px-2 py-1 text-xs text-primary-700">
                  <Briefcase className="h-3 w-3" />
                </span>
              )}
            </div>
          </div>
        </div>
      </Card>

      <div className="rounded-xl bg-blue-50 p-4 border border-blue-200">
        <div className="flex gap-3">
          <FileText className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-900">{t('becomeDriver.verification.title')}</p>
            <p className="text-sm text-blue-700 mt-1">{t('becomeDriver.verification.desc')}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 px-4 py-12">
      {/* Background decorations */}
      <div className="absolute -right-20 -top-20 h-96 w-96 rounded-full bg-primary-100/30 blur-3xl" />
      <div className="absolute -bottom-20 -left-20 h-96 w-96 rounded-full bg-secondary-100/30 blur-3xl" />

      <div className="relative mx-auto max-w-lg">
        {/* Back Button */}
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => navigate(-1)}
          className="mb-6 flex items-center gap-2 text-secondary-600 hover:text-secondary-900 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
          {t('common.back')}
        </motion.button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card padding="lg" className="shadow-xl">
            {/* Header */}
            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold text-secondary-900">
                {t('becomeDriver.title')}
              </h1>
              <p className="mt-2 text-secondary-600">
                {t('becomeDriver.subtitle')}
              </p>
            </div>

            {/* Step Indicator */}
            {renderStepIndicator()}

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 flex items-center gap-3 rounded-xl bg-red-50 p-4 text-red-600"
              >
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </motion.div>
            )}

            {/* Step Content */}
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}

            {/* Navigation Buttons */}
            <div className="mt-8 flex gap-4">
              {currentStep > 1 && (
                <Button
                  variant="outline"
                  onClick={handleBack}
                  leftIcon={<ArrowLeft className="h-4 w-4" />}
                  className="flex-1"
                >
                  {t('common.back')}
                </Button>
              )}
              
              {currentStep < 3 ? (
                <Button
                  variant="primary"
                  onClick={handleNext}
                  rightIcon={<ArrowRight className="h-4 w-4" />}
                  className="flex-1"
                >
                  {t('common.next')}
                </Button>
              ) : (
                <Button
                  variant="primary"
                  onClick={handleSubmit}
                  isLoading={isLoading}
                  leftIcon={<Car className="h-4 w-4" />}
                  className="flex-1"
                >
                  {t('becomeDriver.submit')}
                </Button>
              )}
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default BecomeDriver;

