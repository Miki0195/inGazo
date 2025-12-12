import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Mail, Lock, User, Phone, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Button, Input, Logo, Card } from '@/components/common';
import { RegisterData } from '@/types';

interface FormErrors {
  full_name?: string;
  email?: string;
  phone_number?: string;
  password?: string;
  password_confirm?: string;
}

export const Register: React.FC = () => {
  const { t } = useTranslation();
  const { register } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState<RegisterData>({
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
    password_confirm: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [apiError, setApiError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.full_name) {
      newErrors.full_name = t('auth.register.errors.required');
    }

    if (!formData.email && !formData.phone_number) {
      newErrors.email = t('auth.register.errors.emailOrPhoneRequired');
    } else if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = t('auth.register.errors.invalidEmail');
    }

    if (!formData.password) {
      newErrors.password = t('auth.register.errors.required');
    } else if (formData.password.length < 8) {
      newErrors.password = t('auth.register.errors.passwordTooShort');
    }

    if (!formData.password_confirm) {
      newErrors.password_confirm = t('auth.register.errors.required');
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = t('auth.register.errors.passwordMismatch');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError('');
    setSuccessMessage('');

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      // Clean up form data - remove empty optional fields
      const submitData: RegisterData = {
        full_name: formData.full_name,
        password: formData.password,
        password_confirm: formData.password_confirm,
      };

      if (formData.email) {
        submitData.email = formData.email;
      }
      if (formData.phone_number) {
        submitData.phone_number = formData.phone_number;
      }

      await register(submitData);
      setSuccessMessage(t('auth.register.success'));
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string; email?: string[]; phone_number?: string[] } } };
      if (err.response?.data?.email) {
        setErrors((prev) => ({ ...prev, email: err.response?.data?.email?.[0] }));
      } else if (err.response?.data?.phone_number) {
        setErrors((prev) => ({ ...prev, phone_number: err.response?.data?.phone_number?.[0] }));
      } else {
        setApiError(err.response?.data?.detail || 'Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-secondary-50 px-4 py-12">
      {/* Background decorations */}
      <div className="absolute -right-20 -top-20 h-96 w-96 rounded-full bg-primary-100/30 blur-3xl" />
      <div className="absolute -bottom-20 -left-20 h-96 w-96 rounded-full bg-secondary-100/30 blur-3xl" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md"
      >
        <Card padding="lg" className="shadow-xl">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <Link to="/">
              <Logo size="lg" />
            </Link>
          </div>

          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-secondary-900">
              {t('auth.register.title')}
            </h1>
            <p className="mt-2 text-secondary-600">
              {t('auth.register.subtitle')}
            </p>
          </div>

          {/* Success Message */}
          {successMessage && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 flex items-center gap-3 rounded-xl bg-green-50 p-4 text-green-600"
            >
              <CheckCircle className="h-5 w-5 flex-shrink-0" />
              <p className="text-sm">{successMessage}</p>
            </motion.div>
          )}

          {/* Error Alert */}
          {apiError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 flex items-center gap-3 rounded-xl bg-red-50 p-4 text-red-600"
            >
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              <p className="text-sm">{apiError}</p>
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label={t('auth.register.fullName')}
              name="full_name"
              type="text"
              placeholder={t('auth.register.fullNamePlaceholder')}
              value={formData.full_name}
              onChange={handleChange}
              error={errors.full_name}
              leftIcon={<User className="h-5 w-5" />}
              autoComplete="name"
            />

            <Input
              label={t('auth.register.email')}
              name="email"
              type="email"
              placeholder={t('auth.register.emailPlaceholder')}
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              leftIcon={<Mail className="h-5 w-5" />}
              autoComplete="email"
            />

            <Input
              label={t('auth.register.phoneNumber')}
              name="phone_number"
              type="tel"
              placeholder={t('auth.register.phoneNumberPlaceholder')}
              value={formData.phone_number}
              onChange={handleChange}
              error={errors.phone_number}
              leftIcon={<Phone className="h-5 w-5" />}
              autoComplete="tel"
            />

            <Input
              label={t('auth.register.password')}
              name="password"
              type="password"
              placeholder={t('auth.register.passwordPlaceholder')}
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              leftIcon={<Lock className="h-5 w-5" />}
              autoComplete="new-password"
            />

            <Input
              label={t('auth.register.passwordConfirm')}
              name="password_confirm"
              type="password"
              placeholder={t('auth.register.passwordConfirmPlaceholder')}
              value={formData.password_confirm}
              onChange={handleChange}
              error={errors.password_confirm}
              leftIcon={<Lock className="h-5 w-5" />}
              autoComplete="new-password"
            />

            <Button
              type="submit"
              className="w-full"
              size="lg"
              isLoading={isLoading}
              disabled={!!successMessage}
            >
              {t('auth.register.submit')}
            </Button>
          </form>

          {/* Sign in link */}
          <div className="mt-8 text-center">
            <p className="text-secondary-600">
              {t('auth.register.hasAccount')}{' '}
              <Link
                to="/login"
                className="font-medium text-primary-600 hover:text-primary-700"
              >
                {t('auth.register.signIn')}
              </Link>
            </p>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};

export default Register;
