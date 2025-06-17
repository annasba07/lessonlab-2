'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const topics = [
  'photosynthesis',
  'fractions',
  'World War II',
  'creative writing',
  'the solar system',
  'multiplication tables'
]

const lessonPreviews = {
  'photosynthesis': [
    '📚 Learning Objectives:',
    '• Explain how plants make food from sunlight',
    '• Identify parts of a leaf and their functions',
    '',
    '🔬 Main Activity:',
    '• Leaf dissection experiment',
    '• Light vs. dark plant observation'
  ],
  'fractions': [
    '📚 Learning Objectives:',
    '• Compare and order fractions',
    '• Add fractions with like denominators',
    '',
    '🎯 Main Activity:',
    '• Pizza fraction manipulatives',
    '• Fraction number line games'
  ],
  'World War II': [
    '📚 Learning Objectives:',
    '• Identify major events of WWII',
    '• Analyze causes and effects',
    '',
    '📖 Main Activity:',
    '• Timeline creation project',
    '• Primary source document analysis'
  ],
  'creative writing': [
    '📚 Learning Objectives:',
    '• Develop compelling characters',
    '• Use descriptive language effectively',
    '',
    '✍️ Main Activity:',
    '• Story starter prompts',
    '• Peer review workshops'
  ],
  'the solar system': [
    '📚 Learning Objectives:',
    '• Order planets by distance from sun',
    '• Compare planet characteristics',
    '',
    '🚀 Main Activity:',
    '• Scale model creation',
    '• Planet research presentations'
  ],
  'multiplication tables': [
    '📚 Learning Objectives:',
    '• Memorize facts through 12x12',
    '• Apply multiplication strategies',
    '',
    '🎮 Main Activity:',
    '• Math fact games',
    '• Array visualization exercises'
  ]
}

export default function TypingAnimation() {
  const [currentTopicIndex, setCurrentTopicIndex] = useState(0)
  const [displayedText, setDisplayedText] = useState('')
  const [isTyping, setIsTyping] = useState(true)
  const [showLesson, setShowLesson] = useState(false)
  const [lessonLines, setLessonLines] = useState<string[]>([])

  const currentTopic = topics[currentTopicIndex]

  useEffect(() => {
    const topic = topics[currentTopicIndex]
    let timeoutId: NodeJS.Timeout

    if (isTyping) {
      // Typing effect
      if (displayedText.length < topic.length) {
        timeoutId = setTimeout(() => {
          setDisplayedText(topic.slice(0, displayedText.length + 1))
        }, 100)
      } else {
        // Finished typing, show lesson preview
        setShowLesson(true)
        setLessonLines(lessonPreviews[topic as keyof typeof lessonPreviews] || [])
        
        // Wait before starting to delete
        timeoutId = setTimeout(() => {
          setIsTyping(false)
        }, 2000)
      }
    } else {
      // Deleting effect
      if (displayedText.length > 0) {
        timeoutId = setTimeout(() => {
          setDisplayedText(displayedText.slice(0, -1))
        }, 50)
      } else {
        // Finished deleting, move to next topic
        setShowLesson(false)
        setLessonLines([])
        setCurrentTopicIndex((prev) => (prev + 1) % topics.length)
        setIsTyping(true)
      }
    }

    return () => clearTimeout(timeoutId)
  }, [currentTopicIndex, displayedText, isTyping])

  return (
    <div className="max-w-4xl mx-auto my-16 p-8 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl shadow-lg">
      {/* Typing prompt */}
      <div className="text-center mb-8">
        <p className="text-xl text-gray-600 mb-4">
          Create a lesson about...
        </p>
        <div className="text-3xl font-bold text-indigo-600 min-h-[3rem] flex items-center justify-center">
          <span>{displayedText}</span>
          <motion.span
            animate={{ opacity: [1, 0, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="ml-1"
          >
            |
          </motion.span>
        </div>
      </div>

      {/* Lesson preview */}
      <AnimatePresence>
        {showLesson && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-white rounded-xl p-6 shadow-md"
          >
            <div className="text-sm text-gray-500 mb-4 text-center">
              ✨ Generating your lesson plan...
            </div>
            
            <div className="space-y-2 font-mono text-sm">
              {lessonLines.map((line, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.2 }}
                  className={`${
                    line.startsWith('📚') || line.startsWith('🔬') || line.startsWith('🎯') || 
                    line.startsWith('📖') || line.startsWith('✍️') || line.startsWith('🚀') || 
                    line.startsWith('🎮')
                      ? 'font-semibold text-indigo-600' 
                      : line.startsWith('•') 
                        ? 'text-gray-700 ml-4' 
                        : 'text-gray-600'
                  }`}
                >
                  {line || '\u00A0'}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}