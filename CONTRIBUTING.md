# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/Tofunmi-creator/pymongo_shard/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

pymongo_shard could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/Tofunmi-creator/pymongo_shard/issues.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `pymongo_shard` for local development.

1. Fork the `pymongo_shard` repo on GitHub.
2. Clone your fork locally:

   ```sh
   git clone git@github.com:your_name_here/pymongo_shard.git
   ```

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development:

   ```
   python -m venv yourvirtualenv
   cd pymongo_shard/
   pip install -e .
   ```

4. Create a branch for local development:

   ```sh
   git switch -c name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass pytest tests:

   ```sh
   pytest tests_pymongo_shard/*
   # Or
   pytest tests_pymongo_shard/* -vv
   ```

   To run the tests, "pip install pytest pytest-mock requests-mock" into your virtualenv.

6. Commit your changes and push your branch to GitHub:

   ```sh
   git add .
   git commit -m "Your detailed description of your changes."
   git push master name-of-your-bugfix-or-feature
   ```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, write tests covering all edge cases for your new fuunction(s), and add the feature to the list in README.md.
3. Ensure that your tests are included in file(s) contained in the tests_pymongo_shard folder and run using the process described in section 5 of Get Sarted section.
4. The pull request should work for Python 3.11 or higher. 


## Deploying

Make sure all your changes are committed (including an entry in HISTORY.md).


## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
