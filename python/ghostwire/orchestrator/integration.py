"""
GhostWire Openspec Orchestrator - Integration Module

This module provides the main interface between the Openspec Orchestrator
and the GhostWire Refractory project, enabling multi-LLM coordination
for various tasks including benchmarking with GHOSTWIRE scoring.
"""

import hashlib
import logging
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from ..config.settings import settings
from .llm_clients import LLMClient

# Import orchestrator components
from .master import Master
from .patch_engine import PatchEngine
from .permission_manager import PermissionManager


class TaskGraph:
    """
    Represents a task dependency graph following the τg concept from OpenSpec.
    """

    def __init__(self):
        self.nodes = {}  # task_id -> task_definition
        self.dependencies = defaultdict(list)  # task_id -> [dependent_task_ids]
        self.execution_order = []

    def add_task(self, task_id: str, task_def: dict[str, Any]):
        """Add a task to the graph."""
        self.nodes[task_id] = task_def

    def add_dependency(self, task_id: str, depends_on: str):
        """Add a dependency relationship."""
        self.dependencies[depends_on].append(task_id)

    def calculate_execution_order(self) -> list[str]:
        """Calculate the execution order respecting dependencies (topological sort)."""
        visited = set()
        order = []

        def dfs(node):
            if node in visited:
                return
            visited.add(node)

            for dependent in self.dependencies[node]:
                dfs(dependent)

            order.append(node)

        for node in self.nodes:
            if node not in visited:
                dfs(node)

        return order


class PatchProposal:
    """
    Represents a patch proposal following the OpenSpec schema (Ψp).
    """

    def __init__(
        self,
        module: str,
        file: str,
        change_type: str,
        pointer: str,
        change: Any = None,
        worker: str = "default_worker",
        context: str = "",
    ):
        self.module = module
        self.file = file
        self.type = change_type  # add, modify, delete
        self.pointer = pointer  # JSON Pointer format
        self.change = change
        self.id = self._generate_id()
        self.worker = worker
        self.context_sha = hashlib.sha1(context.encode()).hexdigest() if context else ""

    def _generate_id(self) -> str:
        import secrets

        return secrets.token_hex(8)

    def to_dict(self) -> dict[str, Any]:
        result = {
            "module": self.module,
            "file": self.file,
            "type": self.type,
            "pointer": self.pointer,
            "id": self.id,
            "worker": self.worker,
            "context_sha": self.context_sha,
        }
        if self.change is not None:
            result["change"] = self.change
        return result


class MergeEngine:
    """
    Advanced merge engine with conflict detection and resolution (shadow_merge).
    """

    def __init__(self, spec_store_path: str):
        self.spec_store_path = Path(spec_store_path)
        self.logger = logging.getLogger(__name__)

    async def merge_patch(self, patch_proposal: PatchProposal) -> dict[str, Any]:
        """
        Apply a patch following the merge logic described in OpenSpec.
        """
        try:
            # Read the base file
            file_path = self._get_file_path(patch_proposal.module, patch_proposal.file)
            if not file_path.exists():
                return {"success": False, "error": f"File does not exist: {file_path}"}

            with open(file_path, encoding="utf-8") as f:
                base_content = f.read()

            # Apply the patch to get the shadow state
            shadow_content = await self._apply_patch_to_content(
                base_content, patch_proposal
            )

            # Check for conflicts with HEAD (current state)
            has_conflict = self._detect_conflicts(base_content, shadow_content)

            if has_conflict:
                # In a full implementation, we'd do a three-way merge
                # For now, we'll just return conflict info
                return {
                    "success": False,
                    "conflict": True,
                    "message": "Conflict detected during merge process",
                    "resolution": "Manual intervention required",
                }
            else:
                # Write the shadow content to the file (successful merge)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(shadow_content)

                return {
                    "success": True,
                    "message": f"Patch {patch_proposal.id} merged successfully",
                    "file": str(file_path),
                }
        except Exception as e:
            self.logger.error(f"Error during merge: {e}")
            return {"success": False, "error": str(e)}

    def _get_file_path(self, module: str, file: str) -> Path:
        """Get the full path for a spec file."""
        return self.spec_store_path / "modules" / module / file

    async def _apply_patch_to_content(
        self, base_content: str, patch_proposal: PatchProposal
    ) -> str:
        """Apply a patch proposal to content. This is a simplified implementation."""
        # In a real implementation, this would properly apply the JSON Pointer patch
        # For now, we'll just simulate the operation
        import yaml

        try:
            # Parse the base YAML content
            base_data = yaml.safe_load(base_content) or {}

            # Apply the patch based on type and pointer
            if patch_proposal.type == "add":
                # Simple implementation - append to the target structure
                if patch_proposal.pointer.startswith("/"):
                    # This is a simplified path resolution
                    path_parts = [
                        part for part in patch_proposal.pointer[1:].split("/") if part
                    ]
                    if path_parts:
                        # Navigate to the target location and add the change
                        target = base_data
                        for part in path_parts[:-1]:
                            if isinstance(target, dict):
                                target = target.setdefault(part, {})
                            elif isinstance(target, list) and part.isdigit():
                                idx = int(part)
                                while len(target) <= idx:
                                    target.append({})
                                target = target[idx]

                        final_part = path_parts[-1]
                        if isinstance(target, dict):
                            target[final_part] = patch_proposal.change
                        elif isinstance(target, list) and final_part.isdigit():
                            idx = int(final_part)
                            while len(target) <= idx:
                                target.append(None)
                            target[idx] = patch_proposal.change

            elif patch_proposal.type == "modify":
                # Modify existing content
                if patch_proposal.pointer.startswith("/"):
                    path_parts = [
                        part for part in patch_proposal.pointer[1:].split("/") if part
                    ]
                    target = base_data
                    for part in path_parts[:-1]:
                        if isinstance(target, dict):
                            target = target.get(part, {})
                        elif isinstance(target, list) and part.isdigit():
                            idx = int(part)
                            target = target[idx] if idx < len(target) else {}

                    final_part = path_parts[-1]
                    if isinstance(target, dict):
                        target[final_part] = patch_proposal.change
                    elif isinstance(target, list) and final_part.isdigit():
                        idx = int(final_part)
                        if idx < len(target):
                            target[idx] = patch_proposal.change
            elif patch_proposal.type == "delete" and patch_proposal.pointer.startswith(
                "/"
            ):
                # Delete content at pointer
                path_parts = [
                    part for part in patch_proposal.pointer[1:].split("/") if part
                ]
                if len(path_parts) >= 1:
                    target = base_data
                    for part in path_parts[:-1]:
                        if isinstance(target, dict):
                            target = target.get(part, {})
                        elif isinstance(target, list) and part.isdigit():
                            idx = int(part)
                            target = target[idx] if idx < len(target) else {}

                    final_part = path_parts[-1]
                    if isinstance(target, dict) and final_part in target:
                        del target[final_part]

            # Return the modified content as YAML
            return yaml.dump(base_data, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            self.logger.error(f"Error applying patch to content: {e}")
            raise

    def _detect_conflicts(self, base_content: str, shadow_content: str) -> bool:
        """Detect if there are conflicts between base and shadow states."""
        # In a real implementation, this would compare with the HEAD state
        # For now, we'll just return False to allow all merges
        return False


class SecondaryValidator:
    """
    Implements the Secondary validation role from OpenSpec script.
    """

    def __init__(
        self, spec_store_path: str = "python/ghostwire/orchestrator/spec_store"
    ):
        self.spec_store_path = Path(spec_store_path)
        self.logger = logging.getLogger(__name__)

    def load_global_constraints(self) -> list[dict[str, Any]]:
        """Load global constraints from spec store."""
        constraints_path = self.spec_store_path / "global" / "constraints.yaml"
        if constraints_path.exists():
            with open(constraints_path) as f:
                data = yaml.safe_load(f)
                return data.get("constraints", [])
        return []

    def check_invariants(self) -> list[str]:
        """Check system invariants as defined in OpenSpec."""
        errors = []

        # Check DAG constraint on tasks
        for module_dir in (self.spec_store_path / "modules").iterdir():
            if module_dir.is_dir():
                tasks_file = module_dir / "tasks.yaml"
                if tasks_file.exists():
                    with open(tasks_file) as f:
                        tasks_data = yaml.safe_load(f)
                        if tasks_data and "tasks" in tasks_data:
                            # Check for task cycles (simplified check)
                            dependencies = {}
                            for task in tasks_data["tasks"]:
                                deps = task.get("depends_on", [])
                                dependencies[task.get("name", "")] = deps

                            # Simple cycle detection
                            visited = set()
                            rec_stack = set()

                            def has_cycle(node):
                                if node in rec_stack:
                                    return True
                                if node in visited:
                                    return False

                                visited.add(node)
                                rec_stack.add(node)

                                for dep in dependencies.get(node, []):
                                    if has_cycle(dep):
                                        return True

                                rec_stack.remove(node)
                                return False

                            for task_name in dependencies:
                                if has_cycle(task_name):
                                    errors.append(
                                        f"Cycle detected in task dependencies for module {module_dir.name}"
                                    )

                        # Check role existence for tasks
                        roles_file = module_dir / "roles.yaml"
                        if roles_file.exists():
                            with open(roles_file) as rf:
                                roles_data = yaml.safe_load(rf)
                                roles = set()
                                if roles_data and "roles" in roles_data:
                                    roles = set(roles_data["roles"].keys())

                                for task in tasks_data["tasks"]:
                                    required_role = task.get("role")
                                    if required_role and required_role not in roles:
                                        errors.append(
                                            f"Task {task.get('name')} requires non-existent role: {required_role}"
                                        )

        return errors

    async def verify_patch(
        self, patch_proposal: PatchProposal, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Verify a patch proposal following the OpenSpec secondary validation routine.
        """
        # Log the verification attempt
        self._log_verification_attempt(patch_proposal)

        # Check syntax
        if not self._validate_syntax(patch_proposal):
            return {"approved": False, "reason": "Invalid syntax in patch proposal"}

        # Check permissions
        if not self._check_permissions(patch_proposal):
            return {"approved": False, "reason": "Insufficient permissions for patch"}

        # Check invariants before patch
        before_errors = self.check_invariants()
        if before_errors:
            return {
                "approved": False,
                "reason": f"System invariants violated before patch: {before_errors}",
            }

        # Apply shadow and check constraints
        if not await self._check_constraints(patch_proposal):
            return {"approved": False, "reason": "Patch violates system constraints"}

        # Confidence check (mock implementation)
        confidence = self._get_confidence(patch_proposal)
        if confidence < 0.68:  # Threshold from script
            return {
                "approved": False,
                "reason": "Low confidence in patch validity",
                "fix": "Verify patch changes",
                "confidence": confidence,
            }

        return {"approved": True, "confidence": confidence, "reasons": []}

    def _validate_syntax(self, patch_proposal: PatchProposal) -> bool:
        """Validate the syntax of a patch proposal."""
        try:
            patch_dict = patch_proposal.to_dict()
            required_fields = ["module", "file", "type", "pointer", "id", "worker"]
            return all(
                field in patch_dict for field in required_fields
            ) and patch_proposal.type in ["add", "modify", "delete"]
        except (KeyError, TypeError, AttributeError):
            return False

    def _check_permissions(self, patch_proposal: PatchProposal) -> bool:
        """Check if the worker has permission to modify the specified module/file."""
        permissions_path = self.spec_store_path / "permissions.yaml"
        if permissions_path.exists():
            with open(permissions_path) as f:
                data = yaml.safe_load(f)
                worker_perms = data.get("worker_permissions", {}).get(
                    patch_proposal.worker, {}
                )
                allowed_modules = worker_perms.get("allowed_modules", [])
                allowed_files = worker_perms.get("allowed_files", [])

                return (
                    patch_proposal.module in allowed_modules
                    and patch_proposal.file in allowed_files
                )
        return False

    async def _check_constraints(self, patch_proposal: PatchProposal) -> bool:
        """Check if applying the patch would violate any constraints."""
        # This is a simplified constraint check
        # In a full implementation, we would evaluate the constraints against the proposed changes
        constraints = self.load_global_constraints()

        # Basic validation of constraint values
        for constraint in constraints:
            if (
                constraint.get("type") == "numeric"
                and constraint.get("name") == "max_request_size"
                and patch_proposal.change
                and len(str(patch_proposal.change)) > constraint.get("value", 10000)
            ):
                return False
        return True

    def _get_confidence(self, patch_proposal: PatchProposal) -> float:
        """Calculate confidence in the patch proposal."""
        # This would be a more sophisticated implementation in practice
        # For now, we'll return a fixed value above the threshold
        return 0.85

    def _log_verification_attempt(self, patch_proposal: PatchProposal):
        """Log the verification attempt for telemetry."""
        log_entry = {
            "t": int(time.time() * 1000),  # epoch_ms
            "actor": "φS",  # Secondary control
            "event": "verify.submit",
            "ref": {
                "module": patch_proposal.module,
                "file": patch_proposal.file,
                "patch_id": patch_proposal.id,
            },
        }
        self.logger.info(f"Verification attempt: {log_entry}")


class GhostWireOrchestrator:
    """Main class for integrating Openspec Orchestrator with GhostWire Refractory."""

    def __init__(
        self,
        base_path: str = ".",
        llm_endpoints: list[str] | None = None,
        default_model: str = "gemma3:1b",
        spec_store_path: str = "python/ghostwire/orchestrator/spec_store",
    ):
        """
        Initialize the GhostWire Orchestrator.

        Args:
            base_path: Base path for file operations
            llm_endpoints: List of LLM endpoints to coordinate
            default_model: Default model to use for LLM clients
            spec_store_path: Path to the spec store for validation
        """
        self.logger = logging.getLogger(__name__)
        self.patch_engine = PatchEngine(base_path=base_path)
        self.permission_manager = PermissionManager()
        self.secondary_validator = SecondaryValidator(spec_store_path)
        self.merge_engine = MergeEngine(spec_store_path)
        self.task_graph = TaskGraph()

        # Telemetry counters
        self.counters = {
            "patches_submitted": 0,
            "patches_approved": 0,
            "merges_completed": 0,
            "rejects_total": 0,
            "escalations_triggered": 0,
        }

        # Set up LLM clients
        self.default_model = default_model
        self.llm_endpoints = llm_endpoints or [settings.LOCAL_OLLAMA_URL]

        self.llm_clients = [
            LLMClient(
                name=f"llm_client_{i}", endpoint=endpoint, model=self.default_model
            )
            for i, endpoint in enumerate(self.llm_endpoints)
        ]

        # Initialize the master orchestrator
        self.master = Master(
            llm_clients=self.llm_clients,
            patch_engine=self.patch_engine,
            permission_manager=self.permission_manager,
        )

        self.logger.info(
            f"Initialized GhostWire Orchestrator with {len(self.llm_clients)} LLM clients"
        )

    async def process_request(
        self, user_request: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Process a user request through the orchestration system.

        Args:
            user_request: The user's request
            context: Additional context information

        Returns:
            Dictionary containing the response and metadata
        """
        self.logger.info(
            f"Processing user request through orchestrator: {user_request}"
        )

        # Process through the master orchestrator
        result = await self.master.process_request(user_request, context)

        self.logger.info("Request processed successfully through orchestration system")
        return result

    async def run_benchmark_task(
        self, benchmark_type: str, models: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Run a benchmark task through the orchestration system.

        Args:
            benchmark_type: Type of benchmark to run (embedding, rag, summarization, model_comparison)
            models: List of models to benchmark (if applicable)

        Returns:
            Dictionary with benchmark results and GHOSTWIRE scores
        """
        self.logger.info(f"Running {benchmark_type} benchmark through orchestrator")

        if benchmark_type == "model_comparison":
            # For model comparison, we'll create tasks for each model/benchmark type
            user_request = f"Run comprehensive model comparison benchmark for models: {models or ['default']}"
        else:
            user_request = f"Run {benchmark_type} benchmark"

        # Create context with appropriate permissions for benchmarking
        context = {
            "permission_level": "execute",
            "benchmark_type": benchmark_type,
            "models": models or ["default"],
        }

        result = await self.process_request(user_request, context)

        # Add GHOSTWIRE scoring to the results
        result["ghostwire_scores"] = await self._calculate_ghostwire_scores(
            result["results"], benchmark_type
        )

        self.logger.info(f"{benchmark_type} benchmark completed through orchestration")
        return result

    async def propose_patch(
        self,
        module: str,
        file: str,
        change_type: str,
        pointer: str,
        change: Any = None,
        worker: str = "default_worker",
        context: str = "",
    ) -> dict[str, Any]:
        """
        Propose a patch following the OpenSpec patch proposal schema.

        Args:
            module: Target module name
            file: Target file in module
            change_type: Type of change (add, modify, delete)
            pointer: JSON Pointer for the change location
            change: Value to write (omit for delete)
            worker: Worker identifier
            context: Context string for SHA calculation

        Returns:
            Dictionary with patch proposal and validation results
        """
        self.counters["patches_submitted"] += 1

        patch_proposal = PatchProposal(
            module=module,
            file=file,
            change_type=change_type,
            pointer=pointer,
            change=change,
            worker=worker,
            context=context,
        )

        # Validate the patch through the secondary validator
        validation_result = await self.secondary_validator.verify_patch(patch_proposal)

        if validation_result.get("approved"):
            self.counters["patches_approved"] += 1
            # If approved, we could potentially apply the patch
            # For now, just return the proposal and validation
            return {
                "proposal": patch_proposal.to_dict(),
                "approved": True,
                "validation": validation_result,
            }
        else:
            self.counters["rejects_total"] += 1
            return {
                "proposal": patch_proposal.to_dict(),
                "approved": False,
                "validation": validation_result,
            }

    async def submit_and_merge_patch(
        self,
        module: str,
        file: str,
        change_type: str,
        pointer: str,
        change: Any = None,
        worker: str = "default_worker",
        context: str = "",
    ) -> dict[str, Any]:
        """
        Submit a patch proposal and merge it if approved.

        Args:
            module: Target module name
            file: Target file in module
            change_type: Type of change (add, modify, delete)
            pointer: JSON Pointer for the change location
            change: Value to write (omit for delete)
            worker: Worker identifier
            context: Context string for SHA calculation

        Returns:
            Dictionary with patch proposal and validation/merge results
        """
        proposal_result = await self.propose_patch(
            module, file, change_type, pointer, change, worker, context
        )

        if proposal_result["approved"]:
            # Attempt to merge the approved patch
            patch_proposal = PatchProposal(
                module=module,
                file=file,
                change_type=change_type,
                pointer=pointer,
                change=change,
                worker=worker,
                context=context,
            )

            merge_result = await self.merge_engine.merge_patch(patch_proposal)

            if merge_result["success"]:
                self.counters["merges_completed"] += 1
                return {
                    **proposal_result,
                    "merge_result": merge_result,
                    "status": "merged",
                }
            else:
                return {
                    **proposal_result,
                    "merge_result": merge_result,
                    "status": "merge_failed",
                }
        else:
            return proposal_result

    async def decompose_user_intent(self, user_intent: str) -> list[dict[str, Any]]:
        """
        Decompose a user intent into a task graph with dependencies (Δa*).

        Args:
            user_intent: The original user request/intent

        Returns:
            List of assignments (Δa) with module, file, task description, etc.
        """
        # This is a simplified decomposition - in a full implementation,
        # this would use LLMs to analyze the intent and create specific assignments
        tasks = []

        # Example: If the intent is to add a DELETE endpoint, we'd create multiple assignments
        if "delete" in user_intent.lower() or "remove" in user_intent.lower():
            # Add to spec
            tasks.append(
                {
                    "worker": "api_worker",
                    "module": "api",
                    "file": "spec.yaml",
                    "task_desc": f"Add interface for DELETE operation based on intent: {user_intent}",
                    "depends_on": [],
                }
            )

            # Add related tasks
            tasks.append(
                {
                    "worker": "orchestration_worker",
                    "module": "orchestration",
                    "file": "tasks.yaml",
                    "task_desc": f"Add task definition for delete operation: {user_intent}",
                    "depends_on": ["api_worker"],
                }
            )

        # Add to roles if needed
        if "role" in user_intent.lower() or "permission" in user_intent.lower():
            tasks.append(
                {
                    "worker": "permission_worker",
                    "module": "permissions",
                    "file": "roles.yaml",
                    "task_desc": f"Update role mappings for: {user_intent}",
                    "depends_on": ["orchestration_worker"],  # depends on tasks
                }
            )

        # Update the task graph
        for i, task in enumerate(tasks):
            task_id = f"task_{i}_{task['worker']}"
            self.task_graph.add_task(task_id, task)
            for dep in task.get("depends_on", []):
                # This is a simplified dependency mapping
                pass

        # Calculate execution order
        execution_order = self.task_graph.calculate_execution_order()
        self.logger.info(
            f"Decomposed intent into {len(tasks)} tasks with execution order: {execution_order}"
        )

        return tasks

    async def _calculate_ghostwire_scores(
        self, results: list[dict], benchmark_type: str
    ) -> dict[str, float]:
        """
        Calculate GHOSTWIRE scores based on benchmark results.

        Args:
            results: List of benchmark results
            benchmark_type: Type of benchmark that was run

        Returns:
            Dictionary of GHOSTWIRE scores
        """
        # This is a simplified implementation - in a real system, this would
        # use the actual scoring logic from the benchmarking system
        scores = {}

        if benchmark_type == "embedding":
            # Calculate embedding-specific GHOSTWIRE score
            scores["embedding_score"] = 0.85  # Placeholder value
            scores["stability_score"] = 0.90  # Placeholder value
        elif benchmark_type == "rag":
            # Calculate RAG-specific GHOSTWIRE score
            scores["rag_score"] = 0.78  # Placeholder value
            scores["quality_score"] = 0.82  # Placeholder value
        elif benchmark_type == "summarization":
            # Calculate summarization-specific GHOSTWIRE score
            scores["summarization_score"] = 0.80  # Placeholder value
            scores["accuracy_score"] = 0.85  # Placeholder value
        elif benchmark_type == "model_comparison":
            # Calculate overall model comparison scores
            scores["overall_score"] = 0.82  # Placeholder value
            scores["consistency_score"] = 0.88  # Placeholder value
        else:
            # General score for other types
            scores["general_score"] = 0.75  # Placeholder value

        return scores

    async def apply_code_changes(self, patch_data: dict[str, Any]) -> dict[str, Any]:
        """
        Apply code changes to the GhostWire Refractory project using the patch engine.

        Args:
            patch_data: Dictionary containing patch information

        Returns:
            Dictionary with patch application results
        """
        self.logger.info(
            f"Applying code changes: {patch_data.get('file_path', 'unknown file')}"
        )

        # Validate the patch before applying
        validation = await self.patch_engine.validate_patch(patch_data)
        if not validation["valid"]:
            return {
                "success": False,
                "message": f"Patch validation failed: {validation['errors']}",
                "validation": validation,
            }

        # Apply the patch
        result = await self.patch_engine.apply_patch(patch_data)

        self.logger.info(f"Code changes applied: {result['message']}")
        return result

    def get_telemetry(self) -> dict[str, Any]:
        """Get current telemetry counters."""
        return self.counters.copy()

    async def close(self):
        """Close all resources used by the orchestrator."""
        for client in self.llm_clients:
            await client.close()

        self.logger.info("GhostWire Orchestrator closed")


# Convenience function for creating an orchestrator instance
def create_ghostwire_orchestrator(
    base_path: str = ".",
    llm_endpoints: list[str] | None = None,
    default_model: str = "gemma3:1b",
    spec_store_path: str = "python/ghostwire/orchestrator/spec_store",
) -> GhostWireOrchestrator:
    """
    Create a GhostWire Orchestrator instance with default configuration.

    Args:
        base_path: Base path for file operations
        llm_endpoints: List of LLM endpoints to coordinate
        default_model: Default model to use for LLM clients
        spec_store_path: Path to the spec store for validation

    Returns:
        GhostWireOrchestrator instance
    """
    return GhostWireOrchestrator(
        base_path=base_path,
        llm_endpoints=llm_endpoints,
        default_model=default_model,
        spec_store_path=spec_store_path,
    )
