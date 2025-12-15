VALIDATION REQUIREMENTS:
- Output must be valid {output_format} format that can be decoded to JSON
- All required fields for target provider must be present
- Server configurations must be complete (command, args, env)
- No empty or null values in critical fields
- Environment variables must be key-value pairs
- Command paths should be reasonable (no obviously invalid paths)

If validation fails, correct the output and try again.