import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  Wallet,
  Leaf,
  Users,
  ShieldCheck,
  UserPlus,
  Search,
  Car,
  ArrowRight,
} from 'lucide-react';
import { Button, Card } from '@/components/common';

const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const Home: React.FC = () => {
  const { t } = useTranslation();

  const features = [
    {
      icon: Wallet,
      title: t('home.features.costSaving.title'),
      description: t('home.features.costSaving.description'),
      color: 'text-green-500',
      bgColor: 'bg-green-100',
    },
    {
      icon: Leaf,
      title: t('home.features.ecoFriendly.title'),
      description: t('home.features.ecoFriendly.description'),
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-100',
    },
    {
      icon: Users,
      title: t('home.features.community.title'),
      description: t('home.features.community.description'),
      color: 'text-blue-500',
      bgColor: 'bg-blue-100',
    },
    {
      icon: ShieldCheck,
      title: t('home.features.safety.title'),
      description: t('home.features.safety.description'),
      color: 'text-purple-500',
      bgColor: 'bg-purple-100',
    },
  ];

  const steps = [
    {
      icon: UserPlus,
      title: t('home.howItWorks.step1.title'),
      description: t('home.howItWorks.step1.description'),
    },
    {
      icon: Search,
      title: t('home.howItWorks.step2.title'),
      description: t('home.howItWorks.step2.description'),
    },
    {
      icon: Car,
      title: t('home.howItWorks.step3.title'),
      description: t('home.howItWorks.step3.description'),
    },
  ];

  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50" />
        
        {/* Decorative elements */}
        <div className="absolute -right-20 -top-20 h-96 w-96 rounded-full bg-primary-100/50 blur-3xl" />
        <div className="absolute -bottom-20 -left-20 h-96 w-96 rounded-full bg-secondary-100/50 blur-3xl" />
        
        <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="grid gap-12 lg:grid-cols-2 lg:gap-8 items-center">
            {/* Hero Content */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center lg:text-left"
            >
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-4xl font-bold tracking-tight text-secondary-900 sm:text-5xl lg:text-6xl"
              >
                <span className="block">{t('home.hero.title').split(' ')[0]}</span>
                <span className="block text-gradient mt-2">
                  {t('home.hero.title').split(' ').slice(1).join(' ')}
                </span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="mt-6 text-lg text-secondary-600 sm:text-xl max-w-xl mx-auto lg:mx-0"
              >
                {t('home.hero.subtitle')}
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="mt-10 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
              >
                <Link to="/register">
                  <Button
                    size="lg"
                    rightIcon={<ArrowRight className="h-5 w-5" />}
                    className="w-full sm:w-auto shadow-lg shadow-primary-500/30"
                  >
                    {t('home.hero.cta')}
                  </Button>
                </Link>
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  {t('home.hero.secondaryCta')}
                </Button>
              </motion.div>

              {/* Stats */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="mt-12 grid grid-cols-3 gap-4 text-center lg:text-left"
              >
                {[
                  { value: '10K+', label: 'Users' },
                  { value: '50K+', label: 'Rides' },
                  { value: '€500K+', label: 'Saved' },
                ].map((stat, index) => (
                  <div key={index}>
                    <p className="text-2xl font-bold text-primary-600 sm:text-3xl">
                      {stat.value}
                    </p>
                    <p className="text-sm text-secondary-500">{stat.label}</p>
                  </div>
                ))}
              </motion.div>
            </motion.div>

            {/* Hero Image/Illustration */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative hidden lg:block"
            >
              <div className="relative">
                {/* Main car illustration placeholder */}
                <div className="relative mx-auto h-96 w-full rounded-3xl bg-gradient-to-br from-primary-400 to-primary-600 p-8 shadow-2xl shadow-primary-500/30">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Car className="h-32 w-32 text-white/90" />
                  </div>
                  {/* Route line decoration */}
                  <div className="absolute bottom-8 left-8 right-8">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded-full bg-white" />
                        <span className="text-sm font-medium text-white">Budapest</span>
                      </div>
                      <div className="flex-1 mx-4 border-t-2 border-dashed border-white/50" />
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-white">Wien</span>
                        <div className="h-3 w-3 rounded-full bg-white" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Floating cards */}
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="absolute -left-8 top-20 rounded-2xl bg-white p-4 shadow-xl"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100">
                      <Wallet className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-secondary-900">Save up to</p>
                      <p className="text-lg font-bold text-green-600">€150/month</p>
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  animate={{ y: [0, 10, 0] }}
                  transition={{ duration: 4, repeat: Infinity }}
                  className="absolute -right-8 bottom-32 rounded-2xl bg-white p-4 shadow-xl"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100">
                      <Leaf className="h-5 w-5 text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-secondary-900">CO₂ saved</p>
                      <p className="text-lg font-bold text-emerald-600">2.5 tons/year</p>
                    </div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold text-secondary-900 sm:text-4xl">
              {t('home.features.title')}
            </h2>
            <p className="mt-4 text-lg text-secondary-600">
              {t('home.features.subtitle')}
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4"
          >
            {features.map((feature, index) => (
              <motion.div key={index} variants={fadeInUp}>
                <Card hover className="h-full text-center">
                  <div className={`mx-auto flex h-14 w-14 items-center justify-center rounded-2xl ${feature.bgColor}`}>
                    <feature.icon className={`h-7 w-7 ${feature.color}`} />
                  </div>
                  <h3 className="mt-6 text-lg font-semibold text-secondary-900">
                    {feature.title}
                  </h3>
                  <p className="mt-3 text-secondary-600">
                    {feature.description}
                  </p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-secondary-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold text-secondary-900 sm:text-4xl">
              {t('home.howItWorks.title')}
            </h2>
          </motion.div>

          <div className="mt-16">
            <div className="relative">
              {/* Connection line */}
              <div className="absolute left-1/2 top-8 hidden h-0.5 w-2/3 -translate-x-1/2 bg-gradient-to-r from-primary-200 via-primary-400 to-primary-200 lg:block" />

              <motion.div
                variants={staggerContainer}
                initial="initial"
                whileInView="animate"
                viewport={{ once: true }}
                className="grid gap-8 lg:grid-cols-3"
              >
                {steps.map((step, index) => (
                  <motion.div
                    key={index}
                    variants={fadeInUp}
                    className="relative text-center"
                  >
                    {/* Step number */}
                    <div className="relative mx-auto mb-6">
                      <div className="relative z-10 mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-400 to-primary-600 text-white shadow-lg shadow-primary-500/30">
                        <step.icon className="h-8 w-8" />
                      </div>
                      <span className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-secondary-900 text-sm font-bold text-white">
                        {index + 1}
                      </span>
                    </div>
                    <h3 className="text-xl font-semibold text-secondary-900">
                      {step.title}
                    </h3>
                    <p className="mt-3 text-secondary-600">
                      {step.description}
                    </p>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </div>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
            className="mt-16 text-center"
          >
            <Link to="/register">
              <Button
                size="lg"
                rightIcon={<ArrowRight className="h-5 w-5" />}
                className="shadow-lg shadow-primary-500/30"
              >
                {t('home.hero.cta')}
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;
