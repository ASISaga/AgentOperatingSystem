# Testing & Validation

## Run Validation Tests

```bash
cd /path/to/SelfLearningAgent
python validation_test.py
```

## Test A2A Communication

```bash
python test_consolidated.py
```

## Monitoring and Health Checks

```python
health = await orchestrator.health_check()
print(health)
```
