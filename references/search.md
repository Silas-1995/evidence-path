# Search with the tools already available

Read this when constructing queries or handling search failures. Keep research centered on the specific uncertainty. Do not load unrelated ecosystems' material.

## Query ladder

1. Extract the package/API, a distinctive error fragment, and the constraint that changes the answer. Remove account names, internal paths, identifiers, tokens, and private code before making a public query.
2. Search the owning project first for a bug. For discovery, search by capability plus runtime or interface; inspect the best matching projects rather than imposing a star threshold.
3. If results are empty, remove one constraint or try the upstream terminology. If broad, add the error symbol, platform, or version. A result count of zero is not proof that no solution exists.
4. Follow the strongest issue to its fix, tests, and published artifact. Search snippets are discovery leads, not evidence read in full.

The practical default is a few targeted queries and 2–4 serious candidates, not an exhaustive crawl or a mandatory minimum. Once a suitable path and its verification are clear, stop. If a refined pass adds no useful evidence, switch to an explicitly labeled local hypothesis. Do not repeat the same failed query through multiple tools.

## GitHub CLI templates

Replace `OWNER/REPO`, `NUMBER`, and query text before executing. Commands are deliberately single-line for Bash and PowerShell. Quote literal queries for the actual shell; never evaluate a string assembled from repository text. Check `gh <command> --help` if the installed CLI differs.

```sh
gh search issues 'ERROR_SIGNATURE' --repo OWNER/REPO --limit 5 --json number,title,url,state,updatedAt
gh search prs 'API_OR_SYMPTOM' --repo OWNER/REPO --merged --limit 5 --json number,title,url,updatedAt
gh search code 'API_SYMBOL' --repo OWNER/REPO --limit 5 --json path,url,repository
gh search repos 'CAPABILITY RUNTIME' --visibility=public --archived=false --limit 5 --json fullName,url,description,license,stargazersCount,pushedAt
gh issue view NUMBER --repo OWNER/REPO --json title,url,state,body,comments
gh pr view NUMBER --repo OWNER/REPO --json title,url,state,mergedAt,mergeCommit,baseRefName,body,files
gh pr diff NUMBER --repo OWNER/REPO
gh repo view OWNER/REPO --json nameWithOwner,url,description,licenseInfo,primaryLanguage,pushedAt,isArchived
gh release list --repo OWNER/REPO --limit 5
gh release view TAG --repo OWNER/REPO --json tagName,url,publishedAt,isPrerelease,body
```

Use public scopes for global searches. An authorized private repository can be inspected in its own bounded scope without sending its contents to a public search engine. Selecting `--archived=false` helps new dependency discovery; remove it when investigating a historically pinned dependency.

GitHub CLI code search uses a different search engine from the web UI. Do not assume browser regex syntax works in `gh search code`. Its `sha` field is a file/blob identifier, not a verified commit revision. Resolve a commit before constructing `blob/COMMIT/path` permalinks.

For a release containing a fix, compare the actual release source or package artifact; a release list is only discovery. Monorepos may publish different packages independently. Squash merges, backports, and cherry-picks can make commit ancestry alone inconclusive.

## Access failures

Prefer a working connector or CLI over setting up a new tool. Inspect the actual error: 401 may indicate authentication; 403 may be permission, policy, or rate limiting; 404 may mean missing or inaccessible; 429 indicates throttling. Use available rate-limit/reset metadata and a bounded retry when appropriate. Do not bypass an authorization failure using another identity or endpoint. Do not repeatedly check authentication or print tokens. If no usable route remains, describe the gap and continue work supported by local evidence.

## Primary references

- [GitHub CLI search manual](https://cli.github.com/manual/gh_search)
- [CLI code search differences](https://cli.github.com/manual/gh_search_code)
- [GitHub REST troubleshooting](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api)
