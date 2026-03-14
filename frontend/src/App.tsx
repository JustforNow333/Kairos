"use client";

import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { fetchDashboard, uploadSyllabus } from "./api";
import type { DashboardResponse, ParseResponse, ScheduleBlock, SocialPocket } from "./types";

function formatTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatDueDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function minuteOffset(value: string, dayStart = 8): number {
  const date = new Date(value);
  return (date.getHours() - dayStart) * 60 + date.getMinutes();
}

function blockHeight(startAt: string, endAt: string): number {
  const start = new Date(startAt).getTime();
  const end = new Date(endAt).getTime();
  return Math.max((end - start) / 60000, 30);
}

function blockTone(type: ScheduleBlock["block_type"]): string {
  switch (type) {
    case "work":
      return "block work";
    case "social":
      return "block social";
    case "meal":
      return "block meal";
    default:
      return "block class";
  }
}

function buildFateweaverStrategies(
  dashboard: DashboardResponse,
  targetPocket: SocialPocket | null,
): string[] {
  const targetLabel = targetPocket?.title ?? "this window";
  const strategies: string[] = [];
  const sprintMinutes = Math.min(Math.max(Math.round(dashboard.shuffle_plan.unlocked_minutes / 2), 20), 30);

  const readingAssignment = dashboard.assignments.find(
    (assignment) => assignment.status !== "done" && assignment.task_type === "reading",
  );
  if (readingAssignment) {
    strategies.push(
      `Do ${readingAssignment.title} in focused skim mode and extract only discussion-critical points. That keeps ${targetLabel} reachable.`,
    );
  }

  const problemSetAssignment = dashboard.assignments.find(
    (assignment) =>
      assignment.status !== "done" &&
      (assignment.task_type === "pset" || assignment.task_type === "lab"),
  );
  if (problemSetAssignment) {
    strategies.push(
      `Start ${problemSetAssignment.title} with the fastest wins first so you secure visible progress before you leave.`,
    );
  }

  const laterWorkBlock = dashboard.shuffle_plan.after_blocks.find(
    (block) => block.block_type === "work" && new Date(block.start_at).getHours() >= 19,
  );
  if (laterWorkBlock) {
    strategies.push(
      `Move ${laterWorkBlock.label} into the quieter later block and protect the next clean sprint for ${targetLabel}.`,
    );
  }

  if (strategies.length < 3) {
    strategies.push(
      `Use a ${sprintMinutes}-minute distraction-free sprint now. Fateweaver Protocol only needs one clean burst to unlock ${targetLabel}.`,
    );
  }

  if (strategies.length < 3) {
    strategies.push(
      `Aim for a good-enough pass before this window, then revise later tonight once the opportunity is secured.`,
    );
  }

  return strategies.slice(0, 3);
}

function ScheduleCanvas({
  blocks,
  title,
}: {
  blocks: ScheduleBlock[];
  title: string;
}) {
  return (
    <div className="schedule-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Fateweaver Protocol</p>
          <h3>{title}</h3>
        </div>
        <p className="muted">8 AM to 10 PM</p>
      </div>

      <div className="schedule-grid">
        {Array.from({ length: 8 }, (_, index) => 8 + index * 2).map((hour) => (
          <div className="schedule-tick" key={hour}>
            <span>{hour <= 12 ? `${hour} AM` : `${hour - 12} PM`}</span>
          </div>
        ))}

        <LayoutGroup>
          {blocks.map((block) => (
            <motion.div
              key={block.id}
              layout
              transition={{ type: "spring", stiffness: 220, damping: 26 }}
              className={blockTone(block.block_type)}
              style={{
                top: `${minuteOffset(block.start_at) * 1.18}px`,
                height: `${blockHeight(block.start_at, block.end_at) * 1.18}px`,
              }}
            >
              <div className="block-topline">
                <span>{formatTime(block.start_at)}</span>
                <span>{Math.round(block.intensity * 100)}%</span>
              </div>
              <strong>{block.label}</strong>
              <span>
                {formatTime(block.start_at)} to {formatTime(block.end_at)}
              </span>
            </motion.div>
          ))}
        </LayoutGroup>
      </div>
    </div>
  );
}

const storyLabels = [
  "Ingest syllabus",
  "Price the work debt",
  "Spot a social window",
  "Run Fateweaver Protocol",
];

export default function App() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [parseResult, setParseResult] = useState<ParseResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [showShuffled, setShowShuffled] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [storyStep, setStoryStep] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const response = await fetchDashboard();
        if (!cancelled) {
          setDashboard(response);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load dashboard");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const scheduleBlocks = useMemo(() => {
    if (!dashboard) {
      return [];
    }

    return showShuffled ? dashboard.shuffle_plan.after_blocks : dashboard.shuffle_plan.before_blocks;
  }, [dashboard, showShuffled]);

  const topPocket = dashboard?.pockets[0] ?? null;
  const fateweaverStrategies = useMemo(() => {
    if (!dashboard) {
      return [];
    }

    return buildFateweaverStrategies(dashboard, topPocket);
  }, [dashboard, topPocket]);

  function playDemoStory() {
    setStoryStep(0);
    setShowShuffled(false);
    window.setTimeout(() => setStoryStep(1), 500);
    window.setTimeout(() => setStoryStep(2), 1100);
    window.setTimeout(() => {
      setStoryStep(3);
      setShowShuffled(true);
    }, 1800);
  }

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadSyllabus(file);
      setParseResult(response);
      setStoryStep(1);
      setDashboard((current) =>
        current
          ? {
              ...current,
              course: response.course,
              assignments: response.assignments,
              ledger: response.ledger,
            }
          : current,
      );
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed");
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  if (isLoading) {
    return <div className="screen-state">Loading KAIROS...</div>;
  }

  if (error || !dashboard) {
    return <div className="screen-state">Unable to load the MVP: {error}</div>;
  }

  return (
    <div className="app-shell">
      <div className="background-orb background-orb-left" />
      <div className="background-orb background-orb-right" />

      <motion.header
        className="hero"
        initial={{ opacity: 0, y: 28 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.65 }}
      >
        <div className="hero-copy">
          <p className="eyebrow">KAIROS / Cornell life arbitrage</p>
          <h1>Live the life you planned, not the one you fell into.</h1>
          <p className="hero-text">
            KAIROS turns academic pressure, friend availability, and idle drift into
            Fateweaver Protocol: a system that rewrites flexible work around the moments
            worth saving.
          </p>

          <div className="hero-actions">
            <button className="primary-button" onClick={() => setShowShuffled((value) => !value)}>
              {showShuffled ? "Show original day" : "Trigger Fateweaver Protocol"}
            </button>
            <button className="secondary-button" onClick={playDemoStory}>
              Play demo story
            </button>
            <label className="upload-button">
              {isUploading ? "Parsing syllabus..." : "Upload syllabus"}
              <input type="file" accept=".pdf,.txt,.doc,.docx" onChange={handleUpload} hidden />
            </label>
          </div>

          <div className="hero-metrics">
            <div>
              <span>Work Debt</span>
              <strong>{dashboard.ledger.work_debt_score}</strong>
            </div>
            <div>
              <span>Recovered window</span>
              <strong>{dashboard.shuffle_plan.unlocked_minutes} mins</strong>
            </div>
            <div>
              <span>Friends aligned</span>
              <strong>{topPocket?.friend_names.length ?? 0}</strong>
            </div>
            <div>
              <span>Social readiness</span>
              <strong>{dashboard.social_readiness.score}%</strong>
            </div>
          </div>
        </div>

        <motion.div
          className="hero-card"
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.55, delay: 0.12 }}
        >
          <div className="hero-card-top">
            <span className="badge">Fateweaver engine</span>
            <span>{dashboard.course.code}</span>
          </div>
          <h2>{topPocket?.title ?? dashboard.idle_alert.headline}</h2>
          <p>{topPocket?.emotional_hook ?? dashboard.idle_alert.action}</p>
          <div className="hero-context">
            <span>{dashboard.weather.temperature_f}F</span>
            <span>{dashboard.weather.summary}</span>
            <span>{topPocket?.location_hint ?? "Cornell campus"}</span>
          </div>
          <div className="friend-row">
            {(topPocket?.friend_names ?? dashboard.idle_alert.friend_names).map((name) => (
              <span key={name}>{name}</span>
            ))}
          </div>
        </motion.div>
      </motion.header>

      <section className="story-rail">
        {storyLabels.map((label, index) => {
          const status =
            index < storyStep ? "complete" : index === storyStep ? "active" : "pending";
          return (
            <div className={`story-step ${status}`} key={label}>
              <span>{index + 1}</span>
              <strong>{label}</strong>
            </div>
          );
        })}
      </section>

      <main className="dashboard">
        <section className="dashboard-grid">
          <motion.article
            className={`card debt-card ${storyStep === 1 ? "active-card" : ""}`}
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.1 }}
          >
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Work Debt Ledger</p>
                <h3>{dashboard.ledger.work_debt_score} debt points</h3>
              </div>
              <span className="badge warm">{dashboard.ledger.interest_drag_hours}h lost to delay</span>
            </div>

            <div className="meter-track">
              <motion.div
                className="meter-fill"
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(dashboard.ledger.work_debt_score, 100)}%` }}
                transition={{ duration: 0.7, delay: 0.2 }}
              />
            </div>

            <div className="mini-stats">
              <div>
                <span>Total academic load</span>
                <strong>{dashboard.ledger.total_hours} hrs</strong>
              </div>
              <div>
                <span>Focus needed today</span>
                <strong>{dashboard.ledger.focus_hours_today} hrs</strong>
              </div>
            </div>

            <p className="card-copy">{dashboard.ledger.summary}</p>

            <div className="assignment-list">
              {dashboard.ledger.items.map((item) => (
                <div key={item.assignment_id} className="assignment-row">
                  <div>
                    <strong>{item.title}</strong>
                    <span>
                      due {formatDueDate(item.due_at)} / {item.adjusted_effort_hours.toFixed(1)}h adjusted
                    </span>
                  </div>
                  <span>{item.interest_multiplier.toFixed(2)}x urgency</span>
                </div>
              ))}
            </div>
          </motion.article>

          <motion.article
            className={`card schedule-card ${storyStep === 3 ? "active-card" : ""}`}
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.16 }}
          >
            <ScheduleCanvas
              blocks={scheduleBlocks}
              title={showShuffled ? "Rewoven day" : "Original day plan"}
            />
            <div className="shuffle-footer">
              <div>
                <p className="eyebrow">Rewritten tradeoff</p>
                <h3>{dashboard.shuffle_plan.tradeoff_statement}</h3>
              </div>
              <button className="secondary-button" onClick={() => setShowShuffled((value) => !value)}>
                {showShuffled ? "Show original day" : "Run Fateweaver Protocol"}
              </button>
            </div>
            <div className="strategy-panel">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">AI tactics</p>
                  <h3>How Fateweaver makes this window believable</h3>
                </div>
                <span className="badge">Window-specific</span>
              </div>
              <div className="strategy-list">
                {fateweaverStrategies.map((strategy) => (
                  <div className="strategy-item" key={strategy}>
                    <span className="strategy-index">Protocol</span>
                    <p>{strategy}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.article>
        </section>

        <section className="lower-grid">
          <motion.article
            className={`card ${storyStep === 2 ? "active-card" : ""}`}
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.24 }}
          >
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Social Gravity</p>
                <h3>Claimable micro-pockets</h3>
              </div>
              <span className="badge">{dashboard.pockets.length} live windows</span>
            </div>

            <div className="pocket-list">
              {dashboard.pockets.map((pocket) => (
                <motion.div
                  className="pocket-card"
                  key={pocket.id}
                  whileHover={{ y: -4 }}
                  transition={{ type: "spring", stiffness: 260, damping: 20 }}
                >
                  <div className="pocket-meta">
                    <strong>{pocket.title}</strong>
                    <span>{pocket.claimability} claimability</span>
                  </div>
                  <p>
                    {formatTime(pocket.start_at)} to {formatTime(pocket.end_at)} · {pocket.location_hint}
                  </p>
                  <p>
                    {pocket.weather_label} · {pocket.day_phase}
                  </p>
                  <div className="friend-row">
                    {pocket.friend_names.map((name) => (
                      <span key={name}>{name}</span>
                    ))}
                  </div>
                  <p className="card-copy">{pocket.why_now}</p>
                  <p className="card-copy pocket-hook">{pocket.emotional_hook}</p>
                </motion.div>
              ))}
            </div>
          </motion.article>

          <motion.article
            className="card intervention-card"
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.32 }}
          >
            <p className="eyebrow">Idle intervention</p>
            <AnimatePresence mode="wait">
              <motion.div
                key={showShuffled ? "open" : "closed"}
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -18 }}
                transition={{ duration: 0.3 }}
              >
                <h3>{dashboard.idle_alert.headline}</h3>
                <p className="card-copy">{dashboard.idle_alert.action}</p>
                <div className="mini-stats">
                  <div>
                    <span>Social readiness gap</span>
                    <strong>{dashboard.idle_alert.social_readiness_gap_hours} hrs</strong>
                  </div>
                  <div>
                    <span>Best move now</span>
                    <strong>{showShuffled ? "Leave for the Slope" : "Sprint first"}</strong>
                  </div>
                  <div>
                    <span>Social readiness</span>
                    <strong>{dashboard.social_readiness.score}%</strong>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>

            <div className="social-readiness-panel">
              <p className="eyebrow">Social Readiness</p>
              <h3>
                {dashboard.social_readiness.status === "behind"
                  ? `${dashboard.social_readiness.gap_hours} hours short this week`
                  : "On track for a balanced week"}
              </h3>
              <p className="card-copy">{dashboard.social_readiness.summary}</p>
            </div>

            <div className="assumptions">
              <div>
                <span>Reading speed</span>
                <strong>{dashboard.assumptions.reading_speed_pph} pph</strong>
              </div>
              <div>
                <span>Major difficulty</span>
                <strong>{dashboard.assumptions.major_difficulty_multiplier.toFixed(2)}x</strong>
              </div>
              <div>
                <span>Historical pace</span>
                <strong>{dashboard.assumptions.historical_productivity_multiplier.toFixed(2)}x</strong>
              </div>
            </div>

            {parseResult ? (
              <div className="upload-result">
                <span className="badge warm">{parseResult.parser_mode}</span>
                <strong>
                  Parsed {parseResult.course.code}: {parseResult.course.title}
                </strong>
                <p>{parseResult.notes}</p>
              </div>
            ) : null}
          </motion.article>
        </section>
      </main>
    </div>
  );
}
