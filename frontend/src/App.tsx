"use client";

import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { fetchDashboard, uploadSyllabus, putUserAssumptions, syncGoogleCalendar, getGoogleOAuthUrl, addFriend } from "./api";
import type { DashboardResponse, ParseResponse, ScheduleBlock } from "./types";

type PageView = "home" | "schedule";

type ManagedAssignment = {
  id: string;
  title: string;
  historicalHours: number;
};

type ManagedClass = {
  id: string;
  name: string;
  code: string;
  assignments: ManagedAssignment[];
  syllabusFileName?: string;
};

type TimeBlockDraft = {
  label: string;
  start: string;
  end: string;
};

const storySteps = [
  "See the pressure clearly",
  "Spot the social opening",
  "Reweave the day",
];

function formatTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
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
    case "buffer":
      return "block buffer";
    default:
      return "block class";
  }
}

function toDateTimeLocal(value: string): string {
  const date = new Date(value);
  const offset = date.getTimezoneOffset();
  const adjusted = new Date(date.getTime() - offset * 60_000);
  return adjusted.toISOString().slice(0, 16);
}

function buildManagedClasses(dashboard: DashboardResponse): ManagedClass[] {
  return [
    {
      id: "seeded-course",
      code: dashboard.course.code,
      name: dashboard.course.title,
      assignments: dashboard.assignments.map((assignment) => ({
        id: assignment.id,
        title: assignment.title,
        historicalHours: Number(assignment.base_effort_hours.toFixed(1)),
      })),
    },
  ];
}

function buildOptimizedBlocks(
  dashboard: DashboardResponse,
  draftedBlock: TimeBlockDraft | null,
  showOptimized: boolean,
): ScheduleBlock[] {
  const sourceBlocks = showOptimized
    ? dashboard.shuffle_plan.after_blocks
    : dashboard.shuffle_plan.before_blocks;

  if (!draftedBlock || !showOptimized) {
    return sourceBlocks;
  }

  const customBlock: ScheduleBlock = {
    id: "custom-timeblock",
    label: draftedBlock.label,
    block_type: "social",
    start_at: new Date(draftedBlock.start).toISOString(),
    end_at: new Date(draftedBlock.end).toISOString(),
    movable: false,
    intensity: 0.78,
  };

  return [...sourceBlocks, customBlock].sort(
    (left, right) => new Date(left.start_at).getTime() - new Date(right.start_at).getTime(),
  );
}

function Modal({
  open,
  title,
  onClose,
  children,
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  return (
    <AnimatePresence>
      {open ? (
        <motion.div
          className="modal-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="modal-shell"
            initial={{ opacity: 0, y: 16, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.2 }}
          >
            <div className="modal-header">
              <div>
                <p className="eyebrow">KAIROS</p>
                <h3>{title}</h3>
              </div>
              <button className="ghost-button" onClick={onClose} type="button">
                Close
              </button>
            </div>
            {children}
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}

function ScheduleCanvas({ blocks }: { blocks: ScheduleBlock[] }) {
  return (
    <div className="schedule-panel">
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
                top: `${minuteOffset(block.start_at) * 1.12}px`,
                height: `${blockHeight(block.start_at, block.end_at) * 1.12}px`,
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

export default function App() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [managedClasses, setManagedClasses] = useState<ManagedClass[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState<string | null>(null);
  const [showOptimized, setShowOptimized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pageView, setPageView] = useState<PageView>("home");
  const [showFriends, setShowFriends] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showAddClassModal, setShowAddClassModal] = useState(false);
  const [showTimeBlockModal, setShowTimeBlockModal] = useState(false);
  const [parseResult, setParseResult] = useState<ParseResponse | null>(null);
  const [selectedClassId, setSelectedClassId] = useState<string | null>(null);
  const [newClassName, setNewClassName] = useState("");
  const [assignmentDrafts, setAssignmentDrafts] = useState<Record<string, { title: string; historicalHours: string }>>({});
  const [timeBlockDraft, setTimeBlockDraft] = useState<TimeBlockDraft | null>(null);
  const [timeBlockForm, setTimeBlockForm] = useState<TimeBlockDraft>({
    label: "Slope sunset window",
    start: "",
    end: "",
  });

  // Google Calendar & Add Friend state
  const [showAddFriend, setShowAddFriend] = useState(false);
  const [friendName, setFriendName] = useState("");
  const [friendZone, setFriendZone] = useState("");
  const [isAddingFriend, setIsAddingFriend] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const response = await fetchDashboard();
        if (!cancelled) {
          setDashboard(response);
          setManagedClasses(buildManagedClasses(response));
          const targetPocket = response.pockets[0];
          if (targetPocket) {
            setTimeBlockForm({
              label: targetPocket.title,
              start: toDateTimeLocal(targetPocket.start_at),
              end: toDateTimeLocal(targetPocket.end_at),
            });
          }
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

  const topPocket = dashboard?.pockets[0] ?? null;
  const optimizedBlocks = useMemo(() => {
    if (!dashboard) {
      return [];
    }

    return buildOptimizedBlocks(dashboard, timeBlockDraft, showOptimized);
  }, [dashboard, showOptimized, timeBlockDraft]);

  const fateweaverStrategies = useMemo(() => {
    if (!dashboard) {
      return [];
    }

    return dashboard.shuffle_plan.tactics ?? [];
  }, [dashboard]);

  const selectedClass = managedClasses.find((course) => course.id === selectedClassId) ?? managedClasses[0] ?? null;
  const connectedFriends = dashboard?.friends.flatMap((friend) => friend.windows.map((window) => ({
    id: `${friend.friend_id}-${window.start_at}`,
    name: friend.friend_name,
    startAt: window.start_at,
    endAt: window.end_at,
    locationHint: window.location_hint,
  }))) ?? [];

  function addClass() {
    if (!newClassName.trim()) {
      return;
    }

    const generatedCode = `COURSE ${managedClasses.length + 1}`;
    const newClass: ManagedClass = {
      id: `class-${Date.now()}`,
      name: newClassName.trim(),
      code: generatedCode,
      assignments: [],
    };

    setManagedClasses((current) => [newClass, ...current]);
    setSelectedClassId(newClass.id);
    setNewClassName("");
    setShowAddClassModal(false);
  }

  function updateAssignmentDraft(
    classId: string,
    field: "title" | "historicalHours",
    value: string,
  ) {
    setAssignmentDrafts((current) => ({
      ...current,
      [classId]: {
        title: current[classId]?.title ?? "",
        historicalHours: current[classId]?.historicalHours ?? "",
        [field]: value,
      },
    }));
  }

  function addAssignment(classId: string) {
    const draft = assignmentDrafts[classId];
    if (!draft?.title.trim() || !draft.historicalHours.trim()) {
      return;
    }

    setManagedClasses((current) =>
      current.map((course) =>
        course.id === classId
          ? {
            ...course,
            assignments: [
              ...course.assignments,
              {
                id: `assignment-${Date.now()}`,
                title: draft.title.trim(),
                historicalHours: Number(draft.historicalHours),
              },
            ],
          }
          : course,
      ),
    );

    setAssignmentDrafts((current) => ({
      ...current,
      [classId]: { title: "", historicalHours: "" },
    }));
  }

  async function handleSyllabusUpload(classId: string, file: File) {
    setIsUploading(classId);
    setError(null);

    try {
      const response = await uploadSyllabus(file);
      setParseResult(response);

      setManagedClasses((current) =>
        current.map((course) =>
          course.id === classId
            ? {
              ...course,
              name: response.course.title,
              code: response.course.code,
              syllabusFileName: file.name,
              assignments: response.assignments.map((assignment) => ({
                id: assignment.id,
                title: assignment.title,
                historicalHours: Number(assignment.base_effort_hours.toFixed(1)),
              })),
            }
            : course,
        ),
      );

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
      setIsUploading(null);
    }
  }

  function runFateweaver() {
    setShowOptimized(true);
    setTimeBlockDraft(timeBlockForm);
    setPageView("schedule");
  }

  function handleConnectCalendar() {
    window.location.href = getGoogleOAuthUrl();
  }

  async function handleAddFriendSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!friendName || !friendZone) return;
    setIsAddingFriend(true);
    try {
      await addFriend(friendName, friendZone);
      const newDash = await fetchDashboard();
      setDashboard(newDash);
      setShowAddFriend(false);
      setFriendName("");
      setFriendZone("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add friend");
    } finally {
      setIsAddingFriend(false);
    }
  }

  if (isLoading) {
    return <div className="screen-state">Loading KAIROS...</div>;
  }

  if (error || !dashboard) {
    return <div className="screen-state">Unable to load the MVP: {error}</div>;
  }

  const highlightedFriend = topPocket?.friend_names.slice(0, 3).join(" · ") ?? "Your Cornell circle";

  return (
    <div className="app-shell">
      <div className="background-orb background-orb-left" />
      <div className="background-orb background-orb-right" />

      <header className="topbar">
        <div>
          <p className="eyebrow">KAIROS / Cornell life operating system</p>
          <strong className="brand-lockup">Fateweaver-first student operating system</strong>
        </div>
        <button className="secondary-button" onClick={() => setShowAuthModal(true)} type="button">
          Sign Up / Login
        </button>
        <button className="secondary-button" onClick={handleConnectCalendar} type="button">
          Connect Google Calendar
        </button>
        <button className="secondary-button" onClick={() => setShowAddFriend(true)} type="button">
          + Add Friend
        </button>
      </header>

      <nav className="page-switcher">
        <button
          className={pageView === "home" ? "switch-pill active" : "switch-pill"}
          onClick={() => setPageView("home")}
          type="button"
        >
          Page 1
        </button>
        <button
          className={pageView === "schedule" ? "switch-pill active" : "switch-pill"}
          onClick={() => setPageView("schedule")}
          type="button"
        >
          Page 2
        </button>
      </nav>

      <AnimatePresence mode="wait">
        {pageView === "home" ? (
          <motion.main
            key="home"
            className="page-grid"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -18 }}
            transition={{ duration: 0.35 }}
          >
            <section className="hero-panel">
              <p className="eyebrow">Front page</p>
              <h1>Live the life you planned, not the one you fell into.</h1>
              <p className="hero-text">
                KAIROS maps classes, assignment drag, friend overlap, and campus momentum into
                Fateweaver Protocol so a better version of the day is always one move away.
              </p>

              <div className="story-ribbon">
                {storySteps.map((step, index) => (
                  <motion.div
                    animate={{ opacity: 1, y: 0 }}
                    className="story-node"
                    initial={{ opacity: 0, y: 14 }}
                    key={step}
                    transition={{ delay: index * 0.12 + 0.08, duration: 0.28 }}
                  >
                    <span>{index + 1}</span>
                    <strong>{step}</strong>
                  </motion.div>
                ))}
              </div>

              <div className="hero-actions">
                <button className="primary-button" onClick={() => setShowFriends((value) => !value)} type="button">
                  {showFriends ? "Hide connected friends" : "Show connected friends"}
                </button>
                <button className="secondary-button" onClick={() => setShowAddClassModal(true)} type="button">
                  Add class
                </button>
              </div>

              <div className="hero-metrics">
                <div>
                  <span>Debt hours</span>
                  <strong>{dashboard.ledger.interest_drag_hours}h</strong>
                </div>
                <div>
                  <span>Work debt</span>
                  <strong>{dashboard.ledger.work_debt_score}</strong>
                </div>
                <div>
                  <span>Friends aligned</span>
                  <strong>{topPocket?.friend_names.length ?? 0}</strong>
                </div>
                <div>
                  <span>Recovered window</span>
                  <strong>{dashboard.shuffle_plan.unlocked_minutes} min</strong>
                </div>
              </div>

              <motion.div
                animate={{ opacity: 1, y: 0 }}
                className="fateweaver-preview"
                initial={{ opacity: 0, y: 18 }}
                transition={{ delay: 0.18, duration: 0.35 }}
              >
                <div className="preview-topline">
                  <span className="badge">Fateweaver spotlight</span>
                  <span className="preview-score">{dashboard.social_readiness.score}% ready</span>
                </div>
                <h3>{timeBlockDraft?.label ?? topPocket?.title ?? "A reclaimable Cornell window"}</h3>
                <p>
                  {topPocket?.emotional_hook ??
                    "A sharp rewrite turns pressure into a night that still feels worth remembering."}
                </p>
                <div className="preview-meta">
                  <span>{highlightedFriend}</span>
                  <span>{topPocket?.location_hint ?? "Libe Slope"}</span>
                  <span>{dashboard.weather.summary}</span>
                </div>
              </motion.div>

              <AnimatePresence>
                {showFriends ? (
                  <motion.div
                    className="friends-panel"
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -12 }}
                  >
                    <div className="panel-heading">
                      <div>
                        <p className="eyebrow">Connected network</p>
                        <h3>Friends attached to your schedule</h3>
                      </div>
                      <span className="badge">{connectedFriends.length} windows</span>
                    </div>
                    <div className="friend-grid">
                      {connectedFriends.map((friend) => (
                        <div className="friend-card" key={friend.id}>
                          <strong>{friend.name}</strong>
                          <span>
                            {formatTime(friend.startAt)} to {formatTime(friend.endAt)}
                          </span>
                          <p>{friend.locationHint}</p>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                ) : null}
              </AnimatePresence>
            </section>

            <section className="classes-panel">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">Classes</p>
                  <h3>Add classes, assignments, and syllabus uploads</h3>
                </div>
                <span className="badge warm">{managedClasses.length} tracked</span>
              </div>

              <div className="class-rail">
                <div>
                  <span>Primary course</span>
                  <strong>{dashboard.course.code}</strong>
                </div>
                <div>
                  <span>Assignments loaded</span>
                  <strong>{dashboard.assignments.length}</strong>
                </div>
                <div>
                  <span>Protocol target</span>
                  <strong>{topPocket?.claimability ?? "Live"}</strong>
                </div>
              </div>

              <div className="class-grid">
                <aside className="class-list">
                  {managedClasses.map((course) => (
                    <button
                      className={selectedClass?.id === course.id ? "class-list-item active" : "class-list-item"}
                      key={course.id}
                      onClick={() => setSelectedClassId(course.id)}
                      type="button"
                    >
                      <strong>{course.code}</strong>
                      <span>{course.name}</span>
                    </button>
                  ))}
                </aside>

                {selectedClass ? (
                  <div className="class-detail">
                    <div className="class-summary">
                      <div>
                        <p className="eyebrow">Selected class</p>
                        <h3>
                          {selectedClass.code}: {selectedClass.name}
                        </h3>
                      </div>
                      <label className="upload-button">
                        {isUploading === selectedClass.id ? "Uploading syllabus..." : "Upload syllabus"}
                        <input
                          accept=".pdf,.txt,.doc,.docx"
                          hidden
                          onChange={(event) => {
                            const file = event.target.files?.[0];
                            if (file) {
                              void handleSyllabusUpload(selectedClass.id, file);
                            }
                            event.target.value = "";
                          }}
                          type="file"
                        />
                      </label>
                    </div>

                    <div className="syllabus-meta">
                      <span>{selectedClass.syllabusFileName ?? "No syllabus uploaded yet"}</span>
                    </div>

                    <div className="assignment-form">
                      <input
                        onChange={(event) =>
                          updateAssignmentDraft(selectedClass.id, "title", event.target.value)
                        }
                        placeholder="Assignment title"
                        type="text"
                        value={assignmentDrafts[selectedClass.id]?.title ?? ""}
                      />
                      <input
                        min="0"
                        onChange={(event) =>
                          updateAssignmentDraft(selectedClass.id, "historicalHours", event.target.value)
                        }
                        placeholder="Historical hours"
                        step="0.5"
                        type="number"
                        value={assignmentDrafts[selectedClass.id]?.historicalHours ?? ""}
                      />
                      <button className="primary-button" onClick={() => addAssignment(selectedClass.id)} type="button">
                        Add assignment
                      </button>
                    </div>

                    <div className="assignment-stack">
                      {selectedClass.assignments.map((assignment) => (
                        <div className="assignment-card" key={assignment.id}>
                          <div>
                            <strong>{assignment.title}</strong>
                            <span>Historical completion time</span>
                          </div>
                          <strong>{assignment.historicalHours} hrs</strong>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            </section>
          </motion.main>
        ) : (
          <motion.main
            key="schedule"
            className="schedule-page"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -18 }}
            transition={{ duration: 0.35 }}
          >
            <section className="schedule-shell">
              <div className="schedule-main">
                <div className="panel-heading schedule-header">
                  <div>
                    <p className="eyebrow">Page 2</p>
                    <h2>Reweave the day around a time block worth claiming</h2>
                  </div>
                  <div className="schedule-actions">
                    <button className="secondary-button" onClick={() => setShowTimeBlockModal(true)} type="button">
                      Add time block
                    </button>
                    <button className="primary-button" onClick={runFateweaver} type="button">
                      Fateweaver Protocol
                    </button>
                  </div>
                </div>

                <div className="timeblock-banner">
                  <strong>{timeBlockDraft?.label ?? topPocket?.title ?? "No custom time block selected"}</strong>
                  <span>
                    {timeBlockDraft
                      ? `${formatTime(new Date(timeBlockDraft.start).toISOString())} to ${formatTime(new Date(timeBlockDraft.end).toISOString())}`
                      : topPocket
                        ? `${formatTime(topPocket.start_at)} to ${formatTime(topPocket.end_at)}`
                        : "Add a block to direct the rewrite"}
                  </span>
                </div>

                <div className="schedule-layout">
                  <motion.div
                    animate={{ opacity: 1, scale: 1 }}
                    className="schedule-stage"
                    initial={{ opacity: 0, scale: 0.985 }}
                    transition={{ duration: 0.28 }}
                  >
                    <ScheduleCanvas blocks={optimizedBlocks} />
                  </motion.div>

                  <aside className="schedule-sidebar">
                    <div className="card">
                      <div className="panel-heading">
                        <div>
                          <p className="eyebrow">Rewoven logic</p>
                          <h3>{dashboard.shuffle_plan.tradeoff_statement}</h3>
                        </div>
                        <span className="badge">{showOptimized ? "Optimized" : "Original"}</span>
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
                  </aside>
                </div>
              </div>

              <aside className="stats-dock">
                <div className="card debt-card">
                  <div className="panel-heading">
                    <div>
                      <p className="eyebrow">Bottom-left stats</p>
                      <h3>{dashboard.ledger.interest_drag_hours} debt hours</h3>
                    </div>
                    <span className="badge warm">{dashboard.ledger.work_debt_score} score</span>
                  </div>
                  <div className="meter-track">
                    <motion.div
                      animate={{ width: `${Math.min(dashboard.ledger.work_debt_score, 100)}%` }}
                      className="meter-fill"
                      initial={{ width: 0 }}
                      transition={{ duration: 0.7 }}
                    />
                  </div>
                  <div className="mini-stats">
                    <div>
                      <span>Total load</span>
                      <strong>{dashboard.ledger.total_hours} hrs</strong>
                    </div>
                    <div>
                      <span>Focus today</span>
                      <strong>{dashboard.ledger.focus_hours_today} hrs</strong>
                    </div>
                    <div>
                      <span>Readiness</span>
                      <strong>{dashboard.social_readiness.score}%</strong>
                    </div>
                  </div>
                </div>
              </aside>
            </section>
          </motion.main>
        )}
      </AnimatePresence>

      <Modal onClose={() => setShowAuthModal(false)} open={showAuthModal} title="Sign up or log in">
        <div className="modal-form">
          <input placeholder="Cornell email" type="email" />
          <input placeholder="Password" type="password" />
          <button className="primary-button" type="button">
            Continue
          </button>
        </div>
      </Modal>

      <Modal onClose={() => setShowAddClassModal(false)} open={showAddClassModal} title="Add a class">
        <div className="modal-form">
          <input
            onChange={(event) => setNewClassName(event.target.value)}
            placeholder="Class name"
            type="text"
            value={newClassName}
          />
          <button className="primary-button" onClick={addClass} type="button">
            Save class
          </button>
        </div>
      </Modal>

      <Modal onClose={() => setShowTimeBlockModal(false)} open={showTimeBlockModal} title="Add a target time block">
        <div className="modal-form">
          <input
            onChange={(event) => setTimeBlockForm((current) => ({ ...current, label: event.target.value }))}
            placeholder="Time block name"
            type="text"
            value={timeBlockForm.label}
          />
          <input
            onChange={(event) => setTimeBlockForm((current) => ({ ...current, start: event.target.value }))}
            type="datetime-local"
            value={timeBlockForm.start}
          />
          <input
            onChange={(event) => setTimeBlockForm((current) => ({ ...current, end: event.target.value }))}
            type="datetime-local"
            value={timeBlockForm.end}
          />
          <button
            className="primary-button"
            onClick={() => {
              setTimeBlockDraft(timeBlockForm);
              setShowTimeBlockModal(false);
            }}
            type="button"
          >
            Use time block
          </button>
        </div>
      </Modal>

      {parseResult ? (
        <div className="parse-toast">
          <span className="badge warm">{parseResult.parser_mode}</span>
          <strong>
            Parsed {parseResult.course.code}: {parseResult.course.title}
          </strong>
          <p>{parseResult.notes}</p>
        </div>
      ) : null}

      <Modal open={showAddFriend} title="Add a Friend" onClose={() => setShowAddFriend(false)}>
        <form onSubmit={handleAddFriendSubmit}>
          <div className="modal-form-stack">
            <input
              type="text"
              placeholder="Friend's name"
              value={friendName}
              onChange={(e) => setFriendName(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Home zone (e.g. Collegetown)"
              value={friendZone}
              onChange={(e) => setFriendZone(e.target.value)}
              required
            />
            <button className="primary-button" type="submit" disabled={isAddingFriend}>
              {isAddingFriend ? "Adding..." : "Add Friend"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
