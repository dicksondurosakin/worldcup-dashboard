import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Moon, Search, Star, Sun } from 'lucide-react';
import { groups, flags } from './groups';
import { fixtures } from './fixtures';
import { liveStatus } from './liveStatus';
import './styles.css';

const allTeams = Object.values(groups).flat();
const groupOf = team => Object.keys(groups).find(g => groups[g].includes(team));
const ordinal = n => n + (n === 1 ? 'st' : n === 2 ? 'nd' : n === 3 ? 'rd' : 'th');

function buildStandings() {
  const stats = Object.fromEntries(allTeams.map(team => [team, { team, played:0, won:0, drawn:0, lost:0, gf:0, ga:0, gd:0, points:0 }]));
  fixtures.filter(m => m.status === 'Complete').forEach(m => {
    const h = stats[m.home], a = stats[m.away];
    if (!h || !a) return;
    h.played++; a.played++; h.gf += m.homeScore; h.ga += m.awayScore; a.gf += m.awayScore; a.ga += m.homeScore;
    if (m.homeScore > m.awayScore) { h.won++; a.lost++; h.points += 3; }
    else if (m.homeScore < m.awayScore) { a.won++; h.lost++; a.points += 3; }
    else { h.drawn++; a.drawn++; h.points++; a.points++; }
    h.gd = h.gf - h.ga; a.gd = a.gf - a.ga;
  });
  return stats;
}

function App() {
  const [selected, setSelected] = useState('Japan');
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('all');
  const [view, setView] = useState('all');
  const [dark, setDark] = useState(false);
  const [favourites, setFavourites] = useState(() => JSON.parse(localStorage.getItem('favourites') || '[]'));
  const stats = useMemo(buildStandings, []);
  const rank = team => [...groups[groupOf(team)]].sort((a,b)=>stats[b].points-stats[a].points||stats[b].gd-stats[a].gd||stats[b].gf-stats[a].gf).indexOf(team)+1;
  const toggleFav = team => setFavourites(prev => { const next = prev.includes(team) ? prev.filter(t => t !== team) : [...prev, team]; localStorage.setItem('favourites', JSON.stringify(next)); return next; });
  const teamMatches = fixtures.filter(m => m.home === selected || m.away === selected).filter(m => view === 'all' || (view === 'played' ? m.status === 'Complete' : m.status !== 'Complete'));
  const selectedStats = stats[selected];

  return <div className={dark ? 'app dark' : 'app'}>
    <header className="hero">
      <div><p className="eyebrow">Interactive tracker</p><h1>World Cup 2026 Dashboard</h1><p>Browse groups, click a team, and see every played and upcoming match in one place.</p></div>
      <button className="iconButton" onClick={() => setDark(!dark)}>{dark ? <Sun/> : <Moon/>}</button>
    </header>
    <section className="liveBar">
      <span className={liveStatus.enabled ? 'dot live' : 'dot'}></span>
      <b>{liveStatus.enabled ? 'Live data connected' : 'Sample data'}</b>
      <span>{liveStatus.lastUpdated}</span>
      <small>{liveStatus.source}</small>
    </section>
    <section className="toolbar">
      <label className="search"><Search size={18}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search a country..." /></label>
      <select value={filter} onChange={e=>setFilter(e.target.value)}>
        <option value="all">All groups</option>
        <option value="faves">Favourites</option>
        {Object.keys(groups).map(g => <option key={g} value={g}>Group {g}</option>)}
      </select>
      <button className="pill" onClick={()=>setFilter(filter === 'faves' ? 'all' : 'faves')}>{filter === 'faves' ? 'All groups' : '⭐ Favourites'}</button>
    </section>
    <main className="layout">
      <section className="groups">
        {Object.entries(groups).filter(([g]) => filter === 'all' || filter === g || filter === 'faves').map(([g, teams]) => {
          const shown = teams.filter(t => t.toLowerCase().includes(query.toLowerCase())).filter(t => filter !== 'faves' || favourites.includes(t));
          if (!shown.length) return null;
          return <article className="group" key={g}><h2>Group {g}<span>{shown.length} teams</span></h2>{shown.map(team => <button className={team === selected ? 'team active' : 'team'} key={team} onClick={()=>setSelected(team)}><span className="flag">{flags[team]}</span><span><b>{team}</b><small>{ordinal(rank(team))} • {stats[team].gd >= 0 ? '+' : ''}{stats[team].gd} GD</small></span><strong>{stats[team].points}</strong></button>)}</article>;
        })}
      </section>
      <aside className="panel">
        <div className="panelTop"><div><h2>{flags[selected]} {selected}</h2><p>Group {groupOf(selected)} • {ordinal(rank(selected))} place</p></div><button className="star" onClick={()=>toggleFav(selected)}><Star fill={favourites.includes(selected) ? 'currentColor' : 'none'}/></button></div>
        <div className="stats"><div><b>{selectedStats.points}</b><span>PTS</span></div><div><b>{selectedStats.played}</b><span>Played</span></div><div><b>{selectedStats.gf}</b><span>GF</span></div><div><b>{selectedStats.gd >= 0 ? '+' : ''}{selectedStats.gd}</b><span>GD</span></div></div>
        <div className="tabs">{['all','played','coming'].map(v => <button key={v} className={view===v?'on':''} onClick={()=>setView(v)}>{v}</button>)}</div>
        <div className="fixtures">{teamMatches.length ? teamMatches.map(match => <Match key={match.id} match={match}/>) : <p className="empty">No fixtures found for this view yet.</p>}</div>
      </aside>
    </main>
  </div>;
}

function Match({ match }) {
  const done = match.status === 'Complete';
  return <article className={done ? 'match complete' : 'match upcoming'}>
    <small>{new Date(match.date+'T12:00:00').toLocaleDateString(undefined,{weekday:'short',day:'numeric',month:'short',year:'numeric'})} • {match.group}</small>
    <p><span>{flags[match.home]} {match.home}</span><b>{done ? match.homeScore : '—'}</b></p>
    <p><span>{flags[match.away]} {match.away}</span><b>{done ? match.awayScore : '—'}</b></p>
    <em>{done ? 'Played' : 'Upcoming'}</em>
  </article>;
}

createRoot(document.getElementById('root')).render(<App />);
