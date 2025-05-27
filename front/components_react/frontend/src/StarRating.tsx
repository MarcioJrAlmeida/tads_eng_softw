import React, { useState } from 'react';
import './StarRating.css';

interface StarRatingProps {
  value: number;
  onChange: (value: number) => void;
}

const StarRating: React.FC<StarRatingProps> = ({ value, onChange }) => {
  const [hover, setHover] = useState<number | null>(null);

  const handleClick = (newValue: number) => {
    onChange(newValue);
  };

  const handleMouseMove = (
    event: React.MouseEvent<HTMLSpanElement, MouseEvent>,
    starIndex: number
  ) => {
    const { left, width } = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - left;
    const hoverValue = x < width / 2 ? starIndex - 0.5 : starIndex;
    setHover(hoverValue);
  };

  const handleMouseLeave = () => {
    setHover(null);
  };

  return (
    <div className="star-rating">
      {[...Array(5)].map((_, index) => {
        const starValue = index + 1;
        const displayValue = hover ?? value;

        return (
          <span
            key={index}
            className="star"
            onClick={(e) => {
              const { left, width } = e.currentTarget.getBoundingClientRect();
              const x = e.clientX - left;
              const newValue = x < width / 2 ? starValue - 0.5 : starValue;
              handleClick(newValue);
            }}
            onMouseMove={(e) => handleMouseMove(e, starValue)}
            onMouseLeave={handleMouseLeave}
          >
            {displayValue >= starValue
              ? '★'
              : displayValue >= starValue - 0.5
              ? '⯪' // meia estrela
              : '☆'}
          </span>
        );
      })}
    </div>
  );
};

export default StarRating;
