import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

import CaseDetail from '@/components/CaseDetail';

// The binding test for sourceUrl. src/lib/ovnis-format.test.js proves the
// allowlist rejects javascript: and friends; that says nothing about whether
// this component still routes through it. Dropping the sourceUrl() call and
// using c.source_url directly would leave every one of those lib assertions
// green while putting the rejected value straight into an href — which is the
// only place the rejection actually matters.

const baseCase = {
  case_id: 'PR-1975-003',
  date_raw: '4 March 1975',
  decade: '1970s',
  evidence_tier: 'T2',
  confidence: 'medium',
  description: 'Luz sobre el mar',
  location: { string: 'Cabo Rojo, PR', lat: 18.08, lon: -67.14 },
  reviewer_action: 'promoted',
  promoted_from: 'candidates',
  promoted_at: '2026-01-02T00:00:00Z',
  promoted_by: 'reviewer',
};

const openCase = (over = {}) => render(<CaseDetail case={{ ...baseCase, ...over }} />);
const anchors = () => document.querySelectorAll('a[href]');

describe('CaseDetail — the source link is gated', () => {
  it('renders a real link for an https source', () => {
    openCase({ source_url: 'https://www.faa.gov/foia/123' });

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', 'https://www.faa.gov/foia/123');
    expect(link).toHaveAttribute('rel', expect.stringContaining('noopener'));
  });

  it.each([
    ['javascript:alert(1)'],
    ['data:text/html,<script>alert(1)</script>'],
    ['file:///etc/passwd'],
    ['El Mundo, 4 March 1975, p. 3'],
  ])('renders no anchor at all for %s', (source_url) => {
    // Not "renders a different class" — no href element may exist. This is the
    // assertion that a presence check would have missed.
    openCase({ source_url });

    expect(anchors()).toHaveLength(0);
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  });

  it('still shows the rejected value as text, so nothing is silently dropped', () => {
    // The record keeps its provenance visible; it just is not clickable.
    openCase({ source_url: 'El Mundo, 4 March 1975, p. 3' });

    expect(screen.getByText('El Mundo, 4 March 1975, p. 3')).toBeInTheDocument();
  });

  it('flags a case with no usable URL', () => {
    openCase({ source_url: 'javascript:alert(1)' });

    expect(screen.getByText('No URL')).toBeInTheDocument();
  });

  it('does not flag a case whose URL is usable', () => {
    openCase({ source_url: 'https://www.faa.gov/foia/123' });

    expect(screen.queryByText('No URL')).not.toBeInTheDocument();
  });

  it('labels the link from the citation rather than the raw URL', () => {
    openCase({
      source_url: 'https://www.faa.gov/foia/123',
      source_citation: 'FAA FOIA release 1975-003',
    });

    expect(screen.getByRole('link')).toHaveTextContent('FAA FOIA release 1975-003');
  });
});

describe('CaseDetail — the rest of the record', () => {
  it('renders the identifiers, location and description', () => {
    openCase({});

    expect(screen.getByText(/PR-1975-003/)).toBeInTheDocument();
    expect(screen.getByText(/Cabo Rojo, PR/)).toBeInTheDocument();
    expect(screen.getByText('Luz sobre el mar')).toBeInTheDocument();
  });

  it('marks a case that has no coordinates', () => {
    openCase({ location: { string: 'Unknown, PR' } });

    expect(screen.getByText(/no coordinates/)).toBeInTheDocument();
  });

  it('does not mark a case that has them', () => {
    openCase({});

    expect(screen.queryByText(/no coordinates/)).not.toBeInTheDocument();
  });

  it('shows an agency badge only when a family is present', () => {
    const { unmount } = openCase({ source_family: 'USAF' });
    expect(screen.getByText('Agency involvement')).toBeInTheDocument();
    unmount();

    openCase({ source_family: 'none' });
    expect(screen.queryByText('Agency involvement')).not.toBeInTheDocument();
  });

  it('suppresses the English gloss when it duplicates the original', () => {
    const { unmount } = openCase({ description_en: 'Luz sobre el mar' });
    expect(screen.getAllByText('Luz sobre el mar')).toHaveLength(1);
    unmount();

    openCase({ description_en: 'Light over the sea' });
    expect(screen.getByText('Light over the sea')).toBeInTheDocument();
  });

  it('shows contradictions only when the record has them', () => {
    const { unmount } = openCase({ contradictions_or_gaps: 'Witness count disputed' });
    expect(screen.getByText('Witness count disputed')).toBeInTheDocument();
    unmount();

    openCase({ contradictions_or_gaps: '' });
    expect(screen.queryByText('Contradictions / gaps')).not.toBeInTheDocument();
  });

  it('renders an em dash rather than "undefined" for missing fields', () => {
    openCase({});

    expect(screen.getAllByText('—').length).toBeGreaterThan(0);
  });

  it('renders nothing when there is no case to show', () => {
    render(<CaseDetail case={null} />);

    expect(screen.queryByText(/PR-1975-003/)).not.toBeInTheDocument();
  });
});
