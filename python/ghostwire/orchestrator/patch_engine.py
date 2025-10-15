"""
GhostWire Openspec Orchestrator - Patch Engine

Implements the Patch Engine component that handles code modifications
and file operations based on LLM-generated patches.
"""

import logging
import os
from pathlib import Path
from typing import Any


class PatchEngine:
    def __init__(self, base_path: str = "."):
        """
        Initialize the Patch Engine.

        Args:
            base_path: Base path for file operations
        """
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(__name__)

    async def apply_patch(self, patch_data: dict[str, Any]) -> dict[str, Any]:
        """
        Apply a patch to a file or create a new file.

        Args:
            patch_data: Dictionary containing patch information
                - file_path: Path to the file
                - content: New content for the file
                - operation: 'create', 'update', or 'delete'
                - backup: Whether to create a backup (default: True)

        Returns:
            Dictionary with patch application results
        """
        file_path = self.base_path / patch_data["file_path"]
        operation = patch_data.get("operation", "update")
        backup = patch_data.get("backup", True)

        result = {
            "file_path": str(file_path),
            "operation": operation,
            "success": False,
            "message": "",
        }

        try:
            if operation == "create":
                result.update(
                    await self._create_file(
                        file_path, patch_data.get("content", ""), backup
                    )
                )
            elif operation == "update":
                result.update(
                    await self._update_file(
                        file_path, patch_data.get("content", ""), backup
                    )
                )
            elif operation == "delete":
                result.update(await self._delete_file(file_path))
            else:
                result["message"] = f"Unknown operation: {operation}"

        except Exception as e:
            self.logger.error(f"Patch application failed for {file_path}: {e}")
            result["success"] = False
            result["message"] = str(e)

        return result

    async def _create_file(
        self, file_path: Path, content: str, backup: bool = True
    ) -> dict[str, Any]:
        """Create a new file with the given content."""
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file already exists
        if file_path.exists():
            return {"success": False, "message": f"File already exists: {file_path}"}

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.logger.info(f"Created file: {file_path}")
        return {"success": True, "message": f"Successfully created file: {file_path}"}

    async def _update_file(
        self, file_path: Path, content: str, backup: bool = True
    ) -> dict[str, Any]:
        """Update an existing file with the given content."""
        # Check if file exists
        if not file_path.exists():
            return {"success": False, "message": f"File does not exist: {file_path}"}

        # Create backup if requested
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            with (
                open(file_path, encoding="utf-8") as original,
                open(backup_path, "w", encoding="utf-8") as backup_file,
            ):
                backup_file.write(original.read())

        # Write new content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.logger.info(f"Updated file: {file_path}")
        return {"success": True, "message": f"Successfully updated file: {file_path}"}

    async def _delete_file(self, file_path: Path) -> dict[str, Any]:
        """Delete the specified file."""
        if not file_path.exists():
            return {"success": False, "message": f"File does not exist: {file_path}"}

        # Delete the file
        os.remove(file_path)

        self.logger.info(f"Deleted file: {file_path}")
        return {"success": True, "message": f"Successfully deleted file: {file_path}"}

    async def apply_diff_patch(
        self, file_path: str, old_content: str, new_content: str
    ) -> dict[str, Any]:
        """
        Apply a diff-based patch to update a file.

        Args:
            file_path: Path to the file
            old_content: Original content to match
            new_content: New content to replace with

        Returns:
            Dictionary with patch application results
        """
        file_path_obj = self.base_path / file_path

        if not file_path_obj.exists():
            return {
                "success": False,
                "message": f"File does not exist: {file_path_obj}",
            }

        # Read current file content
        with open(file_path_obj, encoding="utf-8") as f:
            current_content = f.read()

        # Check if old_content exists in current file
        if old_content not in current_content:
            return {
                "success": False,
                "message": f"Original content not found in file: {file_path_obj}",
            }

        # Replace old content with new content
        updated_content = current_content.replace(old_content, new_content, 1)

        # Write updated content back to file
        with open(file_path_obj, "w", encoding="utf-8") as f:
            f.write(updated_content)

        self.logger.info(f"Applied diff patch to file: {file_path_obj}")
        return {
            "success": True,
            "message": f"Successfully applied diff patch to file: {file_path_obj}",
        }

    async def validate_patch(self, patch_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate a patch before applying it.

        Args:
            patch_data: Dictionary containing patch information

        Returns:
            Dictionary with validation results
        """
        file_path = self.base_path / patch_data["file_path"]
        operation = patch_data.get("operation", "update")

        validation_result = {"valid": True, "warnings": [], "errors": []}

        # Check if base directory is safe
        if not str(file_path).startswith(str(self.base_path)):
            validation_result["valid"] = False
            validation_result["errors"].append("File path is outside base directory")

        # Validate operation type
        if operation not in ["create", "update", "delete"]:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Invalid operation: {operation}")

        # Additional validation based on operation
        if operation == "create" and file_path.exists():
            validation_result["warnings"].append(f"File already exists: {file_path}")
        elif operation in ["update", "delete"] and not file_path.exists():
            validation_result["errors"].append(f"File does not exist: {file_path}")

        return validation_result
