export type UserAssumptions = {
  reading_speed_pph: number;
  major_difficulty_multiplier: number;
  historical_productivity_multiplier: number;
  social_readiness_goal_hours: number;
};

export type Assignment = {
  id: string;
  course_code: string;
  title: string;
  task_type: "pset" | "reading" | "essay" | "lab" | "exam_prep";
  due_at: string;
  base_effort_hours: number;
  estimated_weight: number;
  reading_pages: number;
  status: "pending" | "in_progress" | "done";
};

export type WorkDebtItem = {
  assignment_id: string;
  title: string;
  adjusted_effort_hours: number;
  interest_multiplier: number;
  debt_contribution: number;
  due_at: string;
};

export type WorkDebtLedger = {
  work_debt_score: number;
  total_hours: number;
  interest_drag_hours: number;
  focus_hours_today: number;
  summary: string;
  items: WorkDebtItem[];
};

export type FriendAvailability = {
  friend_id: string;
  friend_name: string;
  windows: {
    start_at: string;
    end_at: string;
    location_hint: string;
  }[];
};

export type SocialPocket = {
  id: string;
  start_at: string;
  end_at: string;
  title: string;
  location_hint: string;
  friend_names: string[];
  score: number;
  claimability: string;
  why_now: string;
  activity_suggestion: string;
  day_phase: string;
  weather_label: string;
  emotional_hook: string;
};

export type ScheduleBlock = {
  id: string;
  label: string;
  block_type: "class" | "work" | "social" | "buffer" | "meal";
  start_at: string;
  end_at: string;
  movable: boolean;
  intensity: number;
};

export type ShufflePlan = {
  before_blocks: ScheduleBlock[];
  after_blocks: ScheduleBlock[];
  target_pocket_id: string;
  tradeoff_statement: string;
  focus_boost_multiplier: number;
  unlocked_minutes: number;
  tactics: string[];
  strategy_source: string;
};

export type IdleAlert = {
  headline: string;
  action: string;
  social_readiness_gap_hours: number;
  friend_names: string[];
  target_pocket_id: string;
};

export type SocialReadiness = {
  score: number;
  weekly_target_hours: number;
  projected_hours: number;
  gap_hours: number;
  status: string;
  summary: string;
};

export type WeatherContext = {
  summary: string;
  condition: string;
  temperature_f: number;
};

export type DashboardResponse = {
  generated_at: string;
  tagline: string;
  assumptions: UserAssumptions;
  weather: WeatherContext;
  course: {
    code: string;
    title: string;
  };
  assignments: Assignment[];
  ledger: WorkDebtLedger;
  social_readiness: SocialReadiness;
  friends: FriendAvailability[];
  pockets: SocialPocket[];
  current_schedule: ScheduleBlock[];
  shuffle_plan: ShufflePlan;
  idle_alert: IdleAlert;
};

export type ParseResponse = {
  course: {
    code: string;
    title: string;
  };
  assignments: Assignment[];
  ledger: WorkDebtLedger;
  parser_mode: string;
  notes: string;
};
