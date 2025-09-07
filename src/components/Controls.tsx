import { BarChart3, Clock } from 'lucide-react';
import type { OrderType, DisplayMode } from '../types';

interface ControlsProps {
  orderType: OrderType;
  displayMode: DisplayMode;
  onOrderChange: (order: OrderType) => void;
  onDisplayModeChange: (mode: DisplayMode) => void;
}

export default function Controls({ 
  orderType, 
  displayMode, 
  onOrderChange, 
  onDisplayModeChange 
}: ControlsProps) {
  return (
    <div className="controls">
      <div className="control-group">
        <label>
          <BarChart3 size={20} />
          Order Type:
        </label>
        <div className="button-group">
          <button
            className={`control-btn ${orderType === 'sequential' ? 'active' : ''}`}
            onClick={() => onOrderChange('sequential')}
          >
            Sequential (1-10)
          </button>
          <button
            className={`control-btn ${orderType === 'chronological' ? 'active' : ''}`}
            onClick={() => onOrderChange('chronological')}
          >
            <Clock size={16} />
            Chronological (Talegeri)
          </button>
        </div>
      </div>
      
      <div className="control-group">
        <label>Display Mode:</label>
        <div className="button-group">
          <button
            className={`control-btn ${displayMode === 'absolute' ? 'active' : ''}`}
            onClick={() => onDisplayModeChange('absolute')}
          >
            Absolute Count
          </button>
          <button
            className={`control-btn ${displayMode === 'percentage' ? 'active' : ''}`}
            onClick={() => onDisplayModeChange('percentage')}
          >
            Relative (%)
          </button>
        </div>
      </div>
    </div>
  );
}