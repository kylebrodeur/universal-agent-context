# Topic-Based Retrieval: Real-World Use Cases

This document provides practical examples of topic taxonomies and retrieval patterns for different domains.

---

## Use Case 1: Software Development Project

### Topic Taxonomy

```
security/
├── security/sql-injection
├── security/xss
├── security/csrf
├── security/authentication
└── security/authorization

performance/
├── performance/database
├── performance/caching
├── performance/network
└── performance/rendering

quality/
├── quality/testing
├── quality/coverage
├── quality/documentation
└── quality/code-style

features/
├── features/authentication
├── features/payments
├── features/notifications
└── features/admin

bugs/
├── bugs/critical
├── bugs/high
├── bugs/medium
└── bugs/low
```

### Retrieval Patterns

```python
# Security team reviews all security issues
security_context = uacs.build_context(
    query="Review security issues",
    topics=["security"],  # Matches all security/* topics
    max_tokens=5000
)

# Performance specialist optimizes database
perf_db_context = uacs.build_context(
    query="Optimize database performance",
    topics=["performance/database"],  # Specific subtopic
    max_tokens=3000
)

# QA team checks high-priority bugs
qa_context = uacs.build_context(
    query="Review critical bugs",
    topics=["bugs/critical", "bugs/high"],  # Multiple subtopics
    max_tokens=4000
)

# Feature team works on authentication
auth_context = uacs.build_context(
    query="Implement authentication feature",
    topics=["features/authentication", "security/authentication"],  # Cross-topic
    max_tokens=6000
)
```

### Benefits

- Clear separation of concerns
- Easy delegation to specialist teams
- Cross-functional coordination (e.g., security + features)
- Historical tracking per domain

---

## Use Case 2: Customer Support System

### Topic Taxonomy

```
customer-type/
├── customer-type/enterprise
├── customer-type/pro
└── customer-type/free

issue-category/
├── issue-category/billing
├── issue-category/technical
├── issue-category/feature-request
└── issue-category/bug-report

priority/
├── priority/urgent
├── priority/high
├── priority/normal
└── priority/low

status/
├── status/new
├── status/in-progress
├── status/waiting-customer
├── status/resolved
└── status/escalated
```

### Retrieval Patterns

```python
# Billing specialist handles billing issues
billing_context = uacs.build_context(
    query="Resolve billing issue",
    topics=["issue-category/billing"],
    max_tokens=2000
)

# Technical support handles urgent technical issues
urgent_tech = uacs.build_context(
    query="Resolve urgent technical issue",
    topics=["issue-category/technical", "priority/urgent"],
    max_tokens=3000
)

# Account manager reviews enterprise customer issues
enterprise_context = uacs.build_context(
    query="Review enterprise customer issues",
    topics=["customer-type/enterprise"],  # All enterprise issues
    max_tokens=5000
)

# Escalation manager reviews escalated cases
escalation_context = uacs.build_context(
    query="Review escalated cases",
    topics=["status/escalated"],
    max_tokens=4000
)
```

### Benefits

- Route tickets to appropriate specialists
- Prioritize by urgency
- Track customer segments
- Monitor escalation trends

---

## Use Case 3: Content Creation Pipeline

### Topic Taxonomy

```
content-type/
├── content-type/blog-post
├── content-type/whitepaper
├── content-type/case-study
└── content-type/documentation

stage/
├── stage/research
├── stage/draft
├── stage/review
├── stage/edit
└── stage/publish

audience/
├── audience/technical
├── audience/business
└── audience/general

topic/
├── topic/ai
├── topic/security
├── topic/performance
└── topic/architecture
```

### Retrieval Patterns

```python
# Researcher gathers sources for AI blog post
research_context = uacs.build_context(
    query="Research AI blog post",
    topics=["content-type/blog-post", "stage/research", "topic/ai"],
    max_tokens=8000  # Research needs lots of context
)

# Writer drafts based on research
draft_context = uacs.build_context(
    query="Write AI blog post draft",
    topics=["stage/research", "topic/ai", "audience/technical"],
    max_tokens=4000
)

# Editor reviews draft
review_context = uacs.build_context(
    query="Review draft for quality",
    topics=["stage/draft", "content-type/blog-post"],
    max_tokens=3000
)

# SEO optimizer works on published content
seo_context = uacs.build_context(
    query="Optimize SEO",
    topics=["stage/publish", "content-type/blog-post"],
    max_tokens=2000
)
```

### Benefits

- Track content through pipeline stages
- Maintain context across roles (researcher → writer → editor)
- Organize by content type and audience
- Historical context for similar content

---

## Use Case 4: Data Analysis Project

### Topic Taxonomy

```
data-source/
├── data-source/database
├── data-source/api
├── data-source/files
└── data-source/streaming

analysis-type/
├── analysis-type/exploratory
├── analysis-type/statistical
├── analysis-type/machine-learning
└── analysis-type/visualization

finding-type/
├── finding-type/insight
├── finding-type/anomaly
├── finding-type/trend
└── finding-type/correlation

output/
├── output/report
├── output/dashboard
├── output/model
└── output/recommendation
```

### Retrieval Patterns

```python
# Data collector gathers from APIs
collection_context = uacs.build_context(
    query="Collect data from API sources",
    topics=["data-source/api"],
    max_tokens=2000
)

# Analyst performs exploratory analysis
exploratory_context = uacs.build_context(
    query="Explore customer behavior data",
    topics=["analysis-type/exploratory", "data-source/database"],
    max_tokens=6000
)

# ML engineer builds on insights and anomalies
ml_context = uacs.build_context(
    query="Build predictive model",
    topics=["finding-type/insight", "finding-type/trend", "analysis-type/machine-learning"],
    max_tokens=8000
)

# Report writer summarizes all findings
report_context = uacs.build_context(
    query="Write executive summary",
    topics=["finding-type"],  # All finding-type/* topics
    max_tokens=5000
)
```

### Benefits

- Track data lineage
- Connect analysis types to findings
- Coordinate multi-role data teams
- Generate comprehensive reports

---

## Use Case 5: Research Project

### Topic Taxonomy

```
research-area/
├── research-area/literature-review
├── research-area/methodology
├── research-area/experiments
└── research-area/analysis

paper-section/
├── paper-section/introduction
├── paper-section/related-work
├── paper-section/methods
├── paper-section/results
└── paper-section/conclusion

source-type/
├── source-type/paper
├── source-type/book
├── source-type/dataset
└── source-type/code

status/
├── status/idea
├── status/in-progress
├── status/peer-review
└── status/published
```

### Retrieval Patterns

```python
# Literature review for related work section
lit_review_context = uacs.build_context(
    query="Write related work section",
    topics=["research-area/literature-review", "source-type/paper"],
    max_tokens=10000  # Academic writing needs extensive context
)

# Methodology section based on experiments
methods_context = uacs.build_context(
    query="Document methodology",
    topics=["research-area/experiments", "research-area/methodology"],
    max_tokens=6000
)

# Results section from analysis
results_context = uacs.build_context(
    query="Report results",
    topics=["research-area/analysis", "research-area/experiments"],
    max_tokens=8000
)

# Peer reviewer checks entire paper
review_context = uacs.build_context(
    query="Review paper for submission",
    topics=["paper-section"],  # All sections
    max_tokens=15000
)
```

### Benefits

- Organize research by area and stage
- Track sources and references
- Maintain context across months/years
- Coordinate collaborators

---

## Best Practices for Topic Design

### 1. Use Hierarchical Topics

```python
# Good: Hierarchical
topics = [
    "security/sql-injection",
    "security/xss",
    "performance/database",
    "performance/caching"
]

# Bad: Flat
topics = [
    "sql-injection",
    "xss",
    "database-performance",
    "caching-performance"
]
```

**Why:** Hierarchical enables querying parent ("security") or specific child ("security/xss").

### 2. Keep Topic Names Short

```python
# Good: Concise
topics = ["security", "critical", "sql-injection"]

# Bad: Verbose
topics = [
    "security-vulnerability",
    "critical-priority-level",
    "sql-injection-attack-vector"
]
```

**Why:** Shorter names are easier to remember and type. Use content for details, topics for categories.

### 3. Plan Taxonomy Upfront

```python
# Define taxonomy early
TOPIC_TAXONOMY = {
    "security": ["sql-injection", "xss", "csrf", "auth"],
    "performance": ["database", "caching", "network"],
    "quality": ["testing", "coverage", "docs"]
}

# Validate topics on add
def validate_topics(topics):
    for topic in topics:
        parent, child = topic.split("/") if "/" in topic else (topic, None)
        if parent not in TOPIC_TAXONOMY:
            raise ValueError(f"Unknown topic: {parent}")
```

**Why:** Prevents topic proliferation and inconsistency.

### 4. Use Cross-Cutting Topics

```python
# Add multiple dimensions
uacs.add_to_context(
    content="SQL injection in login form",
    topics=[
        "security/sql-injection",  # What it is
        "features/authentication",  # Where it is
        "priority/critical",        # How important
        "status/new"                # What state
    ]
)

# Query any dimension
by_security = uacs.build_context(topics=["security"])
by_feature = uacs.build_context(topics=["features/authentication"])
by_priority = uacs.build_context(topics=["priority/critical"])
```

**Why:** Enables flexible querying from multiple perspectives.

### 5. Document Your Taxonomy

```markdown
# Project Topic Taxonomy

## Security
- `security/sql-injection`: SQL injection vulnerabilities
- `security/xss`: Cross-site scripting issues
- `security/csrf`: Cross-site request forgery

## Performance
- `performance/database`: Database query optimization
- `performance/caching`: Caching strategy and implementation

Usage:
- Security team: `topics=["security"]`
- Database team: `topics=["performance/database"]`
```

**Why:** Ensures team alignment and consistent usage.

---

## Anti-Patterns to Avoid

### 1. Too Many Topics

```python
# Bad: 50+ top-level topics
topics = ["security", "performance", "testing", "documentation", "deployment",
          "monitoring", "logging", "authentication", "authorization", ...]
```

**Problem:** Hard to remember, query, and maintain.

**Solution:** Group into 5-10 top-level topics with hierarchical subtopics.

### 2. Inconsistent Naming

```python
# Bad: Different naming styles
topics = ["security-sql", "performance/database", "TestingUnit", "docs_api"]
```

**Problem:** Can't query reliably.

**Solution:** Choose one style (recommend: lowercase, hyphen-separated, hierarchical).

### 3. Content in Topics

```python
# Bad: Putting content in topic names
topics = [
    "security-found-sql-injection-at-line-42",
    "performance-n-plus-one-query-in-user-model"
]
```

**Problem:** Topics should be categories, not descriptions.

**Solution:** Use short category names, put details in content.

### 4. No Hierarchy

```python
# Bad: Flat topics for complex domains
topics = [
    "security-web-sql-injection",
    "security-web-xss",
    "security-api-auth",
    "security-api-rate-limit"
]
```

**Problem:** Can't query groups (e.g., all security/web).

**Solution:** Use hierarchy: `security/web/sql-injection`, `security/api/auth`.

---

## Conclusion

Topic-based retrieval is powerful when used correctly:

1. **Plan taxonomy upfront** - Don't let topics grow organically
2. **Use hierarchy** - Enable flexible querying
3. **Keep topics short** - Easy to remember and type
4. **Cross-cutting concerns** - Tag from multiple dimensions
5. **Document and validate** - Ensure team consistency

With a well-designed topic taxonomy, you can:
- Reduce token costs by 50-80%
- Improve response quality
- Enable massive contexts (100K+ tokens)
- Coordinate multi-agent systems
- Track project history

See demo.py for working examples of these patterns.
