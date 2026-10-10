// The two typefaces the product uses, plus a Devanagari face for the name in Hindi.
// Loaded through Remotion so every frame waits for them.
import {loadFont as loadMono} from '@remotion/google-fonts/IBMPlexMono';
import {loadFont as loadDevanagari} from '@remotion/google-fonts/NotoSansDevanagari';
import {loadFont as loadSans} from '@remotion/google-fonts/PlusJakartaSans';

export const SANS = loadSans('normal', {weights: ['500', '600', '700', '800'], subsets: ['latin']}).fontFamily;
export const MONO = loadMono('normal', {weights: ['400', '500'], subsets: ['latin']}).fontFamily;
export const DEVANAGARI = loadDevanagari('normal', {weights: ['600'], subsets: ['devanagari']}).fontFamily;
