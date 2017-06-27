zip benzoin.py.zip benzoin.py
aws lambda update-function-code --profile auth0-ex  --zip-file 'fileb://benzoin.py.zip' --function-name Benzoin-initialize_snapshot_tags
aws lambda update-function-code --profile auth0-ex  --zip-file 'fileb://benzoin.py.zip' --function-name Benzoin-create_validation_instance
aws lambda update-function-code --profile auth0-ex  --zip-file 'fileb://benzoin.py.zip' --function-name Benzoin-wait_for_snapshot_validation
aws lambda update-function-code --profile auth0-ex  --zip-file 'fileb://benzoin.py.zip' --function-name Benzoin-apply_retention_policy
aws lambda update-function-code --profile auth0-ex  --zip-file 'fileb://benzoin.py.zip' --function-name Benzoin-success
aws lambda update-function-code --profile auth0-ex  --zip-file 'fileb://benzoin.py.zip' --function-name Benzoin-error_handler
aws lambda update-function-code --profile auth0-ex  --zip-file 'fileb://benzoin.py.zip' --function-name Benzoin-terminate_instances
rm benzoin.py.zip



