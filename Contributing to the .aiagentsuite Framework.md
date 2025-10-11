# **Contributing to the .aiagentsuite Framework**

This document outlines the process for proposing changes, reporting issues, and contributing to the evolution of the VDE framework itself.

## **Philosophy**

The .aiagentsuite is a living framework. It is expected to evolve as we discover better patterns and protocols. However, changes must be made thoughtfully and systematically to avoid introducing confusion or conflicting principles.

## **Proposing a Change**

1. **Create an Issue**: Before making any changes, create a new Issue in the framework's Git repository. Clearly describe the proposed change, the problem it solves, and why it is an improvement over the current state.  
2. **Discuss**: The proposal will be discussed by the core maintainers. Changes to core principles require a higher degree of consensus than changes to specific protocols.  
3. **Create a PR**: Once the proposal is approved, a pull request can be created. The PR must follow the branching and commit standards defined in the principles.  
4. **Update Documentation**: The PR must include updates to all relevant documentation, including the DEPENDENCY\_MAP.md if the architecture is affected.

## **Versioning**

This framework follows Semantic Versioning 2.0.0.

* **MAJOR version (X.y.z)**: Incremented for incompatible changes to the core philosophy or agent constitution that would require existing projects to change their workflow.  
* **MINOR version (x.Y.z)**: Incremented for new, backward-compatible additions, such as adding a new protocol or a new optional section to the project context.  
* **PATCH version (x.y.Z)**: Incremented for backward-compatible bug fixes, such as correcting typos or clarifying language in existing documents.