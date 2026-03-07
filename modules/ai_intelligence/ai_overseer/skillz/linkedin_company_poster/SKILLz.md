# LinkedIn Company Poster Skill

## Purpose
Post updates and articles to FoundUps LinkedIn company page (1263645) with 0102 signature.

## Trigger
- CLI: `python -m modules.ai_intelligence.ai_overseer.skillz.linkedin_company_poster --post "content"`
- CLI: `python -m modules.ai_intelligence.ai_overseer.skillz.linkedin_company_poster --article "title" --body "content"`
- OpenClaw: `linkedin_post("content")` or `linkedin_article("title", "body")`
- Git hook: Automatic on commit (existing post-commit hook)

## Parameters
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| content | str | Yes (post) | Post content |
| title | str | Yes (article) | Article title |
| body | str | Yes (article) | Article body (markdown supported) |
| signature | str | No | Default: "0102🦞" |

## Company Page
- URL: https://www.linkedin.com/company/1263645/admin/page-posts/published/
- Name: FOUNDUPS
- Logo: Red kangaroo

## DOM Selectors
### Post Creation
- Share button area: `div.org-update.__core-rail`
- Text editor: `div.ql-editor`
- Post button: `//button[contains(@class, 'share-actions__primary-action')]`

### Article Creation
- Write article button: Right side of post creation area
- Article editor: Opens in new modal/page

## Signature Format
```
{content}

0102🦞 #FoundUps #pAVS #0102
```

## Dependencies
- selenium
- modules.infrastructure.foundups_selenium
- modules.platform_integration.linkedin_agent

## WSP Compliance
- WSP 48: Social media posting standards
- WSP 50: Pre-action verification (duplicate detection)
- WSP 77: Agent coordination (skill interface)
