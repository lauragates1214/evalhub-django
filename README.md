# EvalHub
#### Video Demo: <URL HERE>
#### Description:

## Project Overview

EvalHub is a web-based course evaluation platform designed to streamline the collection and analysis of student feedback in academic settings. As an educator, I recognised the limitations of traditional paper-based evaluations and generic survey tools that lack features specific to classroom environments. EvalHub addresses these challenges by providing instructors with a purpose-built system for gathering anonymous student feedback efficiently.

The platform enables instructors to create custom surveys with multiple question types, generate QR codes for instant student access, and view aggregated responses through an intuitive dashboard. Students can participate anonymously by simply scanning a QR code with their mobile devices, eliminating the need for accounts or login credentials. This reduces friction in the feedback process and encourages more candid responses.

Key features include survey creation and management, QR code generation for mobile access, anonymous student response submission, a response viewing dashboard for instructors, and CSV export functionality for further analysis. Built with Django and following test-driven development principles, EvalHub serves both as a practical tool for course evaluation and as a foundation for future development of more sophisticated feedback collection systems.

## Technical Architecture

EvalHub is built with Django 5.2, leveraging Python's robust web framework. I chose Django after gaining Python proficiency through CS50P, and was drawn to its "batteries-included" philosophy - the built-in admin interface, ORM, authentication system, and template engine provided a solid foundation without requiring extensive third-party dependencies.

The frontend uses htmx for dynamic interactions rather than React. While I've used React in previous projects and appreciated its capabilities, htmx proved more appropriate for EvalHub's use case. The primary users (students) access surveys via mobile devices by scanning QR codes, making page load speed critical. htmx's lightweight footprint (14KB vs React's much larger bundle) ensures fast loading on mobile networks, while still delivering a single-page application experience through AJAX-style requests and partial page updates. This means students can submit responses without full page refreshes, maintaining a smooth user experience without the overhead of a full JavaScript framework.

The database schema centres on four core models: User (handling both instructor and student authentication), Survey (storing survey metadata and activation status), Question (supporting text, multiple choice, and rating question types), and Response (capturing student answers linked to specific questions and surveys). For development, I used SQLite due to its simplicity, though the application is designed to migrate to PostgreSQL for production deployment.

The application is containerised using Docker for both development and production environments, ensuring consistency across different deployment contexts.

Django's template system renders server-side HTML enhanced with htmx attributes, striking a balance between traditional server-rendered pages and modern interactive experiences.

## File Structure Explanation

EvalHub follows Django's modular app structure, with functionality separated into discrete applications:

**`accounts/`** manages user authentication and the custom User model. This app handles login/logout functionality and user session management. It includes unit tests (`accounts/tests/`) verifying authentication flows and redirects.

**`surveys/`** contains the core data models (Survey, Question, Answer, Submission) and shared forms. This is the foundation of the application, defining the database schema and business logic for survey creation and response collection. Unit tests ensure model relationships and validations work correctly.

**`instructors/`** handles all instructor-facing views and URLs. Instructors can create surveys, add questions, view responses, export data to CSV, and manage their survey dashboard. The views use htmx for dynamic updates without page refreshes. Unit tests cover survey CRUD operations, permissions, and response viewing.

**`students/`** provides anonymous survey access for students. This app renders survey forms and handles response submission without requiring authentication. Unit tests verify that surveys are accessible, responses are saved correctly, and confirmation messages display properly.

**`functional_tests/`** contains Selenium-based integration tests following Harry Percival's methodology. These tests simulate complete user journeys - from instructor login and survey creation through to student response submission and instructor response viewing. The tests use page objects pattern for maintainability.

**`templates/`** stores shared HTML templates. The project-level `base.html` provides consistent navigation and styling across all apps, while app-specific templates extend this base.

**`static/scss/`** contains custom SCSS stylesheets compiled via django-compressor, integrating with Bootstrap 5 for responsive design.

**`evalhub/settings/`** includes split settings files (base, development, production) managing configuration and environment-specific behaviour.

## Design Decisions

**Modular App Structure:** I organised the project into separate Django apps (accounts, surveys, instructors, students) following Django's philosophy that each app should do one thing well. This separation of concerns improves maintainability and allows each component to be developed and tested independently.

**QR Code Anonymous Access:** Rather than requiring students to create accounts and log in, I implemented QR code-based anonymous access. This decision prioritises frictionless participation - students simply scan a code with their smartphones (which they typically have in class) and immediately access the survey. This eliminates barriers like password resets, account creation friction, and login failures that often reduce response rates in educational settings.

**Simplified Two-Tier Permissions:** The system implements only two roles: instructors (who create and manage surveys) and students (who respond anonymously). I deliberately avoided more complex permission systems as they weren't required for the core functionality, following the principle of not over-engineering solutions.

**Test-Driven Development:** I followed the TDD methodology from Harry Percival's book "Test-Driven Development with Python, 3rd Edition", after attending his workshop at PyCon UK 2025. This approach appealed to me for its emphasis on allowing the solution to fit the shape of the problem, whilst simultaneously building comprehensive and meaningful test coverage. The practice of writing tests first helped clarify requirements and catch edge cases early.

## Challenges & Solutions

**Django Learning Curve:** Transitioning from CS50P's introductory Python to Django's full-stack framework required understanding new concepts like the ORM, URL routing, and template inheritance. I used Claude alongside Django's official documentation to understand these patterns, treating the LLM as an interactive tutor that could explain concepts and suggest implementations.

**htmx Integration:** Implementing htmx for dynamic page updates required learning how to handle CSRF tokens, partial template rendering, and HTTP headers. I worked through this using Claude and htmx documentation to understand the request/response cycle.

**Test-Driven Development:** Following Harry Percival's "Test-Driven Development with Python, 3rd Edition", I learned to distinguish between functional tests (Selenium-based user journeys) and unit tests (isolated component testing). The TDD cycle of writing failing tests first, then implementing minimal code to pass them, helped clarify requirements and catch edge cases early.

**SCSS Compilation:** Configuring django-compressor to correctly compile SCSS files required getting file paths right in settings files.

## AI Assistance

I used AI tools throughout this project whilst maintaining ownership of all design decisions and core implementations. Claude served multiple roles: writing initial test cases following TDD patterns, helping interpret test failure output, explaining Django and htmx concepts, and debugging configuration issues. During the code integration phases of the TDD cycle, I instructed Claude to act as a tutor rather than writing code directly - guiding me through implementations step-by-step. I modelled this approach on CS50's duck debugger system prompt, introduced to me at a CS50 Hackathon in London in June 2025. Additionally, I used VS Code's integrated AI for code completions. All architectural decisions, feature designs, and final code implementations were my own work, with AI serving as an educational amplifier rather than a replacement for learning.

## Deployment & CI/CD

Following the deployment chapters in Percival's book, I configured a CI pipeline using GitHub Actions to automatically run tests on each commit. I containerised the application using Docker for both development and production environments, then set up a Digital Ocean VPS for both staging and production deployments, configuring Nginx, Gunicorn, and systemd services to run the Django application in a production-like environment. While I've since taken down the VPS to avoid ongoing costs, this process taught me valuable lessons about containerisation, server configuration, environment management, and deployment workflows.

---

**Author:** Laura Gates  
**GitHub:** lauragates1214  
**edX:** laurapg22  
**Location:** Bristol, UK  
**Date:** [Date of video recording]