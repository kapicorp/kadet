# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `py.typed` marker (PEP 561) so downstream type checkers honour kadet's
  bundled inline annotations.
- Hypothesis property-based round-trip tests for `dump()` and YAML cycles.

### Changed
- **BREAKING:** `sha256()` now hashes a canonical, key-sorted serialization
  instead of `str(dump())`. Digests no longer depend on dict insertion order.
  Every digest changes once with this release; consumers that persisted kadet
  digests (e.g. Kapitan cache keys) will see a one-time invalidation, after
  which digests are stable and order-independent.

### Fixed
- `optional(key, default=...)` now applies the default when `istype` is
  omitted. Previously the default was silently dropped and the key was
  auto-vivified to `{}`.
- Removed the verbatim duplication of the recursive `_dump` walker between
  `BaseObj` and `BaseModel` (extracted to a single module-level function).

## [0.3.2]

Releases up to and including 0.3.2 predate this changelog. See the
[git history](https://github.com/kapicorp/kadet/commits/master) and
[release tags](https://github.com/kapicorp/kadet/tags).

[Unreleased]: https://github.com/kapicorp/kadet/compare/v0.3.2...HEAD
[0.3.2]: https://github.com/kapicorp/kadet/releases/tag/v0.3.2
