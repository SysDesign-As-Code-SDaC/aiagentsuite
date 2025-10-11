# **.aiagentsuite Dependency Map**

This document provides a visual map of the relationships between the core components of the VDE framework. It clarifies how our high-level principles cascade down to the specific protocols executed by AI agents.

## **Component Architecture**

graph TD  
    A\[Principles\] \--\> B(Agents);  
    C\[Project Context\] \--\> B;  
    B \--\> D{Execution};  
    E\[Protocols\] \--\> D;

    subgraph "High-Level Governance"  
        A("\`  
            \*\*/principles/\*\*  
            \*Core Philosophy\*  
            \*Branching Strategy\*  
            \*YAGNI\*  
        \`");  
    end

    subgraph "AI Persona & Role"  
        B("\`  
            \*\*/agents/\*\*  
            \*Master Constitution\*  
            \*Specialist Personas\*  
        \`");  
    end

    subgraph "Task-Specific Information"  
        C("\`  
            \*\*/project\_context/\*\*  
            \*INSTRUCTIONS\_TEMPLATE.md\*  
            \*Your project's details go here.\*  
        \`");  
        E("\`  
            \*\*/protocols/\*\*  
            \*Secure Coding Protocol\*  
            \*Refactoring Protocol\*  
            \*etc...\*  
        \`");  
    end

    subgraph "Task Execution"  
        D("\`  
            \*\*AI-Assisted Task\*\*  
            The AI Agent, armed with its  
            Constitution, Project Context,  
            and a specific Protocol, performs  
            the development task.  
        \`");  
    end

    style A fill:\#f9f,stroke:\#333,stroke-width:2px  
    style B fill:\#ccf,stroke:\#333,stroke-width:2px  
    style C fill:\#cfc,stroke:\#333,stroke-width:2px  
    style E fill:\#cfc,stroke:\#333,stroke-width:2px

### **Explanation of Relationships:**

1. **Principles \-\> Agents**: The core Principles are injected into every Agent's constitution. The agent's fundamental identity and rules of engagement are derived from these principles.  
2. **Project Context \-\> Agents**: The specific Project Context provides the agent with the necessary domain knowledge to apply its skills effectively.  
3. **Agents \-\> Execution**: The Agent is the actor that performs the work. Its behavior during execution is constrained by its constitution.  
4. **Protocols \-\> Execution**: The Protocols are the step-by-step instructions for a specific task. The Agent must follow the assigned protocol precisely during execution.