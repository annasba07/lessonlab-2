'use client'

import { useState } from 'react'

interface ThumbsRatingProps {
  rating: boolean | null
  onRatingChange?: (rating: boolean) => void
  readonly?: boolean
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

export default function ThumbsRating({ 
  rating, 
  onRatingChange, 
  readonly = false, 
  size = 'md',
  showLabel = true 
}: ThumbsRatingProps) {
  const [hoveredRating, setHoveredRating] = useState<boolean | null>(null)

  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }

  const handleThumbClick = (selectedRating: boolean) => {
    if (!readonly && onRatingChange) {
      onRatingChange(selectedRating)
    }
  }

  const handleThumbHover = (selectedRating: boolean) => {
    if (!readonly) {
      setHoveredRating(selectedRating)
    }
  }

  const handleThumbLeave = () => {
    if (!readonly) {
      setHoveredRating(null)
    }
  }

  const getRatingLabel = (rating: boolean | null) => {
    if (rating === null) return 'No rating'
    return rating ? 'Helpful' : 'Not helpful'
  }

  const getDisplayState = (thumbType: 'up' | 'down') => {
    const isThumbUp = thumbType === 'up'
    const currentRating = hoveredRating !== null ? hoveredRating : rating
    
    if (currentRating === null) {
      return 'inactive'
    }
    
    if (currentRating === isThumbUp) {
      return 'active'
    }
    
    return 'inactive'
  }

  return (
    <div className="flex items-center space-x-3">
      <div className="flex items-center space-x-2">
        {/* Thumbs Up */}
        <button
          type="button"
          disabled={readonly}
          className={`${sizeClasses[size]} ${
            readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110 transition-all'
          } ${
            getDisplayState('up') === 'active'
              ? 'text-green-600'
              : 'text-gray-400 hover:text-green-500'
          }`}
          onClick={() => handleThumbClick(true)}
          onMouseEnter={() => handleThumbHover(true)}
          onMouseLeave={handleThumbLeave}
          title="Helpful"
        >
          <svg
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
          </svg>
        </button>

        {/* Thumbs Down */}
        <button
          type="button"
          disabled={readonly}
          className={`${sizeClasses[size]} ${
            readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110 transition-all'
          } ${
            getDisplayState('down') === 'active'
              ? 'text-red-600'
              : 'text-gray-400 hover:text-red-500'
          }`}
          onClick={() => handleThumbClick(false)}
          onMouseEnter={() => handleThumbHover(false)}
          onMouseLeave={handleThumbLeave}
          title="Not helpful"
        >
          <svg
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.106-1.79l-.05-.025A4 4 0 0011.057 2H5.641a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z" />
          </svg>
        </button>
      </div>
      
      {showLabel && (
        <span className={`text-sm ${
          readonly ? 'text-gray-600' : 'text-gray-700'
        }`}>
          {getRatingLabel(hoveredRating !== null ? hoveredRating : rating)}
        </span>
      )}
    </div>
  )
}