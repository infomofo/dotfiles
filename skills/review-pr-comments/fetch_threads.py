#!/usr/bin/env python3
"""Fetch unresolved, current PR review threads for the current branch.

Prints each thread's author, file, line, thread ID, comment body (truncated
to 300 chars), and any human replies. Output is consumed by the
review-pr-comments skill to triage and act on bot review comments.
"""
import json
import subprocess
import sys


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'Command failed: {" ".join(cmd)}\n{r.stderr}')
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as e:
        sys.exit(f'Failed to parse response from {" ".join(cmd)}: {e}\n{r.stdout[:200]}')


def fetch_deleted_paths(owner, repo, number):
    """Return the set of filenames deleted in this PR."""
    all_files = []
    page = 1
    while True:
        batch = run(['gh', 'api', f'repos/{owner}/{repo}/pulls/{number}/files?per_page=100&page={page}'])
        all_files.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return {f.get('filename') for f in all_files if f.get('status') == 'removed' and f.get('filename')}


def fetch_threads(owner, repo, number):
    """Fetch all review threads for the PR, paginating past 100."""
    cursor = None
    all_threads = []
    while True:
        after_arg = f', after: "{cursor}"' if cursor else ''
        query = f'''
query {{
  repository(owner: "{owner}", name: "{repo}") {{
    pullRequest(number: {number}) {{
      reviewThreads(first: 100{after_arg}) {{
        pageInfo {{ hasNextPage endCursor }}
        nodes {{
          id
          isResolved
          isOutdated
          comments(first: 100) {{
            nodes {{
              path
              line
              body
              author {{ login __typename }}
            }}
          }}
        }}
      }}
    }}
  }}
}}'''
        data = run(['gh', 'api', 'graphql', '-f', f'query={query.strip()}'])
        if 'errors' in data:
            sys.exit('GraphQL errors: ' + json.dumps(data['errors']))
        pr = data.get('data', {}).get('repository', {}).get('pullRequest')
        if not pr:
            sys.exit('PR not found or insufficient permissions')
        rt = pr.get('reviewThreads', {})
        all_threads.extend(rt.get('nodes') or [])
        pi = rt.get('pageInfo', {})
        if not pi.get('hasNextPage'):
            break
        cursor = pi.get('endCursor')
    return all_threads


def print_threads(all_threads, deleted):
    """Print unresolved, current threads not on deleted paths."""
    for t in all_threads:
        if not t or t.get('isResolved') or t.get('isOutdated'):
            continue
        all_comments = t.get('comments', {}).get('nodes') or []
        if not all_comments:
            continue
        c = all_comments[0]
        path = c.get('path') or ''
        if path in deleted:
            continue
        author = c.get('author') or {}
        print(f"[{author.get('login', 'unknown')} / {author.get('__typename', 'unknown')}] {path}:{c.get('line')} thread:{t.get('id')}")
        print(c.get('body', '')[:300])
        human_replies = [
            r for r in all_comments[1:]
            if (r.get('author') or {}).get('__typename') != 'Bot'
        ]
        if human_replies:
            print(f"  *** {len(human_replies)} HUMAN REPLY — treat as higher priority than bot opener ***")
            for r in human_replies:
                r_author = r.get('author') or {}
                print(f"  [{r_author.get('login', 'unknown')}]: {r.get('body', '')[:300]}")
        print()


def main():
    repo_info = run(['gh', 'repo', 'view', '--json', 'owner,name'])
    owner = (repo_info.get('owner') or {}).get('login') or sys.exit('Could not derive owner from gh repo view')
    repo = repo_info.get('name') or sys.exit('Could not derive repo from gh repo view')

    pr_info = run(['gh', 'pr', 'view', '--json', 'number'])
    number = pr_info.get('number') or sys.exit('Could not derive PR number from gh pr view')

    print(f'owner={owner} repo={repo} number={number}')

    deleted = fetch_deleted_paths(owner, repo, number)
    threads = fetch_threads(owner, repo, number)
    print_threads(threads, deleted)


if __name__ == '__main__':
    main()
