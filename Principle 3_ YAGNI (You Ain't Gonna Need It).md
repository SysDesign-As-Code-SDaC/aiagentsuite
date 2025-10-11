# **Principle 3: YAGNI (You Ain't Gonna Need It)**

This principle is a cornerstone of Vibe-Driven Engineering and MUST be applied to all development decisions. YAGNI is the practice of never adding functionality until it is demonstrably necessary.

## **The Mandate**

1. **Do Not Implement What Is Not Asked For**: Never implement features that are not explicitly required by the current task or user story. Do not build for a hypothetical future.  
2. **Avoid Premature Abstraction**: Do not create complex design patterns, abstractions, or configurations for problems you *think* you might have later. Solve the immediate problem in the simplest way possible. Create abstractions only when you see clear, repeated duplication (Rule of Three).  
3. **Question Every "What If"**: When considering adding a piece of code, ask "Is this solving a current, real problem?" If the answer involves a "what if..." scenario, do not build it.  
4. **Simplicity Is Paramount**: The simplest solution that works is the correct solution. Complexity is a liability that we must actively fight to reduce.

## **Application for AI Agents**

As an AI agent, you must be particularly vigilant about adhering to YAGNI. Your vast knowledge of patterns and potential future needs can be a weakness if not disciplined.

* When given a task, fulfill only the requirements of that task.  
* If you identify a potential future improvement or a necessary abstraction, do not implement it. Instead, **propose it as a recommendation** in your final output, clearly marked as a "Next Step" or "Suggested Refactor."  
* Your primary goal is to deliver a minimal, clean, and correct solution to the problem at hand, not to build a framework for all possible future problems.