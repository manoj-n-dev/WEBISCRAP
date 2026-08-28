import os
import uuid
import pandas as pd
from typing import Dict, Any, List
from loguru import logger
from .base import BaseAgent
from datetime import datetime

# In a real app, this should be configurable
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

# C7: Formula injection protection — dangerous leading characters in cells
_FORMULA_CHARS = ('=', '+', '-', '@', '\t', '\r', '\n')

def sanitize_cell_value(val: Any) -> Any:
    """C7: Prefix dangerous leading characters with a single quote to prevent formula injection."""
    if isinstance(val, str) and val and val[0] in _FORMULA_CHARS:
        return "'" + val
    return val

class ExportAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ExportAgent")
        
    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        dataset = input_data.get("filtered_data", input_data.get("cleaned_data", []))
        export_format = input_data.get("export_requested", "none").lower()
        
        if export_format == "none" or not dataset:
            input_data["export_url"] = None
            return input_data
            
        logger.info(f"[{session_id}] ExportAgent generating {export_format} for {len(dataset)} items.")
        
        export_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        owner_prefix = input_data.get("owner_id", "")
        base_filename = f"{owner_prefix}_webiscrap_{timestamp}_{export_id[:8]}" if owner_prefix else f"webiscrap_{timestamp}_{export_id[:8]}"
        file_path = ""
        download_url = ""
        
        try:
            df = pd.DataFrame(dataset)
            # C7: Sanitize all cell values before export
            df = df.map(sanitize_cell_value)
            
            if export_format == "csv":
                file_path = os.path.join(EXPORT_DIR, f"{base_filename}.csv")
                df.to_csv(file_path, index=False)
            elif export_format == "excel":
                file_path = os.path.join(EXPORT_DIR, f"{base_filename}.xlsx")
                df.to_excel(file_path, index=False)
            elif export_format == "json":
                file_path = os.path.join(EXPORT_DIR, f"{base_filename}.json")
                df.to_json(file_path, orient="records", indent=2)
            elif export_format == "markdown":
                file_path = os.path.join(EXPORT_DIR, f"{base_filename}.md")
                md_table = df.to_markdown(index=False)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(md_table)
            else:
                logger.warning(f"[{session_id}] Unsupported export format: {export_format}")
                input_data["export_url"] = None
                return input_data
                
            # Assume we have an endpoint that serves files from the exports directory
            download_url = f"/api/export/download/{os.path.basename(file_path)}"
            
            logger.info(f"[{session_id}] Export generated: {file_path}")
            
        except Exception as e:
            logger.error(f"[{session_id}] Export generation failed: {str(e)}")
            download_url = None
            
        input_data["export_url"] = download_url
        return input_data

export_agent = ExportAgent()
