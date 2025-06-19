'use client'

import { useState } from 'react'

interface StarRatingProps {
  rating: number | null
  onRatingChange?: (rating: number) => void
  readonly?: boolean
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

export default function StarRating({ 
  rating, 
  onRatingChange, 
  readonly = false, 
  size = 'md',
  showLabel = true 
}: StarRatingProps) {
  const [hoveredRating, setHoveredRating] = useState<number | null>(null)

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }

  const handleStarClick = (selectedRating: number) => {
    if (!readonly && onRatingChange) {
      onRatingChange(selectedRating)
    }
  }

  const handleStarHover = (selectedRating: number) => {
    if (!readonly) {
      setHoveredRating(selectedRating)
    }
  }

  const handleStarLeave = () => {
    if (!readonly) {
      setHoveredRating(null)
    }
  }

  const displayRating = hoveredRating || rating || 0

  const getRatingLabel = (rating: number | null) => {
    if (!rating) return 'No rating'
    const labels = {
      1: 'Poor',
      2: 'Fair', 
      3: 'Good',
      4: 'Very Good',
      5: 'Excellent'
    }
    return labels[rating as keyof typeof labels] || 'No rating'
  }

  return (
    <div className="flex items-center space-x-2">
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            disabled={readonly}
            className={`${sizeClasses[size]} ${
              readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110 transition-transform'
            } ${
              star <= displayRating
                ? 'text-yellow-400'
                : 'text-gray-300'
            }`}
            onClick={() => handleStarClick(star)}
            onMouseEnter={() => handleStarHover(star)}
            onMouseLeave={handleStarLeave}
          >
            <svg
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fillRule="evenodd"
                d="M10 15.27L16.18 19l-1.64-7.03L20 7.24l-7.19-.61L10 0 7.19 6.63 0 7.24l5.46 4.73L3.82 19z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        ))}
      </div>
      
      {showLabel && (
        <span className={`text-sm ${
          readonly ? 'text-gray-600' : 'text-gray-700'
        }`}>
          {getRatingLabel(displayRating)}
          {rating && ` (${rating}/5)`}
        </span>
      )}
    </div>
  )
}