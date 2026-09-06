import { FormEvent, useState } from 'react';
import { ArrowLeft, ArrowRight, LockKeyhole } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [forgotSent, setForgotSent] = useState(false);
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setLoading(true); setError('');
    const role = await login(email, password);
    if (!role) setError('We could not find an authorised workspace for that email. Please contact your administrator.');
    else if (role === 'PLATFORM_ADMIN') navigate('/admin/dashboard');
    else if (role === 'FIELD_OFFICER') navigate('/field/dashboard');
    else navigate('/organisation/dashboard');
    setLoading(false);
  };
  return <div className="auth-page"><div className="auth-layout auth-layout--login"><aside className="auth-aside"><Link to="/" className="public-brand"><span className="public-brand__mark">VG</span><span><strong>Voice of a Girl</strong><small>Opportunity, measured.</small></span></Link><div><span className="public-kicker">Workspace access</span><h1>Good work deserves a clear view.</h1><p>Sign in to manage programmes, participants, surveys, and the evidence behind your impact.</p></div><div className="auth-aside__detail"><LockKeyhole className="h-4 w-4" /> Secure access for authorised teams</div></aside><main className="auth-card auth-card--compact"><Link to={location.state?.from || '/'} className="auth-back"><ArrowLeft className="h-4 w-4" /> Back</Link><span className="public-kicker">Team sign in</span><h2>Welcome back</h2><p className="auth-intro">Use your authorised work email to continue to your workspace.</p>{error && <div className="auth-alert auth-alert--error">{error}</div>}{forgotSent && <div className="auth-alert auth-alert--success">A password reset request has been noted. Your administrator will follow up.</div>}<form onSubmit={submit} className="login-form"><label>Work email<input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@organisation.org" /></label><label>Password<input required type="password" minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" /></label><div className="login-form__meta"><button type="button" onClick={() => setForgotSent(true)}>Forgot password?</button><span><LockKeyhole className="h-3.5 w-3.5" /> Protected workspace</span></div><button disabled={loading} className="public-button public-button--primary auth-submit" type="submit">{loading ? 'Signing you in...' : 'Sign in'}<ArrowRight className="h-4 w-4" /></button></form></main></div></div>;
}
