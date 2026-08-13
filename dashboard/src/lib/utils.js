import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
} 


export const isIframe = window.self !== window.top;

// Look a key up in a plain object literal without inheriting from Object.prototype.
//
// `MAP[key] ?? fallback` looks like it degrades safely, and does for ordinary
// misses — but not for `__proto__`, `constructor`, `toString`, `valueOf` or
// `hasOwnProperty`. Those resolve through the prototype chain to a truthy object
// or function, so `??` never fires and the caller gets something that is not a
// value from the map at all.
//
// Every key below is server-supplied (evidence tier, confidence band, review
// status), and the damage here is cosmetic: a badge class becomes an object,
// which clsx then drops entirely because the prototype has no own enumerable
// keys — so the element loses its styling rather than degrading to slate.
//
// Fixed anyway because the identical pattern was a live crash in aguayluz-pr,
// where the key came from the URL: /sector/__proto__ passed an `if (!meta)`
// guard because Object.prototype is truthy, then threw on the next line.
export function lookup(map, key, fallback) {
  return Object.hasOwn(map, key) ? map[key] : fallback
}
