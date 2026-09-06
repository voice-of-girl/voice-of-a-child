import { ArrowRight, BarChart3, CheckCircle2, ClipboardList, LineChart, ShieldCheck, Sparkles, Users } from 'lucide-react';
import { Link } from 'react-router-dom';

const steps = [
  { number: '01', title: 'Create your programme', body: 'Set the target, location, skills, education, and interests your programme needs.' },
  { number: '02', title: 'Find suitable beneficiaries', body: 'See a transparent shortlist of girls whose profiles match your requirements.' },
  { number: '03', title: 'Select and track results', body: 'Manage applications, invite the right people, and measure what happened next.' }
];

const features = [
  { icon: Users, title: 'Find the right people', body: 'Reach beneficiaries who fit your programme instead of searching through disconnected lists.' },
  { icon: ClipboardList, title: 'Save screening time', body: 'Compare skills, education, location, and interests in one clear candidate view.' },
  { icon: LineChart, title: 'Measure your reach', body: 'Track who you reached, matched, selected, and supported through the programme.' }
];

export function PublicHomePage() {
  return (
    <div className="public-site" id="public-home">
      <header className="public-nav">
        <div className="public-nav__inner">
          <Link to="/" className="public-brand" aria-label="Voice of a Girl home">
            <span className="public-brand__mark">VG</span>
            <span><strong>Voice of a Girl</strong><small>Opportunity, measured.</small></span>
          </Link>
          <nav className="public-nav__links" aria-label="Public navigation">
            <a href="#how-it-works">How it works</a>
            <a href="#features">What we track</a>
            <Link to="/login" className="public-button public-button--quiet">Team sign in <ArrowRight className="h-3.5 w-3.5" /></Link>
          </nav>
          <Link to="/login" className="public-nav__menu" aria-label="Team sign in"><ArrowRight className="h-5 w-5" /></Link>
        </div>
      </header>

      <main>
        <section className="public-hero">
          <div className="public-hero__content">
            <div className="public-eyebrow"><Sparkles className="h-3.5 w-3.5" /> Uganda Youth Initiative</div>
              <h1>Reach the right beneficiaries. <em>Run better programmes.</em></h1>
              <p className="public-hero__lead">Voice of a Girl helps organisations find, reach, match, and manage the right young women for their programmes.</p>
            <div className="public-hero__actions">
                <Link to="/login" className="public-button public-button--primary">For organisations <ArrowRight className="h-4 w-4" /></Link>
                <Link to="/register" className="public-button public-button--quiet">Find opportunities</Link>
            </div>
            <div className="public-proof"><span><strong>4,280</strong> beneficiaries reached</span><span><strong>1,284</strong> matched</span><span><strong>180</strong> selected</span></div>
          </div>
          <div className="public-hero__visual">
            <div className="public-hero__image-frame">
              <img src="https://images.unsplash.com/photo-1532375810709-75b1da00537c?auto=format&fit=crop&w=1200&q=85" alt="Black African girls in a rural classroom" />
              <div className="public-hero__caption"><span className="public-status-dot" /> A supported journey, from first contact to measurable change.</div>
            </div>
            <div className="public-hero__note"><ShieldCheck className="h-5 w-5" /><span><strong>Safeguarding first</strong><small>Every record is reviewed by the programme team.</small></span></div>
          </div>
        </section>

        <section className="public-section public-section--tinted" id="project-impact">
          <div className="public-section__heading"><span className="public-kicker">Voice of a Girl — Uganda</span><h2>Real impact in rural communities</h2><p>We work with local organisations across Uganda to reach girls in rural areas with skills, mentorship, and economic opportunities.</p></div>
          <div className="public-steps">
            <article className="public-step"><span>12</span><h3>Districts</h3><p>Reaching girls across rural Uganda from West Nile to Karamoja.</p></article>
            <article className="public-step"><span>6</span><h3>Partner organisations</h3><p>Local NGOs and community-based organisations leading implementation.</p></article>
            <article className="public-step"><span>2,400+</span><h3>Girls supported</h3><p>Beneficiaries enrolled in skills training and livelihood programmes.</p></article>
            <article className="public-step"><span>85%</span><h3>Completion rate</h3><p>Girls who complete their programme and transition to work or further study.</p></article>
          </div>
        </section>

        <section className="public-section public-section--tinted" id="how-it-works">
          <div className="public-section__heading"><span className="public-kicker">How it works</span><h2>Simple for teams. Free for girls.</h2><p>A clear operating rhythm that helps organisations reach the right people and make better programme decisions.</p></div>
          <div className="public-steps">{steps.map((step) => <article key={step.number} className="public-step"><span>{step.number}</span><h3>{step.title}</h3><p>{step.body}</p></article>)}</div>
        </section>

        <section className="public-section" id="features">
          <div className="public-section__heading"><span className="public-kicker">One connected system</span><h2>Built for the work behind the work.</h2><p>From participant intake to donor-ready reporting, the platform keeps your programme story connected.</p></div>
          <div className="public-feature-grid">{features.map(({ icon: Icon, title, body }) => <article key={title} className="public-feature"><span className="public-feature__icon"><Icon className="h-5 w-5" /></span><h3>{title}</h3><p>{body}</p></article>)}</div>
        </section>

        <section className="public-cta">
          <div><span className="public-kicker">For participants</span><h2>Your next chapter can start with one form.</h2><p>No account required. Tell our team a little about yourself and we will help you find the right next step.</p></div>
          <Link to="/register" className="public-button public-button--light">Start your registration <ArrowRight className="h-4 w-4" /></Link>
        </section>
      </main>

      <footer className="public-footer"><span>Voice of a Girl</span><span>Participant pathways · Programme intelligence · Measurable impact</span><Link to="/login">Team sign in</Link></footer>
    </div>
  );
}
