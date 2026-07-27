import { federationTone, FederationEmptyState } from '@pr-federation/react'
import { useCandidates } from '@/lib/hooks'
import { Badge } from '@/components/ui/badge'
import { tierBadge } from '@/lib/format'
import { locString } from '@/lib/ovnis-format'
import { cn } from '@/lib/utils'

// Map this app's candidate review-status vocabulary onto the canonical
// federation status roles (see @pr-federation/react). Colors now come from the
// shared design system's `.fd-status` tokens instead of hard-coded Tailwind
// tone literals.
const STATUS_ROLE = {
  pending: 'warning',
  monitoring: 'info',
  promoted: 'success',
  merged: 'process',
  rejected_to_echoes: 'danger',
}

// Candidate intake queue (awaiting promotion to master).
export default function CandidateReview() {
  const { data: candidates = [] } = useCandidates()

  return (
    <div className="h-full overflow-auto p-2 space-y-1.5">
      <div className="px-1 pb-1 text-xs text-slate-400">{candidates.length} candidates in queue</div>
      {candidates.map((c) => (
        <div key={c.candidate_id} className="rounded-md border border-slate-800 bg-slate-900 p-2.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono text-slate-300">{c.candidate_id}</span>
            {c.evidence_tier && <Badge variant="outline" className={cn('text-[10px]', tierBadge(c.evidence_tier))}>{c.evidence_tier}</Badge>}
            {(() => {
              const { className: fdClass, ...toneAttrs } = federationTone(STATUS_ROLE[c.review_status] ?? 'neutral')
              return (
                <span className={`${fdClass} text-[10px]`} {...toneAttrs}>
                  {c.review_status ?? 'pending'}
                </span>
              )
            })()}
            {c.intake_channel && <span className="text-[10px] text-slate-600">{c.intake_channel}</span>}
          </div>
          <p className="text-xs text-slate-300 mt-1 line-clamp-2">{c.description}</p>
          <p className="text-[11px] text-slate-500 mt-0.5">{c.date_raw || '—'} · {locString(c)}</p>
        </div>
      ))}
      {/* Shared federation empty state (@pr-federation/react) so "nothing here"
          reads the same in the review queue as everywhere else in the federation. */}
      {candidates.length === 0 && <FederationEmptyState className="py-8" title="Queue empty" />}
    </div>
  )
}
