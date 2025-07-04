# Feature Documentation: [Feature Name]

---

## 1. Context before the feature
Describe the current state of the system before implementation. Include:
- How the existing logic works that relates to this feature.
- What limitations or pain points users or the system face.
- Who is affected (users, roles, microservices).

---

## 2. Feature goal
- What **problem** does this solve?
- What is the **goal** (what should change)?
- Provide **success criteria**—how to know the feature works (numbers, scenarios).

---

## 3. Solution

### 3.1 Scope
Describe what will be added or changed: new features, screens, APIs, etc.

### 3.2 Out-of-scope
State what **will not** be done even if it seems like a logical extension.

### 3.3 How it should work
- API request/response examples
- Screenshots, diagrams, or flow descriptions
- Short UX flow description if relevant

### 3.4 Architectural changes
- Which modules, services, or databases will be affected.
- Whether schemas, buses, queues or configs must change.

---

## 4. Implementation plan

List the tasks step by step with explanations.

## 5. Files to change

List which files will be touched and how:
- `src/.../feature.ts` — **update**: new logic
- `api/.../routes.ts` — **add**: new endpoint
- `docs/.../spec.md` — **update**: API description
- `db/migrations/xxxx.sql` — **add**: new column

---

## 6. Potential risks

Describe risks and how to mitigate them:
| Risk | Probability | Impact | Plan |
|------|-------------|--------|------|
| Example: data loss | Medium | High | Make a backup before migration |

---

## 7. Testing plan

### 7.1 Unit tests
What will be covered by unit tests?

### 7.2 Integration tests
Which modules or services are tested together?

### 7.3 Acceptance scenarios
Describe step by step how to verify the feature manually (or use Gherkin):

```gherkin
Scenario: User places an order with multiple items
Given ...
When ...
Then ...
```
