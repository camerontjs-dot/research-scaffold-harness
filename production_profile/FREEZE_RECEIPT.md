# Freeze Receipt — Contract C 2.0 Promotion Consumer B Conformance RC0

Freeze order: exact frozen Consumer B subject -> preregistration -> evaluator -> this receipt -> workflow execution.

Independent Consumer B subject: `ba09743b28e57bc87dd1f315046ef79b93f24021`.

Exact Apparatus production-promotion subject: `b42c827acb0a9fe65353354d709add0e27bab307`.

Frozen experiment blobs:

- `production_profile/PREREGISTRATION.md`: `4d43beb805f081098d63f48fb8de7e03a0d47ef9`;
- `production_profile/evaluate.py`: `ed1f47d13180f1f96bca13e731c51ad7576e3244`.

Frozen independent subject blobs remain:

- `candidate/consumer.py`: `1f0e64d22f11d7dbe620fef209852870e6b5203d`;
- `candidate/test_consumer.py`: `54e03ff388974fb3524b164c17b7af9f7cf9870c`;
- `candidate/FREEZE_RECEIPT.json`: `1f57979b23eb37d8611acfb58b288e4952eaa717`.

This gate does not modify Consumer B or its prereveal tests. Any change to those frozen subject blobs invalidates this experiment. Any post-freeze change to the preregistration or evaluator requires a successor gate identity.
