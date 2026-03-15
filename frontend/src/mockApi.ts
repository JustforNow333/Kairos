import type {
  DashboardResponse,
  ParseResponse,
  UserAssumptions,
} from "./types";

function isoToday(hour: number, minute = 0): string {
  const value = new Date();
  value.setHours(hour, minute, 0, 0);
  return value.toISOString();
}

const baseDashboard: DashboardResponse = {
  generated_at: new Date().toISOString(),
  tagline: "Live the life you planned, not the one you fell into.",
  assumptions: {
    reading_speed_pph: 26,
    major_difficulty_multiplier: 1.15,
    historical_productivity_multiplier: 0.92,
    social_readiness_goal_hours: 7,
  },
  weather: {
    summary: "Clear over Libe Slope with the kind of cold that still feels social.",
    condition: "clear",
    temperature_f: 58,
  },
  course: {
    code: "CS 3110",
    title: "Data Structures and Functional Programming",
  },
  assignments: [
    {
      id: "a1",
      course_code: "CS 3110",
      title: "Problem Set 4",
      task_type: "pset",
      due_at: isoToday(23, 0),
      base_effort_hours: 6.5,
      estimated_weight: 5,
      reading_pages: 0,
      status: "pending",
    },
    {
      id: "a2",
      course_code: "INFO 1300",
      title: "Studio Critique Prep",
      task_type: "essay",
      due_at: isoToday(18, 30),
      base_effort_hours: 3,
      estimated_weight: 3,
      reading_pages: 0,
      status: "in_progress",
    },
    {
      id: "a3",
      course_code: "ECON 1110",
      title: "Behavioral Econ Reading",
      task_type: "reading",
      due_at: isoToday(20, 0),
      base_effort_hours: 1.5,
      estimated_weight: 2,
      reading_pages: 42,
      status: "pending",
    },
  ],
  ledger: {
    work_debt_score: 72,
    total_hours: 11,
    interest_drag_hours: 3.8,
    focus_hours_today: 5.5,
    summary: "You still have a believable path, but only if flexible work is compressed before evening drift takes over.",
    items: [
      {
        assignment_id: "a1",
        title: "Problem Set 4",
        adjusted_effort_hours: 6.8,
        interest_multiplier: 1.45,
        debt_contribution: 39,
        due_at: isoToday(23, 0),
      },
      {
        assignment_id: "a2",
        title: "Studio Critique Prep",
        adjusted_effort_hours: 2.9,
        interest_multiplier: 1.2,
        debt_contribution: 18,
        due_at: isoToday(18, 30),
      },
      {
        assignment_id: "a3",
        title: "Behavioral Econ Reading",
        adjusted_effort_hours: 1.7,
        interest_multiplier: 1.08,
        debt_contribution: 9,
        due_at: isoToday(20, 0),
      },
    ],
  },
  social_readiness: {
    score: 82,
    weekly_target_hours: 7,
    projected_hours: 5.8,
    gap_hours: 1.2,
    status: "behind",
    summary: "One reclaimed social window tonight keeps the week from collapsing into pure academic recovery mode.",
  },
  friends: [
    {
      friend_id: "f1",
      friend_name: "Maya",
      windows: [
        { start_at: isoToday(17, 5), end_at: isoToday(18, 5), location_hint: "Libe Slope" },
      ],
    },
    {
      friend_id: "f2",
      friend_name: "Jonah",
      windows: [
        { start_at: isoToday(17, 10), end_at: isoToday(18, 10), location_hint: "Libe Slope" },
      ],
    },
    {
      friend_id: "f3",
      friend_name: "Sana",
      windows: [
        { start_at: isoToday(17, 15), end_at: isoToday(18, 0), location_hint: "Libe Slope" },
      ],
    },
  ],
  pockets: [
    {
      id: "p1",
      start_at: isoToday(17, 10),
      end_at: isoToday(18, 0),
      title: "Sunset on the Slope",
      location_hint: "Libe Slope",
      friend_names: ["Maya", "Jonah", "Sana"],
      score: 92,
      claimability: "High",
      why_now: "Three friends are already aligned and the walk from your current block is realistic if you compress work now.",
      activity_suggestion: "Take the slope loop and reset before evening work.",
      day_phase: "Golden hour",
      weather_label: "Clear",
      emotional_hook: "This is the kind of Cornell hour people remember later and wonder why they almost missed.",
    },
  ],
  current_schedule: [
    {
      id: "b1",
      label: "Algo lecture",
      block_type: "class",
      start_at: isoToday(9, 5),
      end_at: isoToday(10, 20),
      movable: false,
      intensity: 1,
    },
    {
      id: "b2",
      label: "Problem Set 4 focus sprint",
      block_type: "work",
      start_at: isoToday(15, 50),
      end_at: isoToday(17, 5),
      movable: true,
      intensity: 1,
    },
    {
      id: "b3",
      label: "Duffield reset",
      block_type: "meal",
      start_at: isoToday(14, 55),
      end_at: isoToday(15, 20),
      movable: true,
      intensity: 0.8,
    },
    {
      id: "b4",
      label: "Reading block",
      block_type: "work",
      start_at: isoToday(18, 15),
      end_at: isoToday(19, 0),
      movable: true,
      intensity: 0.9,
    },
  ],
  shuffle_plan: {
    before_blocks: [
      {
        id: "sb1",
        label: "Problem Set 4 focus sprint",
        block_type: "work",
        start_at: isoToday(15, 50),
        end_at: isoToday(17, 5),
        movable: true,
        intensity: 1,
      },
      {
        id: "sb2",
        label: "Reading block",
        block_type: "work",
        start_at: isoToday(18, 15),
        end_at: isoToday(19, 0),
        movable: true,
        intensity: 0.9,
      },
    ],
    after_blocks: [
      {
        id: "sa1",
        label: "Problem Set 4 sprint",
        block_type: "work",
        start_at: isoToday(15, 30),
        end_at: isoToday(16, 35),
        movable: true,
        intensity: 1,
      },
      {
        id: "sa2",
        label: "Sunset on the Slope",
        block_type: "social",
        start_at: isoToday(17, 10),
        end_at: isoToday(18, 0),
        movable: false,
        intensity: 0.82,
      },
      {
        id: "sa3",
        label: "Reading block",
        block_type: "work",
        start_at: isoToday(20, 0),
        end_at: isoToday(20, 45),
        movable: true,
        intensity: 0.72,
      },
    ],
    target_pocket_id: "p1",
    tradeoff_statement: "Compress the pset now, shift reading later, and the social window becomes cleanly claimable.",
    focus_boost_multiplier: 1.15,
    unlocked_minutes: 50,
  },
  idle_alert: {
    headline: "You can still make the slope if you move now.",
    action: "Put the current drift on pause, finish one sharp sprint, and leave before the window decays.",
    social_readiness_gap_hours: 1.2,
    friend_names: ["Maya", "Jonah", "Sana"],
    target_pocket_id: "p1",
  },
};

let dashboardState: DashboardResponse = structuredClone(baseDashboard);

function wait(ms = 180): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

export async function fetchMockDashboard(): Promise<DashboardResponse> {
  await wait();
  return structuredClone(dashboardState);
}

export async function uploadMockSyllabus(file: File): Promise<ParseResponse> {
  await wait();

  const course = {
    code: "ENGRD 2700",
    title: file.name.replace(/\.[^/.]+$/, "") || "Uploaded Course",
  };

  const assignments = [
    {
      id: "mock-upload-1",
      course_code: course.code,
      title: "Syllabus-derived problem set",
      task_type: "pset" as const,
      due_at: isoToday(21, 0),
      base_effort_hours: 4,
      estimated_weight: 4,
      reading_pages: 0,
      status: "pending" as const,
    },
    {
      id: "mock-upload-2",
      course_code: course.code,
      title: "Syllabus-derived reading",
      task_type: "reading" as const,
      due_at: isoToday(19, 30),
      base_effort_hours: 1.5,
      estimated_weight: 2,
      reading_pages: 35,
      status: "pending" as const,
    },
  ];

  const ledger = {
    ...dashboardState.ledger,
    work_debt_score: 68,
    items: assignments.map((assignment, index) => ({
      assignment_id: assignment.id,
      title: assignment.title,
      adjusted_effort_hours: assignment.base_effort_hours,
      interest_multiplier: 1.12 + index * 0.08,
      debt_contribution: 14 + index * 8,
      due_at: assignment.due_at,
    })),
  };

  dashboardState = {
    ...dashboardState,
    course,
    assignments,
    ledger,
    generated_at: new Date().toISOString(),
  };

  return {
    course,
    assignments,
    ledger,
    parser_mode: "mock",
    notes: "Using local mock syllabus parsing so the frontend can run without the FastAPI backend.",
  };
}

export async function putMockUserAssumptions(assumptions: UserAssumptions): Promise<{ status: string }> {
  await wait(120);
  dashboardState = {
    ...dashboardState,
    assumptions,
    generated_at: new Date().toISOString(),
  };
  return { status: "ok" };
}

export function getMockGoogleOAuthUrl(): string {
  return "#mock-google-oauth";
}

export async function syncMockGoogleCalendar(): Promise<{ status: string; blocks_synced: number; mode: string }> {
  await wait(220);
  return { status: "ok", blocks_synced: 4, mode: "mock" };
}

export async function addMockFriend(friendName: string, homeZone: string): Promise<{ status: string; friend_id: string }> {
  await wait(120);
  const friendId = `mock-friend-${Date.now()}`;
  dashboardState = {
    ...dashboardState,
    friends: [
      ...dashboardState.friends,
      {
        friend_id: friendId,
        friend_name: friendName,
        windows: [
          {
            start_at: isoToday(20, 0),
            end_at: isoToday(21, 0),
            location_hint: homeZone,
          },
        ],
      },
    ],
    generated_at: new Date().toISOString(),
  };
  return { status: "ok", friend_id: friendId };
}
