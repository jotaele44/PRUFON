import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'

// MapLibre map of OVNIS sighting cases. Renders the release GeoJSON directly
// (Point features colored by evidence tier). Same wrapper pattern as the
// skywatcher template — note the h-full container (not absolute inset-0), since
// maplibre-gl.css sets .maplibregl-map{position:relative} and would otherwise
// override `absolute` and collapse the height to 0.
// Resolve against the configured base so it works in the normal build
// (served from '/') and the VITE_OFFLINE single-file file:// export (base './').
const MUNICIPIOS_URL = new URL('geo/pr_municipios.geojson', document.baseURI).href

// Municipality outlines ship with the app (public/geo/) and sit under the
// raster tiles, so the map still shows Puerto Rico geography when offline.
const OSM_STYLE = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors',
    },
    municipios: { type: 'geojson', data: MUNICIPIOS_URL },
  },
  layers: [
    { id: 'bg', type: 'background', paint: { 'background-color': '#0b1220' } },
    { id: 'municipios-fill', type: 'fill', source: 'municipios', paint: { 'fill-color': '#101d33', 'fill-opacity': 0.9 } },
    { id: 'municipios-line', type: 'line', source: 'municipios', paint: { 'line-color': '#33517b', 'line-width': 0.8 } },
    { id: 'osm', type: 'raster', source: 'osm', paint: { 'raster-opacity': 0.85, 'raster-saturation': -0.3 } },
  ],
}

const EMPTY = { type: 'FeatureCollection', features: [] }
const PR_CENTER = [-66.4, 18.22]

const TIER_COLOR = [
  'match', ['get', 'evidence_tier'],
  'T1', '#38bdf8', 'T2', '#818cf8', 'T3', '#a78bfa', 'T4', '#64748b',
  '#64748b',
]

export default function CaseMap({ geojson, onSelect }) {
  const containerRef = useRef(null)
  const mapRef = useRef(null)
  const readyRef = useRef(false)
  const dataRef = useRef(geojson)
  dataRef.current = geojson
  const onSelectRef = useRef(onSelect)
  onSelectRef.current = onSelect

  useEffect(() => {
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: OSM_STYLE,
      center: PR_CENTER,
      zoom: 8.2,
    })
    mapRef.current = map
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')

    // 'style.load' instead of 'load': the latter waits for raster tiles,
    // which never resolve offline, and the data layer would never appear.
    map.on('style.load', () => {
      map.addSource('cases', { type: 'geojson', data: dataRef.current || EMPTY })
      map.addLayer({
        id: 'cases-dot', type: 'circle', source: 'cases',
        paint: {
          'circle-radius': 5,
          'circle-color': TIER_COLOR,
          'circle-opacity': 0.85,
          'circle-stroke-color': '#0b1220',
          'circle-stroke-width': 1,
        },
      })
      readyRef.current = true
      map.on('mouseenter', 'cases-dot', () => (map.getCanvas().style.cursor = 'pointer'))
      map.on('mouseleave', 'cases-dot', () => (map.getCanvas().style.cursor = ''))
      map.on('click', 'cases-dot', (e) => onSelectRef.current?.(e.features[0].properties))
    })

    return () => { readyRef.current = false; map.remove() }
  }, [])

  useEffect(() => {
    if (!readyRef.current || !mapRef.current) return
    mapRef.current.getSource('cases')?.setData(geojson || EMPTY)
  }, [geojson])

  return <div ref={containerRef} className="h-full w-full" />
}
