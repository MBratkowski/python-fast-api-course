---
phase: 05-advanced-features
plan: 02
subsystem: course-content
tags: [file-uploads, websockets, uploadfile, connection-manager, s3, presigned-urls, pillow, redis-pubsub]
dependency-graph:
  requires:
    - phase: 03-auth-and-security
      provides: JWT authentication patterns (PyJWT) used in WebSocket auth theory
    - phase: 04-testing-and-async
      provides: async/await patterns used in WebSocket and file upload endpoints
  provides:
    - Module 015 File Uploads and Storage course content (11 files)
    - Module 016 WebSockets and Real-Time course content (11 files)
  affects: [course-content, phase-06]
tech-stack:
  added: [UploadFile, shutil, boto3, Pillow, WebSocket, ConnectionManager, redis-pubsub]
  patterns: [three-gate-validation, uuid-filename, streaming-upload, connection-manager, room-based-messaging, query-param-ws-auth]
key-files:
  created:
    - 015-file-uploads/README.md
    - 015-file-uploads/theory/*.md (6 files)
    - 015-file-uploads/exercises/*.py (3 files)
    - 015-file-uploads/project/README.md
    - 016-websockets/README.md
    - 016-websockets/theory/*.md (6 files)
    - 016-websockets/exercises/*.py (3 files)
    - 016-websockets/project/README.md
  modified: []
key-decisions:
  - "Module 015 exercises use local file storage only (no cloud dependencies)"
  - "Module 016 exercises use TestClient websocket_connect for self-contained testing"
  - "WebSocket authentication theory uses PyJWT (consistent with Phase 3 decision)"
  - "Three-gate validation pattern: content-type, magic numbers, file size"
  - "ConnectionManager pattern from FastAPI docs as standard for all WS exercises"
patterns-established:
  - "Three-gate file validation: content-type check, magic number check, file size check"
  - "UUID-prefixed filenames for safe unique storage"
  - "ConnectionManager singleton for WebSocket connection tracking"
  - "Room-based messaging with dict[str, list[WebSocket]] data structure"
  - "Query parameter JWT token for WebSocket authentication"
requirements-completed: [FEAT-03, FEAT-04]
duration: 6min
completed: 2026-03-08
---

# Phase 05 Plan 02: File Uploads and WebSockets Summary

**UploadFile with three-gate validation and streaming storage, WebSocket ConnectionManager with room-based broadcasting and JWT query-param auth**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-08T17:17:58Z
- **Completed:** 2026-03-08T17:23:40Z
- **Tasks:** 2
- **Files modified:** 22

## Accomplishments
- Module 015 with comprehensive file upload coverage: UploadFile basics, content-type/magic-number/size validation, local storage with streaming, S3 integration, presigned URLs, image processing with Pillow
- Module 016 with full WebSocket coverage: HTTP vs WebSocket decision tree, FastAPI WebSocket lifecycle, ConnectionManager pattern, room-based broadcasting, JWT authentication via query parameters, Redis Pub/Sub scaling
- All 6 exercise files have TODO stubs with `pass` and inline pytest tests that validate implementations
- Both project READMEs include starter templates, success criteria, and stretch goals

## Task Commits

Each task was committed atomically:

1. **Task 1: Module 015 -- File Uploads and Storage** - `c1e2628` (feat)
2. **Task 2: Module 016 -- WebSockets and Real-Time** - `2f36c24` (feat)

## Files Created/Modified
- `015-file-uploads/README.md` - Module overview with mobile-dev upload comparison table
- `015-file-uploads/theory/01-upload-file-basics.md` - UploadFile, SpooledTemporaryFile, multipart/form-data
- `015-file-uploads/theory/02-file-validation.md` - Three-gate validation (content-type, magic numbers, size)
- `015-file-uploads/theory/03-local-storage.md` - shutil.copyfileobj streaming, UUID filenames, StaticFiles
- `015-file-uploads/theory/04-s3-integration.md` - boto3 upload_fileobj, key prefixes, S3StorageService
- `015-file-uploads/theory/05-presigned-urls.md` - Direct client-to-S3 upload/download, expiration config
- `015-file-uploads/theory/06-image-processing.md` - Pillow resize/thumbnail, EXIF handling, format conversion
- `015-file-uploads/exercises/01_file_upload.py` - Single/multiple upload endpoints (13 tests)
- `015-file-uploads/exercises/02_file_validation.py` - Content-type and size validation (15 tests)
- `015-file-uploads/exercises/03_storage_patterns.py` - UUID naming, date org, cleanup (17 tests)
- `015-file-uploads/project/README.md` - File upload service with thumbnails spec
- `016-websockets/README.md` - Module overview with real-time communication comparison table
- `016-websockets/theory/01-websocket-vs-http.md` - HTTP vs WebSocket vs SSE decision tree
- `016-websockets/theory/02-fastapi-websocket.md` - Accept/receive/send lifecycle, try/except pattern
- `016-websockets/theory/03-connection-manager.md` - ConnectionManager class, user tracking, dead connections
- `016-websockets/theory/04-broadcasting-rooms.md` - Room-based messaging, join/leave, room isolation
- `016-websockets/theory/05-websocket-authentication.md` - Query param token, cookie auth, first-message auth
- `016-websockets/theory/06-scaling-redis-pubsub.md` - Redis Pub/Sub for multi-server, room channels
- `016-websockets/exercises/01_basic_websocket.py` - Echo, JSON processing, disconnect tracking (13 tests)
- `016-websockets/exercises/02_connection_manager.py` - Build ConnectionManager class (9 tests)
- `016-websockets/exercises/03_broadcasting.py` - Room-based chat with RoomManager (9 tests)
- `016-websockets/project/README.md` - Real-time notification system with auth spec

## Decisions Made
- Module 015 exercises use local file storage only -- no boto3 or cloud deps required to run exercises
- Module 016 exercises use FastAPI TestClient's websocket_connect -- no external WebSocket server needed
- WebSocket authentication uses PyJWT (not python-jose) consistent with Phase 3 decision
- filetype library recommended over python-magic for validation (pure Python, no system deps)
- ConnectionManager follows exact pattern from FastAPI official documentation

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Modules 013-016 complete for Phase 5 (Advanced Features)
- Ready for Phase 6 (Deployment and DevOps) covering Docker, CI/CD, monitoring
- All WebSocket patterns established for any future real-time features

## Self-Check: PASSED

All 22 files verified present. Both commits (c1e2628, 2f36c24) verified in git log.

---
*Phase: 05-advanced-features*
*Completed: 2026-03-08*
