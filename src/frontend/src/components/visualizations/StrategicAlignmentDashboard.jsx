/**
 * Strategic Alignment Dashboard Component
 * Multi-framework scoring and trend analysis visualization
 */

import React, { useState, useMemo, useCallback } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import ExpandableCard, { ExpandableCardGroup } from '../ExpandableCard';
import './StrategicAlignmentDashboard.css';

const StrategicAlignmentDashboard = ({
  alignmentData = {},
  frameworkData = {},
  trendData = {},
  timeRange = '30d',
  onFrameworkSelect,
  onTrendAnalysis,
  className = ''
}) => {
  const [selectedFramework, setSelectedFramework] = useState('all');
  const [viewMode, setViewMode] = useState('overview');

  // Strategic frameworks configuration
  const frameworks = [
    {
      key: 'sdg',
      name: 'Sustainable Development Goals',
      shortName: 'SDG',
      description: 'UN Sustainable Development Goals alignment',
      color: 'rgba(72, 187, 120, 1)',
      icon: '🌍',
      goals: [
        'No Poverty', 'Zero Hunger', 'Good Health', 'Quality Education',
        'Gender Equality', 'Clean Water', 'Affordable Energy', 'Decent Work',
        'Industry Innovation', 'Reduced Inequalities', 'Sustainable Cities',
        'Responsible Consumption', 'Climate Action', 'Life Below Water',
        'Life on Land', 'Peace & Justice', 'Partnerships'
      ]
    },
    {
      key: 'doughnut',
      name: 'Doughnut Economy',
      shortName: 'Doughnut',
      description: 'Social foundation and ecological ceiling balance',
      color: 'rgba(66, 153, 225, 1)',
      icon: '🍩',
      dimensions: [
        'Social Foundation', 'Ecological Ceiling', 'Regenerative Design',
        'Distributive Design'
      ]
    },
    {
      key: 'spiral',
      name: 'Spiral Dynamics',
      shortName: 'Spiral',
      description: 'Value systems and consciousness levels',
      color: 'rgba(237, 137, 54, 1)',
      icon: '🌀',
      levels: [
        'Beige (Survival)', 'Purple (Tribal)', 'Red (Power)', 'Blue (Order)',
        'Orange (Achievement)', 'Green (Community)', 'Yellow (Integral)',
        'Turquoise (Holistic)'
      ]
    },
    {
      key: 'integral',
      name: 'Integral Theory',
      shortName: 'Integral',
      description: 'Four quadrants of individual/collective and interior/exterior',
      color: 'rgba(118, 75, 162, 1)',
      icon: '🔄',
      quadrants: [
        'Individual Interior (I)', 'Individual Exterior (It)',
        'Collective Interior (We)', 'Collective Exterior (Its)'
      ]
    }
  ];

  // Process alignment scores
  const alignmentScores = useMemo(() => {
    return frameworks.map(framework => ({
      ...framework,
      score: alignmentData[framework.key] || 0,
      previousScore: alignmentData[`${framework.key}_previous`] || 0,
      trend: (alignmentData[framework.key] || 0) - (alignmentData[`${framework.key}_previous`] || 0)
    }));
  }, [alignmentData, frameworks]);

  // Overall alignment score
  const overallAlignment = useMemo(() => {
    const scores = alignmentScores.map(f => f.score);
    return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
  }, [alignmentScores]);

  // Framework comparison chart data
  const comparisonChartData = useMemo(() => {
    return {
      labels: frameworks.map(f => f.shortName),
      datasets: [
        {
          label: 'Current Alignment',
          data: alignmentScores.map(f => f.score),
          backgroundColor: frameworks.map(f => f.color.replace('1)', '0.6)')),
          borderColor: frameworks.map(f => f.color),
          borderWidth: 2,
          borderRadius: 4
        },
        {
          label: 'Previous Period',
          data: alignmentScores.map(f => f.previousScore),
          backgroundColor: 'rgba(163, 177, 198, 0.3)',
          borderColor: 'rgba(163, 177, 198, 1)',
          borderWidth: 1,
          borderRadius: 4
        }
      ]
    };
  }, [alignmentScores, frameworks]);

  // Trend analysis data
  const trendChartData = useMemo(() => {
    const timeLabels = trendData.timeline || [];
    
    return {
      labels: timeLabels,
      datasets: frameworks.map(framework => ({
        label: framework.shortName,
        data: trendData[framework.key] || [],
        borderColor: framework.color,
        backgroundColor: framework.color.replace('1)', '0.1)'),
        tension: 0.4,
        fill: false,
        pointRadius: 4,
        pointHoverRadius: 6
      }))
    };
  }, [trendData, frameworks]);

  // Framework distribution data
  const distributionData = useMemo(() => {
    return {
      labels: frameworks.map(f => f.shortName),
      datasets: [{
        data: alignmentScores.map(f => f.score),
        backgroundColor: frameworks.map(f => f.color.replace('1)', '0.8)')),
        borderColor: frameworks.map(f => f.color),
        borderWidth: 2
      }]
    };
  }, [alignmentScores, frameworks]);

  // Chart options
  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'var(--text-primary)',
          font: { family: 'var(--font-family-primary)' }
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
        ticks: { color: 'var(--text-muted)' },
        grid: { color: 'rgba(163, 177, 198, 0.2)' }
      },
      y: {
        beginAtZero: true,
        max: 100,
        ticks: { 
          color: 'var(--text-muted)',
          callback: (value) => `${value}%`
        },
        grid: { color: 'rgba(163, 177, 198, 0.2)' }
      }
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
          font: { family: 'var(--font-family-primary)' }
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
        ticks: { color: 'var(--text-muted)' },
        grid: { color: 'rgba(163, 177, 198, 0.2)' }
      },
      y: {
        beginAtZero: true,
        max: 100,
        ticks: { 
          color: 'var(--text-muted)',
          callback: (value) => `${value}%`
        },
        grid: { color: 'rgba(163, 177, 198, 0.2)' }
      }
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
          font: { family: 'var(--font-family-primary)' },
          padding: 20
        }
      },
      tooltip: {
        backgroundColor: 'var(--primary-bg)',
        titleColor: 'var(--text-primary)',
        bodyColor: 'var(--text-secondary)',
        borderColor: 'var(--accent-color)',
        borderWidth: 1,
        callbacks: {
          label: (context) => {
            const value = context.parsed;
            return `${context.label}: ${Math.round(value)}%`;
          }
        }
      }
    }
  };

  // Handle framework selection
  const handleFrameworkSelect = useCallback((framework) => {
    setSelectedFramework(framework.key);
    onFrameworkSelect?.(framework);
  }, [onFrameworkSelect]);

  return (
    <div className={`strategic-alignment-dashboard ${className}`}>
      {/* Dashboard Header */}
      <div className="strategic-alignment-dashboard__header">
        <div className="dashboard-title">
          <h2>Strategic Alignment Dashboard</h2>
          <p>Multi-framework scoring and trend analysis</p>
        </div>
        
        <div className="dashboard-controls">
          <div className="view-toggle">
            <button
              className={`neu-button ${viewMode === 'overview' ? 'neu-button--primary' : ''}`}
              onClick={() => setViewMode('overview')}
            >
              Overview
            </button>
            <button
              className={`neu-button ${viewMode === 'detailed' ? 'neu-button--primary' : ''}`}
              onClick={() => setViewMode('detailed')}
            >
              Detailed
            </button>
            <button
              className={`neu-button ${viewMode === 'trends' ? 'neu-button--primary' : ''}`}
              onClick={() => setViewMode('trends')}
            >
              Trends
            </button>
          </div>
        </div>
      </div>

      {/* Overall Alignment Score */}
      <div className="overall-alignment-card neu-card">
        <div className="overall-alignment__content">
          <div className="overall-alignment__score">
            <span className="score-value">{overallAlignment}</span>
            <span className="score-label">Overall Strategic Alignment</span>
          </div>
          
          <div className="framework-scores">
            {alignmentScores.map(framework => (
              <div
                key={framework.key}
                className={`framework-score ${selectedFramework === framework.key ? 'selected' : ''}`}
                onClick={() => handleFrameworkSelect(framework)}
              >
                <div className="framework-score__icon">{framework.icon}</div>
                <div className="framework-score__content">
                  <div className="framework-score__name">{framework.shortName}</div>
                  <div className="framework-score__value">
                    {Math.round(framework.score)}%
                    {framework.trend !== 0 && (
                      <span className={`trend ${framework.trend > 0 ? 'positive' : 'negative'}`}>
                        {framework.trend > 0 ? '+' : ''}{Math.round(framework.trend)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="strategic-alignment-dashboard__content">
        {viewMode === 'overview' && (
          <ExpandableCardGroup layout="grid" columns={2} gap="large">
            {/* Framework Comparison */}
            <ExpandableCard
              title="Framework Comparison"
              subtitle="Current vs previous period alignment scores"
              size="large"
              defaultExpanded={true}
            >
              <div className="chart-container">
                <Bar data={comparisonChartData} options={barOptions} />
              </div>
            </ExpandableCard>

            {/* Alignment Distribution */}
            <ExpandableCard
              title="Alignment Distribution"
              subtitle="Relative alignment across frameworks"
              size="large"
              defaultExpanded={true}
            >
              <div className="chart-container">
                <Doughnut data={distributionData} options={doughnutOptions} />
              </div>
            </ExpandableCard>
          </ExpandableCardGroup>
        )}

        {viewMode === 'detailed' && (
          <div className="detailed-framework-analysis">
            <ExpandableCardGroup layout="grid" columns="auto">
              {frameworks.map(framework => {
                const frameworkScore = alignmentScores.find(f => f.key === framework.key);
                return (
                  <ExpandableCard
                    key={framework.key}
                    title={framework.name}
                    subtitle={framework.description}
                    badge={{
                      text: `${Math.round(frameworkScore?.score || 0)}%`,
                      type: frameworkScore?.score > 75 ? 'success' : 
                            frameworkScore?.score > 50 ? 'warning' : 'error'
                    }}
                    icon={framework.icon}
                    defaultExpanded={selectedFramework === framework.key}
                  >
                    <div className="framework-details">
                      <div className="framework-score-breakdown">
                        <div className="score-item">
                          <span className="score-item__label">Current Score</span>
                          <span className="score-item__value">{Math.round(frameworkScore?.score || 0)}%</span>
                        </div>
                        <div className="score-item">
                          <span className="score-item__label">Previous Score</span>
                          <span className="score-item__value">{Math.round(frameworkScore?.previousScore || 0)}%</span>
                        </div>
                        <div className="score-item">
                          <span className="score-item__label">Change</span>
                          <span className={`score-item__value ${frameworkScore?.trend >= 0 ? 'positive' : 'negative'}`}>
                            {frameworkScore?.trend >= 0 ? '+' : ''}{Math.round(frameworkScore?.trend || 0)}%
                          </span>
                        </div>
                      </div>
                      
                      {framework.goals && (
                        <div className="framework-goals">
                          <h4>SDG Goals</h4>
                          <div className="goals-grid">
                            {framework.goals.map((goal, index) => (
                              <div key={index} className="goal-item">
                                <span className="goal-number">{index + 1}</span>
                                <span className="goal-name">{goal}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {framework.dimensions && (
                        <div className="framework-dimensions">
                          <h4>Key Dimensions</h4>
                          <ul>
                            {framework.dimensions.map((dimension, index) => (
                              <li key={index}>{dimension}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {framework.levels && (
                        <div className="framework-levels">
                          <h4>Consciousness Levels</h4>
                          <ul>
                            {framework.levels.map((level, index) => (
                              <li key={index}>{level}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {framework.quadrants && (
                        <div className="framework-quadrants">
                          <h4>Four Quadrants</h4>
                          <ul>
                            {framework.quadrants.map((quadrant, index) => (
                              <li key={index}>{quadrant}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </ExpandableCard>
                );
              })}
            </ExpandableCardGroup>
          </div>
        )}

        {viewMode === 'trends' && (
          <ExpandableCardGroup layout="grid" columns={1}>
            <ExpandableCard
              title="Strategic Alignment Trends"
              subtitle={`Framework alignment over ${timeRange}`}
              size="large"
              defaultExpanded={true}
            >
              <div className="chart-container chart-container--large">
                <Line data={trendChartData} options={lineOptions} />
              </div>
            </ExpandableCard>
          </ExpandableCardGroup>
        )}
      </div>
    </div>
  );
};

export default StrategicAlignmentDashboard;