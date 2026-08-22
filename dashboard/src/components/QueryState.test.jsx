import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import QueryState from '@/components/QueryState';

// One of the first two component tests in this dashboard, so between them they
// prove the jsdom half of the harness works — the lib tests would pass with
// testing-library entirely absent.
//
// QueryState exists to keep one specific lie off the screen: before it, getJSON
// swallowed failures into [] and a backend outage rendered as "Queue empty",
// asserting an empty queue the app had never successfully asked about. So the
// tests that matter here are the ones that keep failure and emptiness apart.

const CHILD = <p>real content</p>;

describe('QueryState — one state at a time', () => {
  it('renders children when nothing is loading, failing or empty', () => {
    render(<QueryState>{CHILD}</QueryState>);

    expect(screen.getByText('real content')).toBeInTheDocument();
  });

  it('announces loading politely, without the children', () => {
    render(<QueryState loading>{CHILD}</QueryState>);

    const status = screen.getByRole('status');
    expect(status).toHaveTextContent('Loading…');
    expect(status).toHaveAttribute('aria-busy', 'true');
    expect(screen.queryByText('real content')).not.toBeInTheDocument();
  });

  it('announces an error assertively, without the children', () => {
    // role="alert" rather than role="status": a screen reader should be
    // interrupted for a failure but not for a slow load.
    render(<QueryState error={new Error('boom')}>{CHILD}</QueryState>);

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.queryByText('real content')).not.toBeInTheDocument();
  });

  it('renders the empty state without the children', () => {
    render(<QueryState isEmpty emptyTitle="No cases match">{CHILD}</QueryState>);

    expect(screen.getByText('No cases match')).toBeInTheDocument();
    expect(screen.queryByText('real content')).not.toBeInTheDocument();
  });
});

describe('QueryState — failure is not emptiness', () => {
  // The whole reason this component exists.

  it('shows the error, not the empty state, when both are true', () => {
    // A failed request leaves the list empty too, so callers routinely pass
    // both. If isEmpty won here, every outage would read as "nothing found".
    render(<QueryState error={new Error('backend down')} isEmpty emptyTitle="No cases" />);

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.queryByText('No cases')).not.toBeInTheDocument();
  });

  it('says out loud that this is not an empty result', () => {
    render(<QueryState error={new Error('boom')} />);

    expect(screen.getByText(/not an empty result/i)).toBeInTheDocument();
  });

  it('gives the two states different roles, so they are distinguishable', () => {
    const { container: errored, unmount } = render(<QueryState error={new Error('x')} />);
    const errorRole = errored.firstChild.getAttribute('role');
    unmount();

    const { container: empty } = render(<QueryState isEmpty />);
    const emptyRole = empty.firstChild.getAttribute('role');

    expect(errorRole).toBe('alert');
    expect(emptyRole).not.toBe('alert');
  });

  it('shows loading over everything else', () => {
    render(<QueryState loading error={new Error('x')} isEmpty emptyTitle="No cases" />);

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.queryByText('No cases')).not.toBeInTheDocument();
  });
});

describe('QueryState — messages and retry', () => {
  it('shows the error message when there is one', () => {
    render(<QueryState error={new Error('Could not reach the backend at :8000')} />);

    expect(screen.getByText(/Could not reach the backend at :8000/)).toBeInTheDocument();
  });

  it('falls back to a readable message when the error has none', () => {
    // An error thrown with no message would otherwise render an empty paragraph,
    // which looks like the failure has no explanation rather than no detail.
    render(<QueryState error={new Error('')} />);

    expect(screen.getByText('The backend did not respond.')).toBeInTheDocument();
  });

  it('offers a retry button only when a handler is given', () => {
    const { unmount } = render(<QueryState error={new Error('x')} />);
    expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument();
    unmount();

    render(<QueryState error={new Error('x')} onRetry={vi.fn()} />);
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('calls the retry handler when clicked', async () => {
    const onRetry = vi.fn();
    render(<QueryState error={new Error('x')} onRetry={onRetry} />);

    await userEvent.click(screen.getByRole('button', { name: /retry/i }));

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('honours a custom loading label', () => {
    render(<QueryState loading loadingLabel="Fetching cases…" />);

    expect(screen.getByText('Fetching cases…')).toBeInTheDocument();
  });

  it('defaults the empty title rather than rendering a blank state', () => {
    render(<QueryState isEmpty />);

    expect(screen.getByText('Nothing here')).toBeInTheDocument();
  });
});
