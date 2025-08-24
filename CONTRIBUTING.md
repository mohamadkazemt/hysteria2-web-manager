# Contributing to Hysteria2 Web Manager

We love your input! We want to make contributing to Hysteria2 Web Manager as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to sync code to and from our internal repository. We'll use GitHub to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `master`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Report bugs using GitHub's issues

We use GitHub issues to track public bugs. Report a bug by opening a new issue.

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/hysteria2-web-manager.git
cd hysteria2-web-manager
```

2. Set up development environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Set up development server
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python src/app.py
```

## Code Style

- Use Python PEP 8 style guide
- Use meaningful variable names
- Add comments for complex logic
- Follow existing code patterns
- Test your changes

## Testing

- Test all new features
- Test on different Python versions (3.8+)
- Test on different operating systems when possible
- Include both positive and negative test cases

## Persian Language Support

When contributing to the Persian interface:
- Use proper RTL layout
- Test with Persian text
- Ensure proper font rendering
- Check mobile responsiveness

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## References

This document was adapted from the open-source contribution guidelines for Facebook's Draft
