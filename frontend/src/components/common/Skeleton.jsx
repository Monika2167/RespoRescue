import React from "react";

export const Skeleton = ({ className = "", count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`animate-pulse bg-slate-800/60 rounded-lg ${className}`}
        />
      ))}
    </>
  );
};
