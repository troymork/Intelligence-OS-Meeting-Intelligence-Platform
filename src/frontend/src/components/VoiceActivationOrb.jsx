/**
 * Voice Activation Orb Component
 * Interactive voice activation interface with real-time feedback and visual response indicators
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import './VoiceActivationOrb.css';

const VoiceActivationOrb = ({
  onVoiceStart,
  onVoiceEnd,
  onTranscript,
  onError,
  isListening = false,
  isProcessing = false,
  confidence = 0,
  className = '',
  size = 'large',
  disabled = false
}) => {
  const [isActive, setIsActive] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [pulseIntensity, setPulseIntensity] = useState(0);
  const [visualizerData, setVisualizerData] = useState(new Array(32).fill(0));
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const streamRef = useRef(null);
  
  // Voice recognition setup
  const recognition = useRef(null);
  
  useEffect(() => {
    // Initialize Web Speech API if available
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition.current = new SpeechRecognition();
      
      recognition.current.continuous = true;
      recognition.current.interimResults = true;
      recognition.current.lang = 'en-US';
      
      recognition.current.onstart = () => {
        setConnectionStatus('connected');
        onVoiceStart?.();
      };
      
      recognition.current.onresult = (event) => {
        let transcript = '';
        let isFinal = false;
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            isFinal = true;
          }
        }
        
        onTranscript?.(transcript, isFinal);
      };
      
      recognition.current.onerror = (event) => {
        setConnectionStatus('error');
        onError?.(event.error);
      };
      
      recognition.current.onend = () => {
        setConnectionStatus('disconnected');
        setIsActive(false);
        onVoiceEnd?.();
      };
    }
    
    return () => {
      if (recognition.current) {
        recognition.current.stop();
      }
      stopAudioVisualization();
    };
  }, [onVoiceStart, onVoiceEnd, onTranscript, onError]);
  
  // Audio visualization setup
  const startAudioVisualization = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      streamRef.current = stream;
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      analyserRef.current.fftSize = 64;
      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      const updateVisualization = () => {
        if (!analyserRef.current) return;
        
        analyserRef.current.getByteFrequencyData(dataArray);
        
        // Calculate average audio level
        const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
        const normalizedLevel = average / 255;
        
        setAudioLevel(normalizedLevel);
        setPulseIntensity(normalizedLevel * 2);
        
        // Update visualizer data
        const visualData = Array.from(dataArray).map(value => value / 255);
        setVisualizerData(visualData);
        
        animationFrameRef.current = requestAnimationFrame(updateVisualization);
      };
      
      updateVisualization();
    } catch (error) {
      console.error('Error accessing microphone:', error);
      onError?.('microphone_access_denied');
    }
  }, [onError]);
  
  const stopAudioVisualization = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    
    setAudioLevel(0);
    setPulseIntensity(0);
    setVisualizerData(new Array(32).fill(0));
  }, []);
  
  // Handle orb activation
  const handleOrbClick = useCallback(async () => {
    if (disabled) return;
    
    if (!isActive) {
      setIsActive(true);
      await startAudioVisualization();
      
      if (recognition.current) {
        recognition.current.start();
      }
    } else {
      setIsActive(false);
      stopAudioVisualization();
      
      if (recognition.current) {
        recognition.current.stop();
      }
    }
  }, [isActive, disabled, startAudioVisualization, stopAudioVisualization]);
  
  // Handle keyboard activation
  const handleKeyDown = useCallback((event) => {
    if (event.code === 'Space' && !event.repeat) {
      event.preventDefault();
      handleOrbClick();
    }
  }, [handleOrbClick]);
  
  useEffect(() => {
    if (isListening && !isActive) {
      handleOrbClick();
    } else if (!isListening && isActive) {
      handleOrbClick();
    }
  }, [isListening, isActive, handleOrbClick]);
  
  // Generate orb size classes
  const sizeClasses = {
    small: 'voice-orb--small',
    medium: 'voice-orb--medium',
    large: 'voice-orb--large',
    xlarge: 'voice-orb--xlarge'
  };
  
  // Generate status classes
  const statusClasses = {
    disconnected: 'voice-orb--disconnected',
    connected: 'voice-orb--connected',
    error: 'voice-orb--error'
  };
  
  return (
    <div className={`voice-orb-container ${className}`}>
      {/* Main Voice Orb */}
      <div
        className={`
          voice-orb
          ${sizeClasses[size]}
          ${statusClasses[connectionStatus]}
          ${isActive ? 'voice-orb--active' : ''}
          ${isProcessing ? 'voice-orb--processing' : ''}
          ${disabled ? 'voice-orb--disabled' : ''}
        `}
        onClick={handleOrbClick}
        onKeyDown={handleKeyDown}
        tabIndex={disabled ? -1 : 0}
        role="button"
        aria-label={isActive ? 'Stop voice input' : 'Start voice input'}
        aria-pressed={isActive}
        style={{
          '--pulse-intensity': pulseIntensity,
          '--audio-level': audioLevel,
          '--confidence-level': confidence
        }}
      >
        {/* Core Orb */}
        <div className="voice-orb__core">
          {/* Microphone Icon */}
          <div className="voice-orb__icon">
            {isProcessing ? (
              <div className="voice-orb__processing-spinner" />
            ) : (
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
            )}
          </div>
          
          {/* Audio Level Indicator */}
          <div className="voice-orb__level-indicator">
            <div 
              className="voice-orb__level-bar"
              style={{ transform: `scaleY(${audioLevel})` }}
            />
          </div>
        </div>
        
        {/* Pulse Rings */}
        <div className="voice-orb__pulse-ring voice-orb__pulse-ring--1" />
        <div className="voice-orb__pulse-ring voice-orb__pulse-ring--2" />
        <div className="voice-orb__pulse-ring voice-orb__pulse-ring--3" />
        
        {/* Audio Visualizer */}
        <div className="voice-orb__visualizer">
          {visualizerData.map((value, index) => (
            <div
              key={index}
              className="voice-orb__visualizer-bar"
              style={{
                height: `${Math.max(2, value * 100)}%`,
                animationDelay: `${index * 0.05}s`
              }}
            />
          ))}
        </div>
        
        {/* Confidence Indicator */}
        {confidence > 0 && (
          <div className="voice-orb__confidence">
            <div 
              className="voice-orb__confidence-arc"
              style={{
                '--confidence-percentage': `${confidence * 100}%`
              }}
            />
          </div>
        )}
      </div>
      
      {/* Status Indicator */}
      <div className="voice-orb__status">
        <div className={`voice-orb__status-dot voice-orb__status-dot--${connectionStatus}`} />
        <span className="voice-orb__status-text">
          {connectionStatus === 'connected' && 'Listening...'}
          {connectionStatus === 'disconnected' && 'Tap to speak'}
          {connectionStatus === 'error' && 'Connection error'}
          {isProcessing && 'Processing...'}
        </span>
      </div>
      
      {/* Keyboard Hint */}
      <div className="voice-orb__hint">
        Press <kbd>Space</kbd> to activate
      </div>
    </div>
  );
};

export default VoiceActivationOrb;