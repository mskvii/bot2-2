import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ActionManager:
    """アクション記録機能の管理"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self.actions_dir = os.path.join(base_dir, "actions")
        os.makedirs(self.actions_dir, exist_ok=True)
    
    def save_action_record(self, action_type: str, user_id: str, target_id: str, 
                          action_data: Dict[str, Any] = None) -> None:
        """アクション記録を保存"""
        action_record = {
            'action_type': action_type,
            'user_id': user_id,
            'target_id': target_id,
            'timestamp': datetime.now().isoformat(),
            'data': action_data or {}
        }
        
        action_filename = os.path.join(self.actions_dir, f"action_{action_type}_{user_id}_{target_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(action_filename, 'w', encoding='utf-8') as f:
            json.dump(action_record, f, ensure_ascii=False, indent=2)
        
        logger.info(f"アクション記録完了: {action_type} by user {user_id} on target {target_id}")
