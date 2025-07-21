/**
 * Help and Onboarding System
 * Interactive tutorials and contextual guidance for users
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import './HelpOnboardingSystem.css';

// Main onboarding component
const OnboardingSystem = ({ 
  isActive, 
  onComplete, 
  onSkip, 
  userExpertise = 'intermediate',
  features = []
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [tourSteps, setTourSteps] = useState([]);
  const overlayRef = useRef(null);
  const highlightRef = useRef(null);

  // Define onboarding steps based on user expertise
  const onboardingSteps = {
    beginner: [
      {
        id: 'welcome',
        title: 'Welcome to Intelligence OS',
        content: 'Your AI-powered meeting intelligence platform. Let\'s get you started with a quick tour.',
        target: null,
        position: 'center'
      },
      {
        id: 'voice-interface',
        title: 'Voice Interface',
        content: 'Click the voice orb or say "Oracle" to interact using voice commands.',
        target: '[data-tour="voice-orb"]',
        position: 'bottom'
      },
      {
        id: 'dashboard',
        title: 'Analytics Dashboard',
        content: 'View comprehensive insights about your meetings and team dynamics here.',
        target: '[data-tour="analytics-dashboard"]',
        position: 'top'
      },
      {
        id: 'human-needs',
        title: 'Human Needs Analysis',
        content: 'Understand individual and team needs fulfillment patterns.',
        target: '[data-tour="human-needs"]',
        position: 'left'
      },
      {
        id: 'help',
        title: 'Getting Help',
        content: 'Click the help button anytime for contextual assistance.',
        target: '[data-tour="help-button"]',
        position: 'left'
      }
    ],
    intermediate: [
      {
        id: 'welcome',
        title: 'Welcome Back!',
        content: 'Let\'s explore the advanced features available to you.',
        target: null,
        position: 'center'
      },
      {
        id: 'strategic-alignment',
        title: 'Strategic Alignment',
        content: 'Analyze how your meetings align with strategic frameworks like SDGs and Doughnut Economy.',
        target: '[data-tour="strategic-dashboard"]',
        position: 'bottom'
      },
      {
        id: 'pattern-recognition',
        title: 'Pattern Recognition',
        content: 'Discover recurring themes and organizational learning opportunities.',
        target: '[data-tour="pattern-analysis"]',
        position: 'top'
      },
      {
        id: 'ai-conductor',
        title: 'AI Conductor',
        content: 'Orchestrate multiple AI engines for comprehensive analysis.',
        target: '[data-tour="ai-conductor"]',
        position: 'right'
      }
    ],
    advanced: [
      {
        id: 'welcome',
        title: 'Advanced Features',
        content: 'Access powerful tools for deep organizational intelligence.',
        target: null,
        position: 'center'
      },
      {
        id: 'custom-workflows',
        title: 'Custom Workflows',
        content: 'Create and manage custom analysis workflows.',
        target: '[data-tour="workflows"]',
        position: 'bottom'
      },
      {
        id: 'api-integration',
        title: 'API Integration',
        content: 'Connect with external systems and automate processes.',
        target: '[data-tour="integrations"]',
        position: 'top'
      },
      {
        id: 'advanced-analytics',
        title: 'Advanced Analytics',
        content: 'Access detailed metrics and custom reporting tools.',
        target: '[data-tour="advanced-analytics"]',
        position: 'left'
      }
    ]
  };

  useEffect(() => {
    if (isActive) {
      setTourSteps(onboardingSteps[userExpertise] || onboardingSteps.intermediate);
      setIsVisible(true);
      setCurrentStep(0);
    } else {
      setIsVisible(false);
    }
  }, [isActive, userExpertise]);

  useEffect(() => {
    if (isVisible && tourSteps.length > 0) {
      highlightCurrentStep();
    }
  }, [currentStep, isVisible, tourSteps]);

  const highlightCurrentStep = useCallback(() => {
    const step = tourSteps[currentStep];
    if (!step) return;

    if (step.target) {
      const targetElement = document.querySelector(step.target);
      if (targetElement) {
        highlightElement(targetElement, step.position);
        scrollToElement(targetElement);
      }
    } else {
      // Center modal for steps without targets
      removeHighlight();
    }
  }, [currentStep, tourSteps]);

  const highlightElement = (element, position) => {
    const rect = element.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

    // Create highlight overlay
    if (highlightRef.current) {
      const highlight = highlightRef.current;
      highlight.style.display = 'block';
      highlight.style.top = `${rect.top + scrollTop - 8}px`;
      highlight.style.left = `${rect.left + scrollLeft - 8}px`;
      highlight.style.width = `${rect.width + 16}px`;
      highlight.style.height = `${rect.height + 16}px`;
    }

    // Add highlighted class to element
    element.classList.add('onboarding-highlighted');
  };

  const removeHighlight = () => {
    if (highlightRef.current) {
      highlightRef.current.style.display = 'none';
    }
    
    // Remove highlight from all elements
    document.querySelectorAll('.onboarding-highlighted').forEach(el => {
      el.classList.remove('onboarding-highlighted');
    });
  };

  const scrollToElement = (element) => {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'center'
    });
  };

  const handleNext = () => {
    if (currentStep < tourSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    removeHighlight();
    setIsVisible(false);
    onComplete?.();
  };

  const handleSkip = () => {
    removeHighlight();
    setIsVisible(false);
    onSkip?.();
  };

  const getTooltipPosition = () => {
    const step = tourSteps[currentStep];
    if (!step || !step.target) return { position: 'center' };

    const targetElement = document.querySelector(step.target);
    if (!targetElement) return { position: 'center' };

    const rect = targetElement.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let position = step.position || 'bottom';
    let style = {};

    switch (position) {
      case 'top':
        style = {
          top: `${rect.top - 20}px`,
          left: `${rect.left + rect.width / 2}px`,
          transform: 'translate(-50%, -100%)'
        };
        break;
      case 'bottom':
        style = {
          top: `${rect.bottom + 20}px`,
          left: `${rect.left + rect.width / 2}px`,
          transform: 'translate(-50%, 0)'
        };
        break;
      case 'left':
        style = {
          top: `${rect.top + rect.height / 2}px`,
          left: `${rect.left - 20}px`,
          transform: 'translate(-100%, -50%)'
        };
        break;
      case 'right':
        style = {
          top: `${rect.top + rect.height / 2}px`,
          left: `${rect.right + 20}px`,
          transform: 'translate(0, -50%)'
        };
        break;
      default:
        style = {
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)'
        };
    }

    return { position, style };
  };

  if (!isVisible || tourSteps.length === 0) return null;

  const currentStepData = tourSteps[currentStep];
  const tooltipPosition = getTooltipPosition();

  return (
    <div className="onboarding-system">
      {/* Overlay */}
      <div 
        ref={overlayRef}
        className="onboarding-overlay"
        onClick={handleSkip}
      />
      
      {/* Highlight */}
      <div 
        ref={highlightRef}
        className="onboarding-highlight"
      />
      
      {/* Tooltip */}
      <div 
        className={`onboarding-tooltip onboarding-tooltip--${tooltipPosition.position}`}
        style={tooltipPosition.style}
      >
        <div className="onboarding-tooltip__content">
          <div className="onboarding-tooltip__header">
            <h3>{currentStepData.title}</h3>
            <div className="onboarding-tooltip__progress">
              {currentStep + 1} of {tourSteps.length}
            </div>
          </div>
          
          <div className="onboarding-tooltip__body">
            <p>{currentStepData.content}</p>
          </div>
          
          <div className="onboarding-tooltip__footer">
            <div className="onboarding-tooltip__buttons">
              <button 
                className="onboarding-button onboarding-button--secondary"
                onClick={handleSkip}
              >
                Skip Tour
              </button>
              
              {currentStep > 0 && (
                <button 
                  className="onboarding-button onboarding-button--secondary"
                  onClick={handlePrevious}
                >
                  Previous
                </button>
              )}
              
              <button 
                className="onboarding-button onboarding-button--primary"
                onClick={handleNext}
              >
                {currentStep === tourSteps.length - 1 ? 'Finish' : 'Next'}
              </button>
            </div>
          </div>
        </div>
        
        {/* Arrow */}
        <div className={`onboarding-tooltip__arrow onboarding-tooltip__arrow--${tooltipPosition.position}`} />
      </div>
    </div>
  );
};

// Interactive tutorial component
const InteractiveTutorial = ({ 
  tutorialId, 
  isActive, 
  onComplete,
  onClose 
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [userInput, setUserInput] = useState('');
  const [isCompleted, setIsCompleted] = useState(false);

  // Define interactive tutorials
  const tutorials = {
    'voice-commands': {
      title: 'Voice Commands Tutorial',
      steps: [
        {
          type: 'instruction',
          title: 'Activate Voice Interface',
          content: 'Click the voice orb or press the spacebar to activate voice input.',
          target: '[data-tour="voice-orb"]',
          validation: 'voice-activated'
        },
        {
          type: 'practice',
          title: 'Try a Voice Command',
          content: 'Say "Show me the analytics dashboard" to navigate to the dashboard.',
          expectedInput: 'show me the analytics dashboard',
          validation: 'voice-command'
        },
        {
          type: 'completion',
          title: 'Great Job!',
          content: 'You\'ve successfully learned how to use voice commands. Practice with other commands to become more proficient.',
          action: 'complete'
        }
      ]
    },
    'analytics-exploration': {
      title: 'Analytics Dashboard Tutorial',
      steps: [
        {
          type: 'instruction',
          title: 'Navigate to Analytics',
          content: 'Click on the Analytics tab to view your meeting insights.',
          target: '[data-tour="analytics-tab"]',
          validation: 'navigation'
        },
        {
          type: 'interaction',
          title: 'Explore Chart Types',
          content: 'Click on different chart types to see various visualizations of your data.',
          target: '[data-tour="chart-selector"]',
          validation: 'chart-interaction'
        },
        {
          type: 'practice',
          title: 'Filter Data',
          content: 'Use the time range selector to view data from the last 7 days.',
          target: '[data-tour="time-filter"]',
          validation: 'filter-applied'
        }
      ]
    }
  };

  const tutorial = tutorials[tutorialId];
  if (!tutorial || !isActive) return null;

  const currentStepData = tutorial.steps[currentStep];

  const handleStepComplete = () => {
    if (currentStep < tutorial.steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setIsCompleted(true);
      onComplete?.();
    }
  };

  const validateStep = (stepData) => {
    // Implement step validation logic
    switch (stepData.validation) {
      case 'voice-activated':
        return document.querySelector('.voice-interface--active') !== null;
      case 'navigation':
        return window.location.hash.includes('analytics');
      case 'chart-interaction':
        return document.querySelector('.chart--selected') !== null;
      default:
        return true;
    }
  };

  return (
    <div className="interactive-tutorial">
      <div className="tutorial-modal">
        <div className="tutorial-modal__header">
          <h2>{tutorial.title}</h2>
          <button 
            className="tutorial-modal__close"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        
        <div className="tutorial-modal__body">
          <div className="tutorial-step">
            <div className="tutorial-step__header">
              <h3>{currentStepData.title}</h3>
              <div className="tutorial-step__progress">
                Step {currentStep + 1} of {tutorial.steps.length}
              </div>
            </div>
            
            <div className="tutorial-step__content">
              <p>{currentStepData.content}</p>
              
              {currentStepData.type === 'practice' && (
                <div className="tutorial-practice">
                  <input
                    type="text"
                    placeholder="Type your response here..."
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    className="tutorial-input"
                  />
                </div>
              )}
            </div>
            
            <div className="tutorial-step__actions">
              <button 
                className="tutorial-button tutorial-button--primary"
                onClick={handleStepComplete}
                disabled={currentStepData.validation && !validateStep(currentStepData)}
              >
                {currentStep === tutorial.steps.length - 1 ? 'Complete' : 'Continue'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Help tooltip component
const HelpTooltip = ({ 
  target, 
  content, 
  position = 'top',
  isVisible,
  onClose 
}) => {
  const [tooltipStyle, setTooltipStyle] = useState({});
  const tooltipRef = useRef(null);

  useEffect(() => {
    if (isVisible && target) {
      const targetElement = document.querySelector(target);
      if (targetElement) {
        const rect = targetElement.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

        let style = {};
        switch (position) {
          case 'top':
            style = {
              top: `${rect.top + scrollTop - 10}px`,
              left: `${rect.left + scrollLeft + rect.width / 2}px`,
              transform: 'translate(-50%, -100%)'
            };
            break;
          case 'bottom':
            style = {
              top: `${rect.bottom + scrollTop + 10}px`,
              left: `${rect.left + scrollLeft + rect.width / 2}px`,
              transform: 'translate(-50%, 0)'
            };
            break;
          case 'left':
            style = {
              top: `${rect.top + scrollTop + rect.height / 2}px`,
              left: `${rect.left + scrollLeft - 10}px`,
              transform: 'translate(-100%, -50%)'
            };
            break;
          case 'right':
            style = {
              top: `${rect.top + scrollTop + rect.height / 2}px`,
              left: `${rect.right + scrollLeft + 10}px`,
              transform: 'translate(0, -50%)'
            };
            break;
        }
        setTooltipStyle(style);
      }
    }
  }, [isVisible, target, position]);

  if (!isVisible) return null;

  return (
    <div 
      ref={tooltipRef}
      className={`help-tooltip help-tooltip--${position}`}
      style={tooltipStyle}
    >
      <div className="help-tooltip__content">
        {typeof content === 'string' ? (
          <p>{content}</p>
        ) : (
          content
        )}
      </div>
      <button 
        className="help-tooltip__close"
        onClick={onClose}
      >
        ×
      </button>
      <div className={`help-tooltip__arrow help-tooltip__arrow--${position}`} />
    </div>
  );
};

// Feature spotlight component
const FeatureSpotlight = ({ 
  feature, 
  isVisible, 
  onDismiss,
  onTryFeature 
}) => {
  if (!isVisible || !feature) return null;

  return (
    <div className="feature-spotlight">
      <div className="feature-spotlight__overlay" onClick={onDismiss} />
      <div className="feature-spotlight__content">
        <div className="feature-spotlight__icon">
          {feature.icon}
        </div>
        <h3>{feature.title}</h3>
        <p>{feature.description}</p>
        <div className="feature-spotlight__actions">
          <button 
            className="spotlight-button spotlight-button--secondary"
            onClick={onDismiss}
          >
            Maybe Later
          </button>
          <button 
            className="spotlight-button spotlight-button--primary"
            onClick={onTryFeature}
          >
            Try It Now
          </button>
        </div>
      </div>
    </div>
  );
};

// Main help and onboarding system component
const HelpOnboardingSystem = ({ 
  userPreferences,
  onPreferenceChange 
}) => {
  const [activeOnboarding, setActiveOnboarding] = useState(false);
  const [activeTutorial, setActiveTutorial] = useState(null);
  const [activeTooltip, setActiveTooltip] = useState(null);
  const [activeSpotlight, setActiveSpotlight] = useState(null);

  useEffect(() => {
    // Check if user should see onboarding
    const shouldShowOnboarding = !userPreferences?.expertise?.skipOnboarding && 
                                 !localStorage.getItem('onboarding-completed');
    
    if (shouldShowOnboarding) {
      setActiveOnboarding(true);
    }
  }, [userPreferences]);

  const handleOnboardingComplete = () => {
    setActiveOnboarding(false);
    localStorage.setItem('onboarding-completed', 'true');
    onPreferenceChange?.('expertise.skipOnboarding', true);
  };

  const handleOnboardingSkip = () => {
    setActiveOnboarding(false);
    localStorage.setItem('onboarding-skipped', 'true');
  };

  const startTutorial = (tutorialId) => {
    setActiveTutorial(tutorialId);
  };

  const showTooltip = (target, content, position) => {
    setActiveTooltip({ target, content, position });
  };

  const showFeatureSpotlight = (feature) => {
    setActiveSpotlight(feature);
  };

  // Expose methods globally for other components to use
  useEffect(() => {
    window.helpSystem = {
      startTutorial,
      showTooltip,
      showFeatureSpotlight,
      startOnboarding: () => setActiveOnboarding(true)
    };
  }, []);

  return (
    <>
      <OnboardingSystem
        isActive={activeOnboarding}
        onComplete={handleOnboardingComplete}
        onSkip={handleOnboardingSkip}
        userExpertise={userPreferences?.expertise?.level}
      />
      
      <InteractiveTutorial
        tutorialId={activeTutorial}
        isActive={!!activeTutorial}
        onComplete={() => setActiveTutorial(null)}
        onClose={() => setActiveTutorial(null)}
      />
      
      <HelpTooltip
        target={activeTooltip?.target}
        content={activeTooltip?.content}
        position={activeTooltip?.position}
        isVisible={!!activeTooltip}
        onClose={() => setActiveTooltip(null)}
      />
      
      <FeatureSpotlight
        feature={activeSpotlight}
        isVisible={!!activeSpotlight}
        onDismiss={() => setActiveSpotlight(null)}
        onTryFeature={() => {
          // Handle feature activation
          window.dispatchEvent(new CustomEvent('activate-feature', {
            detail: { feature: activeSpotlight.id }
          }));
          setActiveSpotlight(null);
        }}
      />
    </>
  );
};

export default HelpOnboardingSystem;
export { OnboardingSystem, InteractiveTutorial, HelpTooltip, FeatureSpotlight };