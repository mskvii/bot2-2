import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PostManager:
    """投稿機能の管理"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self.posts_dir = os.path.join(base_dir, "posts")
        os.makedirs(self.posts_dir, exist_ok=True)
    
    def get_next_post_id(self) -> int:
        """次の投稿IDを取得"""
        existing_posts = [f for f in os.listdir(self.posts_dir) if f.endswith('.json')]
        if not existing_posts:
            return 1
        
        max_id = 0
        for filename in existing_posts:
            try:
                post_id = int(filename.replace('.json', ''))
                max_id = max(max_id, post_id)
            except ValueError:
                continue
        
        return max_id + 1
    
    def save_post(self, user_id: str, content: str, category: str = None, 
                  is_anonymous: bool = False, is_private: bool = False,
                  display_name: str = None, message_id: str = None, 
                  channel_id: str = None, image_url: str = None) -> int:
        """投稿を保存"""
        post_id = self.get_next_post_id()
        
        post_data = {
            "id": post_id,
            "user_id": user_id,
            "content": content,
            "category": category,
            "is_anonymous": is_anonymous,
            "is_private": is_private,
            "display_name": display_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_id": message_id,
            "channel_id": channel_id,
            "image_url": image_url
        }
        
        filename = os.path.join(self.posts_dir, f"{post_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(post_data, f, ensure_ascii=False, indent=2)
        
        return post_id
    
    def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """投稿を取得"""
        filename = os.path.join(self.posts_dir, f"{post_id}.json")
        
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def get_all_posts(self) -> List[Dict[str, Any]]:
        """全投稿を取得"""
        posts = []
        
        for filename in sorted(os.listdir(self.posts_dir)):
            if filename.endswith('.json'):
                try:
                    post_id = int(filename.replace('.json', ''))
                    post = self.get_post(post_id)
                    if post:
                        posts.append(post)
                except ValueError:
                    continue
        
        return posts
    
    def update_post(self, post_id: int, content: str = None, category: str = None, 
                   image_url: str = None) -> bool:
        """投稿を更新"""
        filename = os.path.join(self.posts_dir, f"{post_id}.json")
        
        if not os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                post_data = json.load(f)
            
            if content is not None:
                post_data['content'] = content
            if category is not None:
                post_data['category'] = category
            if image_url is not None:
                post_data['image_url'] = image_url
            
            post_data['updated_at'] = datetime.now().isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, ensure_ascii=False, indent=2)
            
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False
    
    def delete_post(self, post_id: int) -> bool:
        """投稿を削除"""
        filename = os.path.join(self.posts_dir, f"{post_id}.json")
        
        if os.path.exists(filename):
            os.remove(filename)
            return True
        
        return False
    
    def search_posts(self, keyword: str = None, category: str = None, 
                     user_id: str = None) -> List[Dict[str, Any]]:
        """投稿を検索"""
        posts = self.get_all_posts()
        
        if keyword:
            keyword = keyword.lower()
            posts = [p for p in posts if keyword in p.get('content', '').lower()]
        
        if category:
            posts = [p for p in posts if p.get('category') == category]
        
        if user_id:
            posts = [p for p in posts if p.get('user_id') == user_id]
        
        return posts
