'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/ProtectedRoute'
import Navigation from '@/components/Navigation'
import ThumbsRating from '@/components/ThumbsRating'
import { LessonPlan } from '@/types/lesson'

export default function DashboardPage() {
  const [topic, setTopic] = useState('')
  const [grade, setGrade] = useState('')
  const [duration, setDuration] = useState(60)
  const [showAgentThoughts, setShowAgentThoughts] = useState(false)
  const [loading, setLoading] = useState(false)
  const [lessonPlan, setLessonPlan] = useState<LessonPlan | null>(null)
  const [error, setError] = useState('')
  const [submittingRating, setSubmittingRating] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [revising, setRevising] = useState(false)
  const [viewingRevision, setViewingRevision] = useState(false)

  const { user } = useAuth()
  const router = useRouter()

  const generateLessonPlan = async () => {
    if (!topic || !grade) {
      setError('Please fill in both topic and grade level')
      return
    }

    if (!duration || duration <= 0 || duration > 60) {
      setError('Duration must be between 1 and 60 minutes')
      return
    }

    setLoading(true)
    setError('')
    setLessonPlan(null)

    try {
      // Get the user's session token
      const { data: { session } } = await import('@/lib/supabase').then(({ supabase }) => 
        supabase.auth.getSession()
      )

      if (!session?.access_token) {
        setError('Please sign in again to generate lessons')
        return
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${apiUrl}/api/lessons/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          topic,
          grade,
          duration,
          show_agent_thoughts: showAgentThoughts
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to generate lesson plan')
      }

      const data = await response.json()
      setLessonPlan(data)
      
    } catch (err: any) {
      setError(err.message || 'An error occurred while generating the lesson plan')
    } finally {
      setLoading(false)
    }
  }

  const submitRating = async (rating: boolean) => {
    if (!lessonPlan) return

    setSubmittingRating(true)

    try {
      // Get the user's session token
      const { data: { session } } = await import('@/lib/supabase').then(({ supabase }) => 
        supabase.auth.getSession()
      )

      if (!session?.access_token) {
        setError('Please sign in again to submit rating')
        return
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${apiUrl}/api/lessons/${lessonPlan.id}/rating`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          rating
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to submit rating')
      }

      // Update the lesson plan with the new rating
      setLessonPlan({
        ...lessonPlan,
        user_rating: rating
      })
      
    } catch (err: any) {
      setError(err.message || 'An error occurred while submitting your rating')
    } finally {
      setSubmittingRating(false)
    }
  }

  const reviseLessonPlan = async () => {
    if (!feedback.trim()) {
      setError('Please provide feedback for revision')
      return
    }
    
    if (!lessonPlan) {
      setError('No lesson plan to revise')
      return
    }
    
    setRevising(true)
    setError('')
    
    try {
      // Get the user's session token
      const { data: { session } } = await import('@/lib/supabase').then(({ supabase }) => 
        supabase.auth.getSession()
      )

      if (!session?.access_token) {
        setError('Please sign in again to revise lesson')
        return
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      const response = await fetch(`${apiUrl}/api/lessons/${lessonPlan.id}/revise`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({ feedback })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to revise lesson plan')
      }

      const revisedLesson = await response.json()
      setLessonPlan(revisedLesson)
      setViewingRevision(true)
      setFeedback('')
      
    } catch (err: any) {
      setError(err.message || 'An error occurred while revising the lesson plan')
    } finally {
      setRevising(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navigation />

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="flex flex-col lg:flex-row gap-8">
              
              {/* Input Form */}
              <div className={`bg-white shadow rounded-lg p-6 transition-all duration-500 ${
                lessonPlan 
                  ? 'lg:w-80 lg:flex-shrink-0' 
                  : 'lg:w-1/2'
              }`}>
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  Generate Lesson Plan
                </h2>
                
                <form onSubmit={(e) => { e.preventDefault(); generateLessonPlan(); }} className="space-y-4">
                  <div>
                    <label htmlFor="topic" className="block text-sm font-medium text-gray-700">
                      Lesson Topic
                    </label>
                    <input
                      type="text"
                      id="topic"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      placeholder="e.g., Photosynthesis, Fractions, World War II"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
                      required
                    />
                  </div>

                  <div>
                    <label htmlFor="grade" className="block text-sm font-medium text-gray-700">
                      Grade Level
                    </label>
                    <select
                      id="grade"
                      value={grade}
                      onChange={(e) => setGrade(e.target.value)}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
                      required
                    >
                      <option value="">Select grade level</option>
                      <option value="K">Kindergarten</option>
                      <option value="1">1st Grade</option>
                      <option value="2">2nd Grade</option>
                      <option value="3">3rd Grade</option>
                      <option value="4">4th Grade</option>
                      <option value="5">5th Grade</option>
                      <option value="6">6th Grade</option>
                      <option value="7">7th Grade</option>
                      <option value="8">8th Grade</option>
                      <option value="9">9th Grade</option>
                      <option value="10">10th Grade</option>
                      <option value="11">11th Grade</option>
                      <option value="12">12th Grade</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="duration" className="block text-sm font-medium text-gray-700">
                      Duration (minutes)
                    </label>
                    <input
                      type="number"
                      id="duration"
                      value={duration}
                      onChange={(e) => setDuration(parseInt(e.target.value))}
                      min="15"
                      max="180"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      id="show-thoughts"
                      type="checkbox"
                      checked={showAgentThoughts}
                      onChange={(e) => setShowAgentThoughts(e.target.checked)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label htmlFor="show-thoughts" className="ml-2 block text-sm text-gray-900">
                      Show AI reasoning (agent thoughts)
                    </label>
                  </div>

                  {error && (
                    <div className="rounded-md bg-red-50 p-4">
                      <div className="text-sm text-red-700">{error}</div>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    {loading ? 'Generating...' : 'Generate Lesson Plan'}
                  </button>
                </form>
              </div>

              {/* Results */}
              <div className="bg-white shadow rounded-lg p-6 flex-1">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  Generated Lesson Plan
                </h2>

                {loading && (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    <span className="ml-2 text-gray-600">Creating your lesson plan...</span>
                  </div>
                )}

                {lessonPlan && (
                  <div className="space-y-6">
                    {/* Feedback Section - Always at the top */}
                    <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                      <h4 className="font-semibold text-amber-900 mb-3">
                        💡 Want to improve this lesson?
                      </h4>
                      <textarea
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="What would you like to improve? (e.g., 'Add more hands-on activities', 'Make it more challenging', 'Include group work', 'Simplify the language')"
                        className="w-full p-3 border border-amber-300 rounded-md resize-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                        rows={3}
                        disabled={revising}
                      />
                      <button
                        onClick={reviseLessonPlan}
                        disabled={!feedback.trim() || revising}
                        className="mt-3 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-md transition-colors"
                      >
                        {revising ? (
                          <>
                            <span className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                            Creating revision...
                          </>
                        ) : (
                          'Get Revised Version'
                        )}
                      </button>
                    </div>

                    {/* Version Toggle (only show if revision exists) - Now below feedback */}
                    {lessonPlan.revised_plan_json && (
                      <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold text-green-900">
                            ✨ Revision Available
                          </h4>
                          <div className="flex gap-2">
                            <button
                              onClick={() => setViewingRevision(false)}
                              className={`px-3 py-1 rounded text-sm font-medium ${
                                !viewingRevision 
                                  ? 'bg-green-600 text-white' 
                                  : 'bg-white text-green-600 border border-green-600'
                              }`}
                            >
                              Original
                            </button>
                            <button
                              onClick={() => setViewingRevision(true)}
                              className={`px-3 py-1 rounded text-sm font-medium ${
                                viewingRevision 
                                  ? 'bg-green-600 text-white' 
                                  : 'bg-white text-green-600 border border-green-600'
                              }`}
                            >
                              Revised
                            </button>
                          </div>
                        </div>
                        {viewingRevision && lessonPlan.revision_feedback && (
                          <p className="text-sm text-green-700 mt-2">
                            <strong>Your feedback:</strong> "{lessonPlan.revision_feedback}"
                          </p>
                        )}
                      </div>
                    )}

                    {/* Display current lesson plan (original or revised) */}
                    <div>
                      {(() => {
                        const currentPlan = viewingRevision && lessonPlan.revised_plan_json 
                          ? lessonPlan.revised_plan_json 
                          : lessonPlan.plan_json
                        
                        return (
                          <>
                            <div>
                              <h3 className="text-xl font-bold text-gray-900">{currentPlan.title}</h3>
                              <p className="text-sm text-gray-600">
                                Duration: {lessonPlan.duration} minutes | Grade: {lessonPlan.grade}
                                {viewingRevision && <span className="ml-2 bg-green-100 text-green-800 px-2 py-1 rounded text-xs">Revised</span>}
                              </p>
                            </div>

                            {/* Learning Objectives */}
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">Learning Objectives</h4>
                              <ul className="list-disc list-inside space-y-1">
                                {currentPlan.objectives.map((objective, index) => (
                                  <li key={index} className="text-gray-700">{objective}</li>
                                ))}
                              </ul>
                            </div>

                            {/* Lesson Structure */}
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">Lesson Structure</h4>
                              <div className="space-y-2">
                                <div>
                                  <span className="font-medium">Introduction:</span>
                                  <p className="text-gray-700">{currentPlan.structure.introduction}</p>
                                </div>
                                <div>
                                  <span className="font-medium">Main Activity:</span>
                                  <p className="text-gray-700">{currentPlan.structure.main_activity}</p>
                                </div>
                                <div>
                                  <span className="font-medium">Assessment:</span>
                                  <p className="text-gray-700">{currentPlan.structure.assessment}</p>
                                </div>
                              </div>
                            </div>

                            {/* Resources */}
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">Resources</h4>
                              <div className="space-y-2">
                                {currentPlan.resources.map((resource, index) => (
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
                          </>
                        )
                      })()}
                    </div>

                    {lessonPlan.agent_thoughts && showAgentThoughts && (
                      <div className="bg-blue-50 rounded-lg p-4">
                        <h4 className="font-semibold text-blue-900 mb-3">🤖 Pedagogical Reasoning</h4>
                        <div className="space-y-3 text-sm text-blue-800">
                          <div>
                            <p className="font-medium text-blue-900">Why These Objectives:</p>
                            <p>{lessonPlan.agent_thoughts.objectives_rationale}</p>
                          </div>
                          <div>
                            <p className="font-medium text-blue-900">Why This Structure:</p>
                            <p>{lessonPlan.agent_thoughts.structure_rationale}</p>
                          </div>
                          <div>
                            <p className="font-medium text-blue-900">Why This Activity Approach:</p>
                            <p>{lessonPlan.agent_thoughts.activity_rationale}</p>
                          </div>
                          <div>
                            <p className="font-medium text-blue-900">Why This Assessment:</p>
                            <p>{lessonPlan.agent_thoughts.assessment_rationale}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Rating Section - Keep existing */}
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <h4 className="font-semibold text-blue-900 mb-3">
                        Was this lesson plan helpful?
                      </h4>
                      <div className="flex items-center justify-between">
                        <div>
                          <ThumbsRating
                            rating={lessonPlan.user_rating ?? null}
                            onRatingChange={submitRating}
                            readonly={submittingRating}
                          />
                          {submittingRating && (
                            <p className="text-sm text-gray-600 mt-2">Submitting feedback...</p>
                          )}
                          {typeof lessonPlan.user_rating === 'boolean' && (
                            <p className="text-sm text-green-700 mt-2">Thank you for your feedback!</p>
                          )}
                        </div>
                        {typeof lessonPlan.user_rating !== 'boolean' && (
                          <p className="text-sm text-gray-600">
                            Your feedback helps us improve
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {!loading && !lessonPlan && (
                  <div className="text-center py-12 text-gray-500">
                    Enter a topic and grade level to generate your lesson plan
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}