import { useState, useEffect, useCallback } from 'react'

const API = '/api'

function Badge({ children, color = 'blue' }) {
  const colors = {
    blue: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    green: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    yellow: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    red: 'bg-red-500/20 text-red-300 border-red-500/30',
    purple: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    gray: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
  }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${colors[color] || colors.gray}`}>
      {children}
    </span>
  )
}

function ScoreBadge({ score }) {
  const color = score >= 75 ? 'green' : score >= 50 ? 'yellow' : score >= 25 ? 'blue' : 'gray'
  return <Badge color={color}>{score}/100</Badge>
}

function SeverityDots({ severity }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <div key={i} className={`w-2 h-2 rounded-full ${i <= severity ? 'bg-orange-400' : 'bg-gray-700'}`} />
      ))}
    </div>
  )
}

function PainPointCard({ item, onClick }) {
  const solutions = Array.isArray(item.potential_solutions) ? item.potential_solutions : []
  const existing = Array.isArray(item.existing_solutions) ? item.existing_solutions : []

  return (
    <div
      onClick={() => onClick(item)}
      className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-600 cursor-pointer transition-all hover:shadow-lg hover:shadow-blue-500/5 group"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="font-semibold text-gray-100 group-hover:text-blue-300 transition-colors line-clamp-2 flex-1">
          {item.pain_point_summary}
        </h3>
        <ScoreBadge score={item.opportunity_score} />
      </div>

      <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
        <Badge color="purple">r/{item.subreddit}</Badge>
        <Badge color="blue">{item.category}</Badge>
        <span>⬆ {item.score}</span>
        <span>💬 {item.num_comments}</span>
        <SeverityDots severity={item.severity} />
      </div>

      <p className="text-sm text-gray-400 line-clamp-2 mb-3">
        {item.title}
        {item.body && ` — ${item.body.substring(0, 150)}`}
      </p>

      {solutions.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-800">
          <p className="text-xs text-gray-500 mb-1.5">💡 Product Ideas:</p>
          <div className="flex flex-wrap gap-1.5">
            {solutions.slice(0, 3).map((s, i) => (
              <span key={i} className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded-lg">
                {typeof s === 'string' ? s.substring(0, 60) : s}
                {typeof s === 'string' && s.length > 60 ? '…' : ''}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function DetailModal({ item, onClose }) {
  if (!item) return null
  const solutions = Array.isArray(item.potential_solutions) ? item.potential_solutions : []
  const existing = Array.isArray(item.existing_solutions) ? item.existing_solutions : []

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-gray-900 border border-gray-700 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-start justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-100 flex-1">{item.pain_point_summary}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-300 ml-4 text-xl">✕</button>
        </div>

        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <Badge color="purple">r/{item.subreddit}</Badge>
          <Badge color="blue">{item.category}</Badge>
          <ScoreBadge score={item.opportunity_score} />
          <span className="text-xs text-gray-500">⬆ {item.score} · 💬 {item.num_comments}</span>
          <span className="text-xs text-gray-500">Severity:</span>
          <SeverityDots severity={item.severity} />
        </div>

        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-400 mb-1">Original Post</h4>
          <div className="bg-gray-950 rounded-lg p-4 text-sm text-gray-300 border border-gray-800">
            <p className="font-medium mb-2">{item.title}</p>
            <p className="whitespace-pre-wrap">{item.body?.substring(0, 1000)}</p>
          </div>
          {item.url && (
            <a href={item.url} target="_blank" rel="noopener noreferrer"
               className="text-xs text-blue-400 hover:text-blue-300 mt-1 inline-block">
              View on Reddit →
            </a>
          )}
        </div>

        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-400 mb-1">👥 Affected Audience</h4>
          <p className="text-sm text-gray-300">{item.affected_audience}</p>
        </div>

        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-400 mb-1">📊 Market Size</h4>
          <p className="text-sm text-gray-300">{item.market_size_estimate}</p>
        </div>

        {solutions.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-400 mb-2">💡 Product Ideas</h4>
            <ul className="space-y-2">
              {solutions.map((s, i) => (
                <li key={i} className="text-sm text-gray-300 bg-gray-800/50 rounded-lg px-3 py-2 border border-gray-700">
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {existing.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-400 mb-2">🔍 Existing Solutions</h4>
            <div className="flex flex-wrap gap-2">
              {existing.map((s, i) => (
                <Badge key={i} color="gray">{s}</Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function StatsCard({ label, value, icon }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <div className="text-2xl mb-1">{icon}</div>
      <div className="text-2xl font-bold text-gray-100">{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  )
}

export default function App() {
  const [painPoints, setPainPoints] = useState([])
  const [total, setTotal] = useState(0)
  const [stats, setStats] = useState(null)
  const [trending, setTrending] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [scraping, setScraping] = useState(false)

  // Filters
  const [subreddit, setSubreddit] = useState('')
  const [category, setCategory] = useState('')
  const [sortBy, setSortBy] = useState('opportunity_score')
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [page, setPage] = useState(0)
  const LIMIT = 20

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        limit: LIMIT,
        offset: page * LIMIT,
        sort_by: sortBy,
        order: 'desc',
      })
      if (subreddit) params.set('subreddit', subreddit)
      if (category) params.set('category', category)
      if (search) params.set('search', search)

      const [ppRes, statsRes, trendRes] = await Promise.all([
        fetch(`${API}/pain-points?${params}`).then(r => r.json()),
        fetch(`${API}/stats`).then(r => r.json()),
        fetch(`${API}/trending?limit=5`).then(r => r.json()),
      ])
      setPainPoints(ppRes.items || [])
      setTotal(ppRes.total || 0)
      setStats(statsRes)
      setTrending(trendRes.items || [])
    } catch (e) {
      console.error('Fetch error:', e)
    }
    setLoading(false)
  }, [page, subreddit, category, sortBy, search])

  useEffect(() => { fetchData() }, [fetchData])

  const triggerScrape = async () => {
    setScraping(true)
    try {
      await fetch(`${API}/scrape`, { method: 'POST' })
      // Poll status
      const poll = setInterval(async () => {
        const res = await fetch(`${API}/scrape/status`).then(r => r.json())
        if (!res.running) {
          clearInterval(poll)
          setScraping(false)
          fetchData()
        }
      }, 3000)
    } catch (e) {
      setScraping(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setSearch(searchInput)
    setPage(0)
  }

  const exportData = (format) => {
    window.open(`${API}/export?format=${format}`, '_blank')
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎯</span>
            <div>
              <h1 className="text-lg font-bold text-gray-100">Pain Point Discovery</h1>
              <p className="text-xs text-gray-500">Reddit-sourced product opportunities</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => exportData('csv')}
              className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 text-gray-400 hover:text-gray-200 border border-gray-700"
            >
              📥 Export CSV
            </button>
            <button
              onClick={triggerScrape}
              disabled={scraping}
              className={`text-sm px-4 py-2 rounded-lg font-medium transition-all ${
                scraping
                  ? 'bg-gray-700 text-gray-400 cursor-wait'
                  : 'bg-blue-600 text-white hover:bg-blue-500'
              }`}
            >
              {scraping ? '⏳ Scraping...' : '🔄 Run Scraper'}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats Row */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <StatsCard icon="📊" value={stats.analyzed_posts} label="Pain Points Found" />
            <StatsCard icon="🏷️" value={stats.categories?.length || 0} label="Categories" />
            <StatsCard icon="⭐" value={stats.avg_opportunity_score} label="Avg Opportunity Score" />
            <StatsCard icon="🔥" value={stats.top_opportunity_score} label="Top Score" />
          </div>
        )}

        {/* Trending */}
        {trending.length > 0 && (
          <div className="mb-6">
            <h2 className="text-sm font-medium text-gray-400 mb-3">🔥 Trending Pain Points</h2>
            <div className="flex gap-3 overflow-x-auto pb-2">
              {trending.map(item => (
                <div
                  key={item.id}
                  onClick={() => setSelected(item)}
                  className="flex-shrink-0 w-72 bg-gray-900 border border-gray-800 rounded-xl p-4 hover:border-blue-500/50 cursor-pointer transition-all"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <ScoreBadge score={item.opportunity_score} />
                    <Badge color="purple">r/{item.subreddit}</Badge>
                  </div>
                  <p className="text-sm text-gray-200 line-clamp-2">{item.pain_point_summary}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap gap-3 mb-6 items-center">
          <form onSubmit={handleSearch} className="flex-1 min-w-[200px]">
            <input
              type="text"
              value={searchInput}
              onChange={e => setSearchInput(e.target.value)}
              placeholder="Search pain points..."
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500"
            />
          </form>

          <select
            value={subreddit}
            onChange={e => { setSubreddit(e.target.value); setPage(0) }}
            className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Subreddits</option>
            {stats?.subreddits?.map(s => (
              <option key={s.subreddit} value={s.subreddit}>r/{s.subreddit} ({s.cnt})</option>
            ))}
          </select>

          <select
            value={category}
            onChange={e => { setCategory(e.target.value); setPage(0) }}
            className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Categories</option>
            {stats?.categories?.map(c => (
              <option key={c.category} value={c.category}>{c.category} ({c.cnt})</option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={e => { setSortBy(e.target.value); setPage(0) }}
            className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-blue-500"
          >
            <option value="opportunity_score">Opportunity Score</option>
            <option value="score">Reddit Upvotes</option>
            <option value="severity">Severity</option>
            <option value="num_comments">Comments</option>
            <option value="created_utc">Newest</option>
          </select>
        </div>

        {/* Results */}
        {loading ? (
          <div className="text-center py-20 text-gray-500">
            <div className="text-4xl mb-4 animate-pulse">🎯</div>
            <p>Loading pain points...</p>
          </div>
        ) : painPoints.length === 0 ? (
          <div className="text-center py-20 text-gray-500">
            <div className="text-4xl mb-4">🔍</div>
            <p className="text-lg mb-2">No pain points found yet</p>
            <p className="text-sm mb-4">Run the scraper to discover Reddit pain points</p>
            <button
              onClick={triggerScrape}
              disabled={scraping}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 text-sm"
            >
              {scraping ? '⏳ Scraping...' : '🔄 Start Scraping'}
            </button>
          </div>
        ) : (
          <>
            <p className="text-xs text-gray-500 mb-3">{total} results</p>
            <div className="grid gap-4 md:grid-cols-2">
              {painPoints.map(item => (
                <PainPointCard key={item.id} item={item} onClick={setSelected} />
              ))}
            </div>

            {/* Pagination */}
            {total > LIMIT && (
              <div className="flex justify-center gap-3 mt-6">
                <button
                  onClick={() => setPage(p => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="px-4 py-2 bg-gray-800 rounded-lg text-sm disabled:opacity-30"
                >
                  ← Previous
                </button>
                <span className="text-sm text-gray-500 py-2">
                  Page {page + 1} of {Math.ceil(total / LIMIT)}
                </span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={(page + 1) * LIMIT >= total}
                  className="px-4 py-2 bg-gray-800 rounded-lg text-sm disabled:opacity-30"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Detail Modal */}
      <DetailModal item={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
