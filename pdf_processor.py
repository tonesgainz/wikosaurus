import fitz  # PyMuPDF
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, max_file_size: int = 50 * 1024 * 1024):  # 50MB
        self.max_file_size = max_file_size
        
    def validate_pdf(self, file_path: str) -> Dict[str, any]:
        """Validate PDF file"""
        if not os.path.exists(file_path):
            return {"valid": False, "error": "File not found"}
        
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            return {"valid": False, "error": f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"}
        
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
            
            return {
                "valid": True,
                "file_size": file_size,
                "page_count": page_count
            }
        except Exception as e:
            return {"valid": False, "error": f"Invalid PDF file: {str(e)}"}
    
    def extract_text(self, file_path: str) -> Dict[str, any]:
        """Extract text from PDF"""
        validation = self.validate_pdf(file_path)
        if not validation["valid"]:
            return validation
        
        try:
            doc = fitz.open(file_path)
            text_content = []
            metadata = {
                "page_count": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", "")
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():  # Only add non-empty pages
                    text_content.append({
                        "page": page_num + 1,
                        "text": text.strip()
                    })
            
            doc.close()
            
            # Combine all text
            full_text = "\n\n".join([page["text"] for page in text_content])
            
            return {
                "valid": True,
                "metadata": metadata,
                "page_count": len(text_content),
                "pages": text_content,
                "full_text": full_text,
                "word_count": len(full_text.split()),
                "char_count": len(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return {"valid": False, "error": f"Failed to extract text: {str(e)}"}
    
    def extract_tables(self, file_path: str) -> Dict[str, any]:
        """Extract tables from PDF (basic implementation)"""
        validation = self.validate_pdf(file_path)
        if not validation["valid"]:
            return validation
        
        try:
            doc = fitz.open(file_path)
            tables = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Find tables using PyMuPDF's table detection
                try:
                    page_tables = page.find_tables()
                    for table in page_tables:
                        table_data = table.extract()
                        if table_data:
                            tables.append({
                                "page": page_num + 1,
                                "data": table_data,
                                "rows": len(table_data),
                                "columns": len(table_data[0]) if table_data else 0
                            })
                except Exception as table_error:
                    logger.warning(f"Could not extract tables from page {page_num + 1}: {table_error}")
                    continue
            
            doc.close()
            
            return {
                "valid": True,
                "table_count": len(tables),
                "tables": tables
            }
            
        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {e}")
            return {"valid": False, "error": f"Failed to extract tables: {str(e)}"}
    
    def extract_images(self, file_path: str, output_dir: str) -> Dict[str, any]:
        """Extract images from PDF"""
        validation = self.validate_pdf(file_path)
        if not validation["valid"]:
            return validation
        
        try:
            doc = fitz.open(file_path)
            images = []
            
            os.makedirs(output_dir, exist_ok=True)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                        img_path = os.path.join(output_dir, img_filename)
                        pix.save(img_path)
                        
                        images.append({
                            "page": page_num + 1,
                            "filename": img_filename,
                            "path": img_path,
                            "width": pix.width,
                            "height": pix.height
                        })
                    
                    pix = None
            
            doc.close()
            
            return {
                "valid": True,
                "image_count": len(images),
                "images": images
            }
            
        except Exception as e:
            logger.error(f"Error extracting images from PDF: {e}")
            return {"valid": False, "error": f"Failed to extract images: {str(e)}"}
    
    def get_document_summary(self, file_path: str) -> Dict[str, any]:
        """Get a comprehensive summary of the PDF document"""
        text_result = self.extract_text(file_path)
        if not text_result["valid"]:
            return text_result
        
        tables_result = self.extract_tables(file_path)
        
        summary = {
            "valid": True,
            "file_info": {
                "file_size": text_result.get("file_size", 0),
                "page_count": text_result["page_count"],
                "word_count": text_result["word_count"],
                "char_count": text_result["char_count"]
            },
            "metadata": text_result["metadata"],
            "content": {
                "has_text": text_result["word_count"] > 0,
                "has_tables": tables_result.get("table_count", 0) > 0,
                "table_count": tables_result.get("table_count", 0)
            },
            "text_preview": text_result["full_text"][:1000] + "..." if len(text_result["full_text"]) > 1000 else text_result["full_text"],
            "full_text": text_result["full_text"]
        }
        
        return summary
    
    def analyze_business_content(self, text_content: str) -> Dict[str, any]:
        """Analyze business-relevant content in the text"""
        import re
        
        analysis = {
            "dates": [],
            "amounts": [],
            "emails": [],
            "phone_numbers": [],
            "companies": [],
            "key_terms": []
        }
        
        # Extract dates (various formats)
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            analysis["dates"].extend(matches)
        
        # Extract monetary amounts
        amount_patterns = [
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            r'€\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|dollars?|euros?)\b'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            analysis["amounts"].extend(matches)
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        analysis["emails"] = re.findall(email_pattern, text_content)
        
        # Extract phone numbers
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
        analysis["phone_numbers"] = re.findall(phone_pattern, text_content)
        
        # Extract potential company names (capitalized words)
        company_pattern = r'\b[A-Z][a-z]+ (?:Inc|LLC|Corp|Corporation|Company|Co|Ltd|Limited|GmbH|AG)\b'
        analysis["companies"] = re.findall(company_pattern, text_content)
        
        # Extract cutlery/kitchen related terms
        cutlery_terms = [
            'knife', 'knives', 'fork', 'spoon', 'cutlery', 'kitchen', 'cooking',
            'chef', 'blade', 'handle', 'stainless steel', 'dishwasher safe',
            'warranty', 'quality', 'sharpening', 'maintenance', 'care instructions'
        ]
        
        for term in cutlery_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_content, re.IGNORECASE):
                analysis["key_terms"].append(term)
        
        # Remove duplicates
        for key in analysis:
            analysis[key] = list(set(analysis[key]))
        
        return analysis

