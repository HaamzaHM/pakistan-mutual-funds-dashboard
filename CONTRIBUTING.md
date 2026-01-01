# Contributing to Pakistan Mutual Funds Dashboard

Thank you for your interest in contributing to this project! This dashboard aims to make mutual funds data accessible to every Pakistani investor.

## Ways to Contribute

### 1. **Report Bugs** 🐛
Found a bug? Help us fix it!
- Open a [GitHub Issue](https://github.com/HaamzaHM/pakistan-mutual-funds-dashboard/issues)
- Include steps to reproduce
- Describe what you expected vs. what happened

### 2. **Suggest Features** 💡
Have an idea for improvement?
- Check existing issues first (might already be planned)
- Open a new issue with: [Feature Request]
- Explain why this feature would be useful
- Provide examples if possible

### 3. **Improve Documentation** 📚
Help make the docs clearer:
- Fix typos
- Add examples
- Clarify confusing sections
- Add new guides

### 4. **Add Code Improvements** 💻
Want to code? Great!
- Fork the repository
- Create a feature branch: `git checkout -b feature/your-feature-name`
- Make your changes
- Test thoroughly
- Submit a pull request

### 5. **Update Data** 📊
Help keep the mutual funds data current:
- Download latest data from [MUFAP website](https://www.mufap.com.pk/)
- Update `data/funds_clean.csv`
- Submit a pull request with updated data

### 6. **Spread the Word** 📢
- Star the repository ⭐
- Share with friends and colleagues
- Post about it on social media
- Mention it in forums and communities

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- GitHub account

### Local Development

1. **Fork the repository**
   - Click "Fork" on GitHub

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/pakistan-mutual-funds-dashboard.git
   cd pakistan-mutual-funds-dashboard
   ```

3. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

6. **Make your changes**
   - Edit files as needed
   - Test frequently: `streamlit run app.py`

7. **Test your changes**
   ```bash
   # Test the app
   streamlit run app.py
   
   # Try all filters
   # Check all tabs
   # Verify data loads correctly
   ```

8. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

9. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

10. **Create a Pull Request**
    - Go to GitHub
    - Click "New Pull Request"
    - Describe your changes
    - Wait for review

## Code Guidelines

### Style
- Use clear, descriptive variable names
- Add comments for complex logic
- Keep functions focused and small
- Follow PEP 8 Python style guide

### File Organization
- Main app logic: `app.py`
- Configuration: `config.py`
- Styling: `styles/style.css`
- Data: `data/`

### Before Submitting PR
- Test your changes thoroughly
- Update documentation if needed
- Make sure no debugging code is left
- Keep commits clean and organized

## Pull Request Process

1. **Update README** if adding features
2. **Test everything** before submitting
3. **Write clear commit messages**
4. **Link related issues** in PR description
5. **Be responsive** to feedback
6. **Keep PRs focused** on one feature/fix

### PR Title Format
- `feat: add feature description`
- `fix: fix bug description`
- `docs: update documentation`
- `refactor: improve code structure`

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
How to test these changes

## Related Issues
Fixes #123
```

## Contribution Areas

### High Priority 🔴
- **Data Updates:** Latest MUFAP data
- **Bug Fixes:** Any reported bugs
- **Performance:** Speed improvements

### Medium Priority 🟡
- **Documentation:** Better guides
- **UI Improvements:** Better design
- **New Filters:** Additional filtering options

### Low Priority 🟢
- **Code Refactoring:** Cleaner code
- **Tests:** More comprehensive testing
- **Examples:** Sample usage guides

## Questions?

- **Email:** m.hamzamaliik@gmail.com
- **LinkedIn:** [linkedin.com/in/hamzamaliik](https://www.linkedin.com/in/hamzamaliik/)
- **Open an Issue:** [GitHub Issues](https://github.com/HaamzaHM/pakistan-mutual-funds-dashboard/issues)

## Code of Conduct

- Be respectful to all contributors
- Provide constructive feedback
- Welcome new contributors
- Focus on the code, not the person
- Help others learn

## License

By contributing, you agree that your contributions will be licensed under the same MIT License as the project.

---

**Thank you for contributing to make Pakistani mutual funds data more accessible! 🙏📊**

*Together, we're helping Pakistani investors make better financial decisions.*
