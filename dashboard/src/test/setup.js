import '@testing-library/jest-dom/vitest';
import * as matchers from 'vitest-axe/matchers';
import { expect, vi } from 'vitest';

expect.extend(matchers);

// jsdom does not implement matchMedia. src/hooks/use-mobile.jsx calls it at
// mount and components/ui/sidebar.jsx depends on that hook, so without this any
// test that renders through the layout throws before its first assertion.
// Defaults to the desktop breakpoint; a test that cares can override.
if (!window.matchMedia) {
  window.matchMedia = (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  });
}
