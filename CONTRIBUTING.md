# Contributing to ReddyFit

Thank you for your interest in contributing to ReddyFit! This document provides guidelines and instructions for contributing.

## 🌟 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and encourage diverse contributions
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- OpenAI API access (for testing photo analysis)
- Firebase account (for database testing)

### Development Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/reddy.git
   cd reddy
   ```

2. **Set up virtual environment**
   ```bash
   cd features/photoanalysis
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your test API keys
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## 💻 Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch (if exists)
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates
- `test/*` - Test additions/updates

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(photoanalysis): add image rotation correction"
git commit -m "fix(whoop): handle missing recovery data gracefully"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(validation): add edge cases for image quality"
```

### Code Style

**Python:**
- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions/classes
- Format with Black (optional but recommended)

```python
def calculate_adonis_index(
    shoulder_width_cm: float,
    waist_circumference_cm: float
) -> float:
    """
    Calculate Adonis Index (shoulder-to-waist ratio)

    Args:
        shoulder_width_cm: Shoulder width in centimeters
        waist_circumference_cm: Waist circumference in centimeters

    Returns:
        Adonis Index ratio

    Raises:
        ValueError: If measurements are invalid
    """
    if waist_circumference_cm <= 0:
        raise ValueError("Waist circumference must be positive")

    return shoulder_width_cm / waist_circumference_cm
```

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=features tests/

# Run specific test file
pytest tests/test_photoanalysis/test_image_validator.py
```

**Test Guidelines:**
- Write tests for new features
- Maintain or improve code coverage
- Use descriptive test names
- Include edge cases and error conditions

## 📝 Pull Request Process

### Before Submitting

1. **Update documentation**
   - Update README if feature is user-facing
   - Add docstrings to new functions
   - Update API docs if endpoints changed

2. **Run tests**
   ```bash
   pytest tests/
   ```

3. **Check code style**
   ```bash
   # Optional: Format with Black
   black features/photoanalysis/

   # Check with flake8
   flake8 features/
   ```

4. **Update CHANGELOG** (if exists)
   - Add your changes under "Unreleased"

### Submitting PR

1. **Push your changes**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub**
   - Use a descriptive title
   - Reference any related issues (#123)
   - Describe what changed and why
   - Add screenshots for UI changes
   - List any breaking changes

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for feature
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

3. **Respond to review feedback**
   - Be open to suggestions
   - Make requested changes promptly
   - Ask questions if anything is unclear

### After Merge

1. **Delete your branch**
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update your fork**
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

## 🐛 Reporting Bugs

### Before Reporting

- Check if the bug has already been reported
- Verify it's actually a bug and not intended behavior
- Collect relevant information

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Run command '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g., Windows 11, macOS 14, Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- Package version: [e.g., photoanalysis v0.1.0]

**Additional context**
Any other relevant information.
```

## 💡 Suggesting Features

We welcome feature suggestions! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** the feature would solve
3. **Propose a solution** if you have one in mind
4. **Consider alternatives** you've thought about

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots.
```

## 📚 Documentation

Documentation improvements are always welcome:

- Fix typos or clarify existing docs
- Add examples
- Improve API documentation
- Write tutorials or guides

## 🎯 Priority Areas

We especially welcome contributions in:

1. **Photo Analysis Pipeline** (Steps 2-20)
   - Image preprocessing
   - MediaPipe angle detection
   - GPT-4o integration
   - Mathematical analysis

2. **Testing**
   - Unit tests for utilities
   - Integration tests for full pipeline
   - Performance benchmarking

3. **Documentation**
   - API reference
   - Tutorial videos
   - Architecture diagrams

4. **Performance**
   - Optimization for <30s target
   - Caching strategies
   - Parallel processing

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/DandaAkhilReddy/reddy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/DandaAkhilReddy/reddy/discussions)

## ❓ Questions?

Don't hesitate to ask! Open an issue with the "question" label or start a discussion.

---

Thank you for contributing to ReddyFit! 🎉
