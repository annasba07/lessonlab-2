export interface LessonPlan {
  id: string
  user_id: string
  title?: string
  topic: string
  grade: string
  duration: number
  plan_json: {
    title: string
    objectives: string[]
    structure: {
      introduction: string
      main_activity: string
      assessment: string
      timing: string
    }
    resources: Array<{
      title: string
      type: string
      url: string
      score: number
      reasoning: string
    }>
    materials_needed: string[]
    differentiation: string
  }
  agent_thoughts?: {
    objectives_rationale: string
    structure_rationale: string
    activity_rationale: string
    assessment_rationale: string
  }
  evaluation?: any  // Background evaluation results
  generation_metadata?: any  // AI generation metadata
  // NEW: Revision fields
  revised_plan_json?: {
    title: string
    objectives: string[]
    structure: {
      introduction: string
      main_activity: string
      assessment: string
      timing: string
    }
    resources: Array<{
      title: string
      type: string
      url: string
      score: number
      reasoning: string
    }>
    materials_needed: string[]
    differentiation: string
  }
  revision_feedback?: string
  revision_metadata?: any
  current_revision_number?: number
  user_rating?: boolean
  created_at: string
  updated_at: string
}

export interface LessonRevision {
  id: string
  lesson_id: string
  revision_number: number
  revised_plan_json: {
    title: string
    objectives: string[]
    structure: {
      introduction: string
      main_activity: string
      assessment: string
      timing: string
    }
    resources: Array<{
      title: string
      type: string
      url: string
      score: number
      reasoning: string
    }>
    materials_needed: string[]
    differentiation: string
  }
  revision_feedback: string
  revision_metadata?: any
  created_at: string
} 