# TaskForge changelog

## Milestone 6 — Exam Solver
- Added authenticated PDF/image upload and text extraction using PyMuPDF with optional Tesseract OCR fallback for scanned pages.
- Added question segmentation, basic question-type classification, Gemini worked solutions, and a separate Gemini verification pass.
- Added authenticated exam history and PDF/DOCX solution exports.
- Added MySQL migration `006_exam_solver.sql`, API documentation, OCR setup notes, and frontend Exam Solver Studio.
- Preserved the existing MySQL, Gemini, Tavily, authentication, task execution, research, document and data-analysis modules.
