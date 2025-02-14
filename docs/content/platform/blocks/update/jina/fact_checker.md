
## Fact Checker

### What it is
A tool that analyzes statements and determines their factual accuracy using Jina AI's advanced fact-checking technology.

### What it does
This component examines a given statement and provides a comprehensive assessment of its truthfulness, including a numerical score, a yes/no result, and a detailed explanation of the reasoning behind the assessment.

### How it works
When you provide a statement, the system sends it to Jina AI's specialized fact-checking service. The service analyzes the statement against its knowledge base and returns a detailed evaluation of the statement's factuality. The results are presented in an easy-to-understand format that includes both numerical and written assessments.

### Inputs
- Statement: The text you want to verify (such as "The Earth is round" or "Paris is the capital of Italy")
- Credentials: Your Jina AI account information (automatically handled by the system)

### Outputs
- Factuality Score: A number that indicates how factual the statement is (higher numbers mean more factual)
- Result: A simple yes/no determination of whether the statement is factual
- Reason: A written explanation of why the statement was determined to be true or false
- Error Message: If something goes wrong during the checking process, you'll receive an explanation of what happened

### Possible use cases
A news organization could use this tool to quickly verify facts in their articles before publication. For example, if a reporter writes "Company X announced record profits in 2023," the fact checker could verify this statement against reliable sources and provide a confidence score along with supporting evidence or contradictions.

