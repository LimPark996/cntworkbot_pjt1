"""
건설/법령 문서 PDF 파서
- 단순 텍스트 추출
"""

import pdfplumber
import json
import os

class PDFParser:
    """단순 PDF 파서 (텍스트만)"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf = pdfplumber.open(pdf_path)
    
    def parse(self) -> dict:
        """전체 문서 파싱"""
        print(f"\n📄 파싱 시작: {os.path.basename(self.pdf_path)}")
        
        parsed_data = {
            "file_name": os.path.basename(self.pdf_path),
            "total_pages": len(self.pdf.pages),
            "pages": []
        }
        
        for i, page in enumerate(self.pdf.pages):
            try:
                # 텍스트 추출
                page_text = page.extract_text() or ""
                
                page_data = {
                    "page_number": i + 1,
                    "content": page_text.strip()
                }
                
                parsed_data["pages"].append(page_data)
                
                if (i + 1) % 50 == 0:
                    print(f"  ✓ {i + 1}/{len(self.pdf.pages)} 페이지")
                    
            except Exception as e:
                print(f"  ✗ 페이지 {i + 1} 오류: {e}")
                parsed_data["pages"].append({
                    "page_number": i + 1,
                    "content": "",
                    "error": str(e)
                })
        
        print(f"✅ 완료: {len(self.pdf.pages)} 페이지\n")
        return parsed_data
    
    def save_parsed_data(self, output_path: str):
        """결과 저장"""
        parsed_data = self.parse()
        
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 저장: {output_path}")
    
    def __del__(self):
        if hasattr(self, 'pdf'):
            self.pdf.close()


def main():
    """배치 실행"""
    
    # 처리할 PDF 파일 리스트
    pdf_files = [
        "건축법(법률)(제21065호)(20251001).pdf"
    ]
    
    raw_dir = "../data/raw"
    output_dir = "../data/processed"
    
    print("\n" + "="*70)
    print("📄 PDF 배치 파싱")
    print("="*70)
    print(f"📋 처리 문서: {len(pdf_files)}개")
    print("="*70)
    
    success = 0
    fail = 0
    
    for filename in pdf_files:
        pdf_path = os.path.join(raw_dir, filename)
        
        # 출력 파일명 생성
        output_filename = filename.replace('.pdf', '_processed.json').replace('.PDF', '_processed.json')
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"\n처리 중: {filename}")
        
        if not os.path.exists(pdf_path):
            print(f"  ✗ 파일 없음: {pdf_path}")
            fail += 1
            continue
        
        try:
            parser = PDFParser(pdf_path)
            parser.save_parsed_data(output_path)
            success += 1
        except Exception as e:
            print(f"  ✗ 실패: {e}")
            import traceback
            traceback.print_exc()
            fail += 1
    
    print("\n" + "="*70)
    print("✅ 배치 파싱 완료")
    print(f"  성공: {success}개")
    print(f"  실패: {fail}개")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()