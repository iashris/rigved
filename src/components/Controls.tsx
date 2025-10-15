import { BarChart3, Clock } from 'lucide-react';
import type { OrderType, DisplayMode, VedaMetadata } from '../types';

interface ControlsProps {
  metadata: VedaMetadata;
  orderType: OrderType;
  displayMode: DisplayMode;
  onOrderChange: (order: OrderType) => void;
  onDisplayModeChange: (mode: DisplayMode) => void;
}

export default function Controls({ 
  metadata,
  orderType, 
  displayMode, 
  onOrderChange, 
  onDisplayModeChange 
}: ControlsProps) {
  const hasChronologicalOrder = Boolean(metadata.chronologicalOrder?.length);
  const sequentialStart = metadata.sequentialOrder[0];
  const sequentialEnd = metadata.sequentialOrder[metadata.sequentialOrder.length - 1];
  const chronologicalLabel = metadata.chronologicalDescription ?? 'Chronological';

  const handleChronologicalClick = () => {
    if (hasChronologicalOrder) {
      onOrderChange('chronological');
    }
  };

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
            Sequential ({sequentialStart}-{sequentialEnd})
          </button>
          <button
            className={`control-btn ${orderType === 'chronological' ? 'active' : ''}`}
            onClick={handleChronologicalClick}
            disabled={!hasChronologicalOrder}
            title={
              hasChronologicalOrder
                ? undefined
                : `${metadata.name} currently has only sequential ordering`
            }
          >
            <Clock size={16} />
            {chronologicalLabel}
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
