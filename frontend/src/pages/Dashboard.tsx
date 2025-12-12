import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  Search,
  PlusCircle,
  Car,
  MessageSquare,
  TrendingUp,
  Wallet,
  Leaf,
  Calendar,
  UserPlus,
  Star,
  Shield,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Button, Card } from '@/components/common';

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

export const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();

  const isDriver = !!user?.driver_profile;

  // Driver-aware quick actions
  const quickActions = [
    {
      icon: Search,
      label: t('dashboard.quickActions.findRide'),
      color: 'text-blue-500',
      bgColor: 'bg-blue-100',
      hoverColor: 'hover:bg-blue-50',
      to: '/rides',
    },
    // Conditionally show "Become a Driver" or "Offer a Ride"
    isDriver
      ? {
          icon: PlusCircle,
          label: t('dashboard.quickActions.offerRide'),
          color: 'text-green-500',
          bgColor: 'bg-green-100',
          hoverColor: 'hover:bg-green-50',
          to: '/rides/create',
        }
      : {
          icon: UserPlus,
          label: t('dashboard.quickActions.becomeDriver'),
          color: 'text-green-500',
          bgColor: 'bg-green-100',
          hoverColor: 'hover:bg-green-50',
          to: '/become-driver',
          highlight: true,
        },
    {
      icon: Car,
      label: t('dashboard.quickActions.myRides'),
      color: 'text-purple-500',
      bgColor: 'bg-purple-100',
      hoverColor: 'hover:bg-purple-50',
      to: '/my-rides',
    },
    {
      icon: MessageSquare,
      label: t('dashboard.quickActions.messages'),
      color: 'text-orange-500',
      bgColor: 'bg-orange-100',
      hoverColor: 'hover:bg-orange-50',
      to: '/messages',
    },
  ];

  const stats = [
    {
      icon: TrendingUp,
      label: t('dashboard.stats.ridesCompleted'),
      value: '0',
      color: 'text-blue-500',
      bgColor: 'bg-blue-100',
    },
    {
      icon: Wallet,
      label: t('dashboard.stats.moneySaved'),
      value: '€0',
      color: 'text-green-500',
      bgColor: 'bg-green-100',
    },
    {
      icon: Leaf,
      label: t('dashboard.stats.co2Saved'),
      value: '0 kg',
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-100',
    },
  ];

  const firstName = user?.full_name?.split(' ')[0] || user?.email?.split('@')[0] || 'User';

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Welcome Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-secondary-900">
            {t('dashboard.welcome', { name: firstName })}
          </h1>
          <p className="mt-2 text-secondary-600">
            {t('dashboard.title')}
          </p>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="mb-8 grid gap-4 sm:grid-cols-3"
        >
          {stats.map((stat, index) => (
            <motion.div key={index} variants={fadeInUp}>
              <Card className="flex items-center gap-4">
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-secondary-900">{stat.value}</p>
                  <p className="text-sm text-secondary-500">{stat.label}</p>
                </div>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Driver Status Banners */}
        {!isDriver && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="mb-8"
          >
            <Card className="bg-gradient-to-r from-primary-500 to-primary-600 border-0">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-white/20">
                    <Car className="h-7 w-7 text-white" />
                  </div>
                  <div className="text-center sm:text-left">
                    <h3 className="text-lg font-semibold text-white">
                      {t('dashboard.driverBanner.title')}
                    </h3>
                    <p className="text-primary-100">
                      {t('dashboard.driverBanner.subtitle')}
                    </p>
                  </div>
                </div>
                <Link to="/become-driver">
                  <Button
                    variant="outline"
                    className="bg-white text-primary-600 border-white hover:bg-primary-50"
                  >
                    {t('dashboard.driverBanner.cta')}
                  </Button>
                </Link>
              </div>
            </Card>
          </motion.div>
        )}

        {isDriver && user?.driver_profile && !user.driver_profile.is_verified && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="mb-8"
          >
            <Card className="bg-gradient-to-r from-amber-400 to-amber-500 border-0">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-white">
                <div className="flex items-center gap-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-white/20">
                    <Shield className="h-7 w-7 text-white" />
                  </div>
                  <div className="text-center sm:text-left">
                    <h3 className="text-lg font-semibold">
                      {t('dashboard.driverStatus.underReviewTitle')}
                    </h3>
                    <p className="text-amber-50">
                      {t('dashboard.driverStatus.underReviewDesc')}
                    </p>
                  </div>
                </div>
                <Link to="/profile">
                  <Button variant="outline" className="bg-white text-amber-700 border-white hover:bg-amber-50">
                    {t('nav.profile')}
                  </Button>
                </Link>
              </div>
            </Card>
          </motion.div>
        )}

        {isDriver && user?.driver_profile && user.driver_profile.is_verified && !user.driver_profile.is_active && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="mb-8"
          >
            <Card className="bg-gradient-to-r from-yellow-400 to-yellow-500 border-0">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-white">
                <div className="flex items-center gap-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-white/20">
                    <AlertCircle className="h-7 w-7 text-white" />
                  </div>
                  <div className="text-center sm:text-left">
                    <h3 className="text-lg font-semibold">
                      {t('dashboard.driverStatus.inactiveTitle')}
                    </h3>
                    <p className="text-amber-50">
                      {t('dashboard.driverStatus.inactiveDesc')}
                    </p>
                  </div>
                </div>
                <Link to="/profile">
                  <Button variant="outline" className="bg-white text-amber-700 border-white hover:bg-amber-50">
                    {t('profile.driver.activate')}
                  </Button>
                </Link>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Driver Stats (if driver and verified and active) */}
        {isDriver && user?.driver_profile && user.driver_profile.is_verified && user.driver_profile.is_active &&(
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="mb-8"
          >
            <Card className="bg-gradient-to-r from-green-500 to-emerald-600 border-0">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-white/20">
                    <Car className="h-7 w-7 text-white" />
                  </div>
                  <div className="text-center sm:text-left">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold text-white">
                        {t('dashboard.driverStatus.title')}
                      </h3>
                      {user.driver_profile.is_verified && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-white/20 px-2 py-0.5 text-xs font-medium text-white">
                          <Shield className="h-3 w-3" />
                          {t('dashboard.driverStatus.verified')}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 mt-1">
                      <span className="flex items-center gap-1 text-green-100">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        {user.driver_profile.rating.toFixed(1)}
                      </span>
                      <span className="text-green-100">
                        {user.driver_profile.total_trips} {t('dashboard.driverStatus.trips')}
                      </span>
                    </div>
                  </div>
                </div>
                <Link to="/rides/create">
                  <Button
                    variant="outline"
                    className="bg-white text-green-600 border-white hover:bg-green-50"
                    leftIcon={<PlusCircle className="h-4 w-4" />}
                  >
                    {t('dashboard.quickActions.offerRide')}
                  </Button>
                </Link>
              </div>
            </Card>
          </motion.div>
        )}

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="lg:col-span-2"
          >
            <Card>
              <h2 className="mb-6 text-xl font-semibold text-secondary-900">
                {t('dashboard.quickActions.title')}
              </h2>
              <div className="grid gap-4 sm:grid-cols-2">
                {quickActions.map((action, index) => (
                  <Link key={index} to={action.to}>
                    <motion.div
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`flex items-center gap-4 rounded-xl border p-4 text-left transition-colors ${action.hoverColor} ${
                        action.highlight
                          ? 'border-green-300 bg-green-50 ring-2 ring-green-200'
                          : 'border-secondary-200'
                      }`}
                    >
                      <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${action.bgColor}`}>
                        <action.icon className={`h-6 w-6 ${action.color}`} />
                      </div>
                      <div className="flex-1">
                        <span className="font-medium text-secondary-900">{action.label}</span>
                        {action.highlight && (
                          <p className="text-sm text-green-600 mt-0.5">
                            {t('dashboard.quickActions.becomeDriverHint')}
                          </p>
                        )}
                      </div>
                    </motion.div>
                  </Link>
                ))}
              </div>
            </Card>
          </motion.div>

          {/* Upcoming Rides */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card className="h-full">
              <h2 className="mb-6 text-xl font-semibold text-secondary-900">
                {t('dashboard.upcomingRides.title')}
              </h2>
              
              {/* Empty State */}
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary-100">
                  <Calendar className="h-8 w-8 text-secondary-400" />
                </div>
                <p className="text-secondary-500">
                  {t('dashboard.upcomingRides.empty')}
                </p>
                <Button variant="primary" size="sm" className="mt-4">
                  {t('dashboard.quickActions.findRide')}
                </Button>
              </div>
            </Card>
          </motion.div>
        </div>

        {/* Map Preview Placeholder */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-8"
        >
          <Card padding="none" className="overflow-hidden">
            <div className="relative h-64 bg-gradient-to-br from-primary-100 to-primary-200">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Car className="mx-auto h-12 w-12 text-primary-400" />
                  <p className="mt-2 text-primary-600 font-medium">
                    Map Coming Soon
                  </p>
                  <p className="text-sm text-primary-500">
                    Budapest ⇄ Wien Route
                  </p>
                </div>
              </div>
              {/* Route decoration */}
              <div className="absolute bottom-8 left-8 right-8">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-primary-500" />
                    <span className="text-sm font-medium text-primary-700">Budapest</span>
                  </div>
                  <div className="flex-1 mx-4 border-t-2 border-dashed border-primary-400" />
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-primary-700">Wien</span>
                    <div className="h-3 w-3 rounded-full bg-primary-500" />
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
