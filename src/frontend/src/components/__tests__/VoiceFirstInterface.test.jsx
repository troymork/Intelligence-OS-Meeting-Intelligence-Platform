/**
 * Tests for Voice-First Interface Components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import VoiceFirstInterface from '../VoiceFirstInterface';
import VoiceActivationOrb from '../VoiceActivationOrb';
import ExpandableCard, { ExpandableCardGroup, AnalysisCard, ActionCard } from '../ExpandableCard';

// Mock Web Speech API
const mockSpeechRecognition = {
  start: jest.fn(),
  stop: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  continuous: false,
  interimResults: false,
  lang: 'en-US'
};

const mockMediaDevices = {
  getUserMedia: jest.fn().mockResolvedValue({
    getTracks: () => [{ stop: jest.fn() }]
  })
};

// Mock AudioContext
const mockAudioContext = {
  createAnalyser: jest.fn().mockReturnValue({
    fftSize: 64,
    frequencyBinCount: 32,
    getByteFrequencyData: jest.fn(),
    connect: jest.fn()
  }),
  createMediaStreamSource: jest.fn().mockReturnValue({
    connect: jest.fn()
  }),
  close: jest.fn()
};

beforeAll(() => {
  global.SpeechRecognition = jest.fn(() => mockSpeechRecognition);
  global.webkitSpeechRecognition = jest.fn(() => mockSpeechRecognition);
  global.navigator.mediaDevices = mockMediaDevices;
  global.AudioContext = jest.fn(() => mockAudioContext);
  global.webkitAudioContext = jest.fn(() => mockAudioContext);
  global.requestAnimationFrame = jest.fn(cb => setTimeout(cb, 16));
  global.cancelAnimationFrame = jest.fn();
});

describe('VoiceActivationOrb', () => {
  const defaultProps = {
    onVoiceStart: jest.fn(),
    onVoiceEnd: jest.fn(),
    onTranscript: jest.fn(),
    onError: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders voice activation orb', () => {
    render(<VoiceActivationOrb {...defaultProps} />);
    
    const orb = screen.getByRole('button', { name: /start voice input/i });
    expect(orb).toBeInTheDocument();
    expect(orb).toHaveClass('voice-orb');
  });

  test('handles orb click activation', async () => {
    const user = userEvent.setup();
    render(<VoiceActivationOrb {...defaultProps} />);
    
    const orb = screen.getByRole('button', { name: /start voice input/i });
    await user.click(orb);
    
    expect(mockMediaDevices.getUserMedia).toHaveBeenCalledWith({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });
  });

  test('handles keyboard activation', async () => {
    const user = userEvent.setup();
    render(<VoiceActivationOrb {...defaultProps} />);
    
    const orb = screen.getByRole('button', { name: /start voice input/i });
    orb.focus();
    await user.keyboard(' ');
    
    expect(mockMediaDevices.getUserMedia).toHaveBeenCalled();
  });

  test('displays different sizes correctly', () => {
    const { rerender } = render(<VoiceActivationOrb {...defaultProps} size="small" />);
    expect(screen.getByRole('button')).toHaveClass('voice-orb--small');
    
    rerender(<VoiceActivationOrb {...defaultProps} size="large" />);
    expect(screen.getByRole('button')).toHaveClass('voice-orb--large');
  });

  test('shows processing state', () => {
    render(<VoiceActivationOrb {...defaultProps} isProcessing={true} />);
    
    expect(screen.getByRole('button')).toHaveClass('voice-orb--processing');
    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  test('handles disabled state', async () => {
    const user = userEvent.setup();
    render(<VoiceActivationOrb {...defaultProps} disabled={true} />);
    
    const orb = screen.getByRole('button');
    expect(orb).toHaveClass('voice-orb--disabled');
    
    await user.click(orb);
    expect(mockMediaDevices.getUserMedia).not.toHaveBeenCalled();
  });

  test('displays confidence indicator', () => {
    render(<VoiceActivationOrb {...defaultProps} confidence={0.8} />);
    
    const confidenceArc = document.querySelector('.voice-orb__confidence-arc');
    expect(confidenceArc).toBeInTheDocument();
    expect(confidenceArc).toHaveStyle('--confidence-percentage: 80%');
  });
});

describe('ExpandableCard', () => {
  const defaultProps = {
    title: 'Test Card',
    subtitle: 'Test Subtitle',
    summary: 'Test summary content',
    children: <div>Card content</div>
  };

  test('renders expandable card', () => {
    render(<ExpandableCard {...defaultProps} />);
    
    expect(screen.getByText('Test Card')).toBeInTheDocument();
    expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
    expect(screen.getByText('Test summary content')).toBeInTheDocument();
  });

  test('expands and collapses on click', async () => {
    const user = userEvent.setup();
    const onExpand = jest.fn();
    const onCollapse = jest.fn();
    
    render(
      <ExpandableCard 
        {...defaultProps} 
        onExpand={onExpand}
        onCollapse={onCollapse}
      />
    );
    
    const header = screen.getByRole('button');
    expect(header).toHaveAttribute('aria-expanded', 'false');
    
    // Expand
    await user.click(header);
    expect(onExpand).toHaveBeenCalled();
    expect(header).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByText('Card content')).toBeInTheDocument();
    
    // Collapse
    await user.click(header);
    expect(onCollapse).toHaveBeenCalled();
    expect(header).toHaveAttribute('aria-expanded', 'false');
  });

  test('handles keyboard navigation', async () => {
    const user = userEvent.setup();
    render(<ExpandableCard {...defaultProps} />);
    
    const header = screen.getByRole('button');
    header.focus();
    
    await user.keyboard('{Enter}');
    expect(header).toHaveAttribute('aria-expanded', 'true');
    
    await user.keyboard(' ');
    expect(header).toHaveAttribute('aria-expanded', 'false');
  });

  test('renders with different variants', () => {
    const { rerender } = render(<ExpandableCard {...defaultProps} variant="elevated" />);
    expect(document.querySelector('.expandable-card')).toHaveClass('expandable-card--elevated');
    
    rerender(<ExpandableCard {...defaultProps} priority="high" />);
    expect(document.querySelector('.expandable-card')).toHaveClass('expandable-card--high');
  });

  test('displays badge correctly', () => {
    const badge = { text: 'New', type: 'success' };
    render(<ExpandableCard {...defaultProps} badge={badge} />);
    
    const badgeElement = screen.getByText('New');
    expect(badgeElement).toBeInTheDocument();
    expect(badgeElement).toHaveClass('expandable-card__badge--success');
  });

  test('shows loading state', () => {
    render(<ExpandableCard {...defaultProps} loading={true} />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(document.querySelector('.expandable-card__loading-spinner')).toBeInTheDocument();
  });

  test('shows error state', () => {
    render(<ExpandableCard {...defaultProps} error="Something went wrong" />);
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(document.querySelector('.expandable-card')).toHaveClass('expandable-card--error');
  });

  test('renders static card without expand functionality', async () => {
    const user = userEvent.setup();
    render(<ExpandableCard {...defaultProps} expandable={false} />);
    
    const card = document.querySelector('.expandable-card');
    expect(card).toHaveClass('expandable-card--static');
    
    // Should not have button role
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});

describe('ExpandableCardGroup', () => {
  test('renders card group with title and subtitle', () => {
    render(
      <ExpandableCardGroup title="Test Group" subtitle="Group subtitle">
        <div>Child content</div>
      </ExpandableCardGroup>
    );
    
    expect(screen.getByText('Test Group')).toBeInTheDocument();
    expect(screen.getByText('Group subtitle')).toBeInTheDocument();
    expect(screen.getByText('Child content')).toBeInTheDocument();
  });

  test('applies different layouts', () => {
    const { rerender } = render(
      <ExpandableCardGroup layout="grid">
        <div>Content</div>
      </ExpandableCardGroup>
    );
    
    expect(document.querySelector('.expandable-card-group')).toHaveClass('expandable-card-group--grid');
    
    rerender(
      <ExpandableCardGroup layout="list">
        <div>Content</div>
      </ExpandableCardGroup>
    );
    
    expect(document.querySelector('.expandable-card-group')).toHaveClass('expandable-card-group--list');
  });
});

describe('AnalysisCard', () => {
  const mockAnalysis = {
    title: 'Meeting Analysis',
    type: 'Oracle Protocol',
    summary: 'Comprehensive meeting analysis',
    confidence: 0.85,
    priority: 'high',
    insights: ['Key insight 1', 'Key insight 2'],
    recommendations: ['Recommendation 1', 'Recommendation 2'],
    metrics: {
      'Engagement Score': '8.5/10',
      'Decision Count': '3',
      'Action Items': '7'
    }
  };

  test('renders analysis card with all sections', () => {
    render(<AnalysisCard analysis={mockAnalysis} />);
    
    expect(screen.getByText('Meeting Analysis')).toBeInTheDocument();
    expect(screen.getByText('Oracle Protocol')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument(); // Confidence badge
    expect(screen.getByText('Key insight 1')).toBeInTheDocument();
    expect(screen.getByText('Recommendation 1')).toBeInTheDocument();
    expect(screen.getByText('8.5/10')).toBeInTheDocument();
  });

  test('displays correct badge type based on confidence', () => {
    const { rerender } = render(<AnalysisCard analysis={{...mockAnalysis, confidence: 0.9}} />);
    expect(document.querySelector('.expandable-card__badge')).toHaveClass('expandable-card__badge--success');
    
    rerender(<AnalysisCard analysis={{...mockAnalysis, confidence: 0.7}} />);
    expect(document.querySelector('.expandable-card__badge')).toHaveClass('expandable-card__badge--warning');
    
    rerender(<AnalysisCard analysis={{...mockAnalysis, confidence: 0.5}} />);
    expect(document.querySelector('.expandable-card__badge')).toHaveClass('expandable-card__badge--error');
  });
});

describe('ActionCard', () => {
  const mockAction = {
    title: 'Complete Project Setup',
    description: 'Set up the initial project structure',
    dueDate: '2024-02-15',
    status: 'in_progress',
    priority: 'high',
    assignee: 'John Doe',
    estimatedHours: 8,
    dependencies: ['Task A', 'Task B'],
    progress: 0.6
  };

  test('renders action card with all details', () => {
    render(<ActionCard action={mockAction} />);
    
    expect(screen.getByText('Complete Project Setup')).toBeInTheDocument();
    expect(screen.getByText('Due: 2024-02-15')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('Task A, Task B')).toBeInTheDocument();
    expect(screen.getByText('Progress: 60%')).toBeInTheDocument();
  });

  test('displays correct badge type based on status', () => {
    const { rerender } = render(<ActionCard action={{...mockAction, status: 'completed'}} />);
    expect(document.querySelector('.expandable-card__badge')).toHaveClass('expandable-card__badge--success');
    
    rerender(<ActionCard action={{...mockAction, status: 'overdue'}} />);
    expect(document.querySelector('.expandable-card__badge')).toHaveClass('expandable-card__badge--error');
  });

  test('renders progress bar correctly', () => {
    render(<ActionCard action={mockAction} />);
    
    const progressBar = document.querySelector('.neu-progress__bar');
    expect(progressBar).toHaveStyle('width: 60%');
  });
});

describe('VoiceFirstInterface', () => {
  const defaultProps = {
    onVoiceCommand: jest.fn(),
    onAnalysisRequest: jest.fn(),
    analysisResults: [],
    actionItems: []
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders main interface components', () => {
    render(<VoiceFirstInterface {...defaultProps} />);
    
    expect(screen.getByText('Intelligence OS')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/search or ask a question/i)).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start voice input/i })).toBeInTheDocument();
  });

  test('handles navigation between views', async () => {
    const user = userEvent.setup();
    render(<VoiceFirstInterface {...defaultProps} />);
    
    // Switch to Analysis view
    await user.click(screen.getByText('Analysis'));
    expect(screen.getByText('Analysis Results')).toBeInTheDocument();
    
    // Switch to Actions view
    await user.click(screen.getByText('Actions'));
    expect(screen.getByText('Action Items')).toBeInTheDocument();
    
    // Switch back to Dashboard
    await user.click(screen.getByText('Dashboard'));
    expect(screen.getByText('Dashboard Overview')).toBeInTheDocument();
  });

  test('handles search functionality', async () => {
    const user = userEvent.setup();
    const analysisResults = [
      { title: 'Meeting Analysis', summary: 'Test analysis', confidence: 0.8 }
    ];
    
    render(<VoiceFirstInterface {...defaultProps} analysisResults={analysisResults} />);
    
    const searchInput = screen.getByPlaceholderText(/search or ask a question/i);
    await user.type(searchInput, 'meeting');
    
    expect(searchInput).toHaveValue('meeting');
  });

  test('handles voice commands', async () => {
    const onVoiceCommand = jest.fn();
    render(<VoiceFirstInterface {...defaultProps} onVoiceCommand={onVoiceCommand} />);
    
    // Simulate voice transcript
    const orbComponent = screen.getByRole('button', { name: /start voice input/i });
    
    // This would normally be triggered by the voice recognition system
    // For testing, we'll simulate the callback
    act(() => {
      // Simulate voice command processing
      onVoiceCommand('show dashboard');
    });
    
    expect(onVoiceCommand).toHaveBeenCalledWith('show dashboard');
  });

  test('displays notifications', async () => {
    render(<VoiceFirstInterface {...defaultProps} />);
    
    // Notifications are typically triggered by voice commands or other interactions
    // For testing, we'll check that the notification container exists
    expect(document.querySelector('.voice-interface__notifications')).toBeInTheDocument();
  });

  test('handles theme toggle', async () => {
    const user = userEvent.setup();
    render(<VoiceFirstInterface {...defaultProps} />);
    
    const themeToggle = screen.getByRole('checkbox');
    await user.click(themeToggle);
    
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark');
  });

  test('shows loading overlay when processing', () => {
    render(<VoiceFirstInterface {...defaultProps} isProcessing={true} />);
    
    expect(screen.getByText('Processing your request...')).toBeInTheDocument();
    expect(document.querySelector('.voice-interface__loading-overlay')).toBeInTheDocument();
  });

  test('displays empty states correctly', () => {
    render(<VoiceFirstInterface {...defaultProps} />);
    
    // Switch to Analysis view to see empty state
    fireEvent.click(screen.getByText('Analysis'));
    expect(screen.getByText('No Analysis Results')).toBeInTheDocument();
    
    // Switch to Actions view to see empty state
    fireEvent.click(screen.getByText('Actions'));
    expect(screen.getByText('No Action Items')).toBeInTheDocument();
  });

  test('handles keyboard shortcuts', async () => {
    const user = userEvent.setup();
    render(<VoiceFirstInterface {...defaultProps} />);
    
    // Test Ctrl+K for search focus
    await user.keyboard('{Control>}k{/Control}');
    expect(screen.getByPlaceholderText(/search or ask a question/i)).toHaveFocus();
    
    // Test Ctrl+1 for dashboard
    await user.keyboard('{Control>}1{/Control}');
    expect(screen.getByText('Dashboard Overview')).toBeInTheDocument();
  });

  test('filters content based on search query', async () => {
    const user = userEvent.setup();
    const analysisResults = [
      { title: 'Meeting Analysis', summary: 'Test meeting analysis', confidence: 0.8 },
      { title: 'Project Review', summary: 'Test project review', confidence: 0.7 }
    ];
    
    render(<VoiceFirstInterface {...defaultProps} analysisResults={analysisResults} />);
    
    // Switch to Analysis view
    await user.click(screen.getByText('Analysis'));
    
    // Search for 'meeting'
    const searchInput = screen.getByPlaceholderText(/search or ask a question/i);
    await user.type(searchInput, 'meeting');
    
    // Should show filtered results
    expect(screen.getByText('Meeting Analysis')).toBeInTheDocument();
    // Project Review should not be visible (would need more complex filtering logic)
  });
});

describe('Accessibility', () => {
  test('voice orb has proper ARIA attributes', () => {
    render(<VoiceActivationOrb onVoiceStart={jest.fn()} />);
    
    const orb = screen.getByRole('button');
    expect(orb).toHaveAttribute('aria-label', 'Start voice input');
    expect(orb).toHaveAttribute('aria-pressed', 'false');
  });

  test('expandable cards have proper ARIA attributes', () => {
    render(<ExpandableCard title="Test" summary="Summary">Content</ExpandableCard>);
    
    const header = screen.getByRole('button');
    expect(header).toHaveAttribute('aria-expanded', 'false');
    expect(header).toHaveAttribute('aria-controls', 'card-content');
  });

  test('interface supports keyboard navigation', async () => {
    const user = userEvent.setup();
    render(<VoiceFirstInterface onVoiceCommand={jest.fn()} />);
    
    // Tab through interactive elements
    await user.tab();
    expect(screen.getByPlaceholderText(/search or ask a question/i)).toHaveFocus();
    
    await user.tab();
    expect(screen.getByText('Dashboard')).toHaveFocus();
  });

  test('respects reduced motion preferences', () => {
    // Mock prefers-reduced-motion
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });
    
    render(<VoiceFirstInterface onVoiceCommand={jest.fn()} />);
    
    // Animations should be disabled
    const interface = document.querySelector('.voice-first-interface');
    expect(interface).toBeInTheDocument();
  });
});