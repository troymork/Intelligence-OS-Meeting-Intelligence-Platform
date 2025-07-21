# Intelligence OS Platform 🧠

> **Oracle 9.1 Protocol Compliant Meeting Intelligence Platform**

A comprehensive AI-powered system that transforms meetings into actionable intelligence through sophisticated AI orchestration, voice-first interfaces, and real-time collaborative analysis.

## 🚀 Quick Start with GitHub Codespaces

**Recommended**: Use GitHub Codespaces to run this resource-intensive platform in the cloud, keeping your local machine free!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/your-username/intelligence-os-platform)

### 1. Create Codespace
- Click the "Code" button above
- Select "Codespaces" tab
- Click "Create codespace on main"

### 2. Start the Platform
Once your Codespace loads:
```bash
./start-platform.sh
```

### 3. Access Your Platform
- **Frontend**: `https://your-codespace-3000.app.github.dev`
- **Backend API**: `https://your-codespace-8000.app.github.dev`
- **Voice Processor**: `https://your-codespace-5000.app.github.dev`

📖 **[Full Codespace Setup Guide](README-CODESPACE.md)**

## ✨ Features

### 🎯 Oracle 9.1 Protocol Compliance
- **Six-Dimensional Analysis**: Structural Extraction, Pattern Recognition, Strategic Synthesis, Narrative Integration, Solution Architecture, Human Needs Dynamics
- **Comprehensive Output Generation**: 12 standardized output sections
- **External Integrations**: Zapier, Notion, Dart Action Management, Git

### 🎤 Voice-First Interface
- **Real-time Speech Recognition**: Multi-speaker support with high accuracy
- **Speaker Identification**: Individual voice tracking and attribution
- **Voice Commands**: Hands-free interaction and control
- **Audio Processing**: Noise reduction and enhancement

### 🤖 AI Orchestration Framework
- **AI Conductor**: Coordinates multiple specialized AI engines
- **Specialized AI Performers**: Six dedicated AI systems for different analysis dimensions
- **Conflict Resolution**: Intelligent handling of disagreements between AI analyses
- **Result Synthesis**: Coherent integration of multiple AI outputs

### 📊 Human Needs Analysis
- **Six Fundamental Needs**: Certainty, Variety, Significance, Connection, Growth, Contribution
- **Need Imbalance Detection**: Identifies overemphasis and underemphasis patterns
- **Targeted Interventions**: Personalized recommendations for individual and team development
- **Privacy Protection**: Ethical handling of psychological data

### 🎯 Strategic Framework Integration
- **SDG Alignment**: Sustainable Development Goals assessment
- **Doughnut Economy**: Regenerative and distributive analysis
- **Agreement Economy**: Collaboration and value-sharing evaluation
- **Multi-Framework Synthesis**: Identifies synergies and optimization opportunities

## 🏗 Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        VUI[Voice User Interface]
        WEB[Web Dashboard]
        MOB[Mobile App]
    end
    
    subgraph "AI Processing Layer"
        CONDUCTOR[AI Conductor]
        STRUCT[Structural AI]
        PATTERN[Pattern AI]
        STRATEGIC[Strategic AI]
        NARRATIVE[Narrative AI]
        SOLUTION[Solution AI]
        NEEDS[Human Needs AI]
    end
    
    subgraph "Core Services"
        CONV[Conversation Engine]
        ORCH[AI Orchestration]
        HUMAN[Human Needs Analysis]
        STRAT[Strategic Analysis]
        OUTPUT[Output Generation]
    end
    
    subgraph "Data Layer"
        REALTIME[Real-time Database]
        ANALYTICS[Analytics Database]
        KNOWLEDGE[Knowledge Graph]
    end
    
    VUI --> CONV
    WEB --> CONV
    CONV --> CONDUCTOR
    CONDUCTOR --> STRUCT
    CONDUCTOR --> PATTERN
    CONDUCTOR --> STRATEGIC
    CONDUCTOR --> NARRATIVE
    CONDUCTOR --> SOLUTION
    CONDUCTOR --> NEEDS
    CONV --> ORCH
    ORCH --> OUTPUT
    OUTPUT --> REALTIME
```

## 🛠 Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** with Neumorphic design
- **Web Speech API** for voice interaction
- **D3.js** for data visualization

### Backend
- **Python 3.9** with FastAPI
- **PostgreSQL** for primary database
- **Redis** for caching and real-time data
- **SQLAlchemy** for ORM
- **Celery** for background processing

### AI & ML
- **OpenAI GPT-4** for language processing
- **Anthropic Claude** for analysis
- **Transformers** for NLP tasks
- **SpeechRecognition** for voice processing

### Infrastructure
- **Docker** for containerization
- **Kubernetes** for orchestration
- **Terraform** for infrastructure as code
- **Prometheus & Grafana** for monitoring

## 📋 Requirements

### System Requirements (for local development)
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **OS**: macOS, Linux, or Windows with WSL2

### Cloud Requirements (GitHub Codespaces)
- **GitHub account** with Codespaces access
- **Web browser** (Chrome, Firefox, Safari, Edge)
- **Internet connection**

## 🚀 Deployment Options

### 1. GitHub Codespaces (Recommended)
```bash
# Automatic setup in cloud environment
# No local resources required
./start-platform.sh
```

### 2. Local Development
```bash
# Clone repository
git clone https://github.com/your-username/intelligence-os-platform.git
cd intelligence-os-platform

# Start with Docker Compose
./scripts/deploy-local-simple.sh
```

### 3. Cloud Deployment
```bash
# Deploy to staging
./scripts/deploy.sh staging aws us-west-2

# Deploy to production
./scripts/deploy.sh production aws us-west-2
```

## 📚 Documentation

- **[Codespace Setup Guide](README-CODESPACE.md)** - Cloud development setup
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Comprehensive deployment instructions
- **[API Documentation](docs/api-documentation.md)** - REST API reference
- **[Oracle 9.1 Protocol](docs/oracle-protocol.md)** - Protocol specification
- **[Architecture Guide](docs/architecture-guide.md)** - System architecture details

## 🧪 Testing

```bash
# Run all tests
npm run test:all

# Run specific test suites
npm run test:unit
npm run test:integration
npm run test:security
npm run test:performance
```

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/intelligence_os

# External Integrations
NOTION_API_KEY=your-notion-api-key
ZAPIER_WEBHOOK_SECRET=your-zapier-secret
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Oracle 9.1 Protocol** specification
- **OpenAI** for GPT-4 API
- **Anthropic** for Claude API
- **GitHub** for Codespaces infrastructure
- **Open source community** for foundational tools

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/intelligence-os-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/intelligence-os-platform/discussions)

---

**Built with ❤️ for organizational intelligence and human flourishing**