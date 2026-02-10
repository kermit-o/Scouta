'use client'
import React from 'react';

interface PremiumCardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
  hover?: boolean;
}

export const PremiumCard: React.FC<PremiumCardProps> = ({
  children,
  className = '',
  padding = 'md',
  hover = false
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  return (
    <div className={`
      bg-white/80 backdrop-blur-lg
      border border-white/20
      rounded-2xl
      shadow-2xl shadow-black/10
      ${paddingClasses[padding]}
      ${hover ? 'transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/20 hover:border-purple-300/30' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
};
