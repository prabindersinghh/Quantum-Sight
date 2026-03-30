import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import type { NetworkNode, NetworkLink } from '../types'

interface NetworkGraphProps {
  nodes: NetworkNode[]
  links: NetworkLink[]
  height?: number
}

const GROUP_COLORS: Record<string, string> = {
  bank: '#8B0000',
  safe: '#16A34A',
  standard: '#2563EB',
  legacy: '#D97706',
  critical: '#DC2626',
  ca: '#7C3AED',
}

const GROUP_LABELS: Record<string, string> = {
  bank: 'Bank (Central)',
  safe: 'Elite-PQC',
  standard: 'Standard',
  legacy: 'Legacy',
  critical: 'Critical',
  ca: 'Certificate Authority',
}

export default function NetworkGraph({ nodes, links, height = 420 }: NetworkGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || !nodes.length) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const width = svgRef.current.clientWidth || 800

    // Zoom layer
    const g = svg.append('g')
    svg.call(
      d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.3, 3])
        .on('zoom', (event) => g.attr('transform', event.transform))
    )

    // Prepare link data
    const linkData = links.map(l => ({
      source: l.source,
      target: l.target,
      type: l.type,
    }))

    // Simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(linkData).id((d: any) => d.id).distance(90).strength(0.5))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius((d: any) => (d.size || 12) + 8))

    // Links
    const link = g.append('g')
      .selectAll('line')
      .data(linkData)
      .join('line')
      .attr('stroke', '#334155')
      .attr('stroke-width', 1)
      .attr('stroke-opacity', 0.6)

    // Node groups
    const node = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('cursor', 'pointer')
      .call(
        d3.drag<SVGGElement, NetworkNode>()
          .on('start', (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x; d.fy = d.y
          })
          .on('drag', (event, d: any) => {
            d.fx = event.x; d.fy = event.y
          })
          .on('end', (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null; d.fy = null
          })
      )

    // Circle
    node.append('circle')
      .attr('r', (d) => d.size || 12)
      .attr('fill', (d) => GROUP_COLORS[d.group] || '#64748B')
      .attr('fill-opacity', 0.85)
      .attr('stroke', (d) => GROUP_COLORS[d.group] || '#64748B')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.4)

    // Label
    node.append('text')
      .attr('dy', (d) => (d.size || 12) + 12)
      .attr('text-anchor', 'middle')
      .attr('font-size', '9px')
      .attr('fill', '#94A3B8')
      .text((d) => {
        const label = d.label || ''
        return label.length > 20 ? label.slice(0, 18) + '…' : label
      })

    // Tooltip on hover
    node.append('title')
      .text((d) => `${d.label}\nType: ${d.type}\nGroup: ${d.group}\n${d.ip ? 'IP: ' + d.ip : ''}`)

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`)
    })

    return () => { simulation.stop() }
  }, [nodes, links, height])

  // Legend
  const legendGroups = [...new Set(nodes.map(n => n.group))].filter(g => GROUP_COLORS[g])

  return (
    <div className="relative bg-slate-900/50 rounded-xl border border-slate-700/50 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/50">
        <span className="text-slate-300 text-sm font-semibold">Asset Network Graph</span>
        <span className="text-slate-500 text-xs">{nodes.length} nodes · {links.length} connections</span>
      </div>
      <svg ref={svgRef} width="100%" height={height} style={{ display: 'block' }} />
      {/* Legend */}
      <div className="absolute bottom-3 left-3 flex flex-wrap gap-2">
        {legendGroups.map(group => (
          <div key={group} className="flex items-center gap-1.5 px-2 py-1 rounded bg-slate-800/80 border border-slate-700/50">
            <div className="w-2 h-2 rounded-full" style={{ background: GROUP_COLORS[group] }} />
            <span className="text-slate-400 text-xs">{GROUP_LABELS[group] || group}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
