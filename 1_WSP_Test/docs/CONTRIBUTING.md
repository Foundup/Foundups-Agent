# Contributing to FoundUps Agent

First off, thank you for considering contributing to FoundUps Agent! It's people like you that help make this project a powerful tool for fostering logical discussion and countering misinformation in YouTube livestreams.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and constructive environment. Key points:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Describe the behavior you observed and what you expected
- Include any relevant logs or error messages
- Note your environment (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the proposed functionality
- Explain why this enhancement would be useful
- List any alternative solutions you've considered

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Update `ModLog.md` with your changes
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the ModLog.md with a note describing your changes
3. The PR will be merged once you have the sign-off of at least one maintainer

## Development Guidelines

### Project Structure

Follow the established project structure:
```
foundups-agent/
├── ai/                 # AI/LLM integration modules
├── blockchain/         # Blockchain and token integration
├── composer/          # Message composition and formatting
├── modules/           # Core YouTube API interaction modules
├── utils/             # Utility functions and logging
└── [other directories]
```

### Coding Standards

1. **Python Style Guide**
   - Follow PEP 8
   - Use meaningful variable and function names
   - Add docstrings to all functions and classes
   - Keep functions focused and single-purpose

2. **Documentation**
   - Document all new features
   - Update relevant README sections
   - Include docstrings and type hints
   - Comment complex logic

3. **Testing**
   - Write unit tests for new features
   - Ensure all tests pass before submitting PR
   - Add integration tests where appropriate
   - Maintain test coverage

4. **Error Handling**
   - Use appropriate exception types
   - Log errors with context
   - Provide helpful error messages
   - Handle edge cases gracefully

5. **Security**
   - Never commit credentials or secrets
   - Use environment variables for configuration
   - Follow security best practices
   - Report security issues privately

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Reference issues and pull requests
- Keep commits focused and atomic

Example:
```
Add user message logging feature

- Implement JSONL logging format
- Add user-specific log files
- Include timestamp and metadata
- Update documentation

Fixes #123
```

### Environment Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up pre-commit hooks (recommended):
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
pytest tests/
```

## Getting Help

- Join our community discussions
- Check the documentation
- Ask questions in issues
- Reach out to maintainers

## Recognition

Contributors will be recognized in:
- The project's contributors list
- Release notes
- Special acknowledgments for significant contributions

Thank you for contributing to FoundUps Agent! 🚀 