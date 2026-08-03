from app.parsers.msbuild.msbuild_parser import MsBuildParser

text = """
ErrorHandling\\ExceptionHandler.cs(2,24): error CS0234: O nome do tipo ou do namespace 'Toolbox' não existe no namespace 'Custom.Framework'

Services\\EmailService.cs(10,5): warning CS0618: Método obsoleto

4 Warning(s)
1 Error(s)
"""

parser = MsBuildParser()

result = parser.parse(text)

print(result.summary.total_errors)
print(result.summary.total_warnings)

print(result.errors[0].code)
print(result.warnings[0].code)