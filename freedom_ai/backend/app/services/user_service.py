"""
用户服务层
"""
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.logging import app_logger


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, username: str, nickname: Optional[str] = None) -> User:
        """
        获取或创建用户
        
        Args:
            username: 用户名
            nickname: 昵称
            
        Returns:
            用户对象
        """
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            user = User(
                username=username,
                nickname=nickname or username,
                is_active=True,
                is_online=True
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            app_logger.info(f"创建新用户: {username}")
        
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_user_profile(self, user_id: int, profile_data: Dict) -> Optional[User]:
        """
        更新用户画像
        
        Args:
            user_id: 用户ID
            profile_data: 画像数据
            
        Returns:
            更新后的用户对象
        """
        user = self.get_user_by_id(user_id)
        if user:
            user.profile = {**user.profile, **profile_data}
            self.db.commit()
            self.db.refresh(user)
            app_logger.info(f"更新用户画像: user_id={user_id}")
        return user
    
    def update_user_preferences(self, user_id: int, preferences: Dict) -> Optional[User]:
        """
        更新用户偏好
        
        Args:
            user_id: 用户ID
            preferences: 偏好数据
            
        Returns:
            更新后的用户对象
        """
        user = self.get_user_by_id(user_id)
        if user:
            user.preferences = {**user.preferences, **preferences}
            self.db.commit()
            self.db.refresh(user)
            app_logger.info(f"更新用户偏好: user_id={user_id}")
        return user
    
    def set_user_online_status(self, user_id: int, is_online: bool):
        """设置用户在线状态"""
        user = self.get_user_by_id(user_id)
        if user:
            user.is_online = is_online
            self.db.commit()


def get_user_service(db: Session) -> UserService:
    """获取用户服务实例"""
    return UserService(db)
