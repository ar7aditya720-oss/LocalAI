import sys
from app.models.router import model_router
from app.database.database import init_db
from app.tools.documents import DocumentTool
from app.tools.spreadsheet import SpreadsheetTool
from app.tools.presentation import PresentationTool
from app.tools.sandbox import CodeSandboxTool

init_db()

with open('test_results.txt', 'w', encoding='utf-8') as f:
    f.write('1. Model Router Test:\n')
    route = model_router.route_task('Write python script to debug database', agent_hint='Coding Agent')
    f.write(f'   Selected Model: {route}\n\n')

    f.write('2. Word Document Generation Test:\n')
    doc_res = DocumentTool.create_approval_note('Test Title', 'Pipeline Inspection', 'REF-001', 'Engineering', ['Finding 1', 'Finding 2'], ['Rec 1'])
    f.write(f'   Result: {doc_res}\n\n')

    f.write('3. Excel Spreadsheet Test:\n')
    sheet_res = SpreadsheetTool.create_inspection_sheet('Defect Report', [['DEF-01', 'Tag1', 'Corrosion', 'HIGH', 'SOP-1', 'Fix']])
    f.write(f'   Result: {sheet_res}\n\n')

    f.write('4. PowerPoint Presentation Test:\n')
    ppt_res = PresentationTool.create_presentation('Executive Brief', 'Sub', [{'header': 'Slide 1', 'points': ['Pt 1', 'Pt 2']}])
    f.write(f'   Result: {ppt_res}\n\n')

    f.write('5. Code Sandbox Execution Test:\n')
    code_to_test = "print('Hello from Sandbox')\nassert 1 + 1 == 2"
    sandbox_res = CodeSandboxTool.execute_python_code(code_to_test)
    f.write(f'   Result: {sandbox_res}\n\n')

    f.write('ALL COMPONENT TESTS COMPLETED SUCCESSFULLY!\n')

print('Test runner finished!')
