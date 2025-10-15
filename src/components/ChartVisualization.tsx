import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { SearchResult, OrderType, DisplayMode, VedaMetadata } from '../types';

interface ChartVisualizationProps {
  results: SearchResult[];
  orderType: OrderType;
  displayMode: DisplayMode;
  metadata: VedaMetadata;
}

export default function ChartVisualization({ results, orderType, displayMode, metadata }: ChartVisualizationProps) {
  if (!results || results.length === 0) {
    return (
      <div className="no-results">
        <p>No search results to display. Enter keywords above to begin.</p>
      </div>
    );
  }
  
  // Prepare data for chart
  const hasChronological = Boolean(metadata.chronologicalOrder?.length);
  const ordering = orderType === 'chronological' && hasChronological
    ? metadata.chronologicalOrder!
    : metadata.sequentialOrder;
  const chartData: Record<string, number | string>[] = [];
  
  for (let i = 0; i < ordering.length; i++) {
    const mandalaNum = ordering[i];
    const dataPoint: Record<string, number | string> = {
      mandala: orderType === 'chronological' && hasChronological
        ? `${i + 1} (${metadata.shortLabel}${mandalaNum})`
        : `${metadata.shortLabel}${mandalaNum}`
    };
    
    results.forEach(result => {
      const idx = mandalaNum - 1;
      const value = displayMode === 'percentage' 
        ? result.mandalaPercentages[idx] 
        : result.mandalaCounts[idx];
      dataPoint[result.word] = Number(value.toFixed(2));
    });
    
    chartData.push(dataPoint);
  }
  
  // Generate colors for bars
  const colors = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1',
    '#d084d0', '#ffb347', '#67b7dc', '#a4de6c', '#ffd93d'
  ];
  
  return (
    <div className="chart-container">
      <h3>
        Distribution across {metadata.pluralBookLabel} - {orderType === 'chronological' && hasChronological ? 'Chronological' : 'Sequential'} Order
        ({displayMode === 'percentage' ? 'Percentage of verses' : 'Absolute occurrences'})
      </h3>
      
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="mandala" 
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            label={{ 
              value: displayMode === 'percentage' ? 'Percentage (%)' : 'Occurrences', 
              angle: -90, 
              position: 'insideLeft' 
            }}
          />
          <Tooltip />
          <Legend />
          
          {results.map((result, index) => (
            <Bar 
              key={result.word}
              dataKey={result.word}
              fill={colors[index % colors.length]}
              opacity={0.8}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
      
      <div className="statistics">
        <h4>Statistics:</h4>
        {results.map(result => {
          const baseCounts = displayMode === 'percentage'
            ? result.mandalaPercentages
            : result.mandalaCounts;
          const orderedCounts = ordering.map(m => baseCounts[m - 1] ?? 0);
          
          const avg = orderedCounts.reduce((a, b) => a + b, 0) / orderedCounts.length;
          const max = Math.max(...orderedCounts);
          const maxIndex = orderedCounts.indexOf(max);
          const maxMandala = ordering[maxIndex];
          
          return (
            <div key={result.word} className="stat-item">
              <strong>{result.word}:</strong>
              <ul>
                <li>Total matches: {result.totalMatches}</li>
                <li>Average per {metadata.bookLabel.toLowerCase()}: {avg.toFixed(2)}{displayMode === 'percentage' ? '%' : ''}</li>
                <li>Highest in {metadata.bookLabel} {maxMandala}: {max.toFixed(2)}{displayMode === 'percentage' ? '%' : ''}</li>
              </ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}
