/**
 * Meal Card Component
 * Beautiful card displaying meal information
 */
'use client';

import { Clock, DollarSign, Flame, TrendingUp } from 'lucide-react';
import type { Meal } from '@/lib/api';
import {
  formatPrice,
  getDietaryTagColor,
  formatDietaryTag,
  getMealCategoryIcon,
  cn,
} from '@/lib/utils';

interface MealCardProps {
  meal: Meal;
  onClick?: () => void;
  showDetails?: boolean;
}

export const MealCard = ({ meal, onClick, showDetails = false }: MealCardProps) => {
  const hasFallbackImage = !meal.image_url;
  const mealImage = meal.image_url || '/placeholder-meal.jpg';

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && onClick) {
      e.preventDefault();
      onClick();
    }
  };

  return (
    <div
      onClick={onClick}
      onKeyDown={handleKeyDown}
      tabIndex={onClick ? 0 : undefined}
      role={onClick ? 'button' : undefined}
      aria-label={onClick ? `View details for ${meal.name}` : undefined}
      className={cn(
        'card overflow-hidden transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-calo-primary',
        onClick && 'cursor-pointer card-hover'
      )}
    >
      {/* Image */}
      <div className="relative h-48 bg-gradient-to-br from-calo-primary/10 to-calo-secondary/10">
        {hasFallbackImage ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-6xl">
              {getMealCategoryIcon(meal.category)}
            </span>
          </div>
        ) : (
          <img
            src={mealImage}
            alt={meal.name}
            className="w-full h-full object-cover"
          />
        )}
        
        {/* Category Badge */}
        <div className="absolute top-3 left-3">
          <span className="badge badge-green backdrop-blur-sm bg-white/90">
            {getMealCategoryIcon(meal.category)} {meal.category}
          </span>
        </div>

        {/* Popularity */}
        {meal.popularity_score > 0.8 && (
          <div className="absolute top-3 right-3">
            <div className="w-10 h-10 rounded-full bg-calo-secondary/90 backdrop-blur-sm flex items-center justify-center shadow-lg">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Title */}
        <div>
          <h3 className="font-semibold text-lg text-calo-dark line-clamp-1">
            {meal.name}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-2 mt-1">
            {meal.description}
          </p>
        </div>

        {/* Dietary Tags */}
        <div className="flex flex-wrap gap-1.5">
          {meal.dietary_tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className={cn('badge text-xs', getDietaryTagColor(tag))}
            >
              {formatDietaryTag(tag)}
            </span>
          ))}
          {meal.dietary_tags.length > 3 && (
            <span className="badge badge-blue text-xs">
              +{meal.dietary_tags.length - 3}
            </span>
          )}
        </div>

        {/* Nutrition Info */}
        <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-red-50 flex items-center justify-center">
              <Flame className="w-4 h-4 text-red-500" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Calories</p>
              <p className="font-semibold text-sm text-calo-dark">
                {meal.nutrition.calories}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-blue-500" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Protein</p>
              <p className="font-semibold text-sm text-calo-dark">
                {meal.nutrition.protein}g
              </p>
            </div>
          </div>
        </div>

        {/* Details (if showDetails) */}
        {showDetails && (
          <>
            <div className="pt-2 border-t border-gray-100 space-y-2">
              <p className="text-xs text-gray-500">
                P: {meal.nutrition.protein}g • C: {meal.nutrition.carbs}g • F:{' '}
                {meal.nutrition.fats}g
              </p>
              {meal.nutrition.fiber && (
                <p className="text-xs text-gray-500">
                  Fiber: {meal.nutrition.fiber}g
                </p>
              )}
            </div>

            {meal.ingredients.length > 0 && (
              <div>
                <p className="text-xs font-medium text-gray-700 mb-1">
                  Ingredients:
                </p>
                <p className="text-xs text-gray-600">
                  {meal.ingredients.slice(0, 5).join(', ')}
                  {meal.ingredients.length > 5 && '...'}
                </p>
              </div>
            )}

            {meal.allergens.length > 0 && (
              <div>
                <p className="text-xs font-medium text-gray-700 mb-1">
                  Allergens:
                </p>
                <div className="flex flex-wrap gap-1">
                  {meal.allergens.map((allergen) => (
                    <span
                      key={allergen}
                      className="badge badge-red text-xs"
                    >
                      {allergen}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>{meal.preparation_time} min</span>
            </div>
            <div className="flex items-center gap-1">
              <DollarSign className="w-4 h-4" />
              <span className="font-semibold text-calo-dark">
                {formatPrice(meal.price)}
              </span>
            </div>
          </div>

          {onClick && (
            <span
              className="text-sm font-medium text-calo-primary hover:text-green-600 transition-colors"
              aria-hidden="true"
            >
              View Details →
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
