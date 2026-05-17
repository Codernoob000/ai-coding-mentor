import os
from pathlib import Path
from typing import Set, List
from anyio import to_thread
from app.core.logger import logger

class SafeFileSystem:
    """
    Hardened filesystem utility for safe project traversal.
    Uses non-blocking thread offloading and depth-limited searches.
    """
    
    def __init__(self, workspace_root: str):
        self.root = Path(workspace_root).resolve()
        self.allowed_extensions: Set[str] = {
            ".py", ".js", ".ts", ".html", ".css", ".json", 
            ".md", ".c", ".cpp", ".h", ".rs", ".go"
        }
        # DoS Protection Limits
        self.MAX_LIST_FILES = 500
        self.MAX_RECURSION_DEPTH = 5

    def _safe_path(self, relative_path: str) -> Path:
        """
        Validates path containment and prevents absolute path injection.
        """
        # CRITICAL FIX: Strip leading separators to prevent (root / "/abs/path") resolving to "/abs/path"
        clean_rel = relative_path.lstrip("/\\")
        try:
            target_path = (self.root / clean_rel).resolve()
            
            # CRITICAL FIX: Use is_relative_to for robust cross-platform containment check
            if not target_path.is_relative_to(self.root):
                logger.warning(f"SECURITY: Blocked access attempt outside root: {relative_path}")
                raise ValueError("Access denied: Path is outside workspace root.")
                
            return target_path
        except Exception as e:
            if isinstance(e, ValueError): raise
            logger.error(f"Path validation error: {e}")
            raise ValueError(f"Invalid path requested: {relative_path}")

    async def read_file_safe(self, relative_path: str) -> str:
        """
        Reads file content using a thread pool to avoid blocking the event loop.
        """
        target = self._safe_path(relative_path)
        
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {relative_path}")
            
        if target.suffix.lower() not in self.allowed_extensions:
            raise ValueError(f"File type {target.suffix} is not allowed.")

        # CRITICAL FIX: Offload blocking I/O to a worker thread
        try:
            content = await to_thread.run_sync(target.read_text, "utf-8")
            return content
        except UnicodeDecodeError:
            raise ValueError("File content is not valid UTF-8 text.")

    async def list_project_files(self, sub_dir: str = ".") -> List[str]:
        """
        Lists files with depth and count limits to prevent DoS.
        """
        target_dir = self._safe_path(sub_dir)
        if not target_dir.is_dir():
            return []

        # Offload the recursive search to a thread
        def _sync_list():
            found_files = []
            # Manual walk to control depth
            root_depth = len(target_dir.parts)
            for current_root, dirs, files in os.walk(target_dir):
                curr_path = Path(current_root)
                depth = len(curr_path.parts) - root_depth
                
                if depth > self.MAX_RECURSION_DEPTH:
                    del dirs[:] # Stop deeper recursion
                    continue
                
                for file in files:
                    file_path = curr_path / file
                    if file_path.suffix.lower() in self.allowed_extensions:
                        found_files.append(str(file_path.relative_to(self.root)))
                        if len(found_files) >= self.MAX_LIST_FILES:
                            return found_files
            return found_files

        return await to_thread.run_sync(_sync_list)
