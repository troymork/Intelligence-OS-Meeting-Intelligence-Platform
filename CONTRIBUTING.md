# Contributing to Oracle 9.1 Protocol Development Kit

Thank you for your interest in contributing to the Oracle 9.1 Protocol Development Kit! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project adheres to a code of conduct that promotes a welcoming and inclusive environment. By participating, you agree to uphold these standards:

- Be respectful and inclusive
- Focus on constructive feedback
- Collaborate effectively
- Respect different viewpoints and experiences
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Docker (optional, for containerized development)

### Setup Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/oracle-91-protocol-devkit.git
   cd oracle-91-protocol-devkit
   ```
3. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```
4. Start the development environment:
   ```bash
   ./scripts/dev.sh
   ```

## Development Process

### Branching Strategy

We use a Git flow branching model:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature development branches
- `hotfix/*` - Critical bug fixes
- `release/*` - Release preparation branches

### Workflow

1. Create a feature branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: add new Oracle analysis dimension"
   ```

3. Push to your fork and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

We follow the Conventional Commits specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: implement six-dimensional analysis framework
fix: resolve voice processing timeout issue
docs: update API documentation for Oracle endpoints
test: add unit tests for meeting analysis
```

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use Black for code formatting
- Use isort for import sorting
- Use type hints for all functions
- Maximum line length: 88 characters

```python
# Good example
def analyze_meeting(
    transcript: str, 
    participants: List[str], 
    context: Optional[str] = None
) -> OracleAnalysisResult:
    """Analyze meeting using Oracle 9.1 Protocol."""
    pass
```

### JavaScript/TypeScript (Frontend)

- Follow Airbnb JavaScript Style Guide
- Use Prettier for code formatting
- Use ESLint for linting
- Prefer TypeScript for type safety
- Use functional components with hooks

```typescript
// Good example
interface MeetingAnalysisProps {
  transcript: string;
  participants: string[];
  onAnalysisComplete: (result: AnalysisResult) => void;
}

const MeetingAnalysis: React.FC<MeetingAnalysisProps> = ({
  transcript,
  participants,
  onAnalysisComplete,
}) => {
  // Component implementation
};
```

### Documentation

- Use clear, concise language
- Include code examples
- Document all public APIs
- Update README files when adding features
- Use Markdown for documentation

## Testing Guidelines

### Backend Testing

- Write unit tests for all functions
- Use pytest framework
- Aim for >90% code coverage
- Include integration tests for API endpoints

```python
# Test example
def test_oracle_analysis():
    """Test Oracle 9.1 Protocol analysis functionality."""
    result = analyze_meeting(
        transcript="Test meeting transcript",
        participants=["Alice", "Bob"]
    )
    assert result.overall_score > 0
    assert len(result.analysis) == 6  # Six dimensions
```

### Frontend Testing

- Write unit tests for components
- Use Jest and React Testing Library
- Test user interactions
- Include accessibility tests

```typescript
// Test example
test('renders meeting analysis component', () => {
  render(
    <MeetingAnalysis 
      transcript="Test transcript"
      participants={['Alice', 'Bob']}
      onAnalysisComplete={jest.fn()}
    />
  );
  expect(screen.getByText('Oracle Analysis')).toBeInTheDocument();
});
```

### Running Tests

```bash
# Run all tests
./scripts/test.sh

# Run backend tests only
cd src/backend && python -m pytest

# Run frontend tests only
cd src/frontend && npm test
```

## Documentation

### API Documentation

- Document all endpoints using OpenAPI/Swagger
- Include request/response examples
- Describe error conditions
- Update documentation with code changes

### Code Documentation

- Use docstrings for Python functions
- Use JSDoc for JavaScript/TypeScript
- Document complex algorithms
- Explain business logic

### User Documentation

- Update README files
- Create tutorials for new features
- Include troubleshooting guides
- Provide deployment instructions

## Pull Request Process

### Before Submitting

1. Ensure all tests pass
2. Update documentation
3. Run linting and formatting tools
4. Test your changes locally
5. Rebase your branch on latest develop

### PR Requirements

- Clear title and description
- Link to related issues
- Include screenshots for UI changes
- Add tests for new functionality
- Update CHANGELOG.md

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Review Process

1. Automated checks must pass
2. At least one code review required
3. All feedback addressed
4. Final approval from maintainer
5. Merge to develop branch

## Issue Reporting

### Bug Reports

Include the following information:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, versions)
- Screenshots or logs if applicable

### Feature Requests

Include the following information:

- Clear description of the feature
- Use case and motivation
- Proposed implementation approach
- Alternative solutions considered

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority:high` - High priority issue
- `priority:low` - Low priority issue

## Development Environment

### IDE Configuration

#### VS Code

Recommended extensions:
- Python
- Pylance
- Black Formatter
- ES7+ React/Redux/React-Native snippets
- Prettier
- ESLint

#### Settings

```json
{
  "python.defaultInterpreterPath": "./src/backend/venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### Docker Development

Use Docker for consistent development environment:

```bash
# Build development container
docker-compose -f docker-compose.dev.yml build

# Start development environment
docker-compose -f docker-compose.dev.yml up
```

## Release Process

### Version Numbering

We follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Steps

1. Create release branch from develop
2. Update version numbers
3. Update CHANGELOG.md
4. Test release candidate
5. Merge to main
6. Tag release
7. Deploy to production
8. Merge back to develop

## Community

### Communication Channels

- GitHub Issues - Bug reports and feature requests
- GitHub Discussions - General questions and ideas
- Email - oracle-nexus-dev@example.com

### Meetings

- Weekly development sync (Wednesdays 2 PM UTC)
- Monthly community call (First Friday of each month)
- Quarterly roadmap review

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Annual contributor awards
- Conference speaking opportunities

## Getting Help

If you need help:

1. Check existing documentation
2. Search GitHub issues
3. Ask in GitHub Discussions
4. Contact maintainers directly

Thank you for contributing to the Oracle 9.1 Protocol Development Kit!

