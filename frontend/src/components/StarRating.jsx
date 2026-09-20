import { useState } from "react";

/**
 * Estrellas dibujadas a mano (SVG propio, no un ícono de librería genérico)
 * para calificar un criterio de 1 a 5. Es el elemento visual central de la
 * app de evaluaciones, así que se le puso cuidado aparte.
 */
export default function StarRating({ value, onChange, label }) {
  const [hover, setHover] = useState(0);
  const shown = hover || value;

  return (
    <div className="star-rating">
      <span className="star-rating__label">{label}</span>
      <div className="star-rating__stars" role="radiogroup" aria-label={label}>
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            role="radio"
            aria-checked={value === n}
            aria-label={`${n} de 5`}
            className="star-rating__star"
            onMouseEnter={() => setHover(n)}
            onMouseLeave={() => setHover(0)}
            onClick={() => onChange(n)}
          >
            <svg viewBox="0 0 24 24" width="28" height="28">
              <path
                d="M12 2.6l2.86 5.94 6.44.77-4.72 4.5 1.24 6.53L12 17.3 6.18 20.34l1.24-6.53-4.72-4.5 6.44-.77z"
                fill={n <= shown ? "var(--color-accent)" : "none"}
                stroke={n <= shown ? "var(--color-accent)" : "var(--color-border)"}
                strokeWidth="1.5"
              />
            </svg>
          </button>
        ))}
      </div>
    </div>
  );
}
