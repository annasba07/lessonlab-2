'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/ProtectedRoute'
import Navigation from '@/components/Navigation'
import ThumbsRating from '@/components/ThumbsRating'

interface LessonPlan {
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
    objectives_reasoning: string
    structure_reasoning: string
    resources_reasoning: string
  }
  user_rating?: boolean
  created_at: string
  updated_at: string
}

export default function MyLessonsPage() {
  const [lessons, setLessons] = useState<LessonPlan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedLesson, setSelectedLesson] = useState<LessonPlan | null>(null)

  const { user } = useAuth()

  useEffect(() => {
    fetchLessons()
  }, [])

  const fetchLessons = async () => {
    setLoading(true)
    setError('')

    try {
      // Get the user's session token
      const { data: { session } } = await import('@/lib/supabase').then(({ supabase }) => 
        supabase.auth.getSession()
      )

      if (!session?.access_token) {
        setError('Please sign in again to view your lessons')
        return
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${apiUrl}/api/lessons/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch lessons')
      }

      const data = await response.json()
      setLessons(data.sort((a: LessonPlan, b: LessonPlan) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ))
      
    } catch (err: any) {
      setError(err.message || 'An error occurred while fetching your lessons')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const closeModal = () => {
    setSelectedLesson(null)
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navigation />

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900">My Lessons</h1>
              <p className="text-gray-600">View and manage your saved lesson plans</p>
            </div>

            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <span className="ml-2 text-gray-600">Loading your lessons...</span>
              </div>
            )}

            {error && (
              <div className="rounded-md bg-red-50 p-4 mb-6">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            {!loading && !error && lessons.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-500 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No lessons yet</h3>
                <p className="text-gray-600 mb-4">Create your first lesson plan to get started!</p>
                <a
                  href="/dashboard"
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Generate Lesson Plan
                </a>
              </div>
            )}

            {!loading && lessons.length > 0 && (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {lessons.map((lesson) => (
                  <div key={lesson.id} className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <div className="mb-4">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {lesson.title}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        Topic: {lesson.topic}
                      </p>
                      <p className="text-sm text-gray-600">
                        Grade: {lesson.grade} | Duration: {lesson.duration} min
                      </p>
                    </div>

                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Objectives:</h4>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {lesson.plan_json.objectives.slice(0, 2).map((objective, index) => (
                          <li key={index} className="truncate">• {objective}</li>
                        ))}
                        {lesson.plan_json.objectives.length > 2 && (
                          <li className="text-gray-500 italic">
                            +{lesson.plan_json.objectives.length - 2} more...
                          </li>
                        )}
                      </ul>
                    </div>

                    {lesson.user_rating !== undefined && (
                      <div className="mb-3">
                        <ThumbsRating
                          rating={lesson.user_rating}
                          readonly={true}
                          size="sm"
                          showLabel={false}
                        />
                      </div>
                    )}

                    <div className="flex justify-between items-center">
                      <p className="text-xs text-gray-500">
                        Created: {formatDate(lesson.created_at)}
                      </p>
                      <button
                        onClick={() => setSelectedLesson(lesson)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded text-sm font-medium"
                      >
                        View Full
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>

        {/* Full Lesson Modal */}
        {selectedLesson && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-2xl font-bold text-gray-900">
                  {selectedLesson.plan_json.title}
                </h3>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>

              <div className="max-h-96 overflow-y-auto space-y-6">
                <div>
                  <p className="text-sm text-gray-600 mb-4">
                    Duration: {selectedLesson.duration} minutes | Grade: {selectedLesson.grade}
                  </p>
                  {selectedLesson.user_rating !== undefined && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Your Feedback:</h4>
                      <ThumbsRating
                        rating={selectedLesson.user_rating}
                        readonly={true}
                        size="md"
                      />
                    </div>
                  )}
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Learning Objectives</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {selectedLesson.plan_json.objectives.map((objective, index) => (
                      <li key={index} className="text-gray-700">{objective}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Lesson Structure</h4>
                  <div className="space-y-2">
                    <div>
                      <span className="font-medium">Introduction:</span>
                      <p className="text-gray-700">{selectedLesson.plan_json.structure.introduction}</p>
                    </div>
                    <div>
                      <span className="font-medium">Main Activity:</span>
                      <p className="text-gray-700">{selectedLesson.plan_json.structure.main_activity}</p>
                    </div>
                    <div>
                      <span className="font-medium">Assessment:</span>
                      <p className="text-gray-700">{selectedLesson.plan_json.structure.assessment}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Resources</h4>
                  <div className="space-y-2">
                    {selectedLesson.plan_json.resources.map((resource, index) => (
                      <div key={index} className="border rounded p-3">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium">{resource.title}</p>
                            <p className="text-sm text-gray-600">{resource.type}</p>
                          </div>
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                            Score: {resource.score}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mt-1">{resource.reasoning}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {selectedLesson.agent_thoughts && (
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-900 mb-2">🤖 AI Reasoning</h4>
                    <div className="space-y-2 text-sm text-blue-800">
                      <p><strong>Objectives:</strong> {selectedLesson.agent_thoughts.objectives_reasoning}</p>
                      <p><strong>Structure:</strong> {selectedLesson.agent_thoughts.structure_reasoning}</p>
                      <p><strong>Resources:</strong> {selectedLesson.agent_thoughts.resources_reasoning}</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={closeModal}
                  className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}