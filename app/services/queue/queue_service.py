"""
Queue Service Module
"""

import asyncio
from typing import Optional, Callable, Dict, List, Any
from datetime import datetime
from enum import Enum
import uuid

from app.utils.logger import LoggerMixin


class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueueTask:
    """Queue task entity"""
    
    def __init__(self, task_type: str, data: Any = None, 
                 priority: TaskPriority = TaskPriority.NORMAL,
                 callback: Optional[Callable] = None):
        self.id = str(uuid.uuid4())
        self.task_type = task_type
        self.data = data
        self.priority = priority
        self.callback = callback
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'task_type': self.task_type,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
        }


class QueueService(LoggerMixin):
    """Service for managing task queues"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QueueService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.tasks: Dict[str, QueueTask] = {}
        self.queue: List[QueueTask] = []
        self.history: List[QueueTask] = []
        self._processing = False
        self.max_concurrent = 2
        self.active_tasks = 0
        self.logger.info("QueueService initialized")
    
    async def add_task(self, task_type: str, data: Any = None,
                      priority: TaskPriority = TaskPriority.NORMAL,
                      callback: Optional[Callable] = None) -> str:
        """
        Add task to queue
        
        Args:
            task_type: Type of task
            data: Task data
            priority: Task priority
            callback: Callback function
            
        Returns:
            Task ID
        """
        task = QueueTask(task_type, data, priority, callback)
        self.tasks[task.id] = task
        self.queue.append(task)
        
        # Sort by priority (higher first)
        self.queue.sort(key=lambda t: t.priority.value, reverse=True)
        
        self.logger.debug(f"Task added: {task.id} ({task_type})")
        
        # Start processing if not running
        if not self._processing:
            asyncio.create_task(self._process_queue())
        
        return task.id
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if cancelled
        """
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            
            if task in self.queue:
                self.queue.remove(task)
            
            self.history.append(task)
            self.logger.info(f"Task cancelled: {task_id}")
            return True
        
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get task status"""
        task = self.tasks.get(task_id)
        return task.status if task else None
    
    async def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get task result"""
        task = self.tasks.get(task_id)
        return task.result if task else None
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        pending = sum(1 for t in self.queue if t.status == TaskStatus.PENDING)
        running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
        
        return {
            'pending': pending,
            'running': running,
            'total_tasks': len(self.tasks),
            'completed_today': sum(1 for t in self.history 
                                  if t.status == TaskStatus.COMPLETED 
                                  and t.completed_at 
                                  and t.completed_at.date() == datetime.now().date()),
        }
    
    async def clear_history(self):
        """Clear task history"""
        self.history.clear()
        self.logger.info("Task history cleared")
    
    async def _process_queue(self):
        """Process queue tasks"""
        self._processing = True
        self.logger.info("Queue processing started")
        
        while self.queue:
            # Check concurrent limit
            if self.active_tasks >= self.max_concurrent:
                await asyncio.sleep(0.5)
                continue
            
            # Get next task
            if not self.queue:
                break
            
            task = self.queue.pop(0)
            
            if task.status == TaskStatus.CANCELLED:
                continue
            
            # Execute task
            asyncio.create_task(self._execute_task(task))
            
            await asyncio.sleep(0.1)
        
        self._processing = False
        self.logger.info("Queue processing finished")
    
    async def _execute_task(self, task: QueueTask):
        """Execute a single task"""
        self.active_tasks += 1
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        self.logger.info(f"Executing task: {task.id} ({task.task_type})")
        
        try:
            # Execute based on task type
            if task.task_type == 'download_video':
                result = await self._handle_download(task.data)
            elif task.task_type == 'download_subtitle':
                result = await self._handle_subtitle(task.data)
            elif task.task_type == 'generate_subtitle':
                result = await self._handle_generate(task.data)
            elif task.task_type == 'translate':
                result = await self._handle_translate(task.data)
            elif task.callback:
                result = await task.callback(task.data)
            else:
                result = None
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            self.logger.info(f"Task completed: {task.id}")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self.logger.error(f"Task failed: {task.id} - {e}")
        
        finally:
            task.completed_at = datetime.now()
            self.history.append(task)
            self.active_tasks -= 1
    
    async def _handle_download(self, data: Dict) -> Any:
        """Handle download task"""
        from app.services.download.download_service import DownloadService
        service = DownloadService()
        return await service.start_download(
            data['download_id'],
            data.get('quality', '720p')
        )
    
    async def _handle_subtitle(self, data: Dict) -> Any:
        """Handle subtitle task"""
        from app.services.subtitle.subtitle_service import SubtitleService
        service = SubtitleService()
        return await service.process_subtitles(
            data['url'],
            data.get('video_path')
        )
    
    async def _handle_generate(self, data: Dict) -> Any:
        """Handle generate task"""
        from app.services.speech.speech_service import SpeechService
        service = SpeechService()
        return await service.transcribe_audio(data['audio_path'])
    
    async def _handle_translate(self, data: Dict) -> Any:
        """Handle translate task"""
        from app.services.translation.translation_service import TranslationService
        service = TranslationService()
        return await service.translate_text(
            data['text'],
            data.get('source_lang', 'en'),
            data.get('target_lang', 'ar')
        )