/**
 * Six-Dimensional Analysis Chart Component
 * Specialized radar chart for six-dimensional organizational analysis
 */

import React, { useMemo, useCallback } from 'react';
import { Radar } from 'react-chartjs-2';
import './SixDimensionalChart.css';

const SixDimensionalChart = ({
  data = {},
  comparisonData = null,
  showComparison = false,
  interactive = true,
  size = 'medium',
  onDimensionClick,
  onDataPointHover,
  className = ''
}) => {
  // Six dimensions configuration
  const dimensions = [
    {
      key: 'strategicAlignment',
      label: 'Strategic Alignment',
      description: 'Alignment with organizational strategy and frameworks',
      color: 'rgba(72, 187, 120, 1)',
      icon: '🎯'
    },
    {
      key: 'humanNeeds',
      label: 'Human Needs Fulfillment',
      description: 'Meeting individual and collective human needs',
      color: 'rgba(245, 101, 101, 1)',
      icon: '❤️'
    },
    {
      key: 'communication',
      label: 'Communication Effectiveness',
      description: 'Quality and effectiveness of communication',
      color: 'rgba(66, 153, 225, 1)',
      icon: '💬'
    },
    {
      key: 'decisionQuality',
      label: 'Decision Quality',
      description: 'Quality and effectiveness of decision-making',
      color: 'rgba(237, 137, 54, 1)',
      icon: '⚖️'
    },
    {
      key: 'innovation',
      label: 'Innovation Potential',
      description: 'Capacity for innovation and creative solutions',
      color: 'rgba(118, 75, 162, 1)',
      icon: '💡'
    },
    {
      key: 'learning',
      label: 'Organizational Learning',
      description: 'Learning velocity and knowledge development',
      color: 'rgba(102, 126, 234, 1)',
      icon: '📚'
    }
  ];

  // Process data for chart
  const chartData = useMemo(() => {
    const currentValues = dimensions.map(dim => data[dim.key] || 0);
    const comparisonValues = showComparison && comparisonData 
      ? dimensions.map(dim => comparisonData[dim.key] || 0)
      : null;

    const datasets = [
      {
        label: 'Current Period',
        data: currentValues,
        backgroundColor: 'rgba(102, 126, 234, 0.2)',
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 3,
        pointBackgroundColor: dimensions.map(dim => dim.color),
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointHoverBackgroundColor: dimensions.map(dim => dim.color),
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 3
      }
    ];

    if (comparisonValues) {
      datasets.push({
        label: 'Previous Period',
        data: comparisonValues,
        backgroundColor: 'rgba(163, 177, 198, 0.1)',
        borderColor: 'rgba(163, 177, 198, 1)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointBackgroundColor: 'rgba(163, 177, 198, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: 'rgba(163, 177, 198, 1)',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2
      });
    }

    return {
      labels: dimensions.map(dim => dim.label),
      datasets
    };
  }, [data, comparisonData, showComparison, dimensions]);

  // Chart options
  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: 'var(--text-primary)',
          font: {
            family: 'var(--font-family-primary)',
            size: 14
          },
          padding: 20,
          usePointStyle: true
        }
      },
      tooltip: {
        backgroundColor: 'var(--primary-bg)',
        titleColor: 'var(--text-primary)',
        bodyColor: 'var(--text-secondary)',
        borderColor: 'var(--accent-color)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          title: (context) => {
            const dimension = dimensions[context[0].dataIndex];
            return `${dimension.icon} ${dimension.label}`;
          },
          label: (context) => {
            const value = context.parsed.r;
            const percentage = Math.round(value);
            return `${context.dataset.label}: ${percentage}%`;
          },
          afterLabel: (context) => {
            const dimension = dimensions[context.dataIndex];
            return dimension.description;
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
          font: {
            size: 12
          },
          callback: (value) => `${value}%`
        },
        grid: {
          color: 'rgba(163, 177, 198, 0.3)',
          lineWidth: 1
        },
        angleLines: {
          color: 'rgba(163, 177, 198, 0.3)',
          lineWidth: 1
        },
        pointLabels: {
          color: 'var(--text-primary)',
          font: {
            size: 13,
            weight: '500'
          },
          padding: 15
        }
      }
    },
    interaction: {
      intersect: false,
      mode: 'point'
    },
    onHover: (event, elements) => {
      if (interactive && elements.length > 0 && onDataPointHover) {
        const element = elements[0];
        const dimension = dimensions[element.index];
        const value = chartData.datasets[element.datasetIndex].data[element.index];
        onDataPointHover({
          dimension,
          value,
          datasetIndex: element.datasetIndex
        });
      }
    },
    onClick: (event, elements) => {
      if (interactive && elements.length > 0 && onDimensionClick) {
        const element = elements[0];
        const dimension = dimensions[element.index];
        const value = chartData.datasets[element.datasetIndex].data[element.index];
        onDimensionClick({
          dimension,
          value,
          datasetIndex: element.datasetIndex
        });
      }
    },
    animation: {
      duration: 1000,
      easing: 'easeInOutQuart'
    }
  }), [dimensions, chartData, interactive, onDimensionClick, onDataPointHover]);

  // Calculate overall score
  const overallScore = useMemo(() => {
    const values = dimensions.map(dim => data[dim.key] || 0);
    return Math.round(values.reduce((sum, val) => sum + val, 0) / values.length);
  }, [data, dimensions]);

  // Calculate improvement if comparison data exists
  const improvement = useMemo(() => {
    if (!showComparison || !comparisonData) return null;
    
    const currentAvg = dimensions.reduce((sum, dim) => sum + (data[dim.key] || 0), 0) / dimensions.length;
    const previousAvg = dimensions.reduce((sum, dim) => sum + (comparisonData[dim.key] || 0), 0) / dimensions.length;
    
    return Math.round(currentAvg - previousAvg);
  }, [data, comparisonData, showComparison, dimensions]);

  // Get size class
  const sizeClass = {
    small: 'six-dimensional-chart--small',
    medium: 'six-dimensional-chart--medium',
    large: 'six-dimensional-chart--large'
  }[size];

  return (
    <div className={`six-dimensional-chart ${sizeClass} ${className}`}>
      {/* Chart Header */}
      <div className="six-dimensional-chart__header">
        <div className="six-dimensional-chart__score">
          <div className="overall-score">
            <span className="overall-score__value">{overallScore}</span>
            <span className="overall-score__label">Overall Score</span>
          </div>
          
          {improvement !== null && (
            <div className={`improvement-indicator ${improvement >= 0 ? 'positive' : 'negative'}`}>
              <span className="improvement-indicator__value">
                {improvement >= 0 ? '+' : ''}{improvement}
              </span>
              <span className="improvement-indicator__label">vs Previous</span>
            </div>
          )}
        </div>
        
        {interactive && (
          <div className="six-dimensional-chart__hint">
            Click on data points for detailed analysis
          </div>
        )}
      </div>

      {/* Chart Container */}
      <div className="six-dimensional-chart__container">
        <Radar data={chartData} options={chartOptions} />
      </div>

      {/* Dimension Legend */}
      <div className="six-dimensional-chart__legend">
        {dimensions.map((dimension, index) => {
          const currentValue = data[dimension.key] || 0;
          const previousValue = comparisonData?.[dimension.key] || 0;
          const change = showComparison ? currentValue - previousValue : null;
          
          return (
            <div
              key={dimension.key}
              className={`dimension-item ${interactive ? 'dimension-item--interactive' : ''}`}
              onClick={() => interactive && onDimensionClick?.({ dimension, value: currentValue })}
            >
              <div className="dimension-item__icon">{dimension.icon}</div>
              <div className="dimension-item__content">
                <div className="dimension-item__label">{dimension.label}</div>
                <div className="dimension-item__value">
                  <span className="current-value">{Math.round(currentValue)}%</span>
                  {change !== null && (
                    <span className={`change-value ${change >= 0 ? 'positive' : 'negative'}`}>
                      ({change >= 0 ? '+' : ''}{Math.round(change)})
                    </span>
                  )}
                </div>
              </div>
              <div 
                className="dimension-item__indicator"
                style={{ backgroundColor: dimension.color }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SixDimensionalChart;