/**
 * Human Needs Visualization Component
 * Visualizes individual and team human needs patterns with fulfillment tracking
 */

import React, { useState, useMemo, useCallback } from 'react';
import { Radar, Doughnut, Bar, Line } from 'react-chartjs-2';
import ExpandableCard, { ExpandableCardGroup } from '../ExpandableCard';
import './HumanNeedsVisualization.css';

const HumanNeedsVisualization = ({
  needsData = {},
  individualData = {},
  teamData = {},
  historicalData = {},
  onNeedSelect,
  onPersonSelect,
  onImbalanceDetected,
  className = ''
}) => {
  const [selectedNeed, setSelectedNeed] = useState(null);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [viewMode, setViewMode] = useState('team');
  const [timeRange, setTimeRange] = useState('30d');

  // Human needs configuration
  const humanNeeds = [
    {
      id: 'subsistence',
      name: 'Subsistence',
      description: 'Physical health, food, shelter, rest, movement',
      color: 'rgba(72, 187, 120, 1)',
      icon: '🍃',
      examples: ['Health', 'Food', 'Rest', 'Shelter', 'Air', 'Water', 'Movement']
    },
    {
      id: 'protection',
      name: 'Protection',
      description: 'Safety, security, stability, peace',
      color: 'rgba(66, 153, 225, 1)',
      icon: '🛡️',
      examples: ['Safety', 'Security', 'Stability', 'Peace', 'Order', 'Predictability']
    },
    {
      id: 'affection',
      name: 'Affection',
      description: 'Love, relationships, intimacy, connection',
      color: 'rgba(237, 100, 166, 1)',
      icon: '❤️',
      examples: ['Love', 'Friendship', 'Intimacy', 'Connection', 'Belonging']
    },
    {
      id: 'understanding',
      name: 'Understanding',
      description: 'Learning, growth, curiosity, meaning',
      color: 'rgba(102, 126, 234, 1)',
      icon: '🧠',
      examples: ['Knowledge', 'Learning', 'Curiosity', 'Growth', 'Clarity']
    },
    {
      id: 'participation',
      name: 'Participation',
      description: 'Engagement, contribution, collaboration',
      color: 'rgba(237, 137, 54, 1)',
      icon: '🤝',
      examples: ['Involvement', 'Contribution', 'Cooperation', 'Community']
    },
    {
      id: 'leisure',
      name: 'Leisure',
      description: 'Play, relaxation, enjoyment, creativity',
      color: 'rgba(246, 224, 94, 1)',
      icon: '🎮',
      examples: ['Play', 'Relaxation', 'Humor', 'Joy', 'Pleasure']
    },
    {
      id: 'creation',
      name: 'Creation',
      description: 'Creativity, purpose, contribution, expression',
      color: 'rgba(159, 122, 234, 1)',
      icon: '🎨',
      examples: ['Creativity', 'Purpose', 'Productivity', 'Expression']
    },
    {
      id: 'identity',
      name: 'Identity',
      description: 'Autonomy, authenticity, self-worth, meaning',
      color: 'rgba(245, 101, 101, 1)',
      icon: '🧿',
      examples: ['Autonomy', 'Authenticity', 'Self-worth', 'Meaning']
    },
    {
      id: 'freedom',
      name: 'Freedom',
      description: 'Choice, independence, space, spontaneity',
      color: 'rgba(49, 151, 149, 1)',
      icon: '🕊️',
      examples: ['Choice', 'Independence', 'Space', 'Spontaneity']
    }
  ];

  // Process team needs data
  const teamNeedsData = useMemo(() => {
    const needsValues = humanNeeds.map(need => needsData[need.id] || 0);
    const previousValues = humanNeeds.map(need => needsData[`${need.id}_previous`] || 0);

    return {
      labels: humanNeeds.map(need => need.name),
      datasets: [
        {
          label: 'Current Period',
          data: needsValues,
          backgroundColor: 'rgba(102, 126, 234, 0.2)',
          borderColor: 'rgba(102, 126, 234, 1)',
          borderWidth: 2,
          pointBackgroundColor: humanNeeds.map(need => need.color),
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: humanNeeds.map(need => need.color),
          pointRadius: 5,
          pointHoverRadius: 7
        },
        {
          label: 'Previous Period',
          data: previousValues,
          backgroundColor: 'rgba(163, 177, 198, 0.1)',
          borderColor: 'rgba(163, 177, 198, 0.8)',
          borderWidth: 1,
          borderDash: [5, 5],
          pointBackgroundColor: 'rgba(163, 177, 198, 0.8)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(163, 177, 198, 0.8)',
          pointRadius: 3,
          pointHoverRadius: 5
        }
      ]
    };
  }, [needsData, humanNeeds]);

  // Process individual needs data
  const individualNeedsData = useMemo(() => {
    if (!selectedPerson || !individualData[selectedPerson]) {
      return null;
    }

    const personData = individualData[selectedPerson];
    const needsValues = humanNeeds.map(need => personData[need.id] || 0);

    return {
      labels: humanNeeds.map(need => need.name),
      datasets: [
        {
          label: selectedPerson,
          data: needsValues,
          backgroundColor: 'rgba(159, 122, 234, 0.2)',
          borderColor: 'rgba(159, 122, 234, 1)',
          borderWidth: 2,
          pointBackgroundColor: humanNeeds.map(need => need.color),
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: humanNeeds.map(need => need.color),
          pointRadius: 5,
          pointHoverRadius: 7
        },
        {
          label: 'Team Average',
          data: humanNeeds.map(need => needsData[need.id] || 0),
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          borderColor: 'rgba(102, 126, 234, 0.8)',
          borderWidth: 1,
          borderDash: [5, 5],
          pointBackgroundColor: 'rgba(102, 126, 234, 0.8)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(102, 126, 234, 0.8)',
          pointRadius: 3,
          pointHoverRadius: 5
        }
      ]
    };
  }, [selectedPerson, individualData, humanNeeds, needsData]);

  // Process needs distribution data
  const needsDistributionData = useMemo(() => {
    return {
      labels: humanNeeds.map(need => need.name),
      datasets: [
        {
          data: humanNeeds.map(need => needsData[need.id] || 0),
          backgroundColor: humanNeeds.map(need => need.color.replace('1)', '0.8)')),
          borderColor: humanNeeds.map(need => need.color),
          borderWidth: 2
        }
      ]
    };
  }, [needsData, humanNeeds]);

  // Process historical trend data
  const historicalTrendData = useMemo(() => {
    const timeLabels = historicalData.timeline || [];
    const selectedNeedId = selectedNeed?.id || 'overall';
    
    return {
      labels: timeLabels,
      datasets: [
        {
          label: selectedNeed?.name || 'Overall Fulfillment',
          data: historicalData[selectedNeedId] || [],
          borderColor: selectedNeed?.color || 'rgba(102, 126, 234, 1)',
          backgroundColor: (selectedNeed?.color || 'rgba(102, 126, 234, 1)').replace('1)', '0.1)'),
          tension: 0.4,
          fill: true
        }
      ]
    };
  }, [historicalData, selectedNeed]);

  // Calculate team needs fulfillment score
  const teamFulfillmentScore = useMemo(() => {
    const needsValues = humanNeeds.map(need => needsData[need.id] || 0);
    return Math.round(needsValues.reduce((sum, val) => sum + val, 0) / needsValues.length);
  }, [needsData, humanNeeds]);

  // Detect imbalances in needs fulfillment
  const needsImbalances = useMemo(() => {
    const needsValues = humanNeeds.map(need => ({
      need,
      value: needsData[need.id] || 0
    }));
    
    // Calculate average and standard deviation
    const values = needsValues.map(item => item.value);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    
    // Identify significant imbalances (more than 1.5 standard deviations from mean)
    const threshold = stdDev * 1.5;
    const imbalances = needsValues.filter(item => 
      Math.abs(item.value - avg) > threshold
    );
    
    return imbalances.map(item => ({
      need: item.need,
      value: item.value,
      deviation: Math.round((item.value - avg) / stdDev * 10) / 10,
      type: item.value > avg ? 'excess' : 'deficiency'
    }));
  }, [needsData, humanNeeds]);

  // Notify parent component about imbalances
  React.useEffect(() => {
    if (needsImbalances.length > 0 && onImbalanceDetected) {
      onImbalanceDetected(needsImbalances);
    }
  }, [needsImbalances, onImbalanceDetected]);

  // Handle need selection
  const handleNeedSelect = useCallback((need) => {
    setSelectedNeed(prev => prev?.id === need.id ? null : need);
    onNeedSelect?.(need);
  }, [onNeedSelect]);

  // Handle person selection
  const handlePersonSelect = useCallback((person) => {
    setSelectedPerson(prev => prev === person ? null : person);
    setViewMode('individual');
    onPersonSelect?.(person);
  }, [onPersonSelect]);

  // Chart options
  const radarOptions = {
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
        borderWidth: 1,
        callbacks: {
          title: (context) => {
            const need = humanNeeds[context[0].dataIndex];
            return `${need.icon} ${need.name}`;
          },
          label: (context) => {
            return `${context.dataset.label}: ${Math.round(context.raw)}%`;
          },
          afterLabel: (context) => {
            const need = humanNeeds[context.dataIndex];
            return need.description;
          }
        }
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        min: 0,
        max: 100,
        ticks: {
          stepSize: 20,
          color: 'var(--text-muted)',
          backdropColor: 'transparent'
        },
        grid: {
          color: 'rgba(163, 177, 198, 0.3)'
        },
        angleLines: {
          color: 'rgba(163, 177, 198, 0.3)'
        },
        pointLabels: {
          color: 'var(--text-primary)',
          font: {
            size: 12
          }
        }
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

  // Get team members list
  const teamMembers = useMemo(() => {
    return Object.keys(individualData).map(person => ({
      id: person,
      name: person,
      score: calculatePersonScore(person)
    }));
  }, [individualData]);

  // Calculate person's overall needs score
  function calculatePersonScore(personId) {
    if (!individualData[personId]) return 0;
    
    const personData = individualData[personId];
    const needsValues = humanNeeds.map(need => personData[need.id] || 0);
    return Math.round(needsValues.reduce((sum, val) => sum + val, 0) / needsValues.length);
  }

  return (
    <div className={`human-needs-visualization ${className}`}>
      {/* Header */}
      <div className="human-needs-visualization__header">
        <div className="header-content">
          <h2>Human Needs Visualization</h2>
          <p>Individual and team pattern displays with fulfillment tracking</p>
        </div>
        
        <div className="header-controls">
          <div className="view-toggle">
            <button
              className={`neu-button ${viewMode === 'team' ? 'neu-button--primary' : ''}`}
              onClick={() => setViewMode('team')}
            >
              Team View
            </button>
            <button
              className={`neu-button ${viewMode === 'individual' ? 'neu-button--primary' : ''}`}
              onClick={() => setViewMode('individual')}
            >
              Individual View
            </button>
            <button
              className={`neu-button ${viewMode === 'trends' ? 'neu-button--primary' : ''}`}
              onClick={() => setViewMode('trends')}
            >
              Trends
            </button>
          </div>
          
          <div className="time-range-selector">
            <label htmlFor="time-range">Time Range:</label>
            <select
              id="time-range"
              className="neu-input"
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
          </div>
        </div>
      </div>

      {/* Overall Fulfillment Score */}
      <div className="fulfillment-score-card neu-card">
        <div className="fulfillment-score__content">
          <div className="fulfillment-score__gauge">
            <div 
              className="fulfillment-score__gauge-fill"
              style={{ width: `${teamFulfillmentScore}%` }}
            >
              <span className="fulfillment-score__value">{teamFulfillmentScore}%</span>
            </div>
          </div>
          <div className="fulfillment-score__label">
            {viewMode === 'individual' && selectedPerson ? 
              `${selectedPerson}'s Needs Fulfillment` : 
              'Team Needs Fulfillment'}
          </div>
        </div>
        
        {needsImbalances.length > 0 && (
          <div className="imbalance-alerts">
            <h4>Detected Imbalances</h4>
            <div className="imbalance-list">
              {needsImbalances.map((imbalance, index) => (
                <div 
                  key={index} 
                  className={`imbalance-item imbalance-item--${imbalance.type}`}
                  onClick={() => handleNeedSelect(imbalance.need)}
                >
                  <div className="imbalance-item__icon">{imbalance.need.icon}</div>
                  <div className="imbalance-item__content">
                    <div className="imbalance-item__title">
                      {imbalance.need.name}: {imbalance.type === 'excess' ? 'Excess' : 'Deficiency'}
                    </div>
                    <div className="imbalance-item__details">
                      {imbalance.value}% ({imbalance.deviation > 0 ? '+' : ''}{imbalance.deviation}σ)
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="human-needs-visualization__content">
        {viewMode === 'team' && (
          <ExpandableCardGroup layout="grid" columns={2} gap="large">
            {/* Team Needs Radar */}
            <ExpandableCard
              title="Team Needs Pattern"
              subtitle="Comprehensive view of team needs fulfillment"
              size="large"
              defaultExpanded={true}
            >
              <div className="chart-container chart-container--radar">
                <Radar data={teamNeedsData} options={radarOptions} />
              </div>
            </ExpandableCard>

            {/* Needs Distribution */}
            <ExpandableCard
              title="Needs Distribution"
              subtitle="Relative fulfillment across different needs"
              size="large"
              defaultExpanded={true}
            >
              <div className="chart-container chart-container--doughnut">
                <Doughnut data={needsDistributionData} options={doughnutOptions} />
              </div>
            </ExpandableCard>

            {/* Needs Details */}
            <ExpandableCard
              title="Human Needs Details"
              subtitle="Click on a need to see more information"
              size="large"
              defaultExpanded={true}
              className="span-full"
            >
              <div className="needs-grid">
                {humanNeeds.map(need => {
                  const needValue = needsData[need.id] || 0;
                  const previousValue = needsData[`${need.id}_previous`] || 0;
                  const change = needValue - previousValue;
                  
                  return (
                    <div 
                      key={need.id} 
                      className={`need-card ${selectedNeed?.id === need.id ? 'selected' : ''}`}
                      onClick={() => handleNeedSelect(need)}
                    >
                      <div className="need-card__header">
                        <div 
                          className="need-card__icon"
                          style={{ backgroundColor: need.color }}
                        >
                          {need.icon}
                        </div>
                        <div className="need-card__title">{need.name}</div>
                      </div>
                      
                      <div className="need-card__content">
                        <div className="need-card__description">{need.description}</div>
                        <div className="need-card__score">
                          <div className="need-card__score-value">{Math.round(needValue)}%</div>
                          {change !== 0 && (
                            <div className={`need-card__change ${change > 0 ? 'positive' : 'negative'}`}>
                              {change > 0 ? '+' : ''}{Math.round(change)}%
                            </div>
                          )}
                        </div>
                        <div className="need-card__progress">
                          <div className="progress-bar">
                            <div 
                              className="progress-bar__fill"
                              style={{ 
                                width: `${needValue}%`,
                                backgroundColor: need.color
                              }}
                            />
                          </div>
                        </div>
                      </div>
                      
                      {selectedNeed?.id === need.id && (
                        <div className="need-card__examples">
                          <h5>Examples</h5>
                          <div className="examples-list">
                            {need.examples.map((example, i) => (
                              <div key={i} className="example-tag">{example}</div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </ExpandableCard>
          </ExpandableCardGroup>
        )}

        {viewMode === 'individual' && (
          <div className="individual-view">
            <div className="team-members-list">
              <h3>Team Members</h3>
              <div className="members-grid">
                {teamMembers.map(person => (
                  <div 
                    key={person.id} 
                    className={`person-card ${selectedPerson === person.id ? 'selected' : ''}`}
                    onClick={() => handlePersonSelect(person.id)}
                  >
                    <div className="person-card__avatar">
                      {person.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="person-card__content">
                      <div className="person-card__name">{person.name}</div>
                      <div className="person-card__score">{person.score}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {selectedPerson && individualNeedsData && (
              <ExpandableCardGroup layout="grid" columns={1}>
                <ExpandableCard
                  title={`${selectedPerson}'s Needs Pattern`}
                  subtitle="Individual needs compared to team average"
                  size="large"
                  defaultExpanded={true}
                >
                  <div className="chart-container chart-container--radar">
                    <Radar data={individualNeedsData} options={radarOptions} />
                  </div>
                </ExpandableCard>
                
                <ExpandableCard
                  title="Individual Needs Details"
                  subtitle="Detailed breakdown of individual needs"
                  size="large"
                  defaultExpanded={true}
                >
                  <div className="individual-needs-details">
                    {humanNeeds.map(need => {
                      const personData = individualData[selectedPerson];
                      const needValue = personData?.[need.id] || 0;
                      const teamValue = needsData[need.id] || 0;
                      const difference = needValue - teamValue;
                      
                      return (
                        <div key={need.id} className="individual-need-item">
                          <div 
                            className="individual-need-item__icon"
                            style={{ backgroundColor: need.color }}
                          >
                            {need.icon}
                          </div>
                          
                          <div className="individual-need-item__content">
                            <div className="individual-need-item__name">{need.name}</div>
                            <div className="individual-need-item__bars">
                              <div className="comparison-bars">
                                <div className="comparison-bar">
                                  <div className="comparison-bar__label">Individual</div>
                                  <div className="comparison-bar__track">
                                    <div 
                                      className="comparison-bar__fill"
                                      style={{ 
                                        width: `${needValue}%`,
                                        backgroundColor: need.color
                                      }}
                                    />
                                  </div>
                                  <div className="comparison-bar__value">{Math.round(needValue)}%</div>
                                </div>
                                
                                <div className="comparison-bar">
                                  <div className="comparison-bar__label">Team Avg</div>
                                  <div className="comparison-bar__track">
                                    <div 
                                      className="comparison-bar__fill"
                                      style={{ 
                                        width: `${teamValue}%`,
                                        backgroundColor: 'rgba(102, 126, 234, 0.8)'
                                      }}
                                    />
                                  </div>
                                  <div className="comparison-bar__value">{Math.round(teamValue)}%</div>
                                </div>
                              </div>
                              
                              <div className="difference-indicator">
                                <span className={difference > 0 ? 'positive' : difference < 0 ? 'negative' : ''}>
                                  {difference > 0 ? '+' : ''}{Math.round(difference)}%
                                </span>
                                <span className="difference-label">vs team</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </ExpandableCard>
              </ExpandableCardGroup>
            )}
            
            {!selectedPerson && (
              <div className="select-person-prompt">
                <div className="neu-card">
                  <div className="prompt-content">
                    <div className="prompt-icon">👤</div>
                    <h3>Select a Team Member</h3>
                    <p>Click on a team member above to view their individual needs pattern.</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {viewMode === 'trends' && (
          <ExpandableCardGroup layout="grid" columns={1}>
            <ExpandableCard
              title="Needs Fulfillment Trends"
              subtitle={selectedNeed ? `${selectedNeed.name} over time` : 'Overall fulfillment over time'}
              size="large"
              defaultExpanded={true}
            >
              <div className="chart-container chart-container--line">
                <Line data={historicalTrendData} options={lineOptions} />
              </div>
            </ExpandableCard>
            
            <ExpandableCard
              title="Select Need to Track"
              subtitle="Click on a need to see its historical trend"
              size="large"
              defaultExpanded={true}
            >
              <div className="needs-selector">
                <div className="needs-selector__grid">
                  {humanNeeds.map(need => (
                    <button
                      key={need.id}
                      className={`need-selector-button ${selectedNeed?.id === need.id ? 'selected' : ''}`}
                      onClick={() => handleNeedSelect(need)}
                      style={{ borderColor: need.color }}
                    >
                      <div className="need-selector-button__icon" style={{ backgroundColor: need.color }}>
                        {need.icon}
                      </div>
                      <div className="need-selector-button__name">{need.name}</div>
                    </button>
                  ))}
                </div>
              </div>
            </ExpandableCard>
          </ExpandableCardGroup>
        )}
      </div>
    </div>
  );
};

export default HumanNeedsVisualization;