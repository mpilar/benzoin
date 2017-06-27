zip benzoin.py.zip benzoin.py
aws lambda create-function --profile auth0-ex --runtime python3.6  --runtime python3.6 --role 'arn:aws:iam::201973737062:role/benzoin_lambda_role' --zip-file 'fileb://benzoin.py.zip' --timeout 90 --function-name Benzoin-initialize_snapshot_tags  --handler 'benzoin.initialize_snapshot_tags'
aws lambda create-function --profile auth0-ex --runtime python3.6  --runtime python3.6 --role 'arn:aws:iam::201973737062:role/benzoin_lambda_role' --zip-file 'fileb://benzoin.py.zip' --timeout 90 --function-name Benzoin-create_validation_instance  --handler 'benzoin.create_validation_instance'
aws lambda create-function --profile auth0-ex --runtime python3.6  --runtime python3.6 --role 'arn:aws:iam::201973737062:role/benzoin_lambda_role' --zip-file 'fileb://benzoin.py.zip' --timeout 90 --function-name Benzoin-wait_for_snapshot_validation  --handler 'benzoin.wait_for_snapshot_validation'
aws lambda create-function --profile auth0-ex --runtime python3.6  --runtime python3.6 --role 'arn:aws:iam::201973737062:role/benzoin_lambda_role' --zip-file 'fileb://benzoin.py.zip' --timeout 90 --function-name Benzoin-apply_retention_policy  --handler 'benzoin.apply_retention_policy'
aws lambda create-function --profile auth0-ex --runtime python3.6  --runtime python3.6 --role 'arn:aws:iam::201973737062:role/benzoin_lambda_role' --zip-file 'fileb://benzoin.py.zip' --timeout 90 --function-name Benzoin-success  --handler 'benzoin.success'
aws lambda create-function --profile auth0-ex --runtime python3.6  --runtime python3.6 --role 'arn:aws:iam::201973737062:role/benzoin_lambda_role' --zip-file 'fileb://benzoin.py.zip' --timeout 90 --function-name Benzoin-error_handler  --handler 'benzoin.error_handler'
aws lambda create-function --profile auth0-ex --runtime python3.6  --runtime python3.6 --role 'arn:aws:iam::201973737062:role/benzoin_lambda_role' --zip-file 'fileb://benzoin.py.zip' --timeout 90 --function-name Benzoin-terminate_instances  --handler 'benzoin.terminate_instances'
rm benzoin.py.zip



