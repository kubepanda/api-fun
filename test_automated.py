import os
import subprocess

# Set environment variables
os.environ["TABLE_NAME"] = "test-table"
os.environ["BUCKET_NAME"] = "image-bucket-segregations"

# Map test files to corresponding lambda modules
test_to_lambda = {
    "test_delete_image.py": "lambda_functions.handler_delete",
    "test_lambda_authorizer.py": "lambda_functions.authorizer",
    "test_list_images.py": "lambda_functions.handler_list",
    "test_upload.py": "lambda_functions.handler_upload",
    "test_view_image.py": "lambda_functions.handler_view"
}

for test_file, lambda_module in test_to_lambda.items():
    print(f"\nRunning {test_file} with coverage for {lambda_module}...")
    subprocess.run(
        [
            "pytest",
            f'test/{test_file}',
            "-v",
            f"--cov={lambda_module}",
            "--cov-report=term-missing"
        ],
        check=True
    )