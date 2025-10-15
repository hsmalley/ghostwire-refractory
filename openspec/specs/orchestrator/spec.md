# Orchestrator Capability Specification

## Purpose

The Orchestrator capability provides multi-LLM coordination using the Master, Worker, and Secondary Control model for the GhostWire Refractory system, enabling distributed task processing, permission management, and safe code modifications.

## Requirements

### Requirement: Openspec Orchestrator System

The project SHALL provide a multi-LLM orchestration system with Master, Worker, and Secondary Control components.

#### Scenario: Master Component Coordinates Tasks

- **WHEN** a user request is processed through the orchestrator
- **THEN** the Master component decomposes the request into subtasks and distributes them among LLM clients

#### Scenario: LLM Client Execution

- **WHEN** the orchestrator assigns a task to an LLM client
- **THEN** the LLM client executes the specific task and returns results to the Master

#### Scenario: Permission Validation

- **WHEN** a task requires execution through the orchestrator
- **THEN** the PermissionManager validates appropriate permissions before task execution

### Requirement: Task Decomposition

The project SHALL provide functionality to decompose user requests into distributable subtasks.

#### Scenario: Request Decomposition

- **WHEN** decompose_user_request() is called with a user request
- **THEN** the system returns a list of subtasks appropriate for distribution among LLM clients

#### Scenario: Task Type Identification

- **WHEN** a request contains multiple types of operations (embed, summarize, chat)
- **THEN** the system creates specific subtasks for each operation type

### Requirement: Patch Engine

The project SHALL provide a safe patch engine for applying code modifications.

#### Scenario: Safe Code Patching

- **WHEN** the orchestrator needs to apply code changes
- **THEN** the PatchEngine validates and applies changes with backup capabilities

#### Scenario: Patch Validation

- **WHEN** a patch is submitted to the PatchEngine
- **THEN** the system validates that the patch is safe before application

### Requirement: Permission Management

The project SHALL provide role-based permissions for orchestrator tasks.

#### Scenario: Permission Check

- **WHEN** a task is submitted for execution
- **THEN** the PermissionManager checks if the user has appropriate permissions for the task type

#### Scenario: Session Management

- **WHEN** a user starts an orchestrated session
- **THEN** the system creates appropriate session tokens with time-limited permissions

## Benchmark Integration

The existing benchmarking system SHALL integrate with the orchestrator for multi-LLM benchmarking.

### Scenario: Orchestration Benchmark

- **WHEN** run_benchmark_task() is called through the orchestrator
- **THEN** the system distributes the benchmark across multiple LLMs and calculates GHOSTWIRE scores

## Design Principles

### Master/Worker/Secondary Control Pattern

The orchestrator follows the Master, Worker, and Secondary Control architectural pattern:

- **Master**: Coordinates the overall process, decomposes requests, and aggregates results
- **Worker (LLM Clients)**: Execute individual tasks on different LLM endpoints
- **Secondary Control**: Manages permissions, patches, and constraints

### Security & Safety

- All orchestrator operations SHALL validate permissions before execution
- Code patches SHALL be validated before application
- Session tokens SHALL be time-limited with appropriate permissions

### Extensibility

- The orchestrator SHALL support adding new LLM client types
- The task decomposition system SHALL be extensible for new task types
- The permission system SHALL support custom roles and permissions
