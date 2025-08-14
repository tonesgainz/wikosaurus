import os
import logging
from datetime import datetime, timedelta
from src.models.employee import UploadedDocument, ChatSession, ChatMessage, db

logger = logging.getLogger(__name__)

class DataCleanupService:
    def __init__(self):
        self.retention_days = 30
    
    def cleanup_expired_documents(self):
        """Remove expired documents and their files"""
        try:
            expired_docs = UploadedDocument.query.filter(
                UploadedDocument.expires_at <= datetime.utcnow()
            ).all()
            
            cleaned_count = 0
            for doc in expired_docs:
                # Remove physical file
                if os.path.exists(doc.file_path):
                    try:
                        os.remove(doc.file_path)
                        logger.info(f"Removed file: {doc.file_path}")
                    except OSError as e:
                        logger.error(f"Failed to remove file {doc.file_path}: {e}")
                
                # Remove database record
                db.session.delete(doc)
                cleaned_count += 1
            
            db.session.commit()
            logger.info(f"Cleaned up {cleaned_count} expired documents")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during document cleanup: {e}")
            db.session.rollback()
            return 0
    
    def cleanup_old_chat_sessions(self):
        """Remove chat sessions older than retention period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            # Get old sessions
            old_sessions = ChatSession.query.filter(
                ChatSession.updated_at <= cutoff_date
            ).all()
            
            cleaned_count = 0
            for session in old_sessions:
                # Remove associated messages first
                ChatMessage.query.filter_by(session_id=session.id).delete()
                
                # Remove session
                db.session.delete(session)
                cleaned_count += 1
            
            db.session.commit()
            logger.info(f"Cleaned up {cleaned_count} old chat sessions")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during chat session cleanup: {e}")
            db.session.rollback()
            return 0
    
    def cleanup_orphaned_files(self, upload_dir):
        """Remove files that don't have database records"""
        try:
            if not os.path.exists(upload_dir):
                return 0
            
            # Get all files in upload directory
            files_on_disk = set()
            for root, dirs, files in os.walk(upload_dir):
                for file in files:
                    files_on_disk.add(os.path.join(root, file))
            
            # Get all file paths from database
            db_files = set()
            documents = UploadedDocument.query.all()
            for doc in documents:
                db_files.add(doc.file_path)
            
            # Find orphaned files
            orphaned_files = files_on_disk - db_files
            
            cleaned_count = 0
            for file_path in orphaned_files:
                try:
                    os.remove(file_path)
                    logger.info(f"Removed orphaned file: {file_path}")
                    cleaned_count += 1
                except OSError as e:
                    logger.error(f"Failed to remove orphaned file {file_path}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} orphaned files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during orphaned file cleanup: {e}")
            return 0
    
    def run_full_cleanup(self, upload_dir):
        """Run complete cleanup process"""
        logger.info("Starting data cleanup process...")
        
        doc_count = self.cleanup_expired_documents()
        session_count = self.cleanup_old_chat_sessions()
        file_count = self.cleanup_orphaned_files(upload_dir)
        
        total_cleaned = doc_count + session_count + file_count
        
        logger.info(f"Cleanup completed. Total items cleaned: {total_cleaned}")
        return {
            'documents_cleaned': doc_count,
            'sessions_cleaned': session_count,
            'files_cleaned': file_count,
            'total_cleaned': total_cleaned
        }

def run_cleanup():
    """Standalone function to run cleanup (can be called from cron job)"""
    from src.main import app
    
    with app.app_context():
        cleanup_service = DataCleanupService()
        upload_dir = os.path.join(app.root_path, 'uploads')
        return cleanup_service.run_full_cleanup(upload_dir)

if __name__ == "__main__":
    # Can be run directly for testing
    result = run_cleanup()
    print(f"Cleanup completed: {result}")

