# Migration Log

## Decisions and Notes

### Phase 0 - Safety net

- **Branch**: Created `chore/repo-restructure` for all changes.
- **Test Baseline**: Run existing `pytest` tests. The test suite failed initially due to a FastAPI `RuntimeError` (`Expected ASGI message 'http.response.start', but got 'http.response.template'`). This failure is the baseline.
- **Secret Scan**: Scanned the working tree and `git log -p` for secrets like `client_secret`, `api_key`, `AIza`, `ghp_`, and `BEGIN PRIVATE`. No real secrets were found. Only standard code references and placeholder documentation variables (e.g., `your_gemini_key`) were identified.
- **Vercel Build**: Testing Vercel build phase (results pending).

### Phase 2 - Remove root clutter
- **Decisions**: Deleted one-off patch scripts and temporary outputs from root (ix.py, eplace_script*.py, ind*.py, update_prompt.py, *_debug*, ercel_*.html, out.json, dep.json). Test runners were deleted as their logic is subsumed by standard pytest invocation. models.json moved to docs/data/ with a note as it contains Gemini enumerations rather than config. sensor_logs.csv moved to data/sample/.

