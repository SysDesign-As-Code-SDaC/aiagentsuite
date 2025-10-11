# **Principle 2: Branching and Commit Strategy**

All code contributions, whether from humans or AI agents, MUST adhere to this branching and commit strategy to maintain a clean, understandable, and stable version history.

## **Branching Model: Trunk-Based Development with Short-Lived Feature Branches**

We use a simplified trunk-based development model.

1. **main is Sacred**: The main branch is the single source of truth. It MUST always be stable, deployable, and pass all tests. Direct commits to main are strictly forbidden.  
2. **Feature Branches**: All new work, including bug fixes, features, and refactors, MUST be done on a feature branch created from main.  
   * **Naming Convention**: Branches should be named with the format \[type\]/\[short-description\]. Examples:  
     * feat/user-authentication-api  
     * fix/login-page-css-bug  
     * refactor/database-query-optimization  
3. **Pull Requests (PRs)**: All feature branches MUST be merged into main via a Pull Request. The PR must be reviewed by at least one other team member.

## **Commit Strategy: Minimal, Atomic, and Conventional**

Our commit philosophy focuses on creating a clear and valuable history.

1. **Atomic Commits**: Each commit should represent a single, logical change. A commit should do one thing and do it well. Avoid large, multi-purpose commits.  
   * **Good**: "feat: Add user registration endpoint"  
   * **Bad**: "feat: Add user registration and update docs and fix login bug"  
2. **Minimal Changes**: Focus on making the smallest possible change that achieves the goal. Do not include unrelated refactoring or code cleanup in a feature commit. If you see something to improve, create a separate refactor or chore branch for it.  
3. **Conventional Commits**: All commit messages MUST follow the [Conventional Commits specification](https://www.conventionalcommits.org/). This ensures a consistent and machine-readable commit history.  
   * **Format**: \<type\>\[optional scope\]: \<description\>  
   * **Common Types**: feat, fix, build, chore, ci, docs, style, refactor, perf, test.

**AI Agent Mandate**: When asked to generate code or make changes, you MUST provide the output in a format that includes the proposed commit message, adhering to these standards.