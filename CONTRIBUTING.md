# Contributing Guidelines

Thank you for your interest in contributing to the wind power cannibalization analysis project. This document provides guidelines for contributing to this research code repository.

## Purpose of this Repository

This repository contains the computational scripts accompanying a research publication. The primary purpose is to enable reproducibility and transparency of the published results in accordance with FAIR (Findable, Accessible, Interoperable, Reusable) principles.

## Types of Contributions

We welcome several types of contributions:

### Bug Reports
If you encounter issues running the code:
1. Check that all dependencies are correctly installed
2. Verify your input data matches the specifications in DATA.md
3. Open an issue with:
   - Python version and operating system
   - Complete error message and traceback
   - Steps to reproduce the problem

### Code Improvements
Contributions that improve code quality are welcome:
- Bug fixes
- Performance optimizations
- Code documentation improvements
- Enhanced error handling

### Extended Analysis
If you extend the analysis or apply it to new regions/time periods:
- Fork the repository
- Create a new branch for your analysis
- Document your modifications clearly
- Reference the original work appropriately

## Code Standards

### Python Style
- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings to functions and modules
- Keep functions focused and modular

### Documentation
- Update README.md if adding new scripts
- Document any new data requirements in DATA.md
- Add inline comments for complex logic

### Dependencies
- Minimize new dependencies where possible
- Document all new dependencies in requirements.txt
- Specify version constraints appropriately

## Submission Process

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/description`)
3. Make your changes with clear, descriptive commit messages
4. Test your changes thoroughly
5. Update documentation as needed
6. Submit a pull request with:
   - Clear description of changes
   - Motivation for the changes
   - Any relevant issue numbers

### Commit Messages
Use clear, imperative commit messages:
- Good: "Fix capture price calculation for missing data"
- Good: "Add validation for wind speed inputs"
- Avoid: "Fixed stuff", "Updates"

## Testing

While this repository does not include formal unit tests, please verify:
- Scripts run without errors on the provided data structure
- Output files are generated correctly
- Results are numerically consistent with expectations

## Questions and Discussion

For questions about the methodology or code:
1. Check existing issues and pull requests
2. Consult the README.md and DATA.md documentation
3. Open a new issue for substantive questions

## Code of Conduct

### Expected Behavior
- Be respectful and constructive in all interactions
- Focus on the technical merits of contributions
- Acknowledge the research context and purpose

### Unacceptable Behavior
- Harassment or discriminatory language
- Trolling or inflammatory comments
- Sharing others' private information

## Attribution

Contributors who make substantial improvements will be acknowledged in the repository. However, authorship decisions for any associated publications remain with the original research team.

## Academic Integrity

When using or modifying this code:
- Cite the original publication (see CITATION.cff)
- Clearly indicate any modifications you have made
- Do not misrepresent derivative work as the original analysis

## License

By contributing to this repository, you agree that your contributions will be licensed under the same MIT License that covers the project.

## Contact

For major contributions or collaborations, please contact the repository maintainers before investing significant effort.
