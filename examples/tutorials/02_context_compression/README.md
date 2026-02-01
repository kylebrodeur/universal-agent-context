# Demo 2: Context Compression

## What

This demo demonstrates UACS's powerful context compression capabilities, showing how to achieve **70%+ token reduction** while preserving information quality. You'll see:

- Before/after token comparisons
- Multiple compression strategies in action
- Real cost savings calculations
- Quality scoring and filtering
- Progressive compression at different budget levels

This is the **money-saving** feature of UACS - literally.

## Why

**Value Proposition:** Token costs add up fast in production AI applications:

| Scenario | Monthly Cost (No Compression) | Monthly Cost (70% Compression) | Savings |
|----------|------------------------------|-------------------------------|---------|
| 100 calls/day @ 10K tokens | $300 | $90 | $210/month |
| 1,000 calls/day @ 10K tokens | $3,000 | $900 | $2,100/month |
| 10,000 calls/day @ 10K tokens | $30,000 | $9,000 | $21,000/month |

**Real-world Impact:**
- Reduce API costs by 70%+ without losing information
- Stay within context window limits
- Support longer conversations
- Enable higher agent call volumes

## When

Use context compression when:
- Your context regularly exceeds 5,000 tokens
- You have repeated information across conversation turns
- You need to fit more history within token limits
- API costs are a significant expense
- You're hitting LLM context window limits

**This is essential for production deployments.**

## How

### Compression Strategies

UACS uses 4 complementary strategies:

1. **Deduplication (40% savings)**
   - Hash-based duplicate detection
   - Store identical content once
   - Track frequency for importance scoring

2. **Quality Filtering (30% savings)**
   - Score entries based on:
     - Length and information density
     - Topic relevance
     - Recency
     - Agent importance
   - Summarize or drop low-quality entries

3. **Topic-Based Filtering (50% savings)**
   - Only include relevant topics
   - Example: "security" filter removes "testing" context
   - Dramatically reduces noise

4. **Progressive Loading (60% savings)**
   - Load most recent entries fully
   - Summarize older entries
   - Drop ancient low-quality entries

### Compression Workflow

```python
from uacs import UACS

uacs = UACS(project_path=Path.cwd())

# Add entries (some duplicates, various quality)
for entry in conversation:
    uacs.add_to_context(key=entry.agent, content=entry.text, topics=entry.topics)

# Get compressed context
compressed = uacs.build_context(
    query="Continue the review",
    agent="claude",
    max_tokens=2000,  # Enforce budget
    topics=["security"]  # Filter by topic
)

# Check savings
stats = uacs.get_token_stats()
print(f"Saved {stats['tokens_saved']} tokens ({stats['compression_ratio']}%)")
```

## Output

Running this demo produces detailed compression analytics:

```
Before Compression:
  Total entries: 20
  Original tokens: 8,456
  Duplicates: 3 entries (14%)

After Compression (Budget: 2,000 tokens):
  Compressed tokens: 1,847
  Compression: 78.2% reduction
  Tokens saved: 6,609

Compression Breakdown:
  - Deduplication: 1,234 tokens (14.6%)
  - Quality filtering: 2,890 tokens (34.2%)
  - Topic filtering: 1,567 tokens (18.5%)
  - Progressive loading: 918 tokens (10.9%)

Cost Savings:
  Without compression: $0.084/call
  With compression: $0.018/call
  Savings: $0.066/call (78%)

  Monthly (100 calls/day):
    Without: $252
    With: $54
    Savings: $198/month
```

## What You Learned

1. **Deduplication is Free:**
   - No information loss
   - Immediate 10-40% savings on typical conversations
   - Happens automatically

2. **Quality Scoring Works:**
   - Low-value entries ("Thanks!", "OK") are summarized or dropped
   - High-value entries (findings, decisions) are preserved
   - Automatic quality assessment

3. **Topic Filtering is Powerful:**
   - Most aggressive compression (50%+)
   - No information loss for the focused topic
   - Essential for large multi-topic contexts

4. **Progressive Loading Scales:**
   - Recent context is detailed
   - Older context is summarized
   - Ancient context is dropped
   - Maintains conversation coherence

5. **Cost Savings are Real:**
   - 70%+ compression = 70%+ cost reduction
   - Scales linearly with call volume
   - ROI is immediate

## Key Metrics

Track these metrics to understand compression effectiveness:

- **Compression Ratio:** `(original - compressed) / original * 100`
- **Tokens Saved:** `original - compressed`
- **Cost Savings:** `tokens_saved * price_per_1k_tokens / 1000`
- **Quality Score:** Average quality of preserved entries (0-1)

## Next Steps

1. **Demo 3: Multi-Agent Context** - Share compressed context between agents
2. **Demo 4: Topic-Based Retrieval** - Use topics for maximum compression
3. **Demo 5: Claude Code Integration** - Apply compression to conversation history

## Running the Demo

```bash
# From the project root
uv run python examples/02_context_compression/demo.py

# View detailed comparison
cat examples/02_context_compression/comparison.md
```

Expected runtime: < 2 seconds

## Common Questions

**Q: Does compression lose information?**
A: Depends on the strategy:
- Deduplication: Zero loss (exact duplicates)
- Quality filtering: Minimal loss (low-value content)
- Topic filtering: Zero loss for the topic (100% loss for other topics)
- Progressive loading: Gradual loss for old context

**Q: Can I control compression aggressiveness?**
A: Yes, via `max_tokens` parameter. Lower budget = more aggressive compression.

**Q: How does quality scoring work?**
A: Multiple factors:
- Length (longer = more information)
- Topics (tagged = more specific)
- Recency (newer = more relevant)
- Agent (user > assistant > system)

**Q: What's the minimum viable token budget?**
A: Depends on use case. Generally:
- Simple tasks: 1,000 tokens
- Code review: 2,000-4,000 tokens
- Complex reasoning: 4,000-8,000 tokens

**Q: Does compression affect response quality?**
A: Not if done correctly. UACS preserves high-quality, relevant context. In practice, focused context often improves response quality by reducing noise.

## Troubleshooting

**Issue:** Compression ratio is lower than expected
**Solution:** Check for:
- Few duplicate entries (add more conversation turns)
- All high-quality entries (expected for short conversations)
- No topic filtering (add topics to entries)

**Issue:** Important information was compressed away
**Solution:**
- Increase `max_tokens` budget
- Add topic tags to important entries
- Increase quality scores for critical content

**Issue:** Token counts don't match expected
**Solution:** Different tokenizers count differently. UACS uses `tiktoken` (OpenAI's tokenizer) for consistency.

## Related Documentation

- [Context Management](../../docs/CONTEXT.md) - Compression algorithms deep dive
- [Library Guide](../../docs/LIBRARY_GUIDE.md) - API reference
- [comparison.md](./comparison.md) - Side-by-side token comparisons
