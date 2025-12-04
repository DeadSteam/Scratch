/**
 * Auth Context Provider
 * Manages authentication state across the application
 */

import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { authService } from '@api/AuthService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state from session storage
  useEffect(() => {
    const initAuth = () => {
      try {
        if (authService.isAuthenticated()) {
          const storedUser = authService.getStoredUser();
          setUser(storedUser);
        }
      } catch (err) {
        console.error('Auth init error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // Login handler
  const login = useCallback(async (credentials) => {
    setError(null);
    setIsLoading(true);
    
    try {
      const authData = await authService.login(credentials);
      setUser(authData.user);
      return authData;
    } catch (err) {
      setError(err.message || 'Ошибка авторизации');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Register handler
  const register = useCallback(async (userData) => {
    setError(null);
    setIsLoading(true);
    
    try {
      const newUser = await authService.register(userData);
      return newUser;
    } catch (err) {
      setError(err.message || 'Ошибка регистрации');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Logout handler
  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
    setError(null);
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Check if user is admin
  const isAdmin = useMemo(() => {
    if (!user || !user.roles) return false;
    return user.roles.some(role => role.name === 'admin');
  }, [user]);

  // Memoized context value
  const value = useMemo(() => ({
    user,
    isLoading,
    error,
    isAuthenticated: !!user,
    isAdmin,
    login,
    register,
    logout,
    clearError,
  }), [user, isLoading, error, isAdmin, login, register, logout, clearError]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

export default AuthContext;



