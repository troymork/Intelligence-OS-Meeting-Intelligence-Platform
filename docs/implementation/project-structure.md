# Oracle Nexus Platform Project Structure

**Author:** Manus AI  
**Date:** January 13, 2025  
**Version:** 1.0  
**Document Type:** Project Organization and Development Templates

## Project Directory Structure

```
oracle-nexus-platform/
├── README.md
├── package.json
├── tsconfig.json
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy.yml
│       └── security-scan.yml
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── deployment/
│   └── user-guides/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── controllers/
│   │   │   ├── middleware/
│   │   │   ├── routes/
│   │   │   └── validators/
│   │   ├── services/
│   │   │   ├── ai-orchestration/
│   │   │   ├── meeting-management/
│   │   │   ├── voice-processing/
│   │   │   └── integration/
│   │   ├── models/
│   │   ├── database/
│   │   │   ├── migrations/
│   │   │   └── seeds/
│   │   ├── utils/
│   │   └── config/
│   ├── tests/
│   ├── package.json
│   └── Dockerfile
├── ai-services/
│   ├── orchestration/
│   │   ├── conductor/
│   │   ├── performers/
│   │   └── synthesis/
│   ├── analysis/
│   │   ├── structural-extraction/
│   │   ├── pattern-analysis/
│   │   ├── strategic-synthesis/
│   │   ├── narrative-integration/
│   │   ├── solution-architecture/
│   │   └── human-needs/
│   ├── voice/
│   │   ├── speech-recognition/
│   │   ├── nlp/
│   │   └── conversation-analysis/
│   ├── models/
│   ├── training/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── voice-interface/
│   │   │   ├── analytics/
│   │   │   └── collaboration/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── styles/
│   │   └── types/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── mobile/
│   ├── src/
│   ├── android/
│   ├── ios/
│   └── package.json
├── infrastructure/
│   ├── terraform/
│   ├── kubernetes/
│   ├── monitoring/
│   └── security/
├── scripts/
│   ├── setup/
│   ├── deployment/
│   └── maintenance/
└── tests/
    ├── integration/
    ├── e2e/
    └── performance/
```

## Core Configuration Files

### Root Package.json
```json
{
  "name": "oracle-nexus-platform",
  "version": "1.0.0",
  "description": "AI-powered meeting intelligence platform with Oracle 9.1 Protocol compliance",
  "private": true,
  "workspaces": [
    "backend",
    "frontend",
    "mobile"
  ],
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\" \"npm run dev:ai\"",
    "dev:backend": "cd backend && npm run dev",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:ai": "cd ai-services && python -m uvicorn main:app --reload",
    "build": "npm run build:backend && npm run build:frontend",
    "build:backend": "cd backend && npm run build",
    "build:frontend": "cd frontend && npm run build",
    "test": "npm run test:backend && npm run test:frontend && npm run test:ai",
    "test:backend": "cd backend && npm test",
    "test:frontend": "cd frontend && npm test",
    "test:ai": "cd ai-services && python -m pytest",
    "lint": "npm run lint:backend && npm run lint:frontend",
    "lint:backend": "cd backend && npm run lint",
    "lint:frontend": "cd frontend && npm run lint",
    "docker:build": "docker-compose build",
    "docker:up": "docker-compose up -d",
    "docker:down": "docker-compose down"
  },
  "devDependencies": {
    "concurrently": "^7.6.0",
    "husky": "^8.0.3",
    "lint-staged": "^13.2.0"
  },
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  },
  "lint-staged": {
    "*.{js,ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md}": ["prettier --write"]
  }
}
```

### TypeScript Configuration
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "baseUrl": "./",
    "paths": {
      "@/*": ["src/*"],
      "@/types/*": ["src/types/*"],
      "@/services/*": ["src/services/*"],
      "@/utils/*": ["src/utils/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: oracle_nexus
      POSTGRES_USER: oracle_user
      POSTGRES_PASSWORD: oracle_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/database/init:/docker-entrypoint-initdb.d

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  elasticsearch:
    image: elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://oracle_user:oracle_password@postgres:5432/oracle_nexus
      - REDIS_URL=redis://redis:6379
      - ELASTICSEARCH_URL=http://elasticsearch:9200
    depends_on:
      - postgres
      - redis
      - elasticsearch
    volumes:
      - ./backend:/app
      - /app/node_modules

  ai-services:
    build:
      context: ./ai-services
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=postgresql://oracle_user:oracle_password@postgres:5432/oracle_nexus
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./ai-services:/app
      - ai_models:/app/models

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3001:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:3000
      - REACT_APP_WS_URL=ws://localhost:3000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
  ai_models:
```

## Backend Service Templates

### API Controller Template
```typescript
// backend/src/api/controllers/BaseController.ts
import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';
import { Logger } from '@/utils/logger';
import { ApiResponse } from '@/types/api';

export abstract class BaseController {
  protected logger: Logger;

  constructor() {
    this.logger = new Logger(this.constructor.name);
  }

  protected validateRequest(req: Request, res: Response, next: NextFunction): boolean {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      this.sendError(res, 400, 'Validation failed', errors.array());
      return false;
    }
    return true;
  }

  protected sendSuccess<T>(
    res: Response,
    data: T,
    message: string = 'Success',
    statusCode: number = 200
  ): void {
    const response: ApiResponse<T> = {
      success: true,
      message,
      data,
      timestamp: new Date().toISOString()
    };
    res.status(statusCode).json(response);
  }

  protected sendError(
    res: Response,
    statusCode: number,
    message: string,
    errors?: any[]
  ): void {
    const response: ApiResponse<null> = {
      success: false,
      message,
      data: null,
      errors,
      timestamp: new Date().toISOString()
    };
    res.status(statusCode).json(response);
  }

  protected async handleAsync(
    fn: (req: Request, res: Response, next: NextFunction) => Promise<void>
  ) {
    return (req: Request, res: Response, next: NextFunction) => {
      Promise.resolve(fn(req, res, next)).catch(next);
    };
  }
}
```

### Meeting Management Service
```typescript
// backend/src/services/meeting-management/MeetingService.ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Meeting } from '@/models/Meeting';
import { CreateMeetingDto, UpdateMeetingDto } from '@/types/meeting';
import { Logger } from '@/utils/logger';
import { AIOrchestrationService } from '@/services/ai-orchestration/AIOrchestrationService';

@Injectable()
export class MeetingService {
  private logger = new Logger(MeetingService.name);

  constructor(
    @InjectRepository(Meeting)
    private meetingRepository: Repository<Meeting>,
    private aiOrchestrationService: AIOrchestrationService
  ) {}

  async createMeeting(createMeetingDto: CreateMeetingDto): Promise<Meeting> {
    try {
      this.logger.log('Creating new meeting', { title: createMeetingDto.title });

      const meeting = this.meetingRepository.create({
        ...createMeetingDto,
        status: 'scheduled',
        createdAt: new Date(),
        updatedAt: new Date()
      });

      const savedMeeting = await this.meetingRepository.save(meeting);

      // Initialize AI analysis preparation
      await this.aiOrchestrationService.prepareMeetingAnalysis(savedMeeting.id);

      this.logger.log('Meeting created successfully', { meetingId: savedMeeting.id });
      return savedMeeting;
    } catch (error) {
      this.logger.error('Failed to create meeting', error);
      throw new Error('Failed to create meeting');
    }
  }

  async startMeeting(meetingId: string): Promise<Meeting> {
    try {
      this.logger.log('Starting meeting', { meetingId });

      const meeting = await this.meetingRepository.findOne({
        where: { id: meetingId }
      });

      if (!meeting) {
        throw new Error('Meeting not found');
      }

      meeting.status = 'in_progress';
      meeting.actualStart = new Date();
      meeting.updatedAt = new Date();

      const updatedMeeting = await this.meetingRepository.save(meeting);

      // Start real-time AI analysis
      await this.aiOrchestrationService.startRealTimeAnalysis(meetingId);

      this.logger.log('Meeting started successfully', { meetingId });
      return updatedMeeting;
    } catch (error) {
      this.logger.error('Failed to start meeting', error);
      throw new Error('Failed to start meeting');
    }
  }

  async endMeeting(meetingId: string): Promise<Meeting> {
    try {
      this.logger.log('Ending meeting', { meetingId });

      const meeting = await this.meetingRepository.findOne({
        where: { id: meetingId }
      });

      if (!meeting) {
        throw new Error('Meeting not found');
      }

      meeting.status = 'completed';
      meeting.actualEnd = new Date();
      meeting.updatedAt = new Date();

      const updatedMeeting = await this.meetingRepository.save(meeting);

      // Trigger comprehensive analysis
      await this.aiOrchestrationService.triggerComprehensiveAnalysis(meetingId);

      this.logger.log('Meeting ended successfully', { meetingId });
      return updatedMeeting;
    } catch (error) {
      this.logger.error('Failed to end meeting', error);
      throw new Error('Failed to end meeting');
    }
  }
}
```

## AI Services Templates

### AI Orchestration Conductor
```python
# ai-services/orchestration/conductor/ai_conductor.py
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..performers.base_performer import BasePerformer
from ..synthesis.result_synthesizer import ResultSynthesizer
from ...models.analysis_request import AnalysisRequest
from ...models.analysis_result import AnalysisResult

class AnalysisStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class PerformerAssignment:
    performer: BasePerformer
    dimension: str
    priority: int
    dependencies: List[str]
    status: AnalysisStatus

class AIConductor:
    """
    Central coordinator for multi-AI collaboration implementing the Oracle 9.1 Protocol
    six-dimensional analysis methodology.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performers: Dict[str, BasePerformer] = {}
        self.synthesizer = ResultSynthesizer()
        self.active_analyses: Dict[str, Dict[str, PerformerAssignment]] = {}
        
    def register_performer(self, dimension: str, performer: BasePerformer) -> None:
        """Register a specialized AI performer for a specific analysis dimension."""
        self.performers[dimension] = performer
        self.logger.info(f"Registered performer for dimension: {dimension}")
        
    async def orchestrate_analysis(
        self, 
        request: AnalysisRequest
    ) -> AnalysisResult:
        """
        Orchestrate multi-dimensional analysis according to Oracle 9.1 Protocol.
        """
        try:
            self.logger.info(f"Starting analysis orchestration for meeting: {request.meeting_id}")
            
            # Create performer assignments
            assignments = self._create_performer_assignments(request)
            self.active_analyses[request.analysis_id] = assignments
            
            # Execute analysis in dependency order
            results = await self._execute_analysis_pipeline(request, assignments)
            
            # Synthesize results
            synthesized_result = await self.synthesizer.synthesize_results(
                request, results
            )
            
            # Clean up
            del self.active_analyses[request.analysis_id]
            
            self.logger.info(f"Analysis orchestration completed for meeting: {request.meeting_id}")
            return synthesized_result
            
        except Exception as e:
            self.logger.error(f"Analysis orchestration failed: {str(e)}")
            raise
            
    def _create_performer_assignments(
        self, 
        request: AnalysisRequest
    ) -> Dict[str, PerformerAssignment]:
        """Create performer assignments based on analysis requirements."""
        assignments = {}
        
        # Define analysis dimensions and their dependencies
        dimension_config = {
            "structural_extraction": {
                "priority": 1,
                "dependencies": []
            },
            "pattern_analysis": {
                "priority": 2,
                "dependencies": ["structural_extraction"]
            },
            "strategic_synthesis": {
                "priority": 3,
                "dependencies": ["structural_extraction", "pattern_analysis"]
            },
            "narrative_integration": {
                "priority": 3,
                "dependencies": ["structural_extraction", "pattern_analysis"]
            },
            "solution_architecture": {
                "priority": 4,
                "dependencies": ["strategic_synthesis", "narrative_integration"]
            },
            "human_needs_analysis": {
                "priority": 2,
                "dependencies": ["structural_extraction"]
            }
        }
        
        for dimension in request.analysis_dimensions:
            if dimension in self.performers and dimension in dimension_config:
                config = dimension_config[dimension]
                assignments[dimension] = PerformerAssignment(
                    performer=self.performers[dimension],
                    dimension=dimension,
                    priority=config["priority"],
                    dependencies=config["dependencies"],
                    status=AnalysisStatus.PENDING
                )
                
        return assignments
        
    async def _execute_analysis_pipeline(
        self,
        request: AnalysisRequest,
        assignments: Dict[str, PerformerAssignment]
    ) -> Dict[str, Any]:
        """Execute analysis pipeline respecting dependencies."""
        results = {}
        completed_dimensions = set()
        
        # Group by priority
        priority_groups = {}
        for dimension, assignment in assignments.items():
            priority = assignment.priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append((dimension, assignment))
            
        # Execute by priority groups
        for priority in sorted(priority_groups.keys()):
            group_tasks = []
            
            for dimension, assignment in priority_groups[priority]:
                # Check if dependencies are satisfied
                if all(dep in completed_dimensions for dep in assignment.dependencies):
                    assignment.status = AnalysisStatus.IN_PROGRESS
                    task = self._execute_performer_analysis(
                        assignment.performer, request, results
                    )
                    group_tasks.append((dimension, task))
                    
            # Execute group tasks concurrently
            if group_tasks:
                group_results = await asyncio.gather(
                    *[task for _, task in group_tasks],
                    return_exceptions=True
                )
                
                for (dimension, _), result in zip(group_tasks, group_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Analysis failed for dimension {dimension}: {str(result)}")
                        assignments[dimension].status = AnalysisStatus.FAILED
                    else:
                        results[dimension] = result
                        assignments[dimension].status = AnalysisStatus.COMPLETED
                        completed_dimensions.add(dimension)
                        
        return results
        
    async def _execute_performer_analysis(
        self,
        performer: BasePerformer,
        request: AnalysisRequest,
        previous_results: Dict[str, Any]
    ) -> Any:
        """Execute analysis for a specific performer."""
        return await performer.analyze(request, previous_results)
```

### Human Needs Analysis Performer
```python
# ai-services/analysis/human-needs/human_needs_performer.py
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..base_performer import BasePerformer
from ...models.analysis_request import AnalysisRequest
from ...models.human_needs import HumanNeedsAnalysis, NeedFulfillmentStatus
from ...utils.nlp_processor import NLPProcessor
from ...utils.emotional_analyzer import EmotionalAnalyzer

@dataclass
class NeedIndicator:
    need_category: str
    fulfillment_level: float
    confidence: float
    evidence: List[str]
    manifestations: List[str]

class HumanNeedsPerformer(BasePerformer):
    """
    Specialized AI performer for human needs analysis according to the six fundamental
    human needs framework required by Oracle 9.1 Protocol.
    """
    
    def __init__(self):
        super().__init__("human_needs_analysis")
        self.logger = logging.getLogger(__name__)
        self.nlp_processor = NLPProcessor()
        self.emotional_analyzer = EmotionalAnalyzer()
        
        # Six fundamental human needs categories
        self.need_categories = [
            "certainty",
            "variety", 
            "significance",
            "connection",
            "growth",
            "contribution"
        ]
        
    async def analyze(
        self, 
        request: AnalysisRequest, 
        previous_results: Dict[str, Any]
    ) -> HumanNeedsAnalysis:
        """
        Perform comprehensive human needs analysis on meeting content.
        """
        try:
            self.logger.info(f"Starting human needs analysis for meeting: {request.meeting_id}")
            
            # Extract conversation content
            conversation_data = await self._extract_conversation_data(request)
            
            # Analyze individual participants
            participant_analyses = {}
            for participant_id in conversation_data.get("participants", []):
                participant_analysis = await self._analyze_participant_needs(
                    participant_id, conversation_data, previous_results
                )
                participant_analyses[participant_id] = participant_analysis
                
            # Analyze team dynamics
            team_analysis = await self._analyze_team_needs_dynamics(
                conversation_data, participant_analyses
            )
            
            # Generate interventions
            interventions = await self._generate_need_interventions(
                participant_analyses, team_analysis
            )
            
            # Create comprehensive analysis result
            analysis_result = HumanNeedsAnalysis(
                meeting_id=request.meeting_id,
                participant_analyses=participant_analyses,
                team_analysis=team_analysis,
                interventions=interventions,
                confidence_metrics=self._calculate_confidence_metrics(
                    participant_analyses, team_analysis
                )
            )
            
            self.logger.info(f"Human needs analysis completed for meeting: {request.meeting_id}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Human needs analysis failed: {str(e)}")
            raise
            
    async def _analyze_participant_needs(
        self,
        participant_id: str,
        conversation_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, NeedFulfillmentStatus]:
        """Analyze individual participant's need fulfillment patterns."""
        
        # Extract participant's contributions
        participant_content = self._extract_participant_content(
            participant_id, conversation_data
        )
        
        need_statuses = {}
        
        for need_category in self.need_categories:
            # Analyze need fulfillment for this category
            indicators = await self._analyze_need_category(
                need_category, participant_content, conversation_data
            )
            
            # Calculate fulfillment level
            fulfillment_level = self._calculate_fulfillment_level(indicators)
            
            # Assess fulfillment quality
            fulfillment_quality = self._assess_fulfillment_quality(
                need_category, indicators, conversation_data
            )
            
            need_statuses[need_category] = NeedFulfillmentStatus(
                need_category=need_category,
                fulfillment_level=fulfillment_level,
                fulfillment_quality=fulfillment_quality,
                indicators=indicators,
                temporal_patterns=self._identify_temporal_patterns(
                    need_category, participant_content
                )
            )
            
        return need_statuses
        
    async def _analyze_need_category(
        self,
        need_category: str,
        participant_content: Dict[str, Any],
        conversation_data: Dict[str, Any]
    ) -> List[NeedIndicator]:
        """Analyze specific need category fulfillment."""
        
        indicators = []
        
        if need_category == "certainty":
            indicators.extend(await self._analyze_certainty_needs(
                participant_content, conversation_data
            ))
        elif need_category == "variety":
            indicators.extend(await self._analyze_variety_needs(
                participant_content, conversation_data
            ))
        elif need_category == "significance":
            indicators.extend(await self._analyze_significance_needs(
                participant_content, conversation_data
            ))
        elif need_category == "connection":
            indicators.extend(await self._analyze_connection_needs(
                participant_content, conversation_data
            ))
        elif need_category == "growth":
            indicators.extend(await self._analyze_growth_needs(
                participant_content, conversation_data
            ))
        elif need_category == "contribution":
            indicators.extend(await self._analyze_contribution_needs(
                participant_content, conversation_data
            ))
            
        return indicators
        
    async def _generate_need_interventions(
        self,
        participant_analyses: Dict[str, Dict[str, NeedFulfillmentStatus]],
        team_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate targeted interventions for need fulfillment improvement."""
        
        interventions = []
        
        # Analyze need imbalances
        imbalances = self._identify_need_imbalances(participant_analyses)
        
        for imbalance in imbalances:
            intervention = await self._create_intervention_for_imbalance(
                imbalance, participant_analyses, team_analysis
            )
            if intervention:
                interventions.append(intervention)
                
        return interventions
```

## Frontend Component Templates

### Voice Interface Component
```typescript
// frontend/src/components/voice-interface/VoiceActivationOrb.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useVoiceRecognition } from '@/hooks/useVoiceRecognition';
import { useWebSocket } from '@/hooks/useWebSocket';
import { VoiceState, VoiceCommand } from '@/types/voice';
import './VoiceActivationOrb.scss';

interface VoiceActivationOrbProps {
  onCommand: (command: VoiceCommand) => void;
  isActive: boolean;
  className?: string;
}

export const VoiceActivationOrb: React.FC<VoiceActivationOrbProps> = ({
  onCommand,
  isActive,
  className = ''
}) => {
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [audioLevel, setAudioLevel] = useState(0);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const {
    isListening,
    transcript,
    confidence,
    startListening,
    stopListening,
    error: voiceError
  } = useVoiceRecognition({
    onResult: handleVoiceResult,
    onAudioLevel: setAudioLevel
  });

  const { sendMessage, lastMessage } = useWebSocket('/voice-processing');

  const handleVoiceResult = useCallback((result: string, confidence: number) => {
    if (confidence > 0.7) {
      const command: VoiceCommand = {
        text: result,
        confidence,
        timestamp: new Date(),
        intent: 'unknown' // Will be determined by backend
      };
      onCommand(command);
    }
  }, [onCommand]);

  const handleOrbClick = useCallback(() => {
    if (isListening) {
      stopListening();
      setVoiceState('idle');
    } else {
      startListening();
      setVoiceState('listening');
    }
  }, [isListening, startListening, stopListening]);

  useEffect(() => {
    if (isListening) {
      setVoiceState('listening');
    } else if (transcript) {
      setVoiceState('processing');
      // Simulate processing delay
      setTimeout(() => setVoiceState('idle'), 1000);
    }
  }, [isListening, transcript]);

  const orbVariants = {
    idle: {
      scale: 1,
      boxShadow: '0 0 20px rgba(255, 106, 0, 0.3)',
      background: 'linear-gradient(145deg, #2C2E33, #1A1A1D)'
    },
    listening: {
      scale: 1.1,
      boxShadow: '0 0 40px rgba(255, 106, 0, 0.6)',
      background: 'linear-gradient(145deg, #FF6A00, #E55A00)'
    },
    processing: {
      scale: 1.05,
      boxShadow: '0 0 30px rgba(255, 106, 0, 0.5)',
      background: 'linear-gradient(145deg, #FF8533, #FF6A00)'
    }
  };

  const audioVisualizerVariants = {
    idle: { height: 4 },
    listening: { height: audioLevel * 20 + 4 },
    processing: { height: 12 }
  };

  return (
    <div className={`voice-activation-orb ${className}`}>
      <div className="orb-container">
        <motion.div
          className="orb"
          variants={orbVariants}
          animate={voiceState}
          onClick={handleOrbClick}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="orb-inner">
            <motion.div
              className="audio-visualizer"
              variants={audioVisualizerVariants}
              animate={voiceState}
            />
          </div>
        </motion.div>

        <AnimatePresence>
          {voiceState === 'listening' && (
            <motion.div
              className="listening-indicator"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              Listening...
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {suggestions.length > 0 && voiceState === 'idle' && (
            <motion.div
              className="command-suggestions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
            >
              {suggestions.map((suggestion, index) => (
                <motion.button
                  key={suggestion}
                  className="suggestion-button"
                  onClick={() => handleVoiceResult(suggestion, 1.0)}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  {suggestion}
                </motion.button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {transcript && (
        <div className="transcript-display">
          <span className="transcript-text">{transcript}</span>
          <span className="confidence-indicator">
            {Math.round(confidence * 100)}%
          </span>
        </div>
      )}

      {voiceError && (
        <div className="error-display">
          <span className="error-text">{voiceError}</span>
        </div>
      )}
    </div>
  );
};
```

### Analytics Dashboard Component
```typescript
// frontend/src/components/analytics/AnalyticsDashboard.tsx
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  HumanNeedsChart, 
  StrategicAlignmentChart, 
  PatternRecognitionChart,
  DecisionTrackingChart 
} from './charts';
import { ProtocolOverview } from './ProtocolOverview';
import { useAnalytics } from '@/hooks/useAnalytics';
import { AnalyticsData, ChartType } from '@/types/analytics';
import './AnalyticsDashboard.scss';

interface AnalyticsDashboardProps {
  meetingId: string;
  className?: string;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  meetingId,
  className = ''
}) => {
  const [selectedChart, setSelectedChart] = useState<ChartType>('overview');
  const [timeRange, setTimeRange] = useState('current');
  
  const {
    analyticsData,
    isLoading,
    error,
    refreshAnalytics
  } = useAnalytics(meetingId, timeRange);

  const chartComponents = {
    overview: ProtocolOverview,
    humanNeeds: HumanNeedsChart,
    strategicAlignment: StrategicAlignmentChart,
    patternRecognition: PatternRecognitionChart,
    decisionTracking: DecisionTrackingChart
  };

  const ChartComponent = chartComponents[selectedChart];

  return (
    <div className={`analytics-dashboard ${className}`}>
      <div className="dashboard-header">
        <h2>Oracle 9.1 Protocol Analysis</h2>
        <div className="dashboard-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-selector"
          >
            <option value="current">Current Meeting</option>
            <option value="week">Past Week</option>
            <option value="month">Past Month</option>
            <option value="quarter">Past Quarter</option>
          </select>
          <button 
            onClick={refreshAnalytics}
            className="refresh-button"
            disabled={isLoading}
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="chart-selector">
          {Object.keys(chartComponents).map((chartType) => (
            <motion.button
              key={chartType}
              className={`chart-selector-button ${
                selectedChart === chartType ? 'active' : ''
              }`}
              onClick={() => setSelectedChart(chartType as ChartType)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {chartType.replace(/([A-Z])/g, ' $1').trim()}
            </motion.button>
          ))}
        </div>

        <div className="main-chart-container">
          {isLoading ? (
            <div className="loading-indicator">
              <motion.div
                className="loading-spinner"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
              <span>Analyzing meeting data...</span>
            </div>
          ) : error ? (
            <div className="error-display">
              <span>Error loading analytics: {error}</span>
              <button onClick={refreshAnalytics}>Retry</button>
            </div>
          ) : (
            <motion.div
              key={selectedChart}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <ChartComponent data={analyticsData} />
            </motion.div>
          )}
        </div>

        <div className="insights-panel">
          <h3>Key Insights</h3>
          {analyticsData?.insights?.map((insight, index) => (
            <motion.div
              key={insight.id}
              className="insight-card"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="insight-header">
                <span className="insight-category">{insight.category}</span>
                <span className="insight-confidence">{insight.confidence}%</span>
              </div>
              <p className="insight-text">{insight.text}</p>
              {insight.recommendations && (
                <div className="insight-recommendations">
                  {insight.recommendations.map((rec, recIndex) => (
                    <span key={recIndex} className="recommendation-tag">
                      {rec}
                    </span>
                  ))}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

## Testing Templates

### Integration Test Template
```typescript
// tests/integration/meeting-lifecycle.test.ts
import request from 'supertest';
import { app } from '../../backend/src/app';
import { DatabaseTestHelper } from '../helpers/DatabaseTestHelper';
import { AIServiceMock } from '../mocks/AIServiceMock';

describe('Meeting Lifecycle Integration Tests', () => {
  let dbHelper: DatabaseTestHelper;
  let aiServiceMock: AIServiceMock;
  let authToken: string;

  beforeAll(async () => {
    dbHelper = new DatabaseTestHelper();
    await dbHelper.setup();
    
    aiServiceMock = new AIServiceMock();
    await aiServiceMock.setup();
    
    // Get auth token for testing
    const authResponse = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'testpassword'
      });
    
    authToken = authResponse.body.data.token;
  });

  afterAll(async () => {
    await dbHelper.cleanup();
    await aiServiceMock.cleanup();
  });

  describe('Complete Meeting Flow', () => {
    let meetingId: string;

    it('should create a new meeting', async () => {
      const meetingData = {
        title: 'Test Meeting',
        description: 'Integration test meeting',
        scheduledStart: new Date(Date.now() + 3600000).toISOString(),
        estimatedDuration: 60,
        participants: [
          {
            userId: 'user1',
            role: 'facilitator',
            permissions: ['manage_meeting', 'view_analytics']
          }
        ],
        objectives: ['Test objective 1', 'Test objective 2'],
        analyticalDepth: 'comprehensive'
      };

      const response = await request(app)
        .post('/api/meetings')
        .set('Authorization', `Bearer ${authToken}`)
        .send(meetingData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('id');
      expect(response.body.data.title).toBe(meetingData.title);
      expect(response.body.data.status).toBe('scheduled');

      meetingId = response.body.data.id;
    });

    it('should start the meeting and initialize AI analysis', async () => {
      const response = await request(app)
        .post(`/api/meetings/${meetingId}/start`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.status).toBe('in_progress');
      expect(response.body.data.actualStart).toBeDefined();

      // Verify AI analysis was initialized
      expect(aiServiceMock.getAnalysisStatus(meetingId)).toBe('initialized');
    });

    it('should process voice input and generate real-time insights', async () => {
      const voiceData = {
        meetingId,
        participantId: 'user1',
        transcript: 'I think we should focus on improving our customer satisfaction metrics.',
        confidence: 0.95,
        timestamp: new Date().toISOString()
      };

      const response = await request(app)
        .post('/api/voice/process')
        .set('Authorization', `Bearer ${authToken}`)
        .send(voiceData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('insights');
      expect(response.body.data.insights).toBeInstanceOf(Array);
    });

    it('should end the meeting and trigger comprehensive analysis', async () => {
      const response = await request(app)
        .post(`/api/meetings/${meetingId}/end`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.status).toBe('completed');
      expect(response.body.data.actualEnd).toBeDefined();

      // Verify comprehensive analysis was triggered
      expect(aiServiceMock.getAnalysisStatus(meetingId)).toBe('comprehensive_analysis_started');
    });

    it('should generate Oracle 9.1 Protocol compliant outputs', async () => {
      // Wait for analysis to complete
      await aiServiceMock.waitForAnalysisCompletion(meetingId);

      const response = await request(app)
        .get(`/api/meetings/${meetingId}/analysis`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('executiveSummary');
      expect(response.body.data).toHaveProperty('decisionsAgreements');
      expect(response.body.data).toHaveProperty('actionRegister');
      expect(response.body.data).toHaveProperty('strategicImplications');
      expect(response.body.data).toHaveProperty('humanNeedsAnalysis');
      expect(response.body.data).toHaveProperty('solutionPortfolio');

      // Validate Oracle 9.1 Protocol compliance
      expect(response.body.data.protocolCompliance.version).toBe('9.1');
      expect(response.body.data.protocolCompliance.completeness).toBeGreaterThan(0.9);
    });
  });
});
```

## References

[1] Oracle 9.1 Protocol Specification - Master System Prompt: AI Meeting Oracle, Version 9.1
[2] Oracle Nexus Platform Technical Architecture Documentation
[3] Node.js Best Practices for Enterprise Applications
[4] Python AI Services Architecture Patterns
[5] React TypeScript Component Development Guidelines

