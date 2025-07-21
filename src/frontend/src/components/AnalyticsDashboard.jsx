/**
 * Comprehensive Analytics Dashboard Component
 * Six-dimensional analysis visualization with interactive charts and pattern displays
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  ArcElement,
  Filler
} from 'chart.js';
import { Line, Bar, Radar, Doughnut, Scatter } from 'react-chartjs-2';
import ExpandableCard, { ExpandableCardGroup } from './ExpandableCard';
import './AnalyticsDashboard.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  ArcElement,
  Filler
);

const AnalyticsDashboard = ({
  analysisData = {},
  strategicData = {},
  humanNeedsData = {},
  organizationalData = {},
  timeRange = '30d',
  onTimeRangeChange,
  onDrillDown,
  className = ''
}) => {
  const [activeView, setActiveView] = useState('overview');
  const [selectedMetrics, setSelectedMetrics] = useState([]);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [animationsEnabled, setAnimationsEnabled] = useState(true);

  // Six-dimensional analysis data processing
  const sixDimensionalData = useMemo(() => {
    const dimensions = [
      'Strategic Alignment',
      'Human Needs Fulfillment',
      'Communication Effectiveness',
      'Decision Quality',
      'Innovation Potential',
      'Organizational Learning'
    ];

    const currentPeriod = [
      analysisData.strategicAlignment || 0,
      humanNeedsData.fulfillmentScore || 0,
      analysisData.communicationScore || 0,
      analysisData.decisionQuality || 0,
      analysisData.innovationPotential || 0,
      organizationalData.learningScore || 0
    ];

    const previousPeriod = [
      analysisData.previousStrategicAlignment || 0,
      humanNeedsData.previousFulfillmentScore || 0,
      analysisData.previousCommunicationScore || 0,
      analysisData.previousDecisionQuality || 0,
      analysisData.previousInnovationPotential || 0,
      organizationalData.previousLearningScore || 0
    ];

    return {
      labels: dimensions,
      datasets: [
        {
          label: 'Current Period',
          data: currentPeriod,
          backgroundColor: 'rgba(102, 126, 234, 0.2)',
          borderColor: 'rgba(102, 126, 234, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(102, 126, 234, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
        },
        {
          label: 'Previous Period',
          data: previousPeriod,
          backgroundColor: 'rgba(163, 177, 198, 0.2)',
          borderColor: 'rgba(163, 177, 198, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(163, 177, 198, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(163, 177, 198, 1)'
        }
      ]
    };
  }, [analysisData, humanNeedsData, organizationalData]);

  // Strategic alignment trend data
  const strategicTrendData = useMemo(() => {
    const frameworks = ['SDG', 'Doughnut Economy', 'Spiral Dynamics', 'Integral Theory'];
    const timeLabels = strategicData.timeline || [];
    
    return {
      labels: timeLabels,
      datasets: frameworks.map((framework, index) => ({
        label: framework,
        data: strategicData[framework.toLowerCase().replace(/\s+/g, '_')] || [],
        borderColor: [
          'rgba(72, 187, 120, 1)',
          'rgba(66, 153, 225, 1)',
          'rgba(237, 137, 54, 1)',
          'rgba(118, 75, 162, 1)'
        ][index],
        backgroundColor: [
          'rgba(72, 187, 120, 0.1)',
          'rgba(66, 153, 225, 0.1)',
          'rgba(237, 137, 54, 0.1)',
          'rgba(118, 75, 162, 0.1)'
        ][index],
        tension: 0.4,
        fill: true
      }))
    };
  }, [strategicData]);

  // Human needs distribution data
  const humanNeedsDistribution = useMemo(() => {
    const needs = humanNeedsData.needsBreakdown || {};
    const labels = Object.keys(needs);
    const values = Object.values(needs);
    
    return {
      labels,
      datasets: [{
        data: values,
        backgroundColor: [
          'rgba(72, 187, 120, 0.8)',
          'rgba(66, 153, 225, 0.8)',
          'rgba(237, 137, 54, 0.8)',
          'rgba(245, 101, 101, 0.8)',
          'rgba(118, 75, 162, 0.8)',
          'rgba(102, 126, 234, 0.8)',
          'rgba(163, 177, 198, 0.8)'
        ],
        borderColor: [
          'rgba(72, 187, 120, 1)',
          'rgba(66, 153, 225, 1)',
          'rgba(237, 137, 54, 1)',
          'rgba(245, 101, 101, 1)',
          'rgba(118, 75, 162, 1)',
          'rgba(102, 126, 234, 1)',
          'rgba(163, 177, 198, 1)'
        ],
        borderWidth: 2
      }]
    };
  }, [humanNeedsData]);

  // Organizational learning evolution data
  const learningEvolutionData = useMemo(() => {
    const metrics = ['Knowledge Creation', 'Knowledge Transfer', 'Wisdom Development', 'Collective Intelligence'];
    const timeline = organizationalData.timeline || [];
    
    return {
      labels: timeline,
      datasets: metrics.map((metric, index) => ({
        label: metric,
        data: organizationalData[metric.toLowerCase().replace(/\s+/g, '_')] || [],
        backgroundColor: [
          'rgba(72, 187, 120, 0.6)',
          'rgba(66, 153, 225, 0.6)',
          'rgba(237, 137, 54, 0.6)',
          'rgba(118, 75, 162, 0.6)'
        ][index],
        borderColor: [
          'rgba(72, 187, 120, 1)',
          'rgba(66, 153, 225, 1)',
          'rgba(237, 137, 54, 1)',
          'rgba(118, 75, 162, 1)'
        ][index],
        borderWidth: 1
      }))
    };
  }, [organizationalData]);

  // Chart options
  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'var(--text-primary)',
          font: {
            family: 'var(--font-family-primary)'
          }
        }
      },
      tooltip: {
        backgroundColor: 'var(--primary-bg)',
        titleColor: 'var(--text-primary)',
        bodyColor: 'var(--text-secondary)',
        borderColor: 'var(--accent-color)',
        borderWidth: 1
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: {
          color: 'var(--text-muted)',
          font: {
            size: 12
          }
        },
        grid: {
          color: 'rgba(163, 177, 198, 0.3)'
        },
        angleLines: {
          color: 'rgba(163, 177, 198, 0.3)'
        }
      }
    },
    animation: {
      duration: animationsEnabled ? 1000 : 0
    }
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'var(--text-primary)',
          font: {
            family: 'var(--font-family-primary)'
          }
        }
      },
      tooltip: {
        backgroundColor: 'var(--primary-bg)',
        titleColor: 'var(--text-primary)',
        bodyColor: 'var(--text-secondary)',
        borderColor: 'var(--accent-color)',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        ticks: {
          color: 'var(--text-muted)'
        },
        grid: {
          color: 'rgba(163, 177, 198, 0.2)'
        }
      },
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          color: 'var(--text-muted)'
        },
        grid: {
          color: 'rgba(163, 177, 198, 0.2)'
        }
      }
    },
    animation: {
      duration: animationsEnabled ? 1000 : 0
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: 'var(--text-primary)',
          font: {
            family: 'var(--font-family-primary)'
          },
          padding: 20
        }
      },
      tooltip: {
        backgroundColor: 'var(--primary-bg)',
        titleColor: 'var(--text-primary)',
        bodyColor: 'var(--text-secondary)',
        borderColor: 'var(--accent-color)',
        borderWidth: 1
      }
    },
    animation: {
      duration: animationsEnabled ? 1000 : 0
    }
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'var(--text-primary)',
          font: {
            family: 'var(--font-family-primary)'
          }
        }
      },
      tooltip: {
        backgroundColor: 'var(--primary-bg)',
        titleColor: 'var(--text-primary)',
        bodyColor: 'var(--text-secondary)',
        borderColor: 'var(--accent-color)',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        ticks: {
          color: 'var(--text-muted)'
        },
        grid: {
          color: 'rgba(163, 177, 198, 0.2)'
        }
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: 'var(--text-muted)'
        },
        grid: {
          color: 'rgba(163, 177, 198, 0.2)'
        }
      }
    },
    animation: {
      duration: animationsEnabled ? 1000 : 0
    }
  };

  // Key metrics calculation
  const keyMetrics = useMemo(() => {
    return {
      overallScore: Math.round(
        (sixDimensionalData.datasets[0].data.reduce((a, b) => a + b, 0) / 6) || 0
      ),
      improvement: Math.round(
        ((sixDimensionalData.datasets[0].data.reduce((a, b) => a + b, 0) - 
          sixDimensionalData.datasets[1].data.reduce((a, b) => a + b, 0)) / 6) || 0
      ),
      strategicAlignment: Math.round(strategicData.overallAlignment || 0),
      humanNeedsFulfillment: Math.round(humanNeedsData.overallFulfillment || 0),
      learningVelocity: Math.round(organizationalData.learningVelocity || 0),
      decisionEffectiveness: Math.round(analysisData.decisionEffectiveness || 0)
    };
  }, [sixDimensionalData, strategicData, humanNeedsData, organizationalData, analysisData]);

  // Handle metric selection for comparison
  const handleMetricToggle = useCallback((metric) => {
    setSelectedMetrics(prev => 
      prev.includes(metric) 
        ? prev.filter(m => m !== metric)
        : [...prev, metric]
    );
  }, []);

  // Handle chart interactions
  const handleChartClick = useCallback((event, elements, chartType, dataIndex) => {
    if (elements.length > 0 && onDrillDown) {
      const element = elements[0];
      onDrillDown({
        chartType,
        dataIndex: element.index,
        value: element.element.$context.parsed,
        label: element.element.$context.label
      });
    }
  }, [onDrillDown]);

  return (
    <div className={`analytics-dashboard ${className}`}>
      {/* Dashboard Header */}
      <div className="analytics-dashboard__header">
        <div className="analytics-dashboard__title-section">
          <h1 className="analytics-dashboard__title">Analytics Dashboard</h1>
          <p className="analytics-dashboard__subtitle">
            Comprehensive visualization and analysis across six dimensions
          </p>
        </div>
        
        <div className="analytics-dashboard__controls">
          {/* Time Range Selector */}
          <div className="analytics-dashboard__time-range">
            <label htmlFor="time-range">Time Range:</label>
            <select
              id="time-range"
              className="neu-input"
              value={timeRange}
              onChange={(e) => onTimeRangeChange?.(e.target.value)}
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
          </div>
          
          {/* View Toggle */}
          <div className="analytics-dashboard__view-toggle">
            <button
              className={`neu-button ${activeView === 'overview' ? 'neu-button--primary' : ''}`}
              onClick={() => setActiveView('overview')}
            >
              Overview
            </button>
            <button
              className={`neu-button ${activeView === 'detailed' ? 'neu-button--primary' : ''}`}
              onClick={() => setActiveView('detailed')}
            >
              Detailed
            </button>
            <button
              className={`neu-button ${activeView === 'trends' ? 'neu-button--primary' : ''}`}
              onClick={() => setActiveView('trends')}
            >
              Trends
            </button>
          </div>
          
          {/* Options */}
          <div className="analytics-dashboard__options">
            <div className="neu-toggle">
              <input
                type="checkbox"
                className="neu-toggle__input"
                id="comparison-mode"
                checked={comparisonMode}
                onChange={(e) => setComparisonMode(e.target.checked)}
              />
              <label htmlFor="comparison-mode" className="neu-toggle__slider"></label>
            </div>
            <label htmlFor="comparison-mode">Compare Periods</label>
          </div>
        </div>
      </div>

      {/* Key Metrics Summary */}
      <div className="analytics-dashboard__metrics-summary">
        <div className="metrics-grid">
          <div className="metric-card neu-card">
            <div className="metric-card__icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <div className="metric-card__content">
              <div className="metric-card__value">{keyMetrics.overallScore}</div>
              <div className="metric-card__label">Overall Score</div>
              <div className={`metric-card__change ${keyMetrics.improvement >= 0 ? 'positive' : 'negative'}`}>
                {keyMetrics.improvement >= 0 ? '+' : ''}{keyMetrics.improvement}
              </div>
            </div>
          </div>
          
          <div className="metric-card neu-card">
            <div className="metric-card__icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 11H7v6h2v-6zm4 0h-2v6h2v-6zm4 0h-2v6h2v-6zm2.5-9H19V1h-2v1H7V1H5v1H4.5C3.67 2 3 2.67 3 3.5v15C3 19.33 3.67 20 4.5 20h15c.83 0 1.5-.67 1.5-1.5v-15C21 2.67 20.33 2 19.5 2z"/>
              </svg>
            </div>
            <div className="metric-card__content">
              <div className="metric-card__value">{keyMetrics.strategicAlignment}</div>
              <div className="metric-card__label">Strategic Alignment</div>
            </div>
          </div>
          
          <div className="metric-card neu-card">
            <div className="metric-card__icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </div>
            <div className="metric-card__content">
              <div className="metric-card__value">{keyMetrics.humanNeedsFulfillment}</div>
              <div className="metric-card__label">Human Needs</div>
            </div>
          </div>
          
          <div className="metric-card neu-card">
            <div className="metric-card__icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6L23 9l-11-6zm6.82 6L12 12.72 5.18 9 12 5.28 18.82 9zM17 15.99l-5 2.73-5-2.73v-3.72L12 15l5-2.73v3.72z"/>
              </svg>
            </div>
            <div className="metric-card__content">
              <div className="metric-card__value">{keyMetrics.learningVelocity}</div>
              <div className="metric-card__label">Learning Velocity</div>
            </div>
          </div>
          
          <div className="metric-card neu-card">
            <div className="metric-card__icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div className="metric-card__content">
              <div className="metric-card__value">{keyMetrics.decisionEffectiveness}</div>
              <div className="metric-card__label">Decision Quality</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Dashboard Content */}
      <div className="analytics-dashboard__content">
        {activeView === 'overview' && (
          <ExpandableCardGroup
            title="Six-Dimensional Analysis Overview"
            layout="grid"
            columns={2}
            gap="large"
          >
            {/* Six-Dimensional Radar Chart */}
            <ExpandableCard
              title="Six-Dimensional Analysis"
              subtitle="Comprehensive performance across all dimensions"
              size="large"
              defaultExpanded={true}
              className="chart-card"
            >
              <div className="chart-container chart-container--radar">
                <Radar
                  data={sixDimensionalData}
                  options={radarOptions}
                  onClick={(event, elements) => handleChartClick(event, elements, 'radar')}
                />
              </div>
            </ExpandableCard>

            {/* Strategic Alignment Trends */}
            <ExpandableCard
              title="Strategic Framework Alignment"
              subtitle="Multi-framework scoring and trend analysis"
              size="large"
              defaultExpanded={true}
              className="chart-card"
            >
              <div className="chart-container chart-container--line">
                <Line
                  data={strategicTrendData}
                  options={lineOptions}
                  onClick={(event, elements) => handleChartClick(event, elements, 'strategic')}
                />
              </div>
            </ExpandableCard>

            {/* Human Needs Distribution */}
            <ExpandableCard
              title="Human Needs Distribution"
              subtitle="Individual and team pattern displays"
              size="large"
              defaultExpanded={true}
              className="chart-card"
            >
              <div className="chart-container chart-container--doughnut">
                <Doughnut
                  data={humanNeedsDistribution}
                  options={doughnutOptions}
                  onClick={(event, elements) => handleChartClick(event, elements, 'needs')}
                />
              </div>
            </ExpandableCard>

            {/* Organizational Learning Evolution */}
            <ExpandableCard
              title="Organizational Learning Evolution"
              subtitle="Knowledge evolution and wisdom development metrics"
              size="large"
              defaultExpanded={true}
              className="chart-card"
            >
              <div className="chart-container chart-container--bar">
                <Bar
                  data={learningEvolutionData}
                  options={barOptions}
                  onClick={(event, elements) => handleChartClick(event, elements, 'learning')}
                />
              </div>
            </ExpandableCard>
          </ExpandableCardGroup>
        )}

        {activeView === 'detailed' && (
          <DetailedAnalysisView
            analysisData={analysisData}
            strategicData={strategicData}
            humanNeedsData={humanNeedsData}
            organizationalData={organizationalData}
            selectedMetrics={selectedMetrics}
            onMetricToggle={handleMetricToggle}
            comparisonMode={comparisonMode}
          />
        )}

        {activeView === 'trends' && (
          <TrendsAnalysisView
            analysisData={analysisData}
            strategicData={strategicData}
            humanNeedsData={humanNeedsData}
            organizationalData={organizationalData}
            timeRange={timeRange}
          />
        )}
      </div>
    </div>
  );
};

// Detailed Analysis View Component
const DetailedAnalysisView = ({
  analysisData,
  strategicData,
  humanNeedsData,
  organizationalData,
  selectedMetrics,
  onMetricToggle,
  comparisonMode
}) => {
  return (
    <div className="detailed-analysis-view">
      <ExpandableCardGroup
        title="Detailed Analysis"
        subtitle="Deep dive into specific metrics and patterns"
        layout="grid"
        columns="auto"
      >
        {/* Detailed charts and analysis components would go here */}
        <ExpandableCard
          title="Communication Patterns"
          subtitle="Detailed communication effectiveness analysis"
          defaultExpanded={true}
        >
          <div className="detailed-metrics">
            <p>Detailed communication analysis would be displayed here with specific patterns, trends, and insights.</p>
          </div>
        </ExpandableCard>

        <ExpandableCard
          title="Decision Quality Breakdown"
          subtitle="Analysis of decision-making processes and outcomes"
          defaultExpanded={true}
        >
          <div className="detailed-metrics">
            <p>Decision quality metrics and breakdown would be displayed here.</p>
          </div>
        </ExpandableCard>
      </ExpandableCardGroup>
    </div>
  );
};

// Trends Analysis View Component
const TrendsAnalysisView = ({
  analysisData,
  strategicData,
  humanNeedsData,
  organizationalData,
  timeRange
}) => {
  return (
    <div className="trends-analysis-view">
      <ExpandableCardGroup
        title="Trends Analysis"
        subtitle="Historical trends and predictive insights"
        layout="grid"
        columns="auto"
      >
        <ExpandableCard
          title="Performance Trends"
          subtitle="Historical performance across all dimensions"
          defaultExpanded={true}
        >
          <div className="trends-content">
            <p>Performance trends over the selected time range would be displayed here.</p>
          </div>
        </ExpandableCard>

        <ExpandableCard
          title="Predictive Analytics"
          subtitle="Future performance predictions and recommendations"
          defaultExpanded={true}
        >
          <div className="trends-content">
            <p>Predictive analytics and forecasting would be displayed here.</p>
          </div>
        </ExpandableCard>
      </ExpandableCardGroup>
    </div>
  );
};

export default AnalyticsDashboard;