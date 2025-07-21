/**
 * Tests for HumanNeedsVisualization Component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import HumanNeedsVisualization from '../visualizations/HumanNeedsVisualization';

// Mock Chart.js components
jest.mock('react-chartjs-2', () => ({
  Radar: ({ data, options }) => (
    <div data-testid="radar-chart" data-chart-data={JSON.stringify(data)} />
  ),
  Doughnut: ({ data, options }) => (
    <div data-testid="doughnut-chart" data-chart-data={JSON.stringify(data)} />
  ),
  Line: ({ data, options }) => (
    <div data-testid="line-chart" data-chart-data={JSON.stringify(data)} />
  ),
  Bar: ({ data, options }) => (
    <div data-testid="bar-chart" data-chart-data={JSON.stringify(data)} />
  )
}));

// Mock ExpandableCard components
jest.mock('../ExpandableCard', () => ({
  __esModule: true,
  default: ({ title, subtitle, children, defaultExpanded, className }) => (
    <div 
      data-testid="expandable-card" 
      className={className}
      data-title={title}
      data-subtitle={subtitle}
      data-expanded={defaultExpanded}
    >
      {children}
    </div>
  ),
  ExpandableCardGroup: ({ children, layout, columns }) => (
    <div 
      data-testid="expandable-card-group" 
      data-layout={layout}
      data-columns={columns}
    >
      {children}
    </div>
  )
}));

describe('HumanNeedsVisualization', () => {
  const mockNeedsData = {
    subsistence: 75,
    protection: 80,
    affection: 65,
    understanding: 90,
    participation: 70,
    leisure: 60,
    creation: 85,
    identity: 78,
    freedom: 72,
    subsistence_previous: 70,
    protection_previous: 75,
    affection_previous: 60,
    understanding_previous: 85,
    participation_previous: 65,
    leisure_previous: 55,
    creation_previous: 80,
    identity_previous: 75,
    freedom_previous: 70
  };

  const mockIndividualData = {
    'John Doe': {
      subsistence: 80,
      protection: 85,
      affection: 70,
      understanding: 95,
      participation: 75,
      leisure: 65,
      creation: 90,
      identity: 82,
      freedom: 77
    },
    'Jane Smith': {
      subsistence: 70,
      protection: 75,
      affection: 60,
      understanding: 85,
      participation: 65,
      leisure: 55,
      creation: 80,
      identity: 74,
      freedom: 67
    }
  };

  const mockHistoricalData = {
    timeline: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    overall: [70, 72, 75, 76],
    subsistence: [70, 72, 74, 75],
    protection: [75, 77, 79, 80]
  };

  const defaultProps = {
    needsData: mockNeedsData,
    individualData: mockIndividualData,
    historicalData: mockHistoricalData,
    onNeedSelect: jest.fn(),
    onPersonSelect: jest.fn(),
    onImbalanceDetected: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    test('renders component with header and controls', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      expect(screen.getByText('Human Needs Visualization')).toBeInTheDocument();
      expect(screen.getByText('Individual and team pattern displays with fulfillment tracking')).toBeInTheDocument();
      expect(screen.getByText('Team View')).toBeInTheDocument();
      expect(screen.getByText('Individual View')).toBeInTheDocument();
      expect(screen.getByText('Trends')).toBeInTheDocument();
    });

    test('renders fulfillment score card', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      expect(screen.getByText('Team Needs Fulfillment')).toBeInTheDocument();
      // Score should be calculated as average of all needs
      const expectedScore = Math.round(Object.values(mockNeedsData)
        .filter((_, index) => index < 9) // Only first 9 values (current period)
        .reduce((sum, val) => sum + val, 0) / 9);
      expect(screen.getByText(`${expectedScore}%`)).toBeInTheDocument();
    });

    test('renders team view by default', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      expect(screen.getByTestId('radar-chart')).toBeInTheDocument();
      expect(screen.getByTestId('doughnut-chart')).toBeInTheDocument();
      expect(screen.getByText('Team Needs Pattern')).toBeInTheDocument();
      expect(screen.getByText('Needs Distribution')).toBeInTheDocument();
    });

    test('renders all human needs cards', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      const expectedNeeds = [
        'Subsistence', 'Protection', 'Affection', 'Understanding',
        'Participation', 'Leisure', 'Creation', 'Identity', 'Freedom'
      ];
      
      expectedNeeds.forEach(need => {
        expect(screen.getByText(need)).toBeInTheDocument();
      });
    });
  });

  describe('View Mode Switching', () => {
    test('switches to individual view when button clicked', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Individual View'));
      
      expect(screen.getByText('Team Members')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    test('switches to trends view when button clicked', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Trends'));
      
      expect(screen.getByText('Needs Fulfillment Trends')).toBeInTheDocument();
      expect(screen.getByText('Select Need to Track')).toBeInTheDocument();
      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    });

    test('highlights active view button', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      const teamButton = screen.getByText('Team View');
      const individualButton = screen.getByText('Individual View');
      
      expect(teamButton).toHaveClass('neu-button--primary');
      expect(individualButton).not.toHaveClass('neu-button--primary');
      
      fireEvent.click(individualButton);
      
      expect(teamButton).not.toHaveClass('neu-button--primary');
      expect(individualButton).toHaveClass('neu-button--primary');
    });
  });

  describe('Individual View Interactions', () => {
    test('selects person when clicked', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Individual View'));
      fireEvent.click(screen.getByText('John Doe'));
      
      expect(defaultProps.onPersonSelect).toHaveBeenCalledWith('John Doe');
      expect(screen.getByText("John Doe's Needs Pattern")).toBeInTheDocument();
    });

    test('shows individual radar chart when person selected', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Individual View'));
      fireEvent.click(screen.getByText('John Doe'));
      
      const radarCharts = screen.getAllByTestId('radar-chart');
      expect(radarCharts).toHaveLength(1);
    });

    test('shows comparison bars for individual needs', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Individual View'));
      fireEvent.click(screen.getByText('John Doe'));
      
      expect(screen.getByText('Individual Needs Details')).toBeInTheDocument();
      expect(screen.getAllByText('Individual')).toHaveLength(9); // One for each need
      expect(screen.getAllByText('Team Avg')).toHaveLength(9);
    });
  });

  describe('Need Selection', () => {
    test('selects need when clicked in team view', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Subsistence'));
      
      expect(defaultProps.onNeedSelect).toHaveBeenCalledWith(
        expect.objectContaining({ id: 'subsistence', name: 'Subsistence' })
      );
    });

    test('shows need examples when selected', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Subsistence'));
      
      expect(screen.getByText('Examples')).toBeInTheDocument();
      expect(screen.getByText('Health')).toBeInTheDocument();
      expect(screen.getByText('Food')).toBeInTheDocument();
    });

    test('updates trends chart when need selected', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Trends'));
      fireEvent.click(screen.getByText('Subsistence'));
      
      expect(screen.getByText('Subsistence over time')).toBeInTheDocument();
    });
  });

  describe('Imbalance Detection', () => {
    test('detects and displays imbalances', async () => {
      const imbalancedData = {
        ...mockNeedsData,
        subsistence: 95, // High value
        leisure: 25      // Low value
      };
      
      render(
        <HumanNeedsVisualization 
          {...defaultProps} 
          needsData={imbalancedData}
        />
      );
      
      await waitFor(() => {
        expect(defaultProps.onImbalanceDetected).toHaveBeenCalled();
      });
      
      expect(screen.getByText('Detected Imbalances')).toBeInTheDocument();
    });

    test('shows imbalance types correctly', async () => {
      const imbalancedData = {
        ...mockNeedsData,
        subsistence: 95, // Should be excess
        leisure: 25      // Should be deficiency
      };
      
      render(
        <HumanNeedsVisualization 
          {...defaultProps} 
          needsData={imbalancedData}
        />
      );
      
      await waitFor(() => {
        expect(screen.getByText(/Excess/)).toBeInTheDocument();
        expect(screen.getByText(/Deficiency/)).toBeInTheDocument();
      });
    });
  });

  describe('Time Range Selection', () => {
    test('updates time range when changed', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      const timeRangeSelect = screen.getByLabelText('Time Range:');
      fireEvent.change(timeRangeSelect, { target: { value: '90d' } });
      
      expect(timeRangeSelect.value).toBe('90d');
    });

    test('shows all time range options', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      expect(screen.getByText('Last 7 days')).toBeInTheDocument();
      expect(screen.getByText('Last 30 days')).toBeInTheDocument();
      expect(screen.getByText('Last 90 days')).toBeInTheDocument();
      expect(screen.getByText('Last year')).toBeInTheDocument();
    });
  });

  describe('Data Processing', () => {
    test('handles empty data gracefully', () => {
      render(
        <HumanNeedsVisualization 
          needsData={{}}
          individualData={{}}
          historicalData={{}}
        />
      );
      
      expect(screen.getByText('Human Needs Visualization')).toBeInTheDocument();
      expect(screen.getByText('0%')).toBeInTheDocument(); // Fulfillment score should be 0
    });

    test('calculates person scores correctly', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Individual View'));
      
      // John Doe's average should be calculated from his individual data
      const johnData = mockIndividualData['John Doe'];
      const expectedScore = Math.round(
        Object.values(johnData).reduce((sum, val) => sum + val, 0) / 
        Object.values(johnData).length
      );
      
      expect(screen.getByText(`${expectedScore}%`)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels and roles', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      const timeRangeSelect = screen.getByLabelText('Time Range:');
      expect(timeRangeSelect).toBeInTheDocument();
      
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    test('supports keyboard navigation', () => {
      render(<HumanNeedsVisualization {...defaultProps} />);
      
      const teamViewButton = screen.getByText('Team View');
      teamViewButton.focus();
      expect(document.activeElement).toBe(teamViewButton);
    });
  });

  describe('Responsive Behavior', () => {
    test('applies responsive classes', () => {
      render(<HumanNeedsVisualization className="custom-class" {...defaultProps} />);
      
      const container = screen.getByText('Human Needs Visualization').closest('.human-needs-visualization');
      expect(container).toHaveClass('custom-class');
    });
  });
});