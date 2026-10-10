// AgniDrishti's palette, taken from the product itself: deep navy, an ember accent, indigo for
// neutral data, and the four risk-tier colours as they appear on dark surfaces.
export const W = 1920;
export const H = 1080;
export const FPS = 30;
export const DURATION = 1320; // 44 seconds

export const C = {
  bg: '#060A14',
  navy: '#0B1220',
  navy2: '#16203A',
  text: '#F4F6FF',
  dim: 'rgba(244, 246, 255, 0.64)',
  faint: 'rgba(244, 246, 255, 0.38)',
  hair: 'rgba(255, 255, 255, 0.10)',
  street: 'rgba(160, 175, 210, 0.40)',
  road: 'rgba(205, 216, 240, 0.70)',
  ember: '#F0452F',
  ember2: '#FF8A4C',
  amber: '#FFB25E',
  indigo: '#7C8BFF',
  water: '#5AA9FF',
  slate: '#7E8AA8',
  tiers: ['#FF5A4F', '#FF9142', '#FFC83D', '#2DD4BF'], // Severe, High, Moderate, Low
};

export const TIER_NAMES = ['Severe', 'High', 'Moderate', 'Low'];
export const EMBER_GRADIENT = 'linear-gradient(120deg, #FFC27A 0%, #FF7A45 45%, #F0452F 100%)';

/** Colour of a score on the 0–100 scale, using the app's tier thresholds. */
export const scoreColor = (score: number) => (score >= 70 ? C.tiers[0] : score >= 50 ? C.tiers[1] : score >= 30 ? C.tiers[2] : C.tiers[3]);
export const scoreTier = (score: number) => (score >= 70 ? 'Severe' : score >= 50 ? 'High' : score >= 30 ? 'Moderate' : 'Low');
export const GRADE_COLOR: Record<string, string> = {Critical: C.tiers[0], Poor: C.tiers[1], Fair: C.tiers[2], Good: C.tiers[3]};
