/**
 * Files are loaded in the following order:
 *
 * 1. Managed memory (eg. /etc/claude-code/CLAUDE.md) - Global instructions for all users
 * 2. User memory (~/.claude/CLAUDE.md) - Private global instructions for all projects
 * 3. Project memory (CLAUDE.md, .claude/CLAUDE.md, and .claude/rules/*.md in project roots) - Instructions checked into the codebase
 * 4. Local memory (CLAUDE.local.md in project roots) - Private project-specific instructions
 *
 * Files are loaded in reverse order of priority, i.e. the latest files are highest priority
 * with the model paying more attention to them.
 *
 * File discovery:
 * - User memory is loaded from the user's home directory
 * - Project and Local files are discovered by traversing from the current directory up to root
 * - Files closer to the current directory have higher priority (loaded later)
 * - CLAUDE.md, .claude/CLAUDE.md, and all .md files in .claude/rules/ are checked in each directory for Project memory
 *
 * Memory @include directive:
 * - Memory files can include other files using @ notation
 * - Syntax: @path, @./relative/path, @~/home/path, or @/absolute/path
 * - @path (without prefix) is treated as a relative path (same as @./path)
 * - Works in leaf text nodes only (not inside code blocks or code strings)
 * - Included files are added as separate entries before the including file
 * - Circular references are prevented by tracking processed files
 * - Non-existent files are silently ignored
 */
