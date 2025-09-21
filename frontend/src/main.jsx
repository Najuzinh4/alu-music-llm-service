import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'

function fetchJSON(url) {
  return fetch(url, { credentials: 'include' }).then(r => {
    if (!r.ok) throw new Error('HTTP ' + r.status)
    return r.json()
  })
}

function App() {
  const [q, setQ] = useState('')
  const [categoria, setCategoria] = useState('')
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)

  const params = useMemo(() => {
    const p = new URLSearchParams()
    if (q) p.set('q', q)
    if (categoria) p.set('categoria', categoria)
    if (start) p.set('start', start)
    if (end) p.set('end', end)
    p.set('per_page', '100')
    return p
  }, [q, categoria, start, end])

  const load = () => {
    setLoading(true)
    fetchJSON('/dashboard/data/comentarios?' + params.toString())
      .then(d => { setItems(d.items); setTotal(d.total) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  return (
    <div style={{ fontFamily: 'system-ui, Arial, sans-serif', maxWidth: 1100, margin: '24px auto', padding: '0 16px' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>AluMusic UI</h1>
        <nav>
          <a href="/dashboard">Ver versão clássica</a>
          <span style={{ margin: '0 8px' }}>|</span>
          <a href="/dashboard/logout">Sair</a>
        </nav>
      </header>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 12 }}>
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="Buscar texto…" />
        <select value={categoria} onChange={e => setCategoria(e.target.value)}>
          <option value="">Todas</option>
          {["ELOGIO","CRÍTICA","SUGESTÃO","DÚVIDA","SPAM"].map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <label>De</label>
        <input type="datetime-local" value={start} onChange={e => setStart(e.target.value)} />
        <label>Até</label>
        <input type="datetime-local" value={end} onChange={e => setEnd(e.target.value)} />
        <button onClick={load} disabled={loading}>{loading ? 'Carregando…' : 'Filtrar'}</button>
        <a href={'/dashboard/export?' + params.toString()} style={{ padding: '8px 10px', border: '1px solid #ddd', borderRadius: 6, textDecoration: 'none' }}>Exportar CSV</a>
      </div>

      <p style={{ opacity: 0.7 }}>Total: {total}</p>

      <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff' }}>
        <thead>
          <tr>
            <th style={{ borderBottom: '1px solid #eee', padding: 8 }}>Data</th>
            <th style={{ borderBottom: '1px solid #eee', padding: 8 }}>Categoria</th>
            <th style={{ borderBottom: '1px solid #eee', padding: 8 }}>Confiança</th>
            <th style={{ borderBottom: '1px solid #eee', padding: 8 }}>Tags</th>
            <th style={{ borderBottom: '1px solid #eee', padding: 8 }}>Texto</th>
          </tr>
        </thead>
        <tbody>
          {items.map(r => (
            <tr key={r.id}>
              <td style={{ borderBottom: '1px solid #eee', padding: 8 }}>{r.created_at}</td>
              <td style={{ borderBottom: '1px solid #eee', padding: 8 }}>{r.categoria}</td>
              <td style={{ borderBottom: '1px solid #eee', padding: 8 }}>{(r.confianca ?? 0).toFixed(2)}</td>
              <td style={{ borderBottom: '1px solid #eee', padding: 8 }}>
                {(r.tags_funcionalidades || []).map(t => <span key={t.code} style={{ display: 'inline-block', padding: '2px 6px', background: '#eef5ff', border: '1px solid #d7e7ff', borderRadius: 12, marginRight: 4, fontSize: 12 }}>{t.code}</span>)}
              </td>
              <td style={{ borderBottom: '1px solid #eee', padding: 8, maxWidth: 600 }}>{r.texto}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)

