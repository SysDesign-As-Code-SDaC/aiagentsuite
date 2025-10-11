# **The .aiagentsuite Framework**

Welcome to the .aiagentsuite, the operational core of Vibe-Driven Engineering (VDE). This suite is not just documentation; it is an enforceable framework designed to be the single source of truth for development standards, ensuring that both human and AI contributors adhere to the same high-quality principles and protocols.

This folder should be integrated into your project as a Git Submodule to ensure it stays up-to-date with the latest VDE standards.

## **How It Works**

The framework is broken down into several key areas. To understand how they connect, start with the dependency map.

* [**Dependency Map (DEPENDENCY\_MAP.md)**](https://www.google.com/search?q=./DEPENDENCY_MAP.md): A visual guide to how the principles, agents, protocols, and project context all relate to one another. **START HERE.**  
* [**Principles (/principles)**](https://www.google.com/search?q=./principles/): The core, immutable philosophies that govern all work. This includes our branching strategy and adherence to YAGNI.  
* [**Agents (/agents)**](https://www.google.com/search?q=./agents/): The master system prompts ("Constitutions") that define the roles, personas, and operational mandates for AI agents.  
* [**Project Context (/project\_context)**](https://www.google.com/search?q=./project_context/): Templates for providing stable, high-level context about your specific project to the AI.  
* [**Protocols (/protocols)**](https://www.google.com/search?q=./protocols/): The detailed, step-by-step operational playbooks for specific development tasks (e.g., secure code implementation, refactoring).  
* [**Governance (/governance)**](https://www.google.com/search?q=./governance/): Rules for how to contribute to and version the .aiagentsuite itself.

## **Usage**

For any development task involving an AI agent, the workflow is as follows:

1. **Load the Agent**: Start by providing the AI with the full content of the master agent constitution from /agents/00\_MASTER\_AGENT\_CONSTITUTION.md.  
2. **Provide Context**: Give the AI the relevant project context using the template in /project\_context/INSTRUCTIONS\_TEMPLATE.md.  
3. **Assign Protocol**: Instruct the AI to execute a specific task by following the exact steps outlined in the relevant file from the /protocols/ directory.

This structured approach ensures consistency, quality, and adherence to the VDE methodology.