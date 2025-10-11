# **Protocol: Secure Code Implementation**

**Objective**: To write, review, and commit a new piece of functionality while adhering to the highest security standards.

### **Phase 1: Requirement Analysis**

1. **Acknowledge Task**: Confirm understanding of the feature to be implemented.  
2. **Identify Attack Vectors**: Based on the requirements, list the potential security vulnerabilities. (e.g., SQL Injection, Cross-Site Scripting (XSS), Insecure Direct Object References, CSRF).  
3. **State Mitigation Strategy**: For each identified vector, state the specific mitigation technique you will use. (e.g., "Use parameterized queries via Prisma ORM to prevent SQLi," "Sanitize all user-generated content before rendering to prevent XSS").

### **Phase 2: Code Generation**

1. **Generate Code**: Write the code to implement the feature, applying the stated mitigation strategies.  
2. **Add Comments**: Add inline comments specifically explaining the security-related code (e.g., // Sanitize user input to prevent XSS).  
3. **Generate Tests**: Write unit or integration tests that specifically check the security mitigations. For example, a test that attempts to pass malicious input and asserts that it is correctly handled or rejected.

### **Phase 3: Security & Quality Verification (Self-Correction)**

1. **OWASP Top 10 Review**: Review the generated code against the OWASP Top 10\. State explicitly that you have performed this check.  
2. **Input Validation Check**: Confirm that all external inputs (from users, APIs, etc.) are properly validated, sanitized, and type-checked.  
3. **Error Handling Check**: Ensure that error messages do not leak sensitive information (e.g., stack traces, database error details).  
4. **Principle Adherence Check**: Confirm that the code adheres to the YAGNI and Branching/Commit strategy principles.

### **Phase 4: Output Formatting**

1. **Format Code**: Present the complete, final code block(s).  
2. **Propose Branch Name**: Suggest a branch name according to the branching strategy.  
3. **Propose Commit Message**: Write a complete, conventional commit message.  
4. **Provide Handoff Summary**: Write a brief summary for the human reviewer, highlighting the security measures taken and pointing out any areas that may require special attention or manual configuration (e.g., environment variables).