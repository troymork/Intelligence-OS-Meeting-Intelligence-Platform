/**
 * Responsive Utilities
 * Utilities for handling responsive design and mobile optimization
 */

// Breakpoints
export const BREAKPOINTS = {
  xs: 320,
  sm: 480,
  md: 768,
  lg: 1024,
  xl: 1200,
  xxl: 1400
};

// Media queries
export const MEDIA_QUERIES = {
  xs: `(max-width: ${BREAKPOINTS.xs}px)`,
  sm: `(max-width: ${BREAKPOINTS.sm}px)`,
  md: `(max-width: ${BREAKPOINTS.md}px)`,
  lg: `(max-width: ${BREAKPOINTS.lg}px)`,
  xl: `(max-width: ${BREAKPOINTS.xl}px)`,
  xxl: `(max-width: ${BREAKPOINTS.xxl}px)`,
  
  // Min-width queries
  minXs: `(min-width: ${BREAKPOINTS.xs + 1}px)`,
  minSm: `(min-width: ${BREAKPOINTS.sm + 1}px)`,
  minMd: `(min-width: ${BREAKPOINTS.md + 1}px)`,
  minLg: `(min-width: ${BREAKPOINTS.lg + 1}px)`,
  minXl: `(min-width: ${BREAKPOINTS.xl + 1}px)`,
  minXxl: `(min-width: ${BREAKPOINTS.xxl + 1}px)`,
  
  // Range queries
  smToMd: `(min-width: ${BREAKPOINTS.sm + 1}px) and (max-width: ${BREAKPOINTS.md}px)`,
  mdToLg: `(min-width: ${BREAKPOINTS.md + 1}px) and (max-width: ${BREAKPOINTS.lg}px)`,
  lgToXl: `(min-width: ${BREAKPOINTS.lg + 1}px) and (max-width: ${BREAKPOINTS.xl}px)`,
  
  // Device-specific
  mobile: `(max-width: ${BREAKPOINTS.md}px)`,
  tablet: `(min-width: ${BREAKPOINTS.md + 1}px) and (max-width: ${BREAKPOINTS.lg}px)`,
  desktop: `(min-width: ${BREAKPOINTS.lg + 1}px)`,
  
  // Orientation
  landscape: '(orientation: landscape)',
  portrait: '(orientation: portrait)',
  
  // Touch devices
  touch: '(hover: none) and (pointer: coarse)',
  noTouch: '(hover: hover) and (pointer: fine)',
  
  // High DPI
  retina: '(-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)',
  
  // Reduced motion
  reducedMotion: '(prefers-reduced-motion: reduce)',
  
  // Dark mode
  darkMode: '(prefers-color-scheme: dark)',
  lightMode: '(prefers-color-scheme: light)',
  
  // High contrast
  highContrast: '(prefers-contrast: high)'
};

/**
 * Hook for responsive breakpoints
 */
export const useBreakpoint = () => {
  const [breakpoint, setBreakpoint] = useState(getCurrentBreakpoint());
  
  useEffect(() => {
    const handleResize = () => {
      setBreakpoint(getCurrentBreakpoint());
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return breakpoint;
};

/**
 * Get current breakpoint
 */
export const getCurrentBreakpoint = () => {
  const width = window.innerWidth;
  
  if (width <= BREAKPOINTS.xs) return 'xs';
  if (width <= BREAKPOINTS.sm) return 'sm';
  if (width <= BREAKPOINTS.md) return 'md';
  if (width <= BREAKPOINTS.lg) return 'lg';
  if (width <= BREAKPOINTS.xl) return 'xl';
  return 'xxl';
};

/**
 * Check if current viewport matches media query
 */
export const matchesMediaQuery = (query) => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia(query).matches;
};

/**
 * Hook for media query matching
 */
export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(() => matchesMediaQuery(query));
  
  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    const handleChange = (e) => setMatches(e.matches);
    
    mediaQuery.addListener(handleChange);
    return () => mediaQuery.removeListener(handleChange);
  }, [query]);
  
  return matches;
};

/**
 * Device detection utilities
 */
export const DEVICE_TYPES = {
  MOBILE: 'mobile',
  TABLET: 'tablet',
  DESKTOP: 'desktop'
};

export const getDeviceType = () => {
  const width = window.innerWidth;
  
  if (width <= BREAKPOINTS.md) return DEVICE_TYPES.MOBILE;
  if (width <= BREAKPOINTS.lg) return DEVICE_TYPES.TABLET;
  return DEVICE_TYPES.DESKTOP;
};

export const isMobile = () => getDeviceType() === DEVICE_TYPES.MOBILE;
export const isTablet = () => getDeviceType() === DEVICE_TYPES.TABLET;
export const isDesktop = () => getDeviceType() === DEVICE_TYPES.DESKTOP;

/**
 * Touch device detection
 */
export const isTouchDevice = () => {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
};

/**
 * Viewport utilities
 */
export const getViewportSize = () => ({
  width: window.innerWidth,
  height: window.innerHeight
});

export const getScrollPosition = () => ({
  x: window.pageXOffset || document.documentElement.scrollLeft,
  y: window.pageYOffset || document.documentElement.scrollTop
});

/**
 * Responsive image utilities
 */
export const generateSrcSet = (baseUrl, sizes = [320, 480, 768, 1024, 1200]) => {
  return sizes.map(size => `${baseUrl}?w=${size} ${size}w`).join(', ');
};

export const generateSizes = (breakpoints = {
  sm: '100vw',
  md: '50vw',
  lg: '33vw',
  default: '25vw'
}) => {
  const sizeQueries = [];
  
  if (breakpoints.sm) sizeQueries.push(`(max-width: ${BREAKPOINTS.sm}px) ${breakpoints.sm}`);
  if (breakpoints.md) sizeQueries.push(`(max-width: ${BREAKPOINTS.md}px) ${breakpoints.md}`);
  if (breakpoints.lg) sizeQueries.push(`(max-width: ${BREAKPOINTS.lg}px) ${breakpoints.lg}`);
  
  sizeQueries.push(breakpoints.default || '25vw');
  
  return sizeQueries.join(', ');
};

/**
 * Responsive grid utilities
 */
export const getGridColumns = (breakpoint, columnConfig = {
  xs: 1,
  sm: 2,
  md: 3,
  lg: 4,
  xl: 5,
  xxl: 6
}) => {
  return columnConfig[breakpoint] || columnConfig.md || 3;
};

/**
 * Responsive spacing utilities
 */
export const getResponsiveSpacing = (breakpoint, spacingConfig = {
  xs: 'var(--spacing-sm)',
  sm: 'var(--spacing-md)',
  md: 'var(--spacing-lg)',
  lg: 'var(--spacing-xl)',
  xl: 'var(--spacing-2xl)',
  xxl: 'var(--spacing-3xl)'
}) => {
  return spacingConfig[breakpoint] || spacingConfig.md || 'var(--spacing-lg)';
};

/**
 * Responsive font size utilities
 */
export const getResponsiveFontSize = (breakpoint, sizeConfig = {
  xs: 'var(--font-size-sm)',
  sm: 'var(--font-size-base)',
  md: 'var(--font-size-lg)',
  lg: 'var(--font-size-xl)',
  xl: 'var(--font-size-2xl)',
  xxl: 'var(--font-size-3xl)'
}) => {
  return sizeConfig[breakpoint] || sizeConfig.md || 'var(--font-size-base)';
};

/**
 * Performance utilities for responsive design
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * Responsive component wrapper
 */
export const withResponsive = (Component) => {
  return function ResponsiveComponent(props) {
    const breakpoint = useBreakpoint();
    const deviceType = getDeviceType();
    const isTouchDevice = useMediaQuery(MEDIA_QUERIES.touch);
    const prefersReducedMotion = useMediaQuery(MEDIA_QUERIES.reducedMotion);
    const prefersDarkMode = useMediaQuery(MEDIA_QUERIES.darkMode);
    
    const responsiveProps = {
      ...props,
      breakpoint,
      deviceType,
      isTouchDevice,
      prefersReducedMotion,
      prefersDarkMode,
      isMobile: breakpoint === 'xs' || breakpoint === 'sm',
      isTablet: breakpoint === 'md',
      isDesktop: breakpoint === 'lg' || breakpoint === 'xl' || breakpoint === 'xxl'
    };
    
    return <Component {...responsiveProps} />;
  };
};

/**
 * CSS-in-JS responsive utilities
 */
export const css = {
  media: (query, styles) => `
    @media ${query} {
      ${styles}
    }
  `,
  
  mobile: (styles) => css.media(MEDIA_QUERIES.mobile, styles),
  tablet: (styles) => css.media(MEDIA_QUERIES.tablet, styles),
  desktop: (styles) => css.media(MEDIA_QUERIES.desktop, styles),
  
  touch: (styles) => css.media(MEDIA_QUERIES.touch, styles),
  noTouch: (styles) => css.media(MEDIA_QUERIES.noTouch, styles),
  
  reducedMotion: (styles) => css.media(MEDIA_QUERIES.reducedMotion, styles),
  darkMode: (styles) => css.media(MEDIA_QUERIES.darkMode, styles),
  highContrast: (styles) => css.media(MEDIA_QUERIES.highContrast, styles)
};

/**
 * Responsive container queries (future-proofing)
 */
export const CONTAINER_QUERIES = {
  small: '(max-width: 400px)',
  medium: '(max-width: 600px)',
  large: '(max-width: 800px)',
  xlarge: '(max-width: 1000px)'
};

export default {
  BREAKPOINTS,
  MEDIA_QUERIES,
  DEVICE_TYPES,
  useBreakpoint,
  useMediaQuery,
  getCurrentBreakpoint,
  matchesMediaQuery,
  getDeviceType,
  isMobile,
  isTablet,
  isDesktop,
  isTouchDevice,
  getViewportSize,
  getScrollPosition,
  generateSrcSet,
  generateSizes,
  getGridColumns,
  getResponsiveSpacing,
  getResponsiveFontSize,
  debounce,
  throttle,
  withResponsive,
  css
};