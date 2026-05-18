/**
 * Login Page
 * Authentication page with login and registration forms
 */

import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import { useNotification } from '@context/NotificationContext';
import { Flask } from '@phosphor-icons/react';
import { ph } from '@components/icons/phosphor';
import { Button, Input, ThemeToggle } from '@components/common';
import { ROUTES, ALLOW_PUBLIC_REGISTRATION } from '@utils/constants';
import { validatePassword, validateUsername, isValidEmail } from '@utils/validators';
import styles from './LoginPage.module.css';

export function LoginPage() {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, register } = useAuth();
  const { success, error: showError } = useNotification();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || ROUTES.EXPERIMENTS;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    
    // Clear error on change
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Username validation
    const usernameValidation = validateUsername(formData.username);
    if (!usernameValidation.isValid) {
      newErrors.username = usernameValidation.errors[0];
    }

    // Email validation (only for registration)
    if (isRegisterMode && ALLOW_PUBLIC_REGISTRATION) {
      if (!formData.email) {
        newErrors.email = 'Введите email';
      } else if (!isValidEmail(formData.email)) {
        newErrors.email = 'Некорректный формат email';
      }
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Введите пароль';
    } else if (isRegisterMode && ALLOW_PUBLIC_REGISTRATION) {
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.isValid) {
        newErrors.password = passwordValidation.errors[0];
      }
    }

    // Confirm password (only for registration)
    if (
      isRegisterMode &&
      ALLOW_PUBLIC_REGISTRATION &&
      formData.password !== formData.confirmPassword
    ) {
      newErrors.confirmPassword = 'Пароли не совпадают';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);

    try {
      if (isRegisterMode && ALLOW_PUBLIC_REGISTRATION) {
        await register({
          username: formData.username,
          email: formData.email,
          password: formData.password,
        });
        success('Регистрация успешна! Войдите в систему.');
        setIsRegisterMode(false);
        setFormData((prev) => ({ ...prev, email: '', confirmPassword: '' }));
      } else {
        await login({
          username: formData.username,
          password: formData.password,
        });
        success('Вход выполнен успешно');
        navigate(from, { replace: true });
      }
    } catch (err) {
      const msg = err.message || 'Произошла ошибка';
      if (isRegisterMode && err.status === 403) {
        showError(
          'Регистрация отключена. Обратитесь к администратору для создания учётной записи.',
        );
      } else {
        showError(msg);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    setErrors({});
  };

  return (
    <div className={styles.container}>
      <div className={styles.themeToggleWrap}>
        <ThemeToggle />
      </div>
      {/* Background decoration */}
      <div className={styles.bgDecoration}>
        <div className={styles.gridOverlay} />
        <div className={styles.accentLines} />
      </div>

      <div className={styles.formContainer}>
        <div className={styles.formCard}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.logo}>
              <Flask className={styles.logoIcon} {...ph(36)} aria-hidden />
            </div>
            <span className={styles.brandName}>ScratchLab</span>
            <h1 className={styles.title}>
              {isRegisterMode && ALLOW_PUBLIC_REGISTRATION
                ? 'Регистрация'
                : 'Вход в систему'}
            </h1>
            <p className={styles.subtitle}>
              {isRegisterMode && ALLOW_PUBLIC_REGISTRATION
                ? 'Создайте аккаунт для работы с системой'
                : 'Система анализа устойчивости к царапинам'}
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className={styles.form}>
            <Input
              name="username"
              label="Имя пользователя"
              placeholder="Введите имя пользователя"
              value={formData.username}
              onChange={handleChange}
              error={errors.username}
              required
              autoComplete="username"
            />

            {isRegisterMode && ALLOW_PUBLIC_REGISTRATION && (
              <Input
                name="email"
                type="email"
                label="Email"
                placeholder="example@mail.com"
                value={formData.email}
                onChange={handleChange}
                error={errors.email}
                required
                autoComplete="email"
              />
            )}

            <Input
              name="password"
              type="password"
              label="Пароль"
              placeholder="Введите пароль"
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              required
              autoComplete={isRegisterMode ? 'new-password' : 'current-password'}
            />

            {isRegisterMode && ALLOW_PUBLIC_REGISTRATION && (
              <Input
                name="confirmPassword"
                type="password"
                label="Подтвердите пароль"
                placeholder="Повторите пароль"
                value={formData.confirmPassword}
                onChange={handleChange}
                error={errors.confirmPassword}
                required
                autoComplete="new-password"
              />
            )}

            <Button
              type="submit"
              variant="primary"
              fullWidth
              loading={isSubmitting}
            >
              {isRegisterMode && ALLOW_PUBLIC_REGISTRATION
                ? 'Создать аккаунт'
                : 'Войти'}
            </Button>
          </form>

          {ALLOW_PUBLIC_REGISTRATION && (
            <div className={styles.footer}>
              <span className={styles.footerText}>
                {isRegisterMode ? 'Уже есть аккаунт?' : 'Нет аккаунта?'}
              </span>
              <button
                type="button"
                className={styles.toggleButton}
                onClick={toggleMode}
              >
                {isRegisterMode ? 'Войти' : 'Создать'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default LoginPage;

