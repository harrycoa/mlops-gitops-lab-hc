# Catchup Command

Read all files that have been modified in the current git branch to understand recent changes.

## Instructions

1. First, get the current branch name and compare it to the main branch
2. Use git diff to find all changed files (added, modified, or deleted)
3. For each changed file that still exists:
   - Read the file contents using the Read tool
   - Provide a brief summary of what changed
4. For deleted files, note that they were deleted
5. Provide a concise summary of all changes at the end

Use this command format to get changed files:
```bash
git diff --name-status main...HEAD
```

The output format is:
- M = Modified
- A = Added
- D = Deleted
- R = Renamed

After reading all files, provide:
1. A list of files read with their status
2. A high-level summary of the changes across the branch
3. Any notable patterns or areas of focus in the changes
