---
name: tool-upgrade
description: Upgrade 16 curated brew + npm tools with strict user takeover. Probes versions, requires per-tool approval (major versions get individual questions), runs only the approved list, suggests `proxy-on` on network failure.
disable-model-invocation: true
---

# Tool Upgrade

Curated stack upgrade. **User takeover throughout** — this skill reports and recommends; it does not auto-execute.

> **Control contract**
> - The skill **never** runs `brew upgrade` or `npm update` without an explicit per-run user confirmation.
> - **Major version bumps** are surfaced one-by-one and require individual approval — no bulk accept.
> - After the upgrade, the skill returns control immediately. Any post-upgrade follow-up (config migration, restart services, smoke tests) is the user's call.
> - Network failures never auto-retry. The user decides whether to enable `proxy-on` and re-run.

## The stack

Single source of truth — referenced by steps 1, 4, 5. Edit here when adding or removing tools.

**Brew formulas (10):**
`leboiko/tap/markdown-reader`, `bat`, `glow`, `fzf`, `zoxide`, `gh`, `ripgrep`, `lazygit`, `frpc`, `mycli`

**Brew casks (0):**
_none_

**NPM globals (6):**
`@colbymchenry/codegraph`, `@jackwener/opencli`, `chrome-devtools-mcp`, `pm2`, `@larksuite/cli`, `tokscale`

**Excluded by default** (edit the stack above to re-include):
- `@anthropic-ai/claude-code` — current session depends on it; upgrade in a fresh shell
- `typescript`, `npm`, `pnpm` — not system packages (user preference)
- `codex` (cask) — uninstalled
- Brew libs (ca-certificates, libgit2, etc.) — auto-follow user tool upgrades

## Flow

### 1. Probe

Parallel fetch of installed and latest. Tag each row as `latest`, `outdated`, `uninstalled`, or `error`.

```bash
BREW_FORMULAS=(markdown-reader bat glow fzf zoxide gh ripgrep lazygit frpc mycli)
NPM_GLOBALS=(@colbymchenry/codegraph @jackwener/opencli chrome-devtools-mcp pm2 @larksuite/cli tokscale)

probe_brew() {
  local t=$1
  local installed latest
  installed=$(brew list --versions "$t" 2>/dev/null | awk '{print $2}')
  latest=$(brew info "$t" 2>/dev/null | grep -oE 'stable [^ ]*' | awk '{print $2}')
  printf 'brew  %-32s  %-10s  %-10s\n' "$t" "${installed:-missing}" "${latest:-?}"
}

probe_npm() {
  local p=$1
  local installed latest
  installed=$(npm ls -g "$p" --depth=0 2>/dev/null | grep "$p" | awk -F'@' '{print $NF}')
  latest=$(npm view "$p" version 2>/dev/null)
  printf 'npm   %-32s  %-10s  %-10s\n' "$p" "${installed:-missing}" "${latest:-?}"
}

for t in "${BREW_FORMULAS[@]}"; do probe_brew "$t" & done
for p in "${NPM_GLOBALS[@]}"; do probe_npm "$p" & done
wait
```

**Completion:** output line count equals `${#BREW_FORMULAS[@]} + ${#NPM_GLOBALS[@]}`, with no missing fields.

### 2. Display diff

Group by manager, sort by tool. Mark status:

- `✓ latest` — installed == latest
- `⬆ patch` — third component bumped
- `⬆ minor` — second component bumped, first unchanged
- `⚠ major` — first component bumped, **or** either component bumped while major is 0 (e.g. `0.9.x → 0.10.x` is major under SemVer 0.x convention)
- `— missing` — tool not installed locally
- `? error` — could not read version

If every tool is `latest`: print `All N tools are at latest. Nothing to do.` and stop.

### 3. Confirm

**User takeover gate.** Two passes if major versions exist, one pass otherwise.

**Pass A — partition the diff into two buckets:**

- **Safe bucket:** `latest`, `⬆ patch`, `⬆ minor`
- **Major bucket:** `⚠ major` (each tool listed individually)

**Pass B — ask, in this order:**

1. **If major bucket is non-empty:** present one AskUserQuestion per major tool.

   Resolve the changelog URL for each major tool before asking:
   - **brew formula:** run `brew info <tool> | grep -E '^From:' | head -1` — the `From: <url>` line is the formula source; the changelog is typically `<repo>/releases` or `<repo>/blob/main/CHANGELOG.md`
   - **npm global:** run `npm view <pkg> repository.url` (and `homepage` as fallback) — the changelog is typically `<repo>/releases`

   Question: "`<tool>` has a major version bump `<old>` → `<new>`. See `<changelog-url>`. Upgrade?"
   Options: `Upgrade` / `Skip`
   Resolve all major tools before proceeding.

2. **Ask once for the safe bucket:**
   - "Upgrade `<N>` patch/minor updates? (`<tool list>`)"
   - Options: `Upgrade all` / `Skip — exit`

If both buckets are skipped (or one bucket is empty and the other is skipped), end the skill here. **Never** auto-default to "yes" — if the user does not pick an option, end the skill.

### 4. Upgrade

**Run only the tools the user approved in step 3** — never the full stack. Group by manager, single command per group so output stays contiguous:

```bash
# Substitute the user's approved list — these are placeholders
brew upgrade <approved-brew-list>
npm update -g <approved-npm-list>
```

If the approved list is empty, skip this step and go to step 5.

**Completion:** both commands exit 0. Any non-zero exit jumps to step 6 with the failing command captured.

### 5. Verify

Re-run step 1's probe. Compare against the pre-upgrade probe:

- Every previously-outdated tool must now equal `latest`
- Every previously-`?` row should now resolve, or be flagged again

Final line:

```
Result: <N> upgraded, <M> already at latest, <F> failed.
```

If `F > 0`, jump to step 6.

If the project has a `Brewfile.lock.json`, append:

```
Reminder: check `git status` for `Brewfile.lock.json` changes.
```

### 6. On failure

**Trigger:** any command in step 4 returns non-zero, or step 5's verify finds previously-outdated tools still outdated.

Print:

> **Stuck on network?** Run `proxy-on` (your existing alias for `http://localhost:7890`), wait a few seconds for the proxy to come up, then re-run `/tool-upgrade`.
>
> If `proxy-on` is not already aliased, register it once:
> ```zsh
> alias proxy-on='export ALL_PROXY=http://localhost:7890 && export http_proxy=$ALL_PROXY && export https_proxy=$ALL_PROXY'
> ```

If the failure is non-network (formula conflict, post-install hook error, signature mismatch): surface the brew / npm error verbatim. Do not auto-retry — leave the user in control.
