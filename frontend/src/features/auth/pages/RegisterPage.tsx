import React, { useState } from 'react';
import { Eye, EyeOff, Leaf, ArrowRight, ShieldCheck } from 'lucide-react';

interface RegisterPageProps {
  onNavigate: (route: string) => void;
}

export const RegisterPage: React.FC<RegisterPageProps> = ({ onNavigate }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [organization, setOrganization] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFeedback('');

    if (password !== confirmPassword) {
      setFeedback('Passwords do not match. Please check both password fields.');
      return;
    }

    if (!acceptedTerms) {
      setFeedback('Please accept the Terms & Conditions to continue.');
      return;
    }

    setFeedback(
      'The registration interface is ready. Backend account creation will be connected separately.'
    );
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
            <span className="auth-eyebrow">DISCOVER • LEARN • INNOVATE</span>

            <h1>
              Be part of the
              <span> knowledge journey.</span>
            </h1>

            <p>
              Join a platform designed to make Ayurveda-related research,
              intellectual property and regulatory knowledge more accessible.
            </p>
          </div>

          <div className="auth-brand-footer">
            <ShieldCheck size={18} />
            <span>One platform. A world of knowledge.</span>
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

        <div className="auth-form-container auth-register-container">
          <div className="auth-heading">
            <span className="auth-eyebrow">GET STARTED</span>
            <h2>Create your account</h2>
            <p>Join Ayurlex and start exploring today.</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="auth-field">
              <label htmlFor="register-name">Full name</label>
              <input
                id="register-name"
                type="text"
                placeholder="Enter your full name"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                autoComplete="name"
                required
              />
            </div>

            <div className="auth-field">
              <label htmlFor="register-email">Email address</label>
              <input
                id="register-email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="auth-field">
              <label htmlFor="register-organization">
                Organization / Institution
                <span className="auth-optional">Optional</span>
              </label>
              <input
                id="register-organization"
                type="text"
                placeholder="Enter your organization name"
                value={organization}
                onChange={(event) => setOrganization(event.target.value)}
                autoComplete="organization"
              />
            </div>

            <div className="auth-field">
              <label htmlFor="register-password">Password</label>

              <div className="auth-password-wrapper">
                <input
                  id="register-password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Create a password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="new-password"
                  minLength={8}
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
              <span className="auth-field-hint">Use at least 8 characters.</span>
            </div>

            <div className="auth-field">
              <label htmlFor="register-confirm-password">Confirm password</label>

              <div className="auth-password-wrapper">
                <input
                  id="register-confirm-password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Re-enter your password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  autoComplete="new-password"
                  minLength={8}
                  required
                />

                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() =>
                    setShowConfirmPassword((previous) => !previous)
                  }
                  aria-label={
                    showConfirmPassword
                      ? 'Hide confirm password'
                      : 'Show confirm password'
                  }
                >
                  {showConfirmPassword ? (
                    <EyeOff size={19} />
                  ) : (
                    <Eye size={19} />
                  )}
                </button>
              </div>
            </div>

            <label className="auth-checkbox-label auth-terms">
              <input
                type="checkbox"
                checked={acceptedTerms}
                onChange={(event) => setAcceptedTerms(event.target.checked)}
                required
              />
              <span>
                I agree to the <a href="#terms">Terms & Conditions</a> and
                applicable privacy policies.
              </span>
            </label>

            <button type="submit" className="auth-submit-button">
              Create account
              <ArrowRight size={18} />
            </button>

            {feedback && (
              <p className="auth-feedback" role="status">
                {feedback}
              </p>
            )}
          </form>

          <div className="auth-switch">
            Already have an account?
            <button type="button" onClick={() => onNavigate('login')}>
              Login
            </button>
          </div>

          <p className="auth-legal-note">
            Your information will be handled according to the platform's
            applicable privacy policies.
          </p>
        </div>
      </section>
    </div>
  );
};