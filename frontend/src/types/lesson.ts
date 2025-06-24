export interface LessonPlan {
  id: string
  title: string
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
  user_rating?: boolean
  created_at: string
  updated_at: string
} 