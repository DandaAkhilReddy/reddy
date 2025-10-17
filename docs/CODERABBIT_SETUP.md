# CodeRabbit.ai Setup Guide

## What is CodeRabbit?

CodeRabbit is an AI-powered code review assistant that automatically reviews pull requests, providing:
- Security vulnerability detection
- Performance optimization suggestions
- Code quality improvements
- Best practice recommendations
- Automated test coverage analysis

## Setup Instructions

### 1. Install CodeRabbit GitHub App

1. Go to https://github.com/apps/coderabbitai
2. Click **"Install"**
3. Select **"Only select repositories"**
4. Choose `DandaAkhilReddy/reddy`
5. Click **"Install & Authorize"**

### 2. Verify Installation

After installation:
1. Go to https://github.com/DandaAkhilReddy/reddy/settings/installations
2. You should see **CodeRabbit** in the installed apps list
3. Configuration will be automatically loaded from `.coderabbit.yaml`

### 3. Test the Integration

Create a test PR:
```bash
git checkout -b test/coderabbit-setup
echo "# Test" >> test.md
git add test.md
git commit -m "test: Verify CodeRabbit integration"
git push origin test/coderabbit-setup
```

Then create a PR on GitHub. CodeRabbit should automatically:
- Comment on the PR with a review summary
- Provide inline code suggestions
- Generate a review poem (configurable)

## Configuration

Our CodeRabbit configuration is in `.coderabbit.yaml`:

### Key Settings

**Review Profile**: `chill` (constructive, educational)
- Focuses on high-impact issues
- Provides explanations and examples
- Encourages good patterns

**Auto-Review Triggers**:
- ✅ Automatically reviews all PRs to `main` branch
- ✅ Reviews PRs to `develop` branch
- ❌ Skips draft PRs (you can request manual review)

**Path-Specific Instructions**:
- `features/photoanalysis/**` - Focus on type safety, error handling, performance
- `features/whoop-integration/**` - Focus on async patterns, API handling
- `tests/**` - Focus on coverage, edge cases, clarity

### Custom Rules

We've configured custom rules for:

1. **API Key Security**
   - Detects hardcoded API keys
   - Severity: HIGH

2. **Async Without Await**
   - Flags async functions that don't use await
   - Severity: MEDIUM

3. **Missing Type Hints**
   - Suggests adding return type hints
   - Severity: LOW

4. **Hardcoded Thresholds**
   - Flags magic numbers in conditions
   - Severity: LOW

## Using CodeRabbit in PRs

### Automatic Reviews

CodeRabbit will automatically comment when:
- You open a new PR
- You push new commits to an existing PR
- Someone requests a re-review

### Manual Commands

You can interact with CodeRabbit using comments:

```
@coderabbitai review
```
Request a full review

```
@coderabbitai review --quick
```
Quick review (surface-level only)

```
@coderabbitai explain this
```
Ask for explanation of specific code

```
@coderabbitai suggest improvements
```
Get optimization suggestions

```
@coderabbitai pause
```
Pause reviews for this PR

```
@coderabbitai resume
```
Resume reviews

### Review Workflow

1. **Open PR** → CodeRabbit reviews within ~2-5 minutes
2. **Read Summary** → High-level overview at top
3. **Check Inline Comments** → Specific suggestions in code
4. **Respond** → Reply to comments, ask questions
5. **Push Changes** → CodeRabbit reviews again automatically

## Best Practices

### For Contributors

1. **Don't ignore security warnings** - Address all HIGH severity issues
2. **Consider performance suggestions** - Especially for image processing
3. **Add requested docstrings** - Helps maintainability
4. **Respond to questions** - CodeRabbit learns from discussions

### For Maintainers

1. **Review CodeRabbit's suggestions** - AI isn't perfect, use judgment
2. **Mark helpful reviews** - Thumbs up good suggestions
3. **Provide context** - If rejecting a suggestion, explain why
4. **Update `.coderabbit.yaml`** - Refine rules based on experience

## Customization

### Adjusting Review Sensitivity

Edit `.coderabbit.yaml`:

**More strict:**
```yaml
reviews:
  profile: "assertive"
  request_changes_workflow: true
```

**More lenient:**
```yaml
reviews:
  profile: "chill"
  request_changes_workflow: false
```

### Adding Domain Knowledge

Update the `knowledge_base` section:
```yaml
reviews:
  knowledge_base:
    - "New domain-specific guideline here"
    - "Another project-specific rule"
```

### Custom Rules

Add new rules to `custom_rules`:
```yaml
custom_rules:
  - name: "Your Rule Name"
    pattern: "regex pattern"
    message: "Explanation"
    severity: "high|medium|low"
```

## Troubleshooting

### CodeRabbit not commenting?

**Check:**
1. Installation active: GitHub Settings → Installed Apps
2. Repository access: CodeRabbit should have read/write
3. PR not a draft: CodeRabbit skips drafts by default
4. Branch protection: Ensure CodeRabbit can comment

**Force review:**
Comment on PR: `@coderabbitai review`

### Too many comments?

**Adjust threshold:**
```yaml
issues:
  auto_detect:
    confidence_threshold: 0.9  # Higher = fewer comments
```

### False positives?

**Exclude specific checks:**
```yaml
exclude:
  - "path/to/ignore/**"
```

Or disable specific rules in `.coderabbit.yaml`

## Resources

- [CodeRabbit Documentation](https://docs.coderabbit.ai/)
- [Configuration Reference](https://docs.coderabbit.ai/guides/configure-coderabbit)
- [GitHub App](https://github.com/apps/coderabbitai)
- [Support](https://github.com/coderabbitai/coderabbit/issues)

## Example Reviews

### Good Review Interaction

```markdown
@coderabbitai suggestion:
Consider using asyncio.gather() for parallel image processing

**Response:**
Great suggestion! Updated to use asyncio.gather() in commit abc123.
Performance improved by 40%.
```

### Questioning a Suggestion

```markdown
@coderabbitai comment:
This type hint seems overly complex

**Response:**
The Union type is necessary because this function can return None
during error cases. Added clarifying comment in code.
```

---

**Setup Complete!** CodeRabbit will now review all PRs automatically.
