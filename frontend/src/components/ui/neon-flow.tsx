'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

// Helper for random colors
const randomColors = (count: number) => {
  return new Array(count)
    .fill(0)
    .map(
      () =>
        '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')
    );
};

interface TubesBackgroundProps {
  children?: React.ReactNode;
  className?: string;
  enableClickInteraction?: boolean;
}

export function TubesBackground({
  children,
  className,
  enableClickInteraction = true,
}: TubesBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const tubesRef = useRef<any>(null);

  useEffect(() => {
    let mounted = true;
    let cleanup: (() => void) | undefined;

    const initTubes = async () => {
      if (!canvasRef.current) return;

      try {
        // Load the threejs-components tubes library via script injection
        // (avoids TypeScript static URL import resolution error)
        await new Promise<void>((resolve, reject) => {
          if ((window as any).__tubesCursorLoaded) { resolve(); return; }
          const script = document.createElement('script');
          script.src = 'https://cdn.jsdelivr.net/npm/threejs-components@0.0.19/build/cursors/tubes1.min.js';
          script.type = 'module';
          script.onload = () => { (window as any).__tubesCursorLoaded = true; resolve(); };
          script.onerror = reject;
          document.head.appendChild(script);
        });

        if (!mounted || !canvasRef.current) return;

        // The library exposes a default export on window after module load
        // Use dynamic import with the CDN URL at runtime (not build time)
        const TubesCursorModule = await (Function('return import("https://cdn.jsdelivr.net/npm/threejs-components@0.0.19/build/cursors/tubes1.min.js")')() as Promise<any>);
        const TubesCursor = TubesCursorModule.default;

        if (!mounted || !canvasRef.current) return;

        const app = TubesCursor(canvasRef.current, {
          tubes: {
            colors: ['#10b981', '#14b8a6', '#34d399'],
            lights: {
              intensity: 200,
              colors: ['#10b981', '#14b8a6', '#34d399', '#22c55e'],
            },
          },
        });

        tubesRef.current = app;
        setIsLoaded(true);

        cleanup = () => {};
      } catch (error) {
        console.error('Failed to load TubesCursor:', error);
        // Graceful fallback — still show content without animation
        if (mounted) setIsLoaded(true);
      }
    };

    initTubes();

    return () => {
      mounted = false;
      if (cleanup) cleanup();
    };
  }, []);


  const handleClick = () => {
    if (!enableClickInteraction || !tubesRef.current) return;

    const colors = randomColors(3);
    const lightsColors = randomColors(4);

    tubesRef.current.tubes.setColors(colors);
    tubesRef.current.tubes.setLightsColors(lightsColors);
  };

  return (
    <div
      className={cn(
        'relative w-full h-full min-h-[400px] overflow-hidden bg-background',
        className
      )}
      onClick={handleClick}
    >
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full block"
        style={{ touchAction: 'none' }}
      />

      {/* Fade-in overlay for smooth appearance */}
      <AnimatePresence>
        {!isLoaded && (
          <motion.div
            className="absolute inset-0 bg-[#030712] z-20"
            exit={{ opacity: 0 }}
            transition={{ duration: 1.2 }}
          />
        )}
      </AnimatePresence>

      {/* Content Overlay */}
      <div className="relative z-10 w-full h-full pointer-events-none">
        {children}
      </div>
    </div>
  );
}

export default TubesBackground;
