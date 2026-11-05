
import React, { useState } from 'react';
import {
  Eye,
  EyeOff,
  Leaf,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

import {
  signInWithEmailAndPassword,
  setPersistence,
  browserLocalPersistence,
  browserSessionPersistence,
} from 'firebase/auth';

import { auth } from '../../../firebase';

interface LoginPageProps {
  onNavigate: (route: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onNavigate,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [feedback, setFeedback] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    setFeedback('');
    setIsLoading(true);

    try {
      // Set the authentication persistence
      await setPersistence(
        auth,
        rememberMe
          ? browserLocalPersistence
          : browserSessionPersistence
      );

      // Authenticate user with Firebase
      await signInWithEmailAndPassword(
        auth,
        email.trim(),
        password
      );

      setFeedback('Login successful! Welcome back.');

      // Navigate to the application
      onNavigate('landing');

    } catch (error: any) {
      console.error('Login error:', error);

      switch (error.code) {
        case 'auth/invalid-email':
          setFeedback('Please enter a valid email address.');
          break;

        case 'auth/invalid-credential':
        case 'auth/user-not-found':
        case 'auth/wrong-password':
          setFeedback('Invalid email or password. Please try again.');
          break;

        case 'auth/user-disabled':
          setFeedback('This account has been disabled.');
          break;

        case 'auth/too-many-requests':
          setFeedback('Too many attempts. Please try again later.');
          break;

        case 'auth/network-request-failed':
          setFeedback('Network error. Please check your internet connection.');
          break;

        default:
          setFeedback(error.message || 'Login failed. Please try again.');
      }

    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <section className="auth-brand-panel">
        <div className="auth-brand-content">
          <div className="auth-logo">
            <span className="auth-logo-icon">
              <Leaf size={25} />
            </span>
            <span>Ayurlex</span>
          </div>

          <div className="auth-brand-message">
            <span className="auth-eyebrow">
              AYURVEDA • INTELLECTUAL PROPERTY • INNOVATION
            </span>

            <h1>
              Knowledge deserves
              <span> protection.</span>
            </h1>

            <p>
              Explore the intersection of Ayurveda, intellectual property
              rights and regulatory intelligence through one intelligent platform.
            </p>
          </div>

          <div className="auth-brand-footer">
            <ShieldCheck size={18} />
            <span>Research with clarity. Innovate with confidence.</span>
          </div>
        </div>

        <div className="auth-decoration auth-decoration-one" />
        <div className="auth-decoration auth-decoration-two" />
      </section>

      <section className="auth-form-panel">
        <div className="auth-mobile-logo">
          <Leaf size={23} />
          <span>Ayurlex</span>
        </div>

        <div className="auth-form-container">
          <div className="auth-heading">
            <span className="auth-eyebrow">WELCOME BACK</span>
            <h2>Sign in to Ayurlex</h2>
            <p>Enter your credentials to continue your research journey.</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">

            <div className="auth-field">
              <label htmlFor="login-email">Email address</label>
              <input
                id="login-email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="auth-field">
              <label htmlFor="login-password">Password</label>

              <div className="auth-password-wrapper">
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
                  required
                />

                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword((previous) => !previous)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
                </button>
              </div>
            </div>

            <div className="auth-form-options">
              <label className="auth-checkbox-label">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(event) => setRememberMe(event.target.checked)}
                />
                <span>Remember me</span>
              </label>

              <button
                type="button"
                className="auth-text-button"
                onClick={() =>
                  setFeedback('Password recovery will be implemented next.')
                }
              >
                Forgot password?
              </button>
            </div>

            <button
              type="submit"
              className="auth-submit-button"
              disabled={isLoading}
            >
              {isLoading ? 'Signing in...' : 'Login'}
              {!isLoading && <ArrowRight size={18} />}
            </button>

            {feedback && (
              <p className="auth-feedback" role="status">
                {feedback}
              </p>
            )}
          </form>

          <div className="auth-switch">
            Don't have an account?
            <button
              type="button"
              onClick={() => onNavigate('register')}
            >
              Create an account
            </button>
          </div>

          <p className="auth-legal-note">
            By continuing, you agree to use Ayurlex responsibly and in accordance
            with its applicable policies.
          </p>
        </div>
      </section>
    </div>
  );
};
